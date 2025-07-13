"""
1_INTENT_BOT - Unified text processing and intent detection service.
Combines Hebrew text normalization (formerly REWRITE) with intent classification.
Uses GPT-4o-turbo for superior Hebrew understanding.
"""
import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from uuid import uuid4
from enum import Enum

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from openai import OpenAI
import uvicorn

# Add parent directory to path for common imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logging import setup_logging

# Initialize
logger = setup_logging('UNIFIED_INTENT_BOT_1')
app = FastAPI(title="UNIFIED_INTENT_BOT_1", version="2.0.0")

# Configure OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Intent Enum
class IntentType(str, Enum):
    DATA_QUERY = "DATA_QUERY"
    ANALYSIS = "ANALYSIS"
    RESULT_REF = "RESULT_REF"
    DECISION_GUIDE = "DECISION_GUIDE"
    UNCLEAR = "UNCLEAR"


class UnifiedIntentRequest(BaseModel):
    """Request model for unified intent processing."""
    raw_user_text: str = Field(..., description="Original user text in Hebrew")
    chat_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Previous conversation turns")
    conv_id: str = Field(..., description="Conversation ID for tracking")
    trace_id: Optional[str] = Field(None, description="Request trace ID")


class Correction(BaseModel):
    """Model for text corrections."""
    type: str = Field(..., description="Type of correction: spelling|grammar|normalization")
    original: str
    corrected: str


class RouteFlags(BaseModel):
    """Routing flags for downstream bots."""
    needs_context: bool = False
    is_statistical: bool = False
    is_comparison: bool = False


class TokenUsage(BaseModel):
    """Token usage tracking."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    cost_usd: float = 0.0


class UnifiedIntentResponse(BaseModel):
    """Response model for unified intent processing."""
    conv_id: str
    clean_query: str = Field(..., description="Normalized Hebrew query")
    intent: IntentType = Field(..., description="Detected intent type")
    params: Dict[str, Any] = Field(default_factory=dict, description="Extracted parameters")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    route_flags: RouteFlags = Field(default_factory=RouteFlags)
    corrections: List[Correction] = Field(default_factory=list)
    token_usage: Optional[TokenUsage] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Backward compatibility fields
    intent_type: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    
    @validator('intent_type', always=True)
    def set_intent_type(cls, v, values):
        """Set intent_type for backward compatibility."""
        return values.get('intent', IntentType.UNCLEAR).value
    
    @validator('entities', always=True)
    def set_entities(cls, v, values):
        """Set entities for backward compatibility."""
        return values.get('params', {})


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

# Comprehensive prompt for unified processing
UNIFIED_PROMPT = """You are an expert Hebrew query processor for the Israeli government decisions database.

Your task is to:
1. Normalize the Hebrew text (fix typos, expand abbreviations, convert numbers)
2. Classify the intent as one of: DATA_QUERY, ANALYSIS, RESULT_REF, DECISION_GUIDE, or UNCLEAR
3. Extract all relevant parameters/entities

## Intent Types:
- DATA_QUERY: Searching for decisions (by topic, date, government, etc.)
- ANALYSIS: Deep analysis of a specific decision (keywords: נתח, ניתוח, הסבר לעומק)
- RESULT_REF: Reference to previous results (keywords: הקודם, ששלחת, זה, זו)
- DECISION_GUIDE: Request for help with decision drafting (keywords: עזרה בניסוח, בדוק טיוטה, ניתוח טיוטה, פידבק על החלטה)
- UNCLEAR: Ambiguous or incomplete queries

## Hebrew Number Conversion:
- אחת→1, שתיים→2, שלוש→3, ארבע→4, חמש→5, שש→6, שבע→7, שמונה→8, תשע→9, עשר→10
- עשרים→20, שלושים→30, ארבעים→40, חמישים→50, שישים→60, שבעים→70, שמונים→80, תשעים→90
- Combined: שלושים ושבע→37, עשרים ואחת→21

## Common Typo Corrections:
- החלתה→החלטה, ממשלת→ממשלה, חנוך→חינוך, בראות→בריאות
- נותח→נתח (but preserve נתח/ניתח/ניתוח as analysis keywords)

## Parameter Extraction:
- government_number: ממשלה X (default to 37 if only decision_number given)
- decision_number: החלטה X
- topic: בנושא X, על X, בתחום X
- date_range: {{start: "YYYY-MM-DD", end: "YYYY-MM-DD"}}
- limit: X החלטות (extract number)
- ministries: [list of ministry names]
- decision_type: "אופרטיבית" if mentioned
- comparison_target: for השווה queries

## Date Normalization:
- "השנה" → current year range
- "החודש" → current month range
- "ינואר 2024" → 2024-01-01 to 2024-01-31
- "בין 2020 ל-2023" → {{start: "2020-01-01", end: "2023-12-31"}}
- "ב-2024" → {{start: "2024-01-01", end: "2024-12-31"}}

## Examples:

Input: "החלתה 2983 ממשלת 37 נתח לעומק"
Output: {{
  "clean_query": "החלטה 2983 של ממשלה 37 - ניתוח מעמיק",
  "intent": "ANALYSIS",
  "params": {{
    "decision_number": 2983,
    "government_number": 37,
    "analysis_type": "deep"
  }},
  "confidence": 0.95,
  "route_flags": {{
    "needs_context": false,
    "is_statistical": false,
    "is_comparison": false
  }},
  "corrections": [
    {{"type": "spelling", "original": "החלתה", "corrected": "החלטה"}},
    {{"type": "normalization", "original": "ממשלת", "corrected": "ממשלה"}}
  ]
}}

Input: "כמה החלטות בנושא חינוך היו ב-2024?"
Output: {{
  "clean_query": "כמה החלטות בנושא חינוך היו ב-2024?",
  "intent": "DATA_QUERY",
  "params": {{
    "topic": "חינוך",
    "date_range": {{"start": "2024-01-01", "end": "2024-12-31"}},
    "count_only": true
  }},
  "confidence": 0.98,
  "route_flags": {{
    "needs_context": false,
    "is_statistical": true,
    "is_comparison": false
  }},
  "corrections": []
}}

Input: "תן לי את ההחלטה השלישית ששלחת"
Output: {{
  "clean_query": "תן לי את ההחלטה השלישית ששלחת",
  "intent": "RESULT_REF",
  "params": {{
    "index_in_previous": 3,
    "reference_type": "sent"
  }},
  "confidence": 0.92,
  "route_flags": {{
    "needs_context": true,
    "is_statistical": false,
    "is_comparison": false
  }},
  "corrections": []
}}

Input: "מה?"
Output: {{
  "clean_query": "מה?",
  "intent": "UNCLEAR",
  "params": {{}},
  "confidence": 0.3,
  "route_flags": {{
    "needs_context": false,
    "is_statistical": false,
    "is_comparison": false
  }},
  "corrections": []
}}

Now process this Hebrew query and return ONLY valid JSON:

Query: {query}
"""


async def call_gpt(query: str, chat_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call GPT-4o-turbo for unified processing."""
    try:
        # Build messages
        messages = [
            {"role": "system", "content": "You are an expert Hebrew query processor. Return only valid JSON."}
        ]
        
        # Add relevant chat history if provided (last 3 turns)
        if chat_history:
            for turn in chat_history[-3:]:
                if turn.get('role') == 'user':
                    messages.append({
                        "role": "assistant", 
                        "content": f"Previous query context: {turn.get('content', '')}"
                    })
        
        # Add current query
        messages.append({
            "role": "user", 
            "content": UNIFIED_PROMPT.format(query=query)
        })
        
        # Call OpenAI
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=os.getenv('MODEL', 'gpt-4o'),  # Use gpt-4o-turbo
            messages=messages,
            temperature=float(os.getenv('TEMPERATURE', '0.3')),
            max_tokens=int(os.getenv('MAX_TOKENS', '500')),
            response_format={"type": "json_object"}
        )
        
        # Extract response
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Log token usage
        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            logger.info(f"Token usage - Total: {usage.total_tokens}, Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}")
        else:
            usage = None
        
        # Calculate cost
        model_name = response.model if hasattr(response, 'model') else os.getenv('MODEL', 'gpt-4o')
        cost_usd = 0.0
        if usage:
            # GPT-4o pricing: $5/$15 per 1M tokens
            cost_usd = (usage.prompt_tokens * 0.005 / 1000) + (usage.completion_tokens * 0.015 / 1000)
        
        return {
            "result": result,
            "usage": {
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "total_tokens": usage.total_tokens if usage else 0,
                "model": model_name,
                "cost_usd": cost_usd
            } if usage else None
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse GPT response: {e}", extra={
            "error_type": "json_decode_error",
            "response_content": content if 'content' in locals() else None
        })
        # Return UNCLEAR intent as fallback
        return {
            "result": {
                "clean_query": query,
                "intent": "UNCLEAR",
                "params": {},
                "confidence": 0.0,
                "route_flags": {
                    "needs_context": False,
                    "is_statistical": False,
                    "is_comparison": False
                },
                "corrections": []
            },
            "usage": None
        }
        
    except Exception as e:
        import traceback
        logger.error(f"GPT call failed: {e}\n{traceback.format_exc()}", extra={
            "error_type": type(e).__name__,
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail=f"GPT call failed: {str(e)}")


def post_process_result(result: Dict[str, Any], original_query: str) -> Dict[str, Any]:
    """Post-process GPT result to ensure consistency."""
    # Ensure all required fields exist
    if 'clean_query' not in result:
        result['clean_query'] = original_query
    
    if 'intent' not in result:
        result['intent'] = 'UNCLEAR'
    
    if 'params' not in result:
        result['params'] = {}
    
    if 'confidence' not in result:
        result['confidence'] = 0.5
    
    if 'route_flags' not in result:
        result['route_flags'] = {
            'needs_context': False,
            'is_statistical': False,
            'is_comparison': False
        }
    
    if 'corrections' not in result:
        result['corrections'] = []
    
    # Special handling for specific patterns
    params = result['params']
    
    # If decision_number exists but no government_number, default to 37
    if params.get('decision_number') and not params.get('government_number'):
        params['government_number'] = 37
        logger.info(f"Defaulted to government 37 for decision {params['decision_number']}")
    
    # Set statistical flag for count queries
    if params.get('count_only') or result['intent'] == 'DATA_QUERY' and 'כמה' in original_query:
        result['route_flags']['is_statistical'] = True
    
    # Set comparison flag
    if params.get('comparison_target') or 'השווה' in original_query:
        result['route_flags']['is_comparison'] = True
    
    # Set context flag for RESULT_REF
    if result['intent'] == 'RESULT_REF':
        result['route_flags']['needs_context'] = True
    
    return result


@app.post("/intent", response_model=UnifiedIntentResponse)
async def process_intent(request: UnifiedIntentRequest) -> UnifiedIntentResponse:
    """Process Hebrew query with unified rewrite + intent detection."""
    start = datetime.utcnow()
    
    logger.info(f"Unified intent request received", extra={
        "conv_id": request.conv_id,
        "trace_id": request.trace_id,
        "text_length": len(request.raw_user_text),
        "has_history": bool(request.chat_history)
    })
    
    try:
        # Call GPT for unified processing
        gpt_response = await call_gpt(request.raw_user_text, request.chat_history)
        result = gpt_response["result"]
        
        # Post-process result
        result = post_process_result(result, request.raw_user_text)
        
        # Build response
        response = UnifiedIntentResponse(
            conv_id=request.conv_id,
            clean_query=result['clean_query'],
            intent=IntentType(result['intent']),
            params=result['params'],
            confidence=result['confidence'],
            route_flags=RouteFlags(**result['route_flags']),
            corrections=[Correction(**c) for c in result.get('corrections', [])]
        )
        
        # Add token usage if available
        if gpt_response.get("usage"):
            response.token_usage = TokenUsage(**gpt_response["usage"])
        
        # Log success
        duration_ms = (datetime.utcnow() - start).total_seconds() * 1000
        logger.info(f"Unified intent processing completed", extra={
            "conv_id": request.conv_id,
            "duration_ms": duration_ms,
            "intent": response.intent,
            "confidence": response.confidence,
            "corrections_count": len(response.corrections),
            "has_params": bool(response.params)
        })
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Intent processing failed: {e}", extra={
            "conv_id": request.conv_id,
            "error_type": type(e).__name__
        })
        # Return UNCLEAR intent as fallback
        return UnifiedIntentResponse(
            conv_id=request.conv_id,
            clean_query=request.raw_user_text,
            intent=IntentType.UNCLEAR,
            params={},
            confidence=0.0,
            route_flags=RouteFlags(),
            corrections=[]
        )


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return HealthResponse(
        status="ok",
        layer="1_UNIFIED_INTENT_BOT",
        version="2.0.0",
        model=os.getenv('MODEL', 'gpt-4o'),
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
    port = int(os.getenv('PORT', '8011'))
    logger.info(f"Starting UNIFIED_INTENT_BOT_1 on port {port}")
    logger.info(f"Using model: {os.getenv('MODEL', 'gpt-4o')}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )