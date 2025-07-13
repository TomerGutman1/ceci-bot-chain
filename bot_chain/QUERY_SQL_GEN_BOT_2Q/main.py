"""
2Q_QUERY_SQL_GEN_BOT - SQL query generation service.
"""
import os
import sys
import json
import asyncio
import sqlparse
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
from sql_templates import (
    get_template_by_intent, build_dynamic_filters, validate_parameters,
    sanitize_parameters, SQL_TEMPLATES, DEFAULT_PARAMS
)

# Initialize
logger = setup_logging('QUERY_SQL_GEN_BOT_2Q')
config = get_config('QUERY_SQL_GEN_BOT_2Q')
app = FastAPI(title="QUERY_SQL_GEN_BOT_2Q", version="1.0.0")

# Configure OpenAI
openai.api_key = config.openai_api_key


class ConversationTurn(BaseModel):
    """Model for conversation turn."""
    turn_id: str
    speaker: str  # "user" or "bot"
    clean_text: str
    timestamp: str

class SQLGenRequest(BaseModel):
    """Request model for SQL generation."""
    intent: str = Field(..., description="Intent from intent bot")
    entities: Dict[str, Any] = Field(..., description="Extracted entities")
    conv_id: str = Field(..., description="Conversation ID for tracking")
    trace_id: Optional[str] = Field(None, description="Request trace ID")
    conversation_history: List[ConversationTurn] = Field(default_factory=list, description="Conversation history for context")
    context_summary: Dict[str, Any] = Field(default_factory=dict, description="Context summary")


class SQLParameter(BaseModel):
    """Model for SQL parameters."""
    name: str
    value: Any
    type: str


class TokenUsage(BaseModel):
    """Model for token usage tracking."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    cost_usd: float = 0.0


class SQLGenResponse(BaseModel):
    """Response model for SQL generation."""
    conv_id: str
    sql_query: str
    parameters: List[SQLParameter]
    template_used: Optional[str] = None
    validation_passed: bool
    timestamp: datetime
    layer: str = "2Q_QUERY_SQL_GEN_BOT"
    token_usage: Optional[TokenUsage] = None
    context_used: bool = False
    enhanced_entities: Dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    layer: str
    version: str
    uptime_seconds: int
    timestamp: datetime


# Global variables
start_time = datetime.utcnow()

SQL_GENERATION_PROMPT = """Generate PostgreSQL query for Israeli government decisions.

Schema: israeli_government_decisions(id, government_number, decision_number, decision_date, title, content, summary, topics[], ministries[], status)

Intent: {intent}
Entities: {entities}

Rules:
1. Use %(param)s format
2. Always AND status = 'active'
3. Array: 'value' = ANY(topics)
4. ORDER BY decision_date DESC
5. Default LIMIT 20

Return JSON: {{"sql": "...", "parameters": {{}}, "explanation": "..."}}

Example: {{"sql": "SELECT * FROM government_decisions WHERE government_number = %(gov)s AND %(topic)s = ANY(topics) AND status = 'active' ORDER BY decision_date DESC LIMIT 20", "parameters": {{"gov": 37, "topic": "חינוך"}}, "explanation": "Gov 37 education decisions"}}
"""


async def call_gpt_for_sql(intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
    """Call GPT-4 for SQL generation."""
    try:
        prompt = SQL_GENERATION_PROMPT.format(
            intent=intent,
            entities=json.dumps(entities, ensure_ascii=False, indent=2)
        )
        
        messages = [
            {"role": "system", "content": "You are an expert PostgreSQL query generator."},
            {"role": "user", "content": prompt}
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
        
        # Calculate cost for GPT-3.5-turbo: $0.50/$1.50 per 1M tokens
        cost_usd = (usage.prompt_tokens * 0.0005 / 1000) + (usage.completion_tokens * 0.0015 / 1000)
        
        return {
            "result": result,
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "model": config.model,
                "cost_usd": cost_usd
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


def clean_topic_entity(topic: str) -> str:
    """Clean topic entity from government references and Hebrew verbs."""
    if not topic:
        return topic
    
    import re
    
    # Remove government references and Hebrew verbs that indicate end of topic
    cleaned = topic
    # Remove "ממשלה X" patterns
    cleaned = re.sub(r'\s+ממשלה\s+\d+.*$', '', cleaned)
    cleaned = re.sub(r'\s+של\s+ממשלה.*$', '', cleaned)
    # Remove Hebrew verbs that indicate end of topic
    cleaned = re.sub(r'\s+(?:קיבלה?|ש?קיבל|נתקבל|החליט|החליטה?).*$', '', cleaned)
    # Remove other stopping patterns
    cleaned = re.sub(r'\s+(?:היו|ש?היה|נעשה|נעשו).*$', '', cleaned)
    cleaned = cleaned.strip()
    
    # Hebrew topic normalization mapping
    topic_mapping = {
        # Security variations
        "בטחון": "ביטחון", 
        "ביטחון לאומי": "ביטחון",
        "בטחון פנימי": "ביטחון",
        "ביטחון פנים": "ביטחון",
        
        # Education variations
        "השכלה": "חינוך", 
        "חינוך והשכלה": "חינוך",
        "חינוך וחברה": "חינוך",
        "מערכת החינוך": "חינוך",
        "חנוך": "חינוך", # common typo
        
        # Health variations
        "רפואה": "בריאות",
        "בריאות הציבור": "בריאות",
        "שירותי בריאות": "בריאות",
        "רפואה וחירום": "בריאות",
        "בראות": "בריאות", # common typo
        
        # Economy variations
        "כלכלה ותעשייה": "כלכלה",
        "כלכלי": "כלכלה",
        "התעשייה": "כלכלה",
        "מסחר": "כלכלה",
        "מסחר וכלכלה": "כלכלה",
        
        # Transportation variations
        "תחבורה ציבורית": "תחבורה",
        "תחבורה וכבישים": "תחבורה",
        "כבישים": "תחבורה",
        "תיחבורה": "תחבורה", # common typo
    }
    
    # Apply normalization
    if cleaned in topic_mapping:
        cleaned = topic_mapping[cleaned]
    
    # Additional cleanup - remove articles and prepositions at the end
    cleaned = re.sub(r'\s+(ה|את|של|על|ב|מ|ל)$', '', cleaned).strip()
    
    return cleaned


def convert_hebrew_limit(limit_value: Any) -> int:
    """Convert Hebrew limit words to numeric values."""
    if isinstance(limit_value, int):
        return limit_value
    
    if isinstance(limit_value, str):
        # Hebrew limit mappings
        hebrew_limits = {
            "אחרונות": 10,
            "אחרונה": 1,
            "האחרונות": 10,
            "האחרונה": 1,
            "ראשונות": 10,
            "ראשונה": 1,
            "הראשונות": 10,
            "הראשונה": 1
        }
        
        # Check if it's a Hebrew limit word
        if limit_value in hebrew_limits:
            return hebrew_limits[limit_value]
        
        # Try to parse as number
        try:
            return int(limit_value)
        except ValueError:
            # Default to 10 for unrecognized limit words
            return 10
    
    # Default limit
    return 10

def enhance_entities_with_context(
    entities: Dict[str, Any],
    conversation_history: List[ConversationTurn]
) -> Dict[str, Any]:
    """Extract missing entities from conversation history and clean topic entities."""
    
    enhanced_entities = entities.copy()
    
    # Clean topic entity if it exists
    if enhanced_entities.get("topic"):
        cleaned_topic = clean_topic_entity(enhanced_entities["topic"])
        if cleaned_topic != enhanced_entities["topic"]:
            logger.info(f"Cleaned topic: '{enhanced_entities['topic']}' -> '{cleaned_topic}'")
            enhanced_entities["topic"] = cleaned_topic
    
    # Convert Hebrew limit words to numeric values
    if enhanced_entities.get("limit"):
        original_limit = enhanced_entities["limit"]
        numeric_limit = convert_hebrew_limit(original_limit)
        if numeric_limit != original_limit:
            logger.info(f"Converted limit: '{original_limit}' -> {numeric_limit}")
            enhanced_entities["limit"] = numeric_limit
    
    # Look for missing decision numbers in previous queries
    if not enhanced_entities.get("decision_number"):
        for turn in reversed(conversation_history):
            if turn.speaker == "user":
                import re
                decision_match = re.search(r'החלטה\s*(\d+)', turn.clean_text)
                if decision_match:
                    enhanced_entities["decision_number"] = decision_match.group(1)
                    break
    
    # Look for missing government numbers
    if not enhanced_entities.get("government_number"):
        for turn in reversed(conversation_history):
            if turn.speaker == "user":
                import re
                gov_match = re.search(r'ממשלה\s*(\d+)', turn.clean_text)
                if gov_match:
                    enhanced_entities["government_number"] = gov_match.group(1)
                    break
    
    # If we found a decision number from context, update the operation to specific_decision
    if enhanced_entities.get("decision_number") and not entities.get("decision_number"):
        enhanced_entities["operation"] = "specific_decision"
    
    return enhanced_entities

def generate_sql_from_template(intent: str, entities: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Generate SQL using predefined templates."""
    logger.info(f"Selecting template for intent: {intent}, entities: {entities}")
    template = get_template_by_intent(intent, entities)
    if not template:
        logger.warning(f"No template found for intent: {intent}, entities: {entities}")
        return None
    logger.info(f"Selected template: {template.name}")
    
    # Build parameters
    params = {}
    
    # Add required parameters
    for param in template.required_params:
        if param in entities and entities[param] is not None:
            params[param] = entities[param]
        elif param == "government_number" and entities.get("government_number"):
            params[param] = entities["government_number"]
        elif param == "decision_number" and entities.get("decision_number"):
            params[param] = entities["decision_number"]
        elif param == "topic" and entities.get("topic"):
            params[param] = entities["topic"]
        elif param == "start_date" and entities.get("date_range", {}).get("start"):
            params[param] = entities["date_range"]["start"]
        elif param == "end_date" and entities.get("date_range", {}).get("end"):
            params[param] = entities["date_range"]["end"]
        elif param == "ministry" and entities.get("ministries"):
            params[param] = entities["ministries"][0]  # Take first ministry
        elif param == "government_list" and entities.get("government_numbers"):
            params[param] = entities["government_numbers"]
        elif param == "year" and entities.get("year"):
            params[param] = entities["year"]
        elif param == "start_year" and entities.get("start_year"):
            params[param] = entities["start_year"]
        elif param == "end_year" and entities.get("end_year"):
            params[param] = entities["end_year"]
        elif param == "min_count":
            params[param] = entities.get("min_count", 1)
        else:
            # Missing required parameter
            return None
    
    # Add optional parameters with defaults
    for param in template.optional_params:
        if param in entities and entities[param] is not None:
            params[param] = entities[param]
        elif param in DEFAULT_PARAMS:
            params[param] = DEFAULT_PARAMS[param]
    
    # Validate parameters
    errors = validate_parameters(template, params)
    if errors:
        logger.warning(f"Template validation failed: {errors}")
        return None
    
    # Sanitize parameters
    params = sanitize_parameters(params)
    
    # Build SQL with dynamic filters
    sql = build_dynamic_filters(template, entities)
    
    return {
        "sql": sql,
        "parameters": params,
        "template_used": template.name,
        "explanation": template.description
    }


def validate_sql_syntax(sql: str) -> bool:
    """Validate SQL syntax using sqlparse."""
    try:
        parsed = sqlparse.parse(sql)
        
        # Check if parsing was successful
        if not parsed:
            return False
        
        # Basic validation: should have SELECT statement
        sql_lower = sql.lower().strip()
        if not sql_lower.startswith('select'):
            return False
        
        # Check for dangerous operations
        dangerous_keywords = ['drop', 'delete', 'insert', 'update', 'truncate', 'alter']
        for keyword in dangerous_keywords:
            if keyword in sql_lower:
                return False
        
        return True
        
    except Exception as e:
        logger.warning(f"SQL validation failed: {e}")
        return False


@app.post("/sqlgen", response_model=SQLGenResponse)
async def generate_sql(request: SQLGenRequest) -> SQLGenResponse:
    """Generate SQL query from intent and entities."""
    start = datetime.utcnow()
    
    logger.info(f"SQL generation request received", extra={
        "conv_id": request.conv_id,
        "trace_id": request.trace_id if request.trace_id else None,
        "intent": request.intent,
        "entities_count": len(request.entities)
    })
    
    try:
        # Enhance entities with conversation context
        enhanced_entities = enhance_entities_with_context(
            request.entities,
            request.conversation_history
        )
        
        # Try template-based generation first with enhanced entities
        template_result = generate_sql_from_template(request.intent, enhanced_entities)
        
        sql_query = None
        parameters = []
        template_used = None
        token_usage = None
        
        if template_result:
            # Template generation successful
            sql_query = template_result["sql"]
            params = template_result["parameters"]
            template_used = template_result["template_used"]
            
            # Convert parameters to response format
            for name, value in params.items():
                parameters.append(SQLParameter(
                    name=name,
                    value=value,
                    type=type(value).__name__
                ))
            
            # Create token usage for template (0 tokens)
            token_usage = TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model="template"
            )
            
            logger.info(f"SQL generated using template: {template_used}", extra={
                "conv_id": request.conv_id,
                "template": template_used
            })
        
        else:
            # Fallback to GPT generation
            logger.info("Falling back to GPT SQL generation", extra={
                "conv_id": request.conv_id
            })
            
            gpt_response = await call_gpt_for_sql(request.intent, enhanced_entities)
            result = gpt_response["result"]
            
            sql_query = result["sql"]
            params = result.get("parameters", {})
            
            # Convert parameters to response format
            for name, value in params.items():
                parameters.append(SQLParameter(
                    name=name,
                    value=value,
                    type=type(value).__name__
                ))
            
            token_usage = TokenUsage(**gpt_response["usage"])
        
        # Validate SQL syntax
        validation_passed = validate_sql_syntax(sql_query)
        
        if not validation_passed:
            logger.error(f"Generated SQL failed validation", extra={
                "conv_id": request.conv_id,
                "sql": sql_query
            })
            raise HTTPException(status_code=500, detail="Generated SQL failed validation")
        
        # Create response
        response = SQLGenResponse(
            conv_id=request.conv_id,
            sql_query=sql_query,
            parameters=parameters,
            template_used=template_used,
            validation_passed=validation_passed,
            timestamp=datetime.utcnow(),
            token_usage=token_usage,
            context_used=len(request.conversation_history) > 0,
            enhanced_entities=enhanced_entities
        )
        
        # Log success
        duration_ms = (datetime.utcnow() - start).total_seconds() * 1000
        logger.info(f"SQL generation completed", extra={
            "conv_id": request.conv_id,
            "duration_ms": duration_ms,
            "method": "template" if template_used else "gpt",
            "parameter_count": len(parameters)
        })
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SQL generation failed: {e}", extra={
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
        layer="2Q_QUERY_SQL_GEN_BOT",
        version="1.0.0",
        uptime_seconds=int(uptime),
        timestamp=datetime.utcnow()
    )


@app.get("/templates")
async def get_template_info():
    """Get information about available SQL templates."""
    from sql_templates import get_template_coverage
    return get_template_coverage()


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
    logger.info(f"Starting 2Q_QUERY_SQL_GEN_BOT on port {config.port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.port,
        log_level="info"
    )