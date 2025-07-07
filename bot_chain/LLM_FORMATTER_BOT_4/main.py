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
import openai
import uvicorn

# Add parent directory to path for common imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import setup_logging, get_config, log_api_call, log_gpt_usage

# Initialize
logger = setup_logging('LLM_FORMATTER_BOT_4')
config = get_config('LLM_FORMATTER_BOT_4')
app = FastAPI(title="LLM_FORMATTER_BOT_4", version="2.0.0")

# Configure OpenAI
openai.api_key = config.openai_api_key


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

Card Format:
## [icon] [number]. [title]

**[government info]**

🔗 [לינק להחלטה באתר הממשלה](url) (only if decision_url exists)

**תחומים:** [topics and ministries]

📝 **תקציר:**
[summary or truncated content]

---

Input data: {content}
Original query: {query}
Style: {style}""",

    "analysis": """You are a Hebrew content formatter for deep government decision analysis.
Format the analysis results into a comprehensive Hebrew response.

Rules:
1. Present the analysis clearly with proper Hebrew formatting
2. Use headers and bullet points for structure
3. Highlight key findings
4. Include the feasibility score if available
5. Be professional but accessible

Format:
# 🔬 ניתוח החלטה: [decision title]

## 📊 ציון ישימות: X/100

### 🎯 ממצאים עיקריים:
- [key points]

### 📋 ניתוח מפורט:
[detailed analysis]

### 💡 המלצות:
[recommendations if any]

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
        # Build the prompt
        prompt = prompt_template.format(
            content=json.dumps(content, ensure_ascii=False, indent=2),
            query=query,
            style=style,
            max_results=max_results
        )
        
        messages = [
            {"role": "system", "content": "You are an expert Hebrew content formatter. Return formatted markdown text."},
            {"role": "user", "content": prompt}
        ]
        
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model=config.model or "gpt-4o-mini",
            messages=messages,
            temperature=config.temperature or 0.4,
            max_tokens=config.max_tokens or 2000
        )
        
        # Extract response
        formatted_text = response.choices[0].message.content
        
        # Log token usage
        usage = response.usage
        log_gpt_usage(
            logger,
            model=response.model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens
        )
        
        return {
            "formatted_text": formatted_text,
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "model": response.model
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
        model=config.model or "gpt-4o-mini",
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
    logger.info(f"Starting LLM_FORMATTER_BOT_4 on port {config.port}")
    logger.info(f"Using model: {config.model or 'gpt-4o-mini'}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.port,
        log_level="info"
    )