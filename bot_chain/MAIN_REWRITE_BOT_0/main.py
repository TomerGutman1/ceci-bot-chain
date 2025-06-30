"""
0_MAIN_REWRITE_BOT - Text rewriting and normalization service.
"""
import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, UUID4
import openai
import uvicorn

# Add parent directory to path for common imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import setup_logging, get_config, log_api_call, log_gpt_usage

# Initialize
logger = setup_logging('MAIN_REWRITE_BOT_0')
config = get_config('MAIN_REWRITE_BOT_0')
app = FastAPI(title="MAIN_REWRITE_BOT_0", version="1.0.0")

# Configure OpenAI
openai.api_key = config.openai_api_key


class RewriteRequest(BaseModel):
    """Request model for text rewriting."""
    text: str = Field(..., description="Original user text in Hebrew")
    conv_id: str = Field(..., description="Conversation ID for tracking")
    trace_id: Optional[str] = Field(None, description="Request trace ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class Correction(BaseModel):
    """Model for text corrections."""
    type: str = Field(..., description="Type of correction", 
                     pattern="^(spelling|grammar|normalization)$")
    original: str
    corrected: str


class TokenUsage(BaseModel):
    """Model for token usage tracking."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str


class RewriteResponse(BaseModel):
    """Response model for text rewriting."""
    conv_id: str
    clean_text: str
    original_text: str
    corrections: List[Correction] = Field(default_factory=list)
    timestamp: datetime
    layer: str = "0_MAIN_REWRITE_BOT"
    token_usage: Optional[TokenUsage] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    layer: str
    version: str
    uptime_seconds: int
    timestamp: datetime


# Global variables
start_time = datetime.utcnow()

REWRITE_PROMPT = """You are a Hebrew text improvement assistant. Your task is to:
1. Fix spelling and grammar errors
2. Normalize entity names (e.g., "ממשלה 37" instead of "ממשלה שלושים ושבע")
3. Remove unnecessary words while preserving meaning
4. Keep the text concise and clear

Original text: {text}

Return a JSON object with:
- "clean_text": The improved text
- "corrections": Array of corrections made, each with:
  - "type": "spelling", "grammar", or "normalization"
  - "original": The original text segment
  - "corrected": The corrected text segment

Important:
- Preserve the original meaning
- Keep Hebrew text direction (RTL)
- Don't translate or add information
- Focus on clarity and correctness
"""


async def call_gpt(text: str) -> Dict[str, Any]:
    """Call GPT for text rewriting."""
    try:
        messages = [
            {"role": "system", "content": "You are a Hebrew text improvement assistant."},
            {"role": "user", "content": REWRITE_PROMPT.format(text=text)}
        ]
        
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model=config.model,
            messages=messages,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            response_format={"type": "json_object"}
        )
        
        # Extract response
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Log token usage
        usage = response.usage
        log_gpt_usage(
            logger,
            model=config.model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens
        )
        
        return {
            "result": result,
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "model": config.model
            }
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse GPT response: {e}", extra={
            "error_type": "json_decode_error",
            "response_content": content if 'content' in locals() else None
        })
        raise HTTPException(status_code=500, detail="Invalid response format from GPT")
        
    except Exception as e:
        logger.error(f"GPT call failed: {e}", extra={
            "error_type": type(e).__name__,
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail=f"GPT call failed: {str(e)}")


@app.post("/rewrite", response_model=RewriteResponse)
async def rewrite_text(request: RewriteRequest) -> RewriteResponse:
    """Rewrite and improve Hebrew text."""
    start = datetime.utcnow()
    
    logger.info(f"Rewrite request received", extra={
        "conv_id": str(request.conv_id),
        "trace_id": str(request.trace_id) if request.trace_id else None,
        "text_length": len(request.text)
    })
    
    try:
        # Call GPT
        gpt_response = await call_gpt(request.text)
        result = gpt_response["result"]
        
        # Build corrections list
        corrections = []
        if "corrections" in result:
            for corr in result["corrections"]:
                corrections.append(Correction(
                    type=corr.get("type", "normalization"),
                    original=corr.get("original", ""),
                    corrected=corr.get("corrected", "")
                ))
        
        # Create response
        response = RewriteResponse(
            conv_id=request.conv_id,
            clean_text=result.get("clean_text", request.text),
            original_text=request.text,
            corrections=corrections,
            timestamp=datetime.utcnow(),
            token_usage=TokenUsage(**gpt_response["usage"])
        )
        
        # Log success
        duration_ms = (datetime.utcnow() - start).total_seconds() * 1000
        logger.info(f"Rewrite completed", extra={
            "conv_id": str(request.conv_id),
            "duration_ms": duration_ms,
            "corrections_count": len(corrections)
        })
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rewrite failed: {e}", extra={
            "conv_id": str(request.conv_id),
            "error_type": type(e).__name__
        })
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return HealthResponse(
        status="ok",
        layer="0_MAIN_REWRITE_BOT",
        version="1.0.0",
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
    logger.info(f"Starting 0_MAIN_REWRITE_BOT on port {config.port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.port,
        log_level="info"
    )