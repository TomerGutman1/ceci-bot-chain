"""
4_FORMATTER_BOT - LLM-based response formatting service.
Uses GPT-4o-mini to format query results into rich, Hebrew-aware card layouts.
Handles edge cases like plural-gender agreement and dynamic wording.
"""
import os
import sys
import json
import asyncio
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

    "analysis": """You are a Hebrew content formatter for deep government decision analysis.
Format the analysis results into a comprehensive Hebrew response.

Rules:
1. FIRST show the FULL decision details from the data
2. THEN present the analysis
3. Use the EXACT data provided - do NOT make up any information
4. Include ALL decision metadata before analysis
5. Be professional but accessible

Format:
# 📄 פרטי ההחלטה המלאים

## החלטה {decision_number} - {title}

**ממשלה:** {government_number}  
**ראש ממשלה:** {prime_minister}  
**תאריך:** {decision_date}  
**ועדה:** {committee}  
**מצב:** {operativity}  

🔗 [קישור להחלטה](decision_url)

**תחומים:** {tags_policy_area}

### 📝 תקציר:
{summary}

### 📋 תוכן מלא:
{content}

---

# 🔬 ניתוח ההחלטה

## 📊 ציון ישימות: X/100

### 🎯 ממצאים עיקריים:
- [key points from analysis]

### 📋 ניתוח מפורט:
[detailed analysis]

### 💡 המלצות:
[recommendations if any]

IMPORTANT: Use ONLY the data provided in the input. Do NOT invent or guess any information.

Input data: {content}
Original query: {query}""",

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
Format the comparison results into a clear visual presentation.

Rules:
1. Use tables or side-by-side cards
2. Highlight differences clearly
3. Use consistent formatting for both sides
4. Include totals and percentages
5. Proper Hebrew plural forms

Format suggestions:
- Comparison table with columns
- Side-by-side statistics
- Highlighted differences

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
        
        # Build the prompt
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
            {"role": "system", "content": "You are an expert Hebrew content formatter. Return formatted markdown text."},
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
    """Fallback formatting if GPT fails."""
    try:
        if data_type == DataType.COUNT:
            count = content.get("count", 0)
            return f"📊 מספר התוצאות: **{count}**"
        
        elif data_type == DataType.RANKED_ROWS:
            results = content.get("results", [])
            if not results:
                return "לא נמצאו תוצאות."
            
            lines = [f"# 🔍 תוצאות חיפוש: {query}", f"\n**נמצאו {len(results)} תוצאות**\n"]
            
            for i, result in enumerate(results[:10], 1):
                title = result.get("title", "ללא כותרת")
                gov = result.get("government_number", "")
                dec = result.get("decision_number", "")
                lines.append(f"\n## {i}. {title}")
                lines.append(f"ממשלה {gov} | החלטה {dec}")
                
                if result.get("decision_url"):
                    lines.append(f"🔗 [קישור]({result['decision_url']})")
                
                lines.append("---")
            
            return "\n".join(lines)
        
        elif data_type == DataType.ANALYSIS:
            return content.get("explanation", "ניתוח לא זמין.")
        
        else:
            return json.dumps(content, ensure_ascii=False, indent=2)
            
    except Exception as e:
        logger.error(f"Fallback formatting failed: {e}")
        return "שגיאה בעיצוב התוצאות."


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
        
    # Check if we have actual results
    if request.data_type == DataType.RANKED_ROWS and request.content:
        results = request.content.get('results', [])
        if not results:
            logger.warning("No results provided but formatter was called")
            return FormatterResponse(
                conv_id=request.conv_id,
                formatted_response="לא נמצאו תוצאות עבור השאילתה שלך.",
                metadata=FormatterMetadata(
                    cards_generated=0,
                    format_type="empty_results",
                    word_count=6,
                    truncated=False
                ),
                token_usage=None
            )
            
        # Validate results have real URLs
        for result in results:
            if 'decision_url' in result:
                url = result.get('decision_url', '')
                if url and not url.startswith('https://www.gov.il'):
                    logger.error(f"Invalid URL found: {url}")
                    result['decision_url'] = None  # Remove invalid URLs
    
    # Special handling for analysis data type
    if request.data_type == DataType.ANALYSIS and request.content:
        # Log the content structure for debugging
        logger.info(f"Analysis content structure: {list(request.content.keys())}")
        
        # Extract decision data from content
        decision = request.content.get('decision', {})
        if not decision:
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
        flattened_content = {
            "decision_number": decision.get("decision_number", ""),
            "title": decision.get("title", decision.get("decision_title", "")),
            "government_number": decision.get("government_number", ""),
            "prime_minister": decision.get("prime_minister", ""),
            "decision_date": decision.get("decision_date", ""),
            "committee": decision.get("committee", ""),
            "operativity": decision.get("operativity", ""),
            "decision_url": decision.get("decision_url", ""),
            "tags_policy_area": decision.get("tags_policy_area", decision.get("topics", [])),
            "summary": decision.get("summary", ""),
            "content": decision.get("decision_content", decision.get("content", "")),
            "evaluation": request.content.get("evaluation", {}),
            "explanation": request.content.get("explanation", "")
        }
        
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
            "error_type": type(e).__name__
        })
        
        # Try fallback formatting
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
            raise HTTPException(status_code=500, detail="Formatting failed")


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