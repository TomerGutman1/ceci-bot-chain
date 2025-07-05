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
from memory_service import memory_service
from reference_resolver import ReferenceResolver

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

# Initialize reference resolver
reference_resolver = ReferenceResolver(memory_service=memory_service)

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
    route_flags: Dict[str, Any] = Field(default_factory=dict, description="Context routing flags")

class RoutingDecision(BaseModel):
    """Routing decision output."""
    route: str = Field(..., description="next_bot | clarify | direct_sql")
    needs_clarification: bool = Field(..., description="Whether clarification is needed")
    clarification_type: Optional[str] = Field(None, description="Type of clarification needed")
    context_summary: Dict[str, Any] = Field(..., description="Updated context summary")
    reasoning: str = Field(..., description="Explanation of routing decision")
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation history for downstream bots")

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    redis_connected: bool
    context_cache_size: int
    memory_service_status: Dict[str, Any] = Field(default_factory=dict)
    reference_resolver_status: Dict[str, Any] = Field(default_factory=dict)

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
    
    # DISABLED: Handle "full content" requests to prevent entity persistence bug
    # if "תוכן מלא" in query.lower() or "התוכן המלא" in query.lower():
    #     # Check if we have a previous decision in context
    #     last_decision = context.extracted_entities.get("last_decision_number")
    #     last_government = context.extracted_entities.get("last_government_number")
    #     
    #     if last_decision and not entities.get("decision_number"):
    #         entities["decision_number"] = last_decision
    #         entities["government_number"] = last_government or 37
    #         context.extracted_entities.update(entities)
    
    # DISABLED: Store last decision for continuity to prevent entity persistence
    # if entities.get("decision_number"):
    #     context.extracted_entities["last_decision_number"] = entities["decision_number"]
    #     context.extracted_entities["last_government_number"] = entities.get("government_number", 37)
    
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
    query: str,
    route_flags: Dict[str, Any] = None
) -> tuple[bool, Optional[str], str]:
    """
    Determine if query needs clarification.
    Returns: (needs_clarification, clarification_type, reasoning)
    """
    triggers = ROUTING_RULES["clarification_triggers"]
    
    # Skip confidence check for reference queries that need context
    if route_flags and route_flags.get("needs_context"):
        # Reference queries should use conversation context instead of clarification
        return False, None, "Reference query - using conversation context"
    
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
    
    # STEP 1: Reference Resolution
    # Resolve user references to previous turns before processing
    reference_result = reference_resolver.resolve_references(
        conv_id=request.conv_id,
        user_text=request.current_query,
        current_entities=request.entities,
        intent=request.intent
    )
    
    # Use resolved entities and potentially enriched query
    resolved_entities = reference_result['resolved_entities']
    enriched_query = reference_result['enriched_query']
    
    # If reference resolution recommends clarification, handle it
    if reference_result['needs_clarification']:
        # Update context with original query first
        context = await update_context_with_query(
            context, request.current_query, request.intent,
            resolved_entities, request.confidence_score
        )
        await save_conversation_context(context)
        
        return RoutingDecision(
            route="clarify",
            needs_clarification=True,
            clarification_type="missing_entities",
            context_summary={
                "conv_id": context.conv_id,
                "query_count": len(context.user_queries),
                "entities_count": len(context.extracted_entities),
                "reference_resolution": reference_result['reasoning']
            },
            reasoning=f"Reference resolution needs clarification: {reference_result['clarification_prompt']}"
        )
    
    # Update context with resolved entities and enriched query
    context = await update_context_with_query(
        context, enriched_query, request.intent,
        resolved_entities, request.confidence_score
    )
    
    # Check if we need to access conversation memory
    should_use_memory = (
        request.intent in ["RESULT_REF", "ANALYSIS"] or
        request.route_flags.get('needs_context', False)
    )
    
    conversation_history = []
    if should_use_memory:
        conversation_history = memory_service.fetch(request.conv_id)
        logger.info(f"Loaded {len(conversation_history)} conversation turns from memory")
    
    # Check if clarification is needed (using resolved entities)
    needs_clarify, clarify_type, reasoning = needs_clarification(
        request.intent, resolved_entities, request.confidence_score,
        context, enriched_query, request.route_flags
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
    
    # More lenient direct SQL routing for good scenarios (use resolved entities)
    if (request.confidence_score >= high_confidence and len(resolved_entities) >= 2) or \
       (request.confidence_score >= 0.9 and request.intent == "specific_decision") or \
       (request.confidence_score >= 0.85 and context_score >= 0.6):
        route = "direct_sql"
    else:
        route = "next_bot"
    
    # Save updated context
    await save_conversation_context(context)
    
    # Store conversation turn in memory (for successful non-CLARIFY interactions)
    if route != "clarify":
        # Store user query (use enriched query if reference resolution occurred)
        query_to_store = enriched_query if enriched_query != request.current_query else request.current_query
        user_turn_success = memory_service.append(request.conv_id, {
            'turn_id': str(uuid4()),
            'speaker': 'user',
            'clean_text': query_to_store,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Store bot response (routing decision)
        bot_response = f"Routed to {route} (intent: {request.intent}, confidence: {request.confidence_score:.2f})"
        bot_turn_success = memory_service.append(request.conv_id, {
            'turn_id': str(uuid4()),
            'speaker': 'bot',
            'clean_text': bot_response,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        if user_turn_success and bot_turn_success:
            logger.debug(f"Stored conversation turns in memory for {request.conv_id}")
    
    response = RoutingDecision(
        route=route,
        needs_clarification=False,
        clarification_type=None,
        context_summary={
            "conv_id": context.conv_id,
            "query_count": len(context.user_queries),
            "entities_count": len(context.extracted_entities),
            "context_score": context_score,
            "last_intent": context.last_intent,
            "conversation_history_count": len(conversation_history),
            "reference_resolution": reference_result['reasoning'],
            "enriched_query": enriched_query != request.current_query
        },
        reasoning=f"Route to {route} (confidence: {request.confidence_score:.2f}, context_score: {context_score:.2f}, ref_resolved: {reference_result['route']})"
    )
    
    # Store conversation history in the response for downstream bots
    response.conversation_history = conversation_history
    
    return response

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
    
    # Get memory service health
    memory_health = memory_service.health_check()
    
    # Get reference resolver health
    reference_health = reference_resolver.health_check()
    
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat(),
        redis_connected=redis_connected,
        context_cache_size=cache_size,
        memory_service_status=memory_health,
        reference_resolver_status=reference_health
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

@app.get("/memory/{conv_id}")
async def get_memory(conv_id: str):
    """Get conversation memory for debugging."""
    history = memory_service.fetch(conv_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No conversation history found for {conv_id}"
        )
    return {"conv_id": conv_id, "history": history, "total_turns": len(history)}

@app.delete("/context/{conv_id}")
async def clear_context(conv_id: str):
    """Clear conversation context."""
    try:
        redis_conn = get_redis()
        context_result = redis_conn.delete(f"context:{conv_id}")
        
        # Also clear conversation memory
        memory_result = memory_service.clear(conv_id)
        
        return {
            "context_deleted": bool(context_result),
            "memory_deleted": memory_result,
            "conv_id": conv_id
        }
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
        
        # Get memory service metrics
        memory_metrics = memory_service.get_metrics()
        
        # Get reference resolver metrics
        reference_metrics = reference_resolver.get_metrics()
        
        return {
            "total_contexts": total_contexts,
            "redis_memory_used": info.get("used_memory_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "uptime_seconds": info.get("uptime_in_seconds", 0),
            "memory_metrics": memory_metrics,
            "reference_metrics": reference_metrics
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )

@app.post("/test-reference")
async def test_reference_resolution(
    conv_id: str,
    user_text: str,
    current_entities: Dict[str, Any] = None,
    intent: str = None
):
    """Test reference resolution functionality."""
    if current_entities is None:
        current_entities = {}
    
    try:
        result = reference_resolver.resolve_references(
            conv_id=conv_id,
            user_text=user_text,
            current_entities=current_entities,
            intent=intent
        )
        
        return {
            "test_input": {
                "conv_id": conv_id,
                "user_text": user_text,
                "current_entities": current_entities,
                "intent": intent
            },
            "resolution_result": result,
            "metrics": reference_resolver.get_metrics()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reference resolution test failed: {str(e)}"
        )

# ====================================
# STARTUP
# ====================================
if __name__ == "__main__":
    import uvicorn
    port = config.port if hasattr(config, 'port') else 8013
    uvicorn.run(app, host="0.0.0.0", port=port)