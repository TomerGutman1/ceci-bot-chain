"""
2X Context Router Bot - Manages conversation context and routing decisions.
Determines if queries need clarification or can proceed directly to SQL generation.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import uuid4

import redis
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common.logging import setup_logging, log_api_call, log_gpt_usage
from common.config import get_config

# ====================================
# CONFIGURATION & LOGGING
# ====================================
logger = setup_logging('MAIN_CTX_ROUTER_BOT_2X')
config = get_config('MAIN_CTX_ROUTER_BOT_2X')
app = FastAPI(
    title="2X Context Router Bot",
    description="Manages conversation context and routing decisions",
    version="1.0.0"
)

# Redis connection for context caching
redis_client = None

def get_redis():
    global redis_client
    if redis_client is None:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        redis_client = redis.from_url(redis_url, decode_responses=True)
    return redis_client

# ====================================
# PYDANTIC MODELS
# ====================================
class ConversationContext(BaseModel):
    """Conversation context data model."""
    conv_id: str
    user_queries: List[str] = Field(default_factory=list)
    clarifications: List[str] = Field(default_factory=list)
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)
    ambiguity_flags: List[str] = Field(default_factory=list)
    last_intent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ContextRequest(BaseModel):
    """Request for context routing decision."""
    conv_id: str = Field(..., description="Conversation ID for context tracking")
    current_query: str = Field(..., description="Current user query")
    intent: str = Field(..., description="Detected intent from intent bot")
    entities: Dict[str, Any] = Field(..., description="Extracted entities")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Intent confidence score")

class RoutingDecision(BaseModel):
    """Routing decision output."""
    route: str = Field(..., description="next_bot | clarify | direct_sql")
    needs_clarification: bool = Field(..., description="Whether clarification is needed")
    clarification_type: Optional[str] = Field(None, description="Type of clarification needed")
    context_summary: Dict[str, Any] = Field(..., description="Updated context summary")
    reasoning: str = Field(..., description="Explanation of routing decision")

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    redis_connected: bool
    context_cache_size: int

# ====================================
# ROUTING RULES ENGINE
# ====================================
import yaml

def load_routing_rules():
    """Load routing rules from YAML configuration file."""
    try:
        rules_path = os.path.join(os.path.dirname(__file__), '..', 'schemas', 'routing_rules.yml')
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)
        logger.info("Loaded routing rules from YAML configuration")
        return rules
    except Exception as e:
        logger.warning(f"Failed to load routing rules YAML: {e}, using defaults")
        # Fallback to hardcoded rules
        return {
            "clarification_triggers": {
                "confidence_thresholds": {"low_confidence": 0.7},
                "ambiguous_entities": {"time_references": ["תקופה", "זמן", "מתי"]},
                "vague_topics": ["זה", "דבר", "עניין", "משהו"],
                "incomplete_questions": ["מה", "איך", "למה"],
                "required_entities": {
                    "search": {"mandatory": ["topic"]},
                    "count": {"mandatory": ["government_number"]},
                    "specific_decision": {"mandatory": ["government_number", "decision_number"]},
                    "comparison": {"mandatory": ["governments", "topic"]}
                }
            },
            "direct_sql_conditions": {
                "high_confidence_threshold": 0.85
            },
            "context_weights": {
                "previous_queries": 0.3,
                "extracted_entities": 0.4,
                "intent_confidence": 0.3
            }
        }

# Load routing rules from YAML
ROUTING_RULES = load_routing_rules()

# ====================================
# CONTEXT MANAGEMENT
# ====================================
async def get_conversation_context(conv_id: str) -> Optional[ConversationContext]:
    """Retrieve conversation context from Redis cache."""
    try:
        redis_conn = get_redis()
        context_data = redis_conn.get(f"context:{conv_id}")
        
        if context_data:
            data = json.loads(context_data)
            return ConversationContext(**data)
        return None
    except Exception as e:
        logger.error(f"Failed to retrieve context for {conv_id}: {e}")
        return None

async def save_conversation_context(context: ConversationContext) -> bool:
    """Save conversation context to Redis cache with TTL."""
    try:
        redis_conn = get_redis()
        context.updated_at = datetime.utcnow()
        
        # Set TTL to 2 hours for conversation context
        ttl_seconds = 2 * 60 * 60
        
        redis_conn.setex(
            f"context:{context.conv_id}",
            ttl_seconds,
            context.json()
        )
        return True
    except Exception as e:
        logger.error(f"Failed to save context for {context.conv_id}: {e}")
        return False

async def update_context_with_query(
    context: ConversationContext,
    query: str,
    intent: str,
    entities: Dict[str, Any],
    confidence: float
) -> ConversationContext:
    """Update context with new query information."""
    context.user_queries.append(query)
    context.last_intent = intent
    
    # Merge entities (new ones override existing)
    context.extracted_entities.update(entities)
    
    # Keep only last 5 queries to prevent context from growing too large
    if len(context.user_queries) > 5:
        context.user_queries = context.user_queries[-5:]
    
    return context

# ====================================
# ROUTING LOGIC
# ====================================
def needs_clarification(
    intent: str,
    entities: Dict[str, Any],
    confidence: float,
    context: ConversationContext,
    query: str
) -> tuple[bool, Optional[str], str]:
    """
    Determine if query needs clarification.
    Returns: (needs_clarification, clarification_type, reasoning)
    """
    triggers = ROUTING_RULES["clarification_triggers"]
    
    # Check confidence threshold
    low_threshold = triggers["confidence_thresholds"]["low_confidence"]
    if confidence < low_threshold:
        return True, "low_confidence", f"Intent confidence {confidence:.2f} below threshold {low_threshold}"
    
    # Check for ambiguous entities in Hebrew
    query_lower = query.lower()
    
    # Check ambiguous time references
    time_refs = triggers["ambiguous_entities"]["time_references"]
    for ambiguous in time_refs:
        if ambiguous in query_lower:
            return True, "ambiguous_time", f"Query contains ambiguous time reference: '{ambiguous}'"
    
    # Check for vague topics
    vague_topics = triggers.get("vague_topics", [])
    for vague in vague_topics:
        if vague in query_lower:
            return True, "vague_topic", f"Query contains vague topic reference: '{vague}'"
    
    # Check for incomplete queries (questions without sufficient context)
    incomplete_questions = triggers.get("incomplete_questions", [])
    if any(incomplete in query_lower for incomplete in incomplete_questions):
        if not context.extracted_entities and len(context.user_queries) == 1:
            return True, "incomplete_query", "Question word without sufficient context in first query"
    
    # Check if required entities are missing for the intent
    required_config = triggers.get("required_entities", {}).get(intent, {})
    mandatory = required_config.get("mandatory", [])
    missing_entities = [req for req in mandatory if req not in entities or not entities[req]]
    
    if missing_entities:
        return True, "missing_entities", f"Missing required entities for {intent}: {missing_entities}"
    
    return False, None, "All routing checks passed"

def calculate_context_score(context: ConversationContext, current_confidence: float) -> float:
    """Calculate overall context score based on conversation history."""
    weights = ROUTING_RULES["context_weights"]
    
    # Previous queries score (more queries = better context)
    prev_score = min(len(context.user_queries) / 3.0, 1.0)
    
    # Entities score (more entities = better context)
    entity_score = min(len(context.extracted_entities) / 3.0, 1.0)
    
    # Intent confidence score
    intent_score = current_confidence
    
    total_score = (
        prev_score * weights["previous_queries"] +
        entity_score * weights["extracted_entities"] +
        intent_score * weights["intent_confidence"]
    )
    
    return total_score

async def make_routing_decision(request: ContextRequest) -> RoutingDecision:
    """Main routing decision logic."""
    # Get or create conversation context
    context = await get_conversation_context(request.conv_id)
    if context is None:
        context = ConversationContext(conv_id=request.conv_id)
    
    # Update context with current query
    context = await update_context_with_query(
        context, request.current_query, request.intent,
        request.entities, request.confidence_score
    )
    
    # Check if clarification is needed
    needs_clarify, clarify_type, reasoning = needs_clarification(
        request.intent, request.entities, request.confidence_score,
        context, request.current_query
    )
    
    # Calculate overall context score
    context_score = calculate_context_score(context, request.confidence_score)
    
    # Make routing decision
    if needs_clarify:
        route = "clarify"
        await save_conversation_context(context)
        
        return RoutingDecision(
            route=route,
            needs_clarification=True,
            clarification_type=clarify_type,
            context_summary={
                "conv_id": context.conv_id,
                "query_count": len(context.user_queries),
                "entities_count": len(context.extracted_entities),
                "context_score": context_score
            },
            reasoning=f"Clarification needed: {reasoning}"
        )
    
    # Check if we can go directly to SQL generation
    high_confidence = ROUTING_RULES["direct_sql_conditions"]["high_confidence_threshold"]
    
    # More lenient direct SQL routing for good scenarios
    if (request.confidence_score >= high_confidence and len(request.entities) >= 2) or \
       (request.confidence_score >= 0.9 and request.intent == "specific_decision") or \
       (request.confidence_score >= 0.85 and context_score >= 0.6):
        route = "direct_sql"
    else:
        route = "next_bot"
    
    # Save updated context
    await save_conversation_context(context)
    
    return RoutingDecision(
        route=route,
        needs_clarification=False,
        clarification_type=None,
        context_summary={
            "conv_id": context.conv_id,
            "query_count": len(context.user_queries),
            "entities_count": len(context.extracted_entities),
            "context_score": context_score,
            "last_intent": context.last_intent
        },
        reasoning=f"Route to {route} (confidence: {request.confidence_score:.2f}, context_score: {context_score:.2f})"
    )

# ====================================
# API ENDPOINTS
# ====================================
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        redis_conn = get_redis()
        # Test Redis connection
        redis_conn.ping()
        redis_connected = True
        
        # Get cache size (approximate)
        cache_size = len(redis_conn.keys("context:*"))
    except Exception:
        redis_connected = False
        cache_size = -1
    
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat(),
        redis_connected=redis_connected,
        context_cache_size=cache_size
    )

@app.post("/route", response_model=RoutingDecision)
async def route_conversation(request: ContextRequest):
    """Main routing endpoint for conversation context management."""
    start_time = datetime.utcnow()
    
    try:
        log_api_call(
            logger, "route_conversation", request.dict(),
            request.conv_id, "2X_MAIN_CTX_ROUTER_BOT"
        )
        
        # Make routing decision
        decision = await make_routing_decision(request)
        
        # Log successful routing
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            "Routing decision completed",
            extra={
                "conv_id": request.conv_id,
                "route": decision.route,
                "needs_clarification": decision.needs_clarification,
                "duration_ms": duration * 1000,
                "context_score": decision.context_summary.get("context_score", 0)
            }
        )
        
        return decision
        
    except Exception as e:
        logger.error(
            f"Routing failed for conv_id {request.conv_id}: {e}",
            extra={"conv_id": request.conv_id, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Routing failed: {str(e)}"
        )

@app.get("/context/{conv_id}")
async def get_context(conv_id: str):
    """Get conversation context for debugging."""
    context = await get_conversation_context(conv_id)
    if context is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Context not found for conversation {conv_id}"
        )
    return context

@app.delete("/context/{conv_id}")
async def clear_context(conv_id: str):
    """Clear conversation context."""
    try:
        redis_conn = get_redis()
        result = redis_conn.delete(f"context:{conv_id}")
        return {"deleted": bool(result), "conv_id": conv_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear context: {str(e)}"
        )

@app.get("/stats")
async def get_cache_stats():
    """Get Redis cache statistics."""
    try:
        redis_conn = get_redis()
        info = redis_conn.info()
        
        # Count contexts
        context_keys = redis_conn.keys("context:*")
        total_contexts = len(context_keys)
        
        return {
            "total_contexts": total_contexts,
            "redis_memory_used": info.get("used_memory_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "uptime_seconds": info.get("uptime_in_seconds", 0)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )

# ====================================
# STARTUP
# ====================================
if __name__ == "__main__":
    import uvicorn
    port = config.port if hasattr(config, 'port') else 8013
    uvicorn.run(app, host="0.0.0.0", port=port)