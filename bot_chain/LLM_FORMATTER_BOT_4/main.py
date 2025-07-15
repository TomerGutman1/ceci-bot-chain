"""
4_FORMATTER_BOT - LLM-based response formatting service.
Uses GPT-4o-mini to format query results into rich, Hebrew-aware card layouts.
Handles edge cases like plural-gender agreement and dynamic wording.
"""
import os
import sys
import json
import asyncio
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from logging_setup import setup_logger

# Initialize
logger = setup_logger('LLM_FORMATTER_BOT_4', os.getenv('LOG_LEVEL', 'INFO'))
app = FastAPI(title="LLM_FORMATTER_BOT_4", version="2.0.0")

# Configure OpenAI
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


class DataType(str, Enum):
    RANKED_ROWS = "ranked_rows"
    ANALYSIS = "analysis"
    COUNT = "count"
    COMPARISON = "comparison"


class PresentationStyle(str, Enum):
    CARD = "card"           # Rich card layout (default)
    BRIEF = "brief"         # Minimal text
    DETAILED = "detailed"   # Full information


class FormatterRequest(BaseModel):
    """Request model for LLM-based formatting."""
    data_type: DataType = Field(..., description="Type of data to format")
    content: Dict[str, Any] = Field(..., description="Content to format (structure varies by data_type)")
    original_query: str = Field(..., description="Original user query for context")
    presentation_style: PresentationStyle = Field(default=PresentationStyle.CARD)
    locale: str = Field(default="he", description="Language locale")
    conv_id: str = Field(..., description="Conversation ID")
    trace_id: Optional[str] = Field(None)
    include_metadata: bool = Field(default=True)
    include_scores: bool = Field(default=False)
    max_results: int = Field(default=10)


class FormatterMetadata(BaseModel):
    """Metadata about the formatting process."""
    cards_generated: int = 0
    format_type: str = ""
    word_count: int = 0
    truncated: bool = False


class TokenUsage(BaseModel):
    """Token usage tracking."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    cost_usd: float = 0.0


def format_analysis_results(content: Dict[str, Any]) -> str:
    """Format analysis results with scores and text examples."""
    lines = []
    
    # Extract data
    decision = content.get('decision', {})
    evaluation = content.get('evaluation', {})
    explanation = content.get('explanation', '')
    
    # Always use structured data if available for consistency and citations
    # Only use explanation as fallback if no structured data exists
    criteria_breakdown = evaluation.get('content_analysis', {}).get('criteria_breakdown', [])
    if not criteria_breakdown and explanation and "ניתוח החלטת ממשלה" in explanation:
        return explanation
    
    # Otherwise, build our own formatting
    decision_num = decision.get('decision_number', '')
    title = decision.get('title', decision.get('decision_title', 'ללא כותרת'))
    
    lines.append(f"## 🔍 ניתוח החלטת ממשלה {decision_num}")
    lines.append("")
    lines.append(f"**כותרת ההחלטה:** {title}")
    lines.append("")
    
    # Check if we have criteria breakdown
    criteria_breakdown = evaluation.get('content_analysis', {}).get('criteria_breakdown', [])
    if criteria_breakdown:
        lines.append("### 📊 ניתוח מפורט לפי קריטריונים")
        lines.append("")
        
        # Format each criterion as a separate block for better readability
        for criterion in criteria_breakdown:
            name = criterion.get('name', '')
            weight = criterion.get('weight', 0)
            score = criterion.get('score', 0)
            explanation = criterion.get('explanation', '')
            reference = criterion.get('reference_from_document', 'לא נמצא ציטוט')
            
            lines.append(f"**{name}** (משקל: {weight}%)")
            lines.append(f"ציון: {score}/5")
            lines.append(f"*{explanation}*")
            if reference and reference != 'לא נמצא ציטוט':
                lines.append(f"💬 ציטוט: \"{reference}\"")
            lines.append("")  # Empty line
            lines.append("")  # Extra empty line for more spacing
        
        # Overall score section
        final_score = evaluation.get('content_analysis', {}).get('final_score', 0)
        if final_score > 0:
            lines.append("---")  # Separator
            lines.append("")
            lines.append("")  # Extra spacing
            lines.append(f"### 🎯 ציון ישימות כולל: {final_score}/100")
            lines.append("")
            
            if final_score >= 75:
                lines.append("✅ **רמת ישימות: גבוהה**")
            elif final_score >= 50:
                lines.append("⚠️ **רמת ישימות: בינונית**")
            else:
                lines.append("❌ **רמת ישימות: נמוכה**")
            lines.append("")
            lines.append("")  # Extra spacing
    
    # Add summary/conclusions if available
    summary = evaluation.get('content_analysis', {}).get('feasibility_analysis', '')
    if summary:
        lines.append("### 📝 מסקנות מרכזיות")
        lines.append("")
        lines.append(summary)
        lines.append("")
        lines.append("")  # Extra spacing
    
    # Extract recommendations from the explanation text if not in structured data
    recommendations = evaluation.get('recommendations', [])
    
    # If we only have the default recommendation (score), try to extract from explanation
    if len(recommendations) == 1 and "ציון ישימות כולל:" in recommendations[0]:
        # Look for recommendations in the explanation text
        if "המלצות לשיפור" in explanation:
            # Extract the recommendations section
            rec_start = explanation.find("המלצות לשיפור")
            if rec_start > -1:
                rec_text = explanation[rec_start:]
                # Split by common patterns
                rec_lines = rec_text.split('\n')
                extracted_recs = []
                for line in rec_lines[1:]:  # Skip the header line
                    line = line.strip()
                    if line and not line.startswith('🔧') and not line.startswith('###'):
                        # Clean up the line
                        if line.startswith('- '):
                            line = line[2:]
                        if line:
                            extracted_recs.append(line)
                if extracted_recs:
                    recommendations = extracted_recs
    
    # Add recommendations section
    if recommendations and not (len(recommendations) == 1 and "ציון ישימות כולל:" in recommendations[0]):
        lines.append("### 💡 המלצות לשיפור היישום")
        lines.append("")
        
        # Focus on low-scoring criteria for recommendations
        if criteria_breakdown:
            low_score_criteria = [c for c in criteria_breakdown if c.get('score', 0) <= 2]
            if low_score_criteria:
                lines.append("*בהתבסס על הקריטריונים שקיבלו ציון נמוך:*")
                lines.append("")
                for criterion in sorted(low_score_criteria, key=lambda x: x.get('score', 0)):
                    name = criterion.get('name', '')
                    lines.append(f"• **{name}** - מומלץ להוסיף הגדרות ברורות יותר")
                    lines.append("")  # Line break after each recommendation
        
        # Add any additional recommendations
        for rec in recommendations:
            if "ציון ישימות כולל:" not in rec:  # Skip the score recommendation
                lines.append(f"• {rec}")
                lines.append("")  # Line break after each recommendation
        lines.append("")  # Extra spacing at the end
    
    return "\n".join(lines)


def format_decision_typescript_style(decision: Dict[str, Any], index: int, include_full_content: bool = False) -> str:
    """Format a single decision in TypeScript-inspired Hebrew style."""
    lines = []
    
    # Title with number
    title = decision.get('title', decision.get('decision_title', 'ללא כותרת'))
    decision_num = decision.get('decision_number', '')
    lines.append(f"**{index}. החלטה מס' {decision_num}**")
    lines.append(f"📋 {title}")
    lines.append("")  # Add blank line
    
    # Basic details
    gov_num = decision.get('government_number', '')
    lines.append("")  # Add blank line before government number
    lines.append(f"🏢 ממשלה מספר: {gov_num}")
    
    # Format date
    date_str = decision.get('decision_date', '')
    if date_str:
        try:
            if 'T' in date_str:
                date_str = date_str.split('T')[0]
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Hebrew month names
            hebrew_months = {
                1: 'ינואר', 2: 'פברואר', 3: 'מרץ', 4: 'אפריל',
                5: 'מאי', 6: 'יוני', 7: 'יולי', 8: 'אוגוסט',
                9: 'ספטמבר', 10: 'אוקטובר', 11: 'נובמבר', 12: 'דצמבר'
            }
            day = date_obj.day
            month = hebrew_months[date_obj.month]
            year = date_obj.year
            date_str = f"{day} ב{month} {year}"
        except:
            pass
    lines.append("")  # Add blank line before date
    lines.append(f"📅 תאריך: {date_str}")
    
    # Prime minister
    pm = decision.get('prime_minister', '')
    if pm:
        lines.append("")  # Add blank line before prime minister
        lines.append(f"👤 ראש הממשלה: {pm}")
    
    # Policy areas
    policy_areas = decision.get('tags_policy_area', decision.get('topics', []))
    if policy_areas:
        lines.append("")  # Add blank line before policy areas
        if isinstance(policy_areas, list) and policy_areas:
            lines.append(f"🏷️ תחומים: {', '.join(policy_areas)}")
        elif isinstance(policy_areas, str) and policy_areas:
            lines.append(f"🏷️ תחומים: {policy_areas}")
    
    # Summary
    summary = decision.get('summary', '')
    if summary:
        summary = summary.replace('\n', ' ').strip()
        # Truncate if too long
        if len(summary) > 150 and not include_full_content:
            summary = summary[:147] + '...'
        lines.append("")  # Add blank line before summary
        lines.append(f"📝 תקציר: {summary}")
    
    # URL
    url = decision.get('decision_url', '')
    if url and url.startswith('https://www.gov.il'):
        lines.append("")  # Add blank line before URL
        lines.append(f"🔗 קישור: {url}")
    
    # Status
    status = decision.get('operativity', decision.get('status', ''))
    if status in ['operative', 'אופרטיבי', 'active']:
        lines.append("✅ סטטוס: אופרטיבי")
    elif status in ['canceled', 'בוטל', 'cancelled']:
        lines.append("❌ סטטוס: בוטל")
    
    # Full content if requested
    if include_full_content:
        content = decision.get('content', decision.get('decision_content', ''))
        if content and len(str(content)) > 500:
            lines.append("")  # Add blank line before content
            lines.append("📄 מתוך ההחלטה:")
            # Show first 500 chars of content
            content_preview = str(content)[:500]
            if len(str(content)) > 500:
                content_preview += '...'
            lines.append(content_preview)
    
    return '\n'.join(lines)


def format_count_typescript_style(count: int, original_query: str) -> str:
    """Format count result in TypeScript-inspired style."""
    # Extract context from query
    gov_match = re.search(r'ממשלה\s+(?:מס(?:פר)?\s*)?(\d+)', original_query)
    government_number = gov_match.group(1) if gov_match else None
    
    topic_match = re.search(r'בנושא\s+([\u0590-\u05FF\s]+?)(?:\s|\?|$)', original_query)
    topic = topic_match.group(1).strip() if topic_match else None
    
    year_match = re.search(r'(?:ב|מ)?שנת\s+(\d{4})', original_query)
    year = year_match.group(1) if year_match else None
    
    # Build specific response based on query context
    if government_number and topic:
        return f"📊 ממשלה {government_number} קיבלה **{count:,}** החלטות בנושא {topic}"
    
    if government_number and not topic:
        return f"📊 ממשלה {government_number} קיבלה **{count:,}** החלטות בסך הכל"
    
    if topic and year:
        return f"📊 בשנת {year} התקבלו **{count:,}** החלטות בנושא {topic}"
    
    if topic and not year and not government_number:
        return f"📊 נמצאו **{count:,}** החלטות בנושא {topic}"
    
    if year and not topic:
        return f"📊 בשנת {year} התקבלו **{count:,}** החלטות ממשלה"
    
    # Default
    return f"📊 נמצאו **{count:,}** החלטות"


class FormatterResponse(BaseModel):
    """Response model for formatted content."""
    conv_id: str
    formatted_response: str = Field(..., description="Formatted markdown response")
    metadata: FormatterMetadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    token_usage: Optional[TokenUsage] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    layer: str
    version: str
    model: str
    uptime_seconds: int
    timestamp: datetime


# Global variables
start_time = datetime.utcnow()

# Formatting prompts for different data types
FORMATTER_PROMPTS = {
    "ranked_rows": """You are a Hebrew content formatter for Israeli government decisions.
Format the provided search results into a user-friendly Hebrew response using markdown.

Rules:
1. Use clear Hebrew with proper plural-gender agreement
2. Format as decision cards with consistent structure
3. Include status icons: ✅ בתוקף, ❌ בוטל, 📄 אחר
4. For links, use ONLY the decision_url from the data (never generate URLs)
5. Be concise but informative
6. Maximum {max_results} results
7. Format dates as DD/MM/YYYY (e.g., 15/03/2024)
8. CRITICAL: Use ONLY the data provided - NEVER invent decisions, titles, summaries or any other information
9. If no results provided, say "לא נמצאו תוצאות"
10. For URLs: Show link ONLY if decision_url field exists and starts with https://www.gov.il - otherwise completely omit the link line
11. Full Content: If the 'content' field has more than 500 characters, display it in the "תוכן" section. This indicates the user requested full content ("תוכן מלא")

Card Format:
## [icon] [number]. [title]

**ממשלה [government_number] | החלטה [decision_number] | תאריך: [decision_date in DD/MM/YYYY format]**

🔗 [לינק להחלטה באתר הממשלה](url) (only if decision_url exists and is a valid gov.il URL, otherwise omit this line completely)

**תחומים:** [topics and ministries]

📝 **תקציר:**
[summary]

📋 **תוכן:**
[If the result has content field with more than 500 characters, display it here, otherwise omit this section]

---

IMPORTANT: Only if there are MORE than 5 results, add at the end:

### 💡 רוצה לצמצם את התוצאות?
נסה להיות יותר ספציפי:
- **תאריכים מדויקים**: "החלטות בנושא X בין ינואר למרץ 2025"
- **נושא ספציפי**: "החלטות בנושא חינוך יסודי" במקום רק "חינוך"
- **ממשלה ספציפית**: "החלטות בנושא X בממשלה 37"
- **משרד מסוים**: "החלטות משרד החינוך בנושא X"

Input data: {content}
Original query: {query}
Style: {style}""",

    "analysis": """You are a Hebrew content formatter for government decision analysis.
Format the analysis results into a clear, readable Hebrew report - NOT as code or YAML.

CRITICAL: Create a professional analysis report in markdown format with:
1. Clear section headers with emojis for visual appeal
2. Narrative text, NOT technical formats
3. Tables only for criteria scores
4. NO code blocks or YAML - write in normal Hebrew prose
5. Focus on insights and readability

Available data:
- Decision details: {decision_number}, {title}, {government_number}, {decision_date}, {prime_minister}, {committee}, {tags_policy_area}, {summary}, {operativity}, {decision_url}
- Evaluation object with: overall_score, relevance_level, quality_metrics, content_analysis (includes criteria_breakdown), recommendations, confidence, explanation
- Full decision content in {content}

Format as follows:

## 🔍 ניתוח ישימות - החלטת ממשלה {decision_number}

### 📋 פרטי ההחלטה
כותרת: **{title}**
ממשלה {government_number} בראשות {prime_minister} | תאריך: {decision_date}
תחומי מדיניות: {tags_policy_area}

{IF committee exists: ועדה: {committee}}
{IF decision_url exists and starts with https://www.gov.il: 🔗 [קישור להחלטה המלאה]({decision_url})}

### 📊 ניתוח מפורט לפי קריטריונים

{IF evaluation.content_analysis.criteria_breakdown exists, create a markdown table:}
| קריטריון | משקל | ציון (0-5) | הסבר | ציטוט מהטקסט |
|----------|------|------------|-------|---------------|
{For each criterion: | {name} | {weight}% | {score} | {explanation} | {reference_from_document} |}

### 🎯 ציון ישימות כולל: {evaluation.overall_score או evaluation.content_analysis.final_score}/100

{Based on score: 
- 75+: ✅ רמת ישימות גבוהה - ההחלטה כוללת את רוב המרכיבים הנדרשים ליישום מוצלח
- 50-74: ⚠️ רמת ישימות בינונית - ההחלטה דורשת חיזוק במספר תחומים
- <50: ❌ רמת ישימות נמוכה - חסרים מרכיבים קריטיים ליישום אפקטיבי}

### 📝 ממצאים עיקריים
{Write 2-3 paragraphs summarizing the key findings from the analysis, focusing on strengths and weaknesses}

### 💡 המלצות לשיפור הישימות
{List specific recommendations based on low-scoring criteria, written as actionable items}

### 📌 סיכום
{Brief concluding paragraph summarizing the overall assessment}

REMEMBER: Write in flowing Hebrew prose, not technical format!

Input data: {content}
Original query: {query}
Style: {style}""",

    "count": """You are a Hebrew formatter for statistical queries about government decisions.
Format the count result into a clear, concise Hebrew response.

Rules:
1. Use the 📊 icon for statistics
2. Build a descriptive message based on the query context
3. Bold the count number
4. Be precise with Hebrew grammar (singular/plural)
5. Include relevant context (year, topic, government) if available

Examples:
- 📊 מספר החלטות בנושא חינוך: **15**
- 📊 מספר החלטות ממשלה 37 בשנת 2024: **42**
- 📊 מספר החלטות אופרטיביות בתחום ביטחון: **8**

Input data: {content}
Original query: {query}""",

    "comparison": """You are a Hebrew formatter for comparison queries.
Format the comparison results into a Hebrew YAML structure within a single code block.

Rules:
1. Output ONLY a single markdown code block with YAML-like format
2. Use Hebrew field names with emojis
3. Show clear comparisons between entities
4. Include totals and percentages where relevant
5. Use proper Hebrew plural forms

Format as follows:
```yaml
📊 השוואה: {description of comparison}

{entity_1_name}:
  🎯 מספר החלטות: {count}
  🏛️ ממשלות: [{gov1}, {gov2}, ...]
  📅 תקופה: {start_date} - {end_date}
  🏷️ תחומים עיקריים: [{area1}, {area2}, ...]
  📈 אחוז מהסך הכל: {percentage}%

{entity_2_name}:
  🎯 מספר החלטות: {count}
  🏛️ ממשלות: [{gov1}, {gov2}, ...]
  📅 תקופה: {start_date} - {end_date}
  🏷️ תחומים עיקריים: [{area1}, {area2}, ...]
  📈 אחוז מהסך הכל: {percentage}%

📌 סיכום:
  🔸 הבדל במספר החלטות: {difference}
  🔸 תחומים משותפים: [{shared1}, {shared2}, ...]
  🔸 תחומים ייחודיים ל{entity_1}: [{unique1}, ...]
  🔸 תחומים ייחודיים ל{entity_2}: [{unique1}, ...]
```

Use the exact data provided. Format dates as DD/MM/YYYY.

Input data: {content}
Original query: {query}"""
}


async def call_gpt_formatter(
    prompt_template: str,
    content: Dict[str, Any],
    query: str,
    style: str,
    max_results: int
) -> Dict[str, Any]:
    """Call GPT-4o-mini for formatting."""
    try:
        # Truncate content if it has too many results
        truncated_content = content.copy()
        if "results" in truncated_content and isinstance(truncated_content["results"], list):
            # Limit to max_results items
            truncated_content["results"] = truncated_content["results"][:max_results]
            # Also truncate large text fields
            for result in truncated_content["results"]:
                if isinstance(result, dict):
                    # Truncate content field if it exists and is too long
                    if "content" in result and isinstance(result["content"], str) and len(result["content"]) > 1000:
                        result["content"] = result["content"][:997] + "..."
                    # Truncate summary field if it's too long
                    if "summary" in result and isinstance(result["summary"], str) and len(result["summary"]) > 500:
                        result["summary"] = result["summary"][:497] + "..."
        
        # Build the prompt - special handling for analysis
        if isinstance(truncated_content, dict) and 'decision_number' in truncated_content:
            # For analysis, the template expects individual fields
            try:
                prompt = prompt_template.format(
                    decision_number=truncated_content.get('decision_number', ''),
                    title=truncated_content.get('title', ''),
                    government_number=truncated_content.get('government_number', ''),
                    prime_minister=truncated_content.get('prime_minister', ''),
                    decision_date=truncated_content.get('decision_date', ''),
                    committee=truncated_content.get('committee', ''),
                    operativity=truncated_content.get('operativity', ''),
                    decision_url=truncated_content.get('decision_url', ''),
                    tags_policy_area=truncated_content.get('tags_policy_area', ''),
                    summary=truncated_content.get('summary', ''),
                    content=truncated_content.get('content', ''),
                    query=query,
                    style=style
                )
            except KeyError as e:
                logger.error(f"Missing field in analysis template: {e}")
                # Fallback to JSON format
                prompt = f"Format this analysis data in Hebrew:\n\nData: {json.dumps(truncated_content, ensure_ascii=False, indent=2)}\n\nOriginal query: {query}"
        else:
            # Regular format for non-analysis requests
            prompt = prompt_template.format(
                content=json.dumps(truncated_content, ensure_ascii=False, indent=2),
                query=query,
                style=style,
                max_results=max_results
            )
        
        # Safety check: ensure prompt doesn't exceed reasonable size
        MAX_PROMPT_LENGTH = 50000  # ~12.5K tokens approximately
        if len(prompt) > MAX_PROMPT_LENGTH:
            logger.warning(f"Prompt too long ({len(prompt)} chars), truncating content further")
            # Reduce results further
            if "results" in truncated_content:
                truncated_content["results"] = truncated_content["results"][:3]
            prompt = prompt_template.format(
                content=json.dumps(truncated_content, ensure_ascii=False, indent=2),
                query=query,
                style=style,
                max_results=3
            )
            # If still too long, use minimal content
            if len(prompt) > MAX_PROMPT_LENGTH:
                truncated_content = {"results": [], "message": "התוצאות גדולות מדי לעיבוד"}
                prompt = prompt_template.format(
                    content=json.dumps(truncated_content, ensure_ascii=False, indent=2),
                    query=query,
                    style=style,
                    max_results=0
                )
        
        messages = [
            {"role": "system", "content": "You are an expert Hebrew content formatter. Return all responses as a single markdown code block in Hebrew YAML-like format. Be visual and approachable for non-technical users. Use emojis where appropriate."},
            {"role": "user", "content": prompt}
        ]
        
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=os.getenv('MODEL', 'gpt-4o-mini'),
            messages=messages,
            temperature=float(os.getenv('TEMPERATURE', '0.4')),
            max_tokens=int(os.getenv('MAX_TOKENS', '2000'))
        )
        
        # Extract response
        formatted_text = response.choices[0].message.content
        
        # Log token usage
        usage = response.usage
        logger.info(f"Token usage - Total: {usage.total_tokens}, Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}")
        
        # Calculate cost for GPT-4o-mini: $0.15/$0.60 per 1M tokens
        cost_usd = (usage.prompt_tokens * 0.00015 / 1000) + (usage.completion_tokens * 0.0006 / 1000)
        
        return {
            "formatted_text": formatted_text,
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "model": response.model,
                "cost_usd": cost_usd
            }
        }
        
    except Exception as e:
        logger.error(f"GPT formatter call failed: {e}", extra={
            "error_type": type(e).__name__,
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail=f"Formatter GPT call failed: {str(e)}")


def extract_metadata(formatted_text: str, data_type: DataType, content: Dict) -> FormatterMetadata:
    """Extract metadata from formatted response."""
    metadata = FormatterMetadata()
    
    # Count cards/sections
    if data_type == DataType.RANKED_ROWS:
        metadata.cards_generated = formatted_text.count("## ")
        metadata.format_type = "decision_cards"
    elif data_type == DataType.ANALYSIS:
        metadata.cards_generated = 1
        metadata.format_type = "analysis_report"
    elif data_type == DataType.COUNT:
        metadata.cards_generated = 0
        metadata.format_type = "statistic"
    elif data_type == DataType.COMPARISON:
        metadata.cards_generated = 2  # Typically comparing 2 entities
        metadata.format_type = "comparison_table"
    
    # Count words (approximate for Hebrew)
    metadata.word_count = len(formatted_text.split())
    
    # Check if results were truncated
    if data_type == DataType.RANKED_ROWS and isinstance(content, dict):
        results = content.get("results", [])
        if len(results) > 10:  # Default max
            metadata.truncated = True
    
    return metadata


def fallback_format(data_type: DataType, content: Dict, query: str) -> str:
    """Fallback formatting if GPT fails - uses TypeScript style."""
    try:
        if data_type == DataType.COUNT:
            count = content.get("count", 0)
            return format_count_typescript_style(count, query)
        
        elif data_type == DataType.RANKED_ROWS:
            results = content.get("results", [])
            if not results:
                return "😔 לא נמצאו החלטות התואמות לבקשה"
            
            # Check if full content is present
            include_full = any(
                result.get('content', '') and len(str(result.get('content', ''))) > 500 
                for result in results
            )
            
            response_parts = [f"📊 נמצאו {len(results)} החלטות רלוונטיות:\n"]
            
            for i, result in enumerate(results[:10], 1):
                response_parts.append(format_decision_typescript_style(result, i, include_full))
                if i < min(len(results), 10):
                    response_parts.append("\n")  # Add space between decisions
            
            return "\n".join(response_parts)
        
        elif data_type == DataType.ANALYSIS:
            # Try to format analysis with available data in YAML
            decision = content.get("decision", {})
            evaluation = content.get("evaluation", {})
            
            if decision:
                yaml_lines = []
                yaml_lines.append(f"📌 כותרת: {decision.get('title', decision.get('decision_title', ''))}")
                yaml_lines.append(f"מספר החלטה: {decision.get('decision_number', '')}")
                yaml_lines.append(f"🏛️ מספר ממשלה: {decision.get('government_number', '')}")
                yaml_lines.append(f"📅 תאריך: {decision.get('decision_date', '')}")
                yaml_lines.append(f"👤 ראש ממשלה: {decision.get('prime_minister', '')}")
                yaml_lines.append(f"📝 תקציר: {decision.get('summary', '')}")
                
                # Status
                status = decision.get('operativity', '')
                if status == 'operative':
                    status = '✅ פעיל'
                elif status == 'canceled':
                    status = '❌ בוטל'
                else:
                    status = '❓ לא ידוע'
                yaml_lines.append(f"סטטוס: {status}")
                
                # URL
                url = decision.get('decision_url', '')
                if url and url.startswith('https://www.gov.il'):
                    yaml_lines.append(f"🔗 קישור: {url}")
                
                if evaluation:
                    yaml_lines.append("\n🔬 ניתוח:")
                    if evaluation.get('overall_score'):
                        yaml_lines.append(f"  📊 ציון ישימות: {evaluation['overall_score']}/100")
                    if evaluation.get('explanation'):
                        yaml_lines.append(f"  📋 הסבר: {evaluation['explanation']}")
                
                return "```yaml\n" + "\n".join(yaml_lines) + "\n```"
            else:
                return f"```yaml\n❌ שגיאה: {content.get('explanation', 'ניתוח לא זמין')}\n```"
        
        else:
            return "```yaml\n" + json.dumps(content, ensure_ascii=False, indent=2) + "\n```"
            
    except Exception as e:
        logger.error(f"Fallback formatting failed: {e}")
        return "```yaml\n❌ שגיאה: שגיאה בעיצוב התוצאות\n```"


@app.post("/format", response_model=FormatterResponse)
async def format_response(request: FormatterRequest) -> FormatterResponse:
    """Format query results using GPT-4o-mini."""
    start = datetime.utcnow()
    
    logger.info(f"Formatting request received", extra={
        "conv_id": request.conv_id,
        "data_type": request.data_type,
        "style": request.presentation_style,
        "content_keys": list(request.content.keys()) if request.content else []
    })
    
    # Debug logging for decision 2000
    if request.original_query and "2000" in request.original_query:
        print(f"[DEBUG] Decision 2000 request - Full content: {request.content}")
        logger.warning(f"Decision 2000 request - Content: {request.content}")
        
    # Use Python formatting for RANKED_ROWS
    if request.data_type == DataType.RANKED_ROWS:
        results = request.content.get('results', [])
        if not results:
            logger.warning("No results provided but formatter was called")
            return FormatterResponse(
                conv_id=request.conv_id,
                formatted_response="```yaml\n❌ אין תוצאות: לא נמצאו החלטות התואמות לחיפוש\n```",
                metadata=FormatterMetadata(
                    cards_generated=0,
                    format_type="empty_results",
                    word_count=7,
                    truncated=False
                ),
                token_usage=None
            )
        
        # Validate and clean URLs
        for result in results:
            if 'decision_url' in result:
                url = result.get('decision_url', '')
                if url and not url.startswith('https://www.gov.il'):
                    logger.error(f"Invalid URL found: {url}")
                    result['decision_url'] = None  # Remove invalid URLs
        
        # Check if any result has content > 500 chars (indicates full content request)
        include_full = any(
            result.get('content', '') and len(str(result.get('content', ''))) > 500 
            for result in results
        )
        
        # Format using TypeScript-inspired style
        response_parts = []
        
        # Header
        response_parts.append(f"📊 נמצאו {len(results)} החלטות רלוונטיות:\n")
        
        # Format each decision
        for i, result in enumerate(results[:request.max_results], 1):
            response_parts.append(format_decision_typescript_style(result, i, include_full))
            if i < min(len(results), request.max_results):
                response_parts.append("\n")  # Add space between decisions
        
        # Add tips if many results
        if len(results) > 5:
            response_parts.append("\n💡 רוצה לצמצם את התוצאות?")
            response_parts.append("נסה להיות יותר ספציפי:")
            response_parts.append("• **תאריכים מדויקים**: \"החלטות בנושא X בין ינואר למרץ 2025\"")
            response_parts.append("• **נושא ספציפי**: \"החלטות בנושא חינוך יסודי\" במקום רק \"חינוך\"")
            response_parts.append("• **ממשלה ספציפית**: \"החלטות בנושא X בממשלה 37\"")
        
        formatted_response = "\n".join(response_parts)
        
        # Calculate metadata
        word_count = len(formatted_response.split())
        
        # Log the formatted response for debugging
        cards_count = min(len(results), request.max_results)
        logger.info(f"Returning formatted response", extra={
            "conv_id": request.conv_id,
            "response_preview": formatted_response[:200] + "..." if len(formatted_response) > 200 else formatted_response,
            "cards_count": cards_count
        })
        
        return FormatterResponse(
            conv_id=request.conv_id,
            formatted_response=formatted_response,
            metadata=FormatterMetadata(
                cards_generated=cards_count,
                format_type="decision_cards",
                word_count=word_count,
                truncated=len(results) > request.max_results
            ),
            token_usage=None  # No GPT usage for Python formatting
        )
    
    # Use Python formatting for COUNT queries
    if request.data_type == DataType.COUNT:
        count = request.content.get('count', 0)
        formatted_response = format_count_typescript_style(count, request.original_query)
        
        return FormatterResponse(
            conv_id=request.conv_id,
            formatted_response=formatted_response,
            metadata=FormatterMetadata(
                cards_generated=0,
                format_type="count",
                word_count=len(formatted_response.split()),
                truncated=False
            ),
            token_usage=None  # No GPT usage for Python formatting
        )
    
    # Special handling for analysis data type
    if request.data_type == DataType.ANALYSIS and request.content:
        # Log the content structure for debugging
        logger.info(f"Analysis content structure: {list(request.content.keys())}")
        
        # Try Python formatting first for analysis
        try:
            formatted_response = format_analysis_results(request.content)
            
            if formatted_response:
                logger.info("Successfully formatted analysis results with Python formatter")
                return FormatterResponse(
                    conv_id=request.conv_id,
                    formatted_response=formatted_response,
                    metadata=FormatterMetadata(
                        cards_generated=1,
                        format_type="analysis",
                        word_count=len(formatted_response.split()),
                        truncated=False
                    ),
                    token_usage=None  # No GPT usage
                )
        except Exception as e:
            logger.warning(f"Python analysis formatting failed: {e}, falling back to GPT")
        
        # Extract decision data from content
        decision = request.content.get('decision', {})
        logger.info(f"Decision data: {decision}")
        
        # Handle None or empty decision
        if not decision or decision is None:
            logger.error("No decision data provided for analysis")
            return FormatterResponse(
                conv_id=request.conv_id,
                formatted_response="שגיאה: לא נמצאו נתוני החלטה לניתוח.",
                metadata=FormatterMetadata(
                    cards_generated=0,
                    format_type="error",
                    word_count=6,
                    truncated=False
                ),
                token_usage=None
            )
        
        # Flatten the content structure for the prompt
        # The prompt expects fields like {decision_number}, {title}, etc. directly
        # Use safe get with defaults to avoid None values
        decision = decision if isinstance(decision, dict) else {}
        
        flattened_content = {
            "decision_number": decision.get("decision_number", "") or "",
            "title": decision.get("title", decision.get("decision_title", "")) or "",
            "government_number": decision.get("government_number", "") or "",
            "prime_minister": decision.get("prime_minister", "") or "",
            "decision_date": decision.get("decision_date", "") or "",
            "committee": decision.get("committee", "") or "",
            "operativity": decision.get("operativity", "") or "",
            "decision_url": decision.get("decision_url", "") or "",
            "tags_policy_area": decision.get("tags_policy_area", decision.get("topics", [])) or [],
            "summary": decision.get("summary", "") or "",
            "content": decision.get("decision_content", decision.get("content", "")) or "",
            "evaluation": request.content.get("evaluation", {}) or {},
            "explanation": request.content.get("explanation", "") or ""
        }
        
        logger.info(f"Flattened content keys: {list(flattened_content.keys())}")
        
        # Update request content with flattened structure
        request.content = flattened_content
    
    try:
        # Select appropriate prompt template
        prompt_template = FORMATTER_PROMPTS.get(
            request.data_type.value,
            FORMATTER_PROMPTS["ranked_rows"]  # Default
        )
        
        # Call GPT for formatting
        gpt_response = await call_gpt_formatter(
            prompt_template,
            request.content,
            request.original_query,
            request.presentation_style.value,
            request.max_results
        )
        
        formatted_text = gpt_response["formatted_text"]
        
        # Extract metadata
        metadata = extract_metadata(formatted_text, request.data_type, request.content)
        
        # Build response
        response = FormatterResponse(
            conv_id=request.conv_id,
            formatted_response=formatted_text,
            metadata=metadata
        )
        
        # Add token usage
        if gpt_response.get("usage"):
            response.token_usage = TokenUsage(**gpt_response["usage"])
        
        # Log success
        duration_ms = (datetime.utcnow() - start).total_seconds() * 1000
        logger.info(f"Formatting completed", extra={
            "conv_id": request.conv_id,
            "duration_ms": duration_ms,
            "format_type": metadata.format_type,
            "word_count": metadata.word_count
        })
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Formatting failed: {e}", extra={
            "conv_id": request.conv_id,
            "error_type": type(e).__name__,
            "data_type": request.data_type.value
        })
        
        # Special handling for analysis failures
        if request.data_type == DataType.ANALYSIS:
            logger.error(f"Analysis formatting failed - returning default message")
            return FormatterResponse(
                conv_id=request.conv_id,
                formatted_response="מצטערים, לא הצלחנו להציג את הניתוח. נסה שוב מאוחר יותר.",
                metadata=FormatterMetadata(
                    cards_generated=0,
                    format_type="error",
                    word_count=10,
                    truncated=False
                ),
                token_usage=None
            )
        
        # Try fallback formatting for other types
        try:
            fallback_text = fallback_format(
                request.data_type,
                request.content,
                request.original_query
            )
            
            return FormatterResponse(
                conv_id=request.conv_id,
                formatted_response=fallback_text,
                metadata=FormatterMetadata(
                    format_type="fallback",
                    word_count=len(fallback_text.split())
                )
            )
        except:
            # Last resort - return error message
            return FormatterResponse(
                conv_id=request.conv_id,
                formatted_response="מצטערים, אירעה שגיאה בעיבוד התשובה.",
                metadata=FormatterMetadata(
                    format_type="error",
                    word_count=6
                )
            )


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return HealthResponse(
        status="ok",
        layer="4_LLM_FORMATTER_BOT",
        version="2.0.0",
        model=os.getenv('MODEL', 'gpt-4o-mini'),
        uptime_seconds=int(uptime),
        timestamp=datetime.utcnow()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", extra={
        "error_type": type(exc).__name__,
        "path": request.url.path
    })
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


if __name__ == "__main__":
    port = int(os.getenv('PORT', '8017'))
    logger.info(f"Starting LLM_FORMATTER_BOT_4 on port {port}")
    logger.info(f"Using model: {os.getenv('MODEL', 'gpt-4o-mini')}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )