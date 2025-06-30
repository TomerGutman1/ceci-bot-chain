"""
1_MAIN_INTENT_BOT - Intent detection and entity extraction service.
"""
import os
import sys
import json
import asyncio
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, UUID4
import requests
import uvicorn

# Add parent directory to path for common imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import setup_logging, get_config, log_api_call, log_gpt_usage
from prompts import build_intent_prompt, validate_intent_response, calculate_confidence_score

# Initialize
logger = setup_logging('MAIN_INTENT_BOT_1')
config = get_config('MAIN_INTENT_BOT_1')
app = FastAPI(title="MAIN_INTENT_BOT_1", version="1.0.0")

# Configure OpenAI
# openai.api_key = config.openai_api_key

# Load taxonomy
with open('/app/schemas/intent_taxonomy.yml', 'r', encoding='utf-8') as f:
    TAXONOMY = yaml.safe_load(f)


class IntentRequest(BaseModel):
    """Request model for intent detection."""
    text: str = Field(..., description="Cleaned text from rewrite bot")
    conv_id: str = Field(..., description="Conversation ID for tracking")
    trace_id: Optional[str] = Field(None, description="Request trace ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Previous conversation context")


class RouteFlags(BaseModel):
    """Model for routing flags."""
    needs_clarification: bool
    has_context: bool
    is_follow_up: bool


class IntentEntities(BaseModel):
    """Model for extracted entities."""
    government_number: Optional[int] = None
    decision_number: Optional[int] = None
    topic: Optional[str] = None
    date_range: Optional[Dict[str, str]] = None
    ministries: Optional[List[str]] = None
    count_target: Optional[str] = None
    comparison_target: Optional[str] = None
    limit: Optional[int] = None


class TokenUsage(BaseModel):
    """Model for token usage tracking."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str


class IntentResponse(BaseModel):
    """Response model for intent detection."""
    conv_id: str
    intent: str = Field(..., pattern="^(search|count|specific_decision|comparison|clarification_needed)$")
    entities: IntentEntities
    confidence: float = Field(..., ge=0, le=1)
    route_flags: RouteFlags
    timestamp: datetime
    layer: str = "1_MAIN_INTENT_BOT"
    token_usage: Optional[TokenUsage] = None
    explanation: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    layer: str
    version: str
    uptime_seconds: int
    timestamp: datetime


# Global variables
start_time = datetime.utcnow()


async def call_gpt_for_intent(text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Call GPT-4 for intent detection."""
    try:
        prompt = build_intent_prompt(text, context)
        
        messages = [
            {"role": "system", "content": "You are an expert Hebrew intent extraction system. Always respond with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        # Debug log
        logger.info(f"Calling GPT with prompt length: {len(prompt)}")
        
        # Call OpenAI API using requests
        headers = {
            "Authorization": f"Bearer {config.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": config.model,
            "messages": messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to OpenAI failed: {e}")
            raise HTTPException(status_code=500, detail=f"OpenAI API request failed: {str(e)}")
        
        if response.status_code != 200:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {response.status_code}")
        
        response_data = response.json()
        content = response_data['choices'][0]['message']['content']
        logger.info(f"GPT raw response: {content[:200]}...")  # Log first 200 chars
        
        result = json.loads(content)
        
        # Validate response structure
        if not validate_intent_response(result):
            logger.error(f"Invalid response structure: {result}")
            raise ValueError("Invalid response structure from GPT")
        
        # Log token usage
        usage = response_data['usage']
        log_gpt_usage(
            logger,
            model=config.model,
            prompt_tokens=usage['prompt_tokens'],
            completion_tokens=usage['completion_tokens'],
            total_tokens=usage['total_tokens']
        )
        
        return {
            "result": result,
            "usage": {
                "prompt_tokens": usage['prompt_tokens'],
                "completion_tokens": usage['completion_tokens'],
                "total_tokens": usage['total_tokens'],
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
            "error_message": str(e),
            "traceback": str(e.__traceback__)
        })
        raise HTTPException(status_code=500, detail=f"GPT call failed: {str(e)}")


def normalize_entities(entities: Dict[str, Any]) -> IntentEntities:
    """Normalize and validate extracted entities."""
    # Government number normalization
    gov_num = entities.get("government_number")
    if isinstance(gov_num, str):
        # Convert Hebrew numbers to digits
        hebrew_to_digit = {
            "שלושים ושבע": 37,
            "שלושים וחמש": 35,
            "שלושים ושש": 36,
            "שלושים ושמונה": 38
        }
        gov_num = hebrew_to_digit.get(gov_num.strip(), None)
    
    # Topic normalization
    topic = entities.get("topic")
    if topic:
        topic = topic.strip()
        # Remove common prefixes
        for prefix in ["בנושא", "על", "לגבי"]:
            if topic.startswith(prefix + " "):
                topic = topic[len(prefix):].strip()
    
    # Ministry normalization
    ministries = entities.get("ministries")
    if ministries:
        normalized_ministries = []
        ministry_map = {
            "החינוך": "משרד החינוך",
            "הביטחון": "משרד הביטחון",
            "האוצר": "משרד האוצר",
            "משה\"ב": "משרד הביטחון"
        }
        for ministry in ministries:
            normalized = ministry_map.get(ministry, ministry)
            normalized_ministries.append(normalized)
        ministries = normalized_ministries
    
    return IntentEntities(
        government_number=gov_num,
        decision_number=entities.get("decision_number"),
        topic=topic,
        date_range=entities.get("date_range"),
        ministries=ministries,
        count_target=entities.get("count_target"),
        comparison_target=entities.get("comparison_target"),
        limit=entities.get("limit")
    )


def determine_routing(intent: str, confidence: float, entities: IntentEntities, text: str) -> RouteFlags:
    """Determine routing flags based on intent and entities."""
    needs_clarification = False
    has_context = False
    is_follow_up = False
    
    # Check if clarification is needed
    threshold_str = TAXONOMY['routing_rules']['needs_clarification']['conditions'][0].split('<')[1].strip()
    threshold = float(threshold_str)
    if confidence < threshold:
        needs_clarification = True
    
    if intent == "clarification_needed":
        needs_clarification = True
    
    # Check for context indicators
    context_words = ["זה", "זו", "אלה", "אתמול", "השנה", "הפעם הקודמת"]
    if any(word in text for word in context_words):
        has_context = True
        is_follow_up = True
    
    # Check for missing required entities
    if intent == "specific_decision" and not entities.decision_number:
        needs_clarification = True
    
    if intent == "count" and not entities.count_target:
        needs_clarification = True
    
    return RouteFlags(
        needs_clarification=needs_clarification,
        has_context=has_context,
        is_follow_up=is_follow_up
    )


@app.post("/intent", response_model=IntentResponse)
async def extract_intent(request: IntentRequest) -> IntentResponse:
    """Extract intent and entities from Hebrew text."""
    start = datetime.utcnow()
    
    logger.info(f"Intent extraction request received", extra={
        "conv_id": str(request.conv_id),
        "trace_id": str(request.trace_id) if request.trace_id else None,
        "text_length": len(request.text),
        "has_context": request.context is not None
    })
    
    try:
        # Call GPT for intent extraction
        gpt_response = await call_gpt_for_intent(request.text, request.context)
        result = gpt_response["result"]
        
        # Normalize entities
        entities = normalize_entities(result["entities"])
        
        # Determine routing flags
        route_flags = determine_routing(
            result["intent"], 
            result["confidence"], 
            entities, 
            request.text
        )
        
        # Adjust confidence based on entity quality
        adjusted_confidence = calculate_confidence_score(
            result["entities"], 
            request.text
        )
        final_confidence = (result["confidence"] + adjusted_confidence) / 2
        
        # Create response
        response = IntentResponse(
            conv_id=request.conv_id,
            intent=result["intent"],
            entities=entities,
            confidence=min(1.0, final_confidence),
            route_flags=route_flags,
            timestamp=datetime.utcnow(),
            token_usage=TokenUsage(**gpt_response["usage"]),
            explanation=result.get("explanation")
        )
        
        # Log success
        duration_ms = (datetime.utcnow() - start).total_seconds() * 1000
        logger.info(f"Intent extraction completed", extra={
            "conv_id": str(request.conv_id),
            "duration_ms": duration_ms,
            "intent": result["intent"],
            "confidence": final_confidence,
            "needs_clarification": route_flags.needs_clarification
        })
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Intent extraction failed: {e}", extra={
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
        layer="1_MAIN_INTENT_BOT",
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
    logger.info(f"Starting 1_MAIN_INTENT_BOT on port {config.port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.port,
        log_level="info"
    )