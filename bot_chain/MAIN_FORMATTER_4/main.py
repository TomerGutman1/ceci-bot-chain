#!/usr/bin/env python3
"""
MAIN Formatter 4 - Format search results into user-friendly responses.

This bot takes ranked and evaluated search results and formats them into 
different output formats including Markdown, JSON, HTML, and plain text.
Supports Hebrew language formatting and different presentation styles.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys

# Add parent directory to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.logging import setup_logging
from common.config import get_config

# Initialize logging and config
logger = setup_logging('MAIN_FORMATTER_4')
config = get_config('MAIN_FORMATTER_4')

app = FastAPI(
    title="MAIN_FORMATTER_4",
    description="Response Formatting Service",
    version="1.0.0"
)

class OutputFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"
    PLAIN_TEXT = "plain_text"
    SUMMARY = "summary"

class PresentationStyle(str, Enum):
    DETAILED = "detailed"      # Full information
    COMPACT = "compact"        # Brief summaries
    LIST = "list"             # Simple list format
    CARDS = "cards"           # Card-style layout
    TABLE = "table"           # Tabular format

class FormattingRequest(BaseModel):
    conv_id: str
    original_query: str
    intent: str
    entities: Dict[str, Any]
    ranked_results: List[Dict[str, Any]]
    evaluation_summary: Optional[Dict[str, Any]] = None
    ranking_explanation: Optional[str] = None
    output_format: Optional[str] = "markdown"
    presentation_style: Optional[str] = "detailed"
    max_results: Optional[int] = 10
    include_metadata: Optional[bool] = True
    include_scores: Optional[bool] = False

class FormattingResponse(BaseModel):
    success: bool
    conv_id: str
    formatted_response: str
    format_used: str
    style_used: str
    total_results: int
    metadata: Dict[str, Any]

# Hebrew month names for date formatting
HEBREW_MONTHS = {
    1: "ינואר", 2: "פברואר", 3: "מרץ", 4: "אפריל",
    5: "מאי", 6: "יוני", 7: "יולי", 8: "אוגוסט",
    9: "ספטמבר", 10: "אוקטובר", 11: "נובמבר", 12: "דצמבר"
}

def format_hebrew_date(date_str: str) -> str:
    """Format date string to Hebrew format."""
    if not date_str:
        return "תאריך לא זמין"
    
    try:
        # Parse date (assuming YYYY-MM-DD format)
        date_obj = datetime.strptime(date_str[:10], "%Y-%m-%d")
        hebrew_month = HEBREW_MONTHS.get(date_obj.month, str(date_obj.month))
        return f"{date_obj.day} ב{hebrew_month} {date_obj.year}"
    except (ValueError, TypeError):
        return date_str

def truncate_hebrew_text(text: str, max_length: int = 150) -> str:
    """Truncate Hebrew text while preserving word boundaries."""
    if not text or len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    # Find last space to avoid cutting words
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.8:  # Don't cut too much
        truncated = truncated[:last_space]
    
    return truncated + "..."

def extract_key_phrases(text: str, max_phrases: int = 3) -> List[str]:
    """Extract key phrases from Hebrew text."""
    if not text:
        return []
    
    # Simple extraction based on sentence structure
    sentences = text.split('.')
    phrases = []
    
    for sentence in sentences[:max_phrases]:
        sentence = sentence.strip()
        if len(sentence) > 20:  # Meaningful sentences
            phrases.append(sentence)
    
    return phrases

def format_government_info(result: Dict[str, Any]) -> str:
    """Format government and decision information with icons."""
    parts = []
    
    if result.get("government_number"):
        parts.append(f"🏛️ ממשלה {result['government_number']}")
    
    if result.get("decision_number"):
        parts.append(f"📋 החלטה {result['decision_number']}")
    
    if result.get("decision_date"):
        date_str = format_hebrew_date(result["decision_date"])
        parts.append(f"📅 {date_str}")
    
    return " | ".join(parts) if parts else "מידע לא זמין"

# Removed generate_decision_link function - URLs come ONLY from database

def format_topics_and_ministries(result: Dict[str, Any]) -> str:
    """Format topics and ministries information with icons."""
    parts = []
    
    topics = result.get("topics", [])
    if topics:
        if len(topics) == 1:
            parts.append(f"🏷️ נושא: {topics[0]}")
        else:
            parts.append(f"🏷️ נושאים: {', '.join(topics[:3])}")
    
    ministries = result.get("ministries", [])
    if ministries:
        if len(ministries) == 1:
            parts.append(f"🏢 משרד: {ministries[0]}")
        else:
            parts.append(f"🏢 משרדים: {', '.join(ministries[:2])}")
    
    return " | ".join(parts) if parts else ""

def format_ranking_info(result: Dict[str, Any]) -> str:
    """Format ranking score information with visual indicators."""
    ranking = result.get("_ranking", {})
    if not ranking:
        return ""
    
    total_score = ranking.get("total_score", 0)
    explanation = ranking.get("explanation", "")
    
    # Visual score indicator
    if total_score >= 0.8:
        score_icon = "⭐⭐⭐⭐⭐"
    elif total_score >= 0.6:
        score_icon = "⭐⭐⭐⭐"
    elif total_score >= 0.4:
        score_icon = "⭐⭐⭐"
    elif total_score >= 0.2:
        score_icon = "⭐⭐"
    else:
        score_icon = "⭐"
    
    return f"{score_icon} ציון: {total_score:.2f} ({explanation})"

# Add table format support
def format_table_response(
    results: List[Dict[str, Any]], 
    query: str, 
    intent: str
) -> str:
    """Format results as a markdown table."""
    lines = []
    lines.append(f"# 📊 תוצאות חיפוש: {query}")
    lines.append(f"\n**נמצאו {len(results)} תוצאות**\n")
    
    # Table header
    lines.append("| # | כותרת | ממשלה | החלטה | תאריך | נושאים | סטטוס |")
    lines.append("|---|-------|--------|--------|--------|---------|--------|")
    
    # Table rows
    for i, result in enumerate(results[:10], 1):  # Limit to 10 for table format
        title = truncate_hebrew_text(result.get('title', 'ללא כותרת'), 40)
        gov = result.get('government_number', '-')
        dec = result.get('decision_number', '-')
        date = format_hebrew_date(result.get('decision_date', ''))
        topics = ', '.join(result.get('topics', [])[:2]) or '-'
        status = result.get('status', '-')
        
        # Status icon
        if status == 'בתוקף':
            status_display = "✅ בתוקף"
        elif status == 'בוטל':
            status_display = "❌ בוטל"
        else:
            status_display = status
        
        lines.append(f"| {i} | {title} | {gov} | {dec} | {date} | {topics} | {status_display} |")
    
    return "\n".join(lines)

def format_markdown_response(
    results: List[Dict[str, Any]], 
    query: str, 
    intent: str,
    style: PresentationStyle,
    include_metadata: bool = True,
    include_scores: bool = False,
    evaluation_summary: Optional[Dict] = None,
    ranking_explanation: Optional[str] = None
) -> str:
    """Format results as Markdown."""
    
    lines = []
    
    # Header and special handling for different intents
    if intent == "count":
        lines.append(f"# 📊 תוצאות ספירה: {query}")
        if results and isinstance(results[0], dict) and "count" in results[0]:
            count = results[0]["count"]
            lines.append(f"\n**✅ מספר ההחלטות:** {count}")
            return "\n".join(lines)
    elif intent == "EVAL" and evaluation_summary:
        # For EVAL intent, return the evaluator's formatted response directly
        print(f"DEBUG: EVAL intent detected! evaluation_summary keys: {evaluation_summary.keys() if evaluation_summary else 'None'}")
        
        # Check if decision was not suitable for analysis
        content_analysis = evaluation_summary.get("content_analysis", {})
        if content_analysis.get("analysis_status") == "not_suitable":
            # Return the informative message about why analysis couldn't be performed
            informative_message = content_analysis.get("informative_message", "")
            if informative_message:
                return informative_message
        
        explanation = evaluation_summary.get("explanation", "")
        print(f"DEBUG: explanation content: {explanation[:100] if explanation else 'Empty'}")
        if explanation:
            return explanation
        else:
            # Fallback if no explanation available
            lines.append(f"# 🔬 ניתוח החלטה: {query}")
            if "error" in content_analysis:
                lines.append(f"\n❌ **שגיאה בניתוח:** {content_analysis['error']}")
                recommendations = evaluation_summary.get("recommendations", [])
                if recommendations:
                    lines.append(f"\n**המלצות:** {', '.join(recommendations)}")
            return "\n".join(lines)
    else:
        lines.append(f"# 🔍 תוצאות חיפוש: {query}")
    
    lines.append(f"\n**נמצאו {len(results)} תוצאות** 📑")
    
    # Ranking explanation
    if ranking_explanation:
        lines.append(f"\n*{ranking_explanation}*")
    
    # Evaluation summary
    if evaluation_summary and include_metadata:
        overall_score = evaluation_summary.get("overall_score", 0)
        relevance_level = evaluation_summary.get("relevance_level", "")
        
        # Map relevance levels to icons
        relevance_icons = {
            "high": "🎯 גבוהה",
            "medium": "🎪 בינונית",
            "low": "⚠️ נמוכה"
        }
        relevance_display = relevance_icons.get(relevance_level.lower(), relevance_level)
        
        lines.append(f"\n**📈 איכות התוצאות:** {overall_score:.2f} ({relevance_display})")
    
    lines.append("\n---\n")
    
    # Results formatting based on style
    for i, result in enumerate(results, 1):
        if style == PresentationStyle.DETAILED:
            # Title with status icon
            title = result.get('title', 'ללא כותרת')
            status = result.get('status', '')
            if status == 'בתוקף':
                status_icon = "✅"
            elif status == 'בוטל':
                status_icon = "❌"
            else:
                status_icon = "📄"
            
            lines.append(f"## {status_icon} {i}. {title}")
            lines.append("")
            lines.append(f"**{format_government_info(result)}**")
            
            # Add clickable link to government decision - ONLY from DB
            decision_url = result.get('decision_url')
            if decision_url and decision_url.strip():
                lines.append(f"🔗 [לינק להחלטה באתר הממשלה]({decision_url})")
            # No fallback - only use URLs from database
            
            lines.append("")
            
            topic_info = format_topics_and_ministries(result)
            if topic_info:
                lines.append(f"**תחומים:** {topic_info}")
                lines.append("")
            
            # Determine if full content was explicitly requested
            full_content_requested = any(phrase in query.lower() for phrase in [
                "תוכן מלא", "התוכן המלא", "את התוכן המלא", 
                "תן לי תוכן מלא", "הבא תוכן מלא", "תוכן מפורט"
            ])
            
            if full_content_requested:
                # Show full content when explicitly requested
                content = result.get('decision_content') or result.get('content', '')
                if content:
                    lines.append(f"📝 **תוכן מלא:**")
                    lines.append("")
                    lines.append(content)
                    lines.append("")
            else:
                # Show only summary for regular requests
                content = result.get('content', '')  # Use summary field only
                if content:
                    summary = truncate_hebrew_text(content, 200)  # Limit to 200 chars
                    lines.append(f"📝 **תקציר:**")
                    lines.append("")
                    lines.append(summary)
                    lines.append("")
            
            if include_scores:
                score_info = format_ranking_info(result)
                if score_info:
                    lines.append(f"*{score_info}*")
                    lines.append("")
            
            lines.append("---")
            lines.append("")
            
        elif style == PresentationStyle.COMPACT:
            title = result.get('title', 'ללא כותרת')
            gov_info = format_government_info(result)
            lines.append(f"**📌 {i}. {title}**")
            lines.append(f"   {gov_info}")
            
            content = result.get('content', '')
            if content:
                summary = truncate_hebrew_text(content, 100)
                lines.append(f"   {summary}")
            lines.append("")
            
        elif style == PresentationStyle.LIST:
            title = result.get('title', 'ללא כותרת')
            gov_num = result.get('government_number', '')
            dec_num = result.get('decision_number', '')
            info = f"(ממשלה {gov_num}, החלטה {dec_num})" if gov_num and dec_num else ""
            lines.append(f"{i}. **{title}** {info}")
    
    return "\n".join(lines)

def format_json_response(
    results: List[Dict[str, Any]], 
    query: str, 
    intent: str,
    include_metadata: bool = True,
    include_scores: bool = False,
    evaluation_summary: Optional[Dict] = None,
    ranking_explanation: Optional[str] = None
) -> str:
    """Format results as JSON."""
    
    # Clean results for JSON output
    clean_results = []
    for result in results:
        clean_result = {
            "id": result.get("id"),
            "title": result.get("title"),
            "content": result.get("content"),
            "government_number": result.get("government_number"),
            "decision_number": result.get("decision_number"),
            "decision_date": result.get("decision_date"),
            "topics": result.get("topics", []),
            "ministries": result.get("ministries", []),
            "status": result.get("status")
        }
        
        if include_scores and "_ranking" in result:
            clean_result["ranking"] = result["_ranking"]
        
        clean_results.append(clean_result)
    
    response_data = {
        "query": query,
        "intent": intent,
        "total_results": len(results),
        "results": clean_results
    }
    
    if include_metadata:
        response_data["metadata"] = {
            "evaluation": evaluation_summary,
            "ranking_explanation": ranking_explanation,
            "formatted_at": datetime.now().isoformat()
        }
    
    return json.dumps(response_data, ensure_ascii=False, indent=2)

def format_html_response(
    results: List[Dict[str, Any]], 
    query: str, 
    intent: str,
    style: PresentationStyle,
    include_metadata: bool = True,
    include_scores: bool = False,
    evaluation_summary: Optional[Dict] = None,
    ranking_explanation: Optional[str] = None
) -> str:
    """Format results as HTML."""
    
    html_parts = [
        "<!DOCTYPE html>",
        "<html dir='rtl' lang='he'>",
        "<head>",
        "    <meta charset='UTF-8'>",
        "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        f"    <title>תוצאות חיפוש: {query}</title>",
        "    <style>",
        "        body { font-family: 'Segoe UI', Tahoma, Arial, sans-serif; margin: 20px; line-height: 1.6; }",
        "        .header { border-bottom: 2px solid #007acc; padding-bottom: 10px; margin-bottom: 20px; }",
        "        .result-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: #f9f9f9; }",
        "        .result-title { color: #007acc; font-size: 1.2em; font-weight: bold; margin-bottom: 8px; }",
        "        .result-meta { color: #666; font-size: 0.9em; margin-bottom: 8px; }",
        "        .result-content { margin-bottom: 10px; }",
        "        .score-info { color: #888; font-size: 0.8em; font-style: italic; }",
        "        .summary-box { background: #e7f3ff; border-left: 4px solid #007acc; padding: 10px; margin-bottom: 20px; }",
        "    </style>",
        "</head>",
        "<body>"
    ]
    
    # Header
    html_parts.append(f"<div class='header'>")
    html_parts.append(f"<h1>תוצאות חיפוש: {query}</h1>")
    html_parts.append(f"<p><strong>נמצאו {len(results)} תוצאות</strong></p>")
    html_parts.append("</div>")
    
    # Summary box
    if (evaluation_summary or ranking_explanation) and include_metadata:
        html_parts.append("<div class='summary-box'>")
        if ranking_explanation:
            html_parts.append(f"<p>{ranking_explanation}</p>")
        if evaluation_summary:
            overall_score = evaluation_summary.get("overall_score", 0)
            relevance_level = evaluation_summary.get("relevance_level", "")
            html_parts.append(f"<p><strong>איכות התוצאות:</strong> {overall_score:.2f} ({relevance_level})</p>")
        html_parts.append("</div>")
    
    # Results
    for i, result in enumerate(results, 1):
        html_parts.append("<div class='result-card'>")
        
        # Title
        title = result.get('title', 'ללא כותרת')
        html_parts.append(f"<div class='result-title'>{i}. {title}</div>")
        
        # Metadata
        gov_info = format_government_info(result)
        topic_info = format_topics_and_ministries(result)
        html_parts.append(f"<div class='result-meta'>{gov_info}")
        if topic_info:
            html_parts.append(f" | {topic_info}")
        html_parts.append("</div>")
        
        # Content
        content = result.get('content', '')
        if content:
            if style == PresentationStyle.COMPACT:
                content = truncate_hebrew_text(content, 200)
            elif style == PresentationStyle.DETAILED:
                content = truncate_hebrew_text(content, 400)
            html_parts.append(f"<div class='result-content'>{content}</div>")
        
        # Scores
        if include_scores:
            score_info = format_ranking_info(result)
            if score_info:
                html_parts.append(f"<div class='score-info'>{score_info}</div>")
        
        html_parts.append("</div>")
    
    html_parts.extend(["</body>", "</html>"])
    
    return "\n".join(html_parts)

def format_plain_text_response(
    results: List[Dict[str, Any]], 
    query: str, 
    intent: str,
    style: PresentationStyle,
    include_metadata: bool = True,
    evaluation_summary: Optional[Dict] = None,
    ranking_explanation: Optional[str] = None
) -> str:
    """Format results as plain text."""
    
    lines = []
    
    # Header
    lines.append(f"תוצאות חיפוש: {query}")
    lines.append("=" * 50)
    lines.append(f"נמצאו {len(results)} תוצאות")
    
    if ranking_explanation:
        lines.append(f"\n{ranking_explanation}")
    
    if evaluation_summary and include_metadata:
        overall_score = evaluation_summary.get("overall_score", 0)
        relevance_level = evaluation_summary.get("relevance_level", "")
        lines.append(f"איכות התוצאות: {overall_score:.2f} ({relevance_level})")
    
    lines.append("\n" + "-" * 50)
    
    # Results
    for i, result in enumerate(results, 1):
        lines.append(f"\n{i}. {result.get('title', 'ללא כותרת')}")
        lines.append(f"   {format_government_info(result)}")
        
        topic_info = format_topics_and_ministries(result)
        if topic_info:
            lines.append(f"   {topic_info}")
        
        content = result.get('content', '')
        if content and style == PresentationStyle.DETAILED:
            content = truncate_hebrew_text(content, 200)
            lines.append(f"   {content}")
        
        lines.append("")
    
    return "\n".join(lines)

def format_summary_response(
    results: List[Dict[str, Any]], 
    query: str, 
    intent: str,
    evaluation_summary: Optional[Dict] = None,
    ranking_explanation: Optional[str] = None
) -> str:
    """Format a brief summary response."""
    
    if intent == "count":
        if results and "count" in results[0]:
            count = results[0]["count"]
            return f"נמצאו {count} החלטות עבור השאילתא '{query}'"
        else:
            return f"לא נמצאו תוצאות עבור השאילתא '{query}'"
    
    if not results:
        return f"לא נמצאו תוצאות עבור השאילתא '{query}'"
    
    if len(results) == 1:
        result = results[0]
        title = result.get('title', 'החלטה')
        gov_info = format_government_info(result)
        return f"נמצאה החלטה: {title} ({gov_info})"
    
    # Multiple results
    summary_parts = [f"נמצאו {len(results)} החלטות עבור '{query}'"]
    
    # Add most recent or highest scored
    first_result = results[0]
    title = truncate_hebrew_text(first_result.get('title', ''), 60)
    summary_parts.append(f"התוצאה הראשונה: {title}")
    
    # Add topics summary
    all_topics = set()
    for result in results[:5]:  # Check first 5 results
        all_topics.update(result.get('topics', []))
    
    if all_topics:
        topics_list = list(all_topics)[:3]  # Show max 3 topics
        summary_parts.append(f"נושאים: {', '.join(topics_list)}")
    
    return " | ".join(summary_parts)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "MAIN_FORMATTER_4"}

@app.post("/format", response_model=FormattingResponse)
async def format_response(request: FormattingRequest):
    """Format search results into the requested output format."""
    
    try:
        logger.info(f"Processing formatting request: {request.conv_id}")
        logger.info(f"Intent: {request.intent}, Has evaluation_summary: {request.evaluation_summary is not None}")
        if request.evaluation_summary:
            logger.info(f"Evaluation summary keys: {list(request.evaluation_summary.keys())}")
        
        # Validate format and style
        try:
            output_format = OutputFormat(request.output_format or "markdown")
            presentation_style = PresentationStyle(request.presentation_style or "detailed")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid format or style: {str(e)}")
        
        # Limit results
        max_results = min(request.max_results or 10, 50)
        limited_results = request.ranked_results[:max_results]
        
        # Format based on output format
        if output_format == OutputFormat.MARKDOWN:
            formatted_content = format_markdown_response(
                limited_results, 
                request.original_query,
                request.intent,
                presentation_style,
                request.include_metadata,
                request.include_scores,
                request.evaluation_summary,
                request.ranking_explanation
            )
            
        elif output_format == OutputFormat.JSON:
            formatted_content = format_json_response(
                limited_results,
                request.original_query,
                request.intent,
                request.include_metadata,
                request.include_scores,
                request.evaluation_summary,
                request.ranking_explanation
            )
            
        elif output_format == OutputFormat.HTML:
            formatted_content = format_html_response(
                limited_results,
                request.original_query,
                request.intent,
                presentation_style,
                request.include_metadata,
                request.include_scores,
                request.evaluation_summary,
                request.ranking_explanation
            )
            
        elif output_format == OutputFormat.PLAIN_TEXT:
            formatted_content = format_plain_text_response(
                limited_results,
                request.original_query,
                request.intent,
                presentation_style,
                request.include_metadata,
                request.evaluation_summary,
                request.ranking_explanation
            )
            
        elif output_format == OutputFormat.SUMMARY:
            formatted_content = format_summary_response(
                limited_results,
                request.original_query,
                request.intent,
                request.evaluation_summary,
                request.ranking_explanation
            )
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {output_format}")
        
        # Prepare metadata
        metadata = {
            "total_input_results": len(request.ranked_results),
            "formatted_results": len(limited_results),
            "format_settings": {
                "output_format": output_format.value,
                "presentation_style": presentation_style.value,
                "include_metadata": request.include_metadata,
                "include_scores": request.include_scores
            },
            "query_info": {
                "intent": request.intent,
                "entities_count": len(request.entities),
                "has_evaluation": request.evaluation_summary is not None,
                "has_ranking": request.ranking_explanation is not None
            },
            "formatted_at": datetime.now().isoformat()
        }
        
        response = FormattingResponse(
            success=True,
            conv_id=request.conv_id,
            formatted_response=formatted_content,
            format_used=output_format.value,
            style_used=presentation_style.value,
            total_results=len(limited_results),
            metadata=metadata
        )
        
        logger.info(f"Formatted {len(limited_results)} results as {output_format.value}")
        return response
        
    except Exception as e:
        logger.error(f"Error in format_response: {e}")
        raise HTTPException(status_code=500, detail=f"Formatting failed: {str(e)}")

@app.get("/formats")
async def get_available_formats():
    """Get available output formats and presentation styles."""
    
    formats = {
        "markdown": {
            "name": "Markdown",
            "description": "טקסט מפורמט עם Markdown",
            "best_for": ["דוחות", "תיעוד", "הצגה מובנית"],
            "supports_styles": ["detailed", "compact", "list"]
        },
        "json": {
            "name": "JSON",
            "description": "נתונים מובנים בפורמט JSON",
            "best_for": ["אפליקציות", "עיבוד אוטומטי", "API"],
            "supports_styles": ["detailed"]
        },
        "html": {
            "name": "HTML",
            "description": "עמוד אינטרנט מעוצב",
            "best_for": ["הצגה בדפדפן", "דוחות מעוצבים"],
            "supports_styles": ["detailed", "compact", "cards"]
        },
        "plain_text": {
            "name": "Plain Text",
            "description": "טקסט פשוט ללא עיצוב",
            "best_for": ["הודעות פשוטות", "התראות"],
            "supports_styles": ["detailed", "compact", "list"]
        },
        "summary": {
            "name": "Summary",
            "description": "סיכום קצר של התוצאות",
            "best_for": ["תגובות מהירות", "הודעות קצרות"],
            "supports_styles": ["compact"]
        }
    }
    
    styles = {
        "detailed": {
            "name": "מפורט",
            "description": "מידע מלא עם כל הפרטים"
        },
        "compact": {
            "name": "קומפקטי",
            "description": "מידע חיוני בלבד"
        },
        "list": {
            "name": "רשימה",
            "description": "רשימה פשוטה של תוצאות"
        },
        "cards": {
            "name": "כרטיסים",
            "description": "תצוגת כרטיסים מעוצבת"
        },
        "table": {
            "name": "טבלה",
            "description": "תצוגה טבלאית"
        }
    }
    
    return {
        "available_formats": formats,
        "available_styles": styles,
        "default_format": "markdown",
        "default_style": "detailed"
    }

@app.get("/templates/{format_name}")
async def get_format_template(format_name: str):
    """Get a template for the specified format."""
    
    templates = {
        "markdown": {
            "header": "# תוצאות חיפוש: {query}\n\n**נמצאו {count} תוצאות**\n\n---\n",
            "result": "## {index}. {title}\n\n**מידע כללי:** {info}\n\n**תוכן:**\n{content}\n\n---\n",
            "footer": "\n*נוצר על ידי CECI-AI*"
        },
        "html": {
            "header": "<h1>תוצאות חיפוש: {query}</h1><p><strong>נמצאו {count} תוצאות</strong></p>",
            "result": "<div class='result-card'><div class='result-title'>{index}. {title}</div><div class='result-meta'>{info}</div><div class='result-content'>{content}</div></div>",
            "footer": "<footer><em>נוצר על ידי CECI-AI</em></footer>"
        },
        "plain_text": {
            "header": "תוצאות חיפוש: {query}\n{'=' * 50}\nנמצאו {count} תוצאות\n{'-' * 50}\n",
            "result": "{index}. {title}\n   {info}\n   {content}\n",
            "footer": "\nנוצר על ידי CECI-AI"
        }
    }
    
    if format_name not in templates:
        raise HTTPException(status_code=404, detail=f"Template not found for format: {format_name}")
    
    return templates[format_name]

if __name__ == "__main__":
    import uvicorn
    
    port = config.port
    logger.info(f"Starting MAIN_FORMATTER_4 on port {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )