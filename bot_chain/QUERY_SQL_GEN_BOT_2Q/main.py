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


class SQLGenRequest(BaseModel):
    """Request model for SQL generation."""
    intent: str = Field(..., description="Intent from intent bot")
    entities: Dict[str, Any] = Field(..., description="Extracted entities")
    conv_id: str = Field(..., description="Conversation ID for tracking")
    trace_id: Optional[str] = Field(None, description="Request trace ID")


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


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    layer: str
    version: str
    uptime_seconds: int
    timestamp: datetime


# Global variables
start_time = datetime.utcnow()

SQL_GENERATION_PROMPT = """You are an expert SQL query generator for Israeli government decisions database.

Database schema:
- government_decisions: Main table with columns: id, government_number, decision_number, decision_date, title, content, summary, topics (text[]), ministries (text[]), status
- governments: Metadata table with government information
- Topics and ministries are stored as PostgreSQL arrays

Your task: Generate a PostgreSQL query based on the intent and entities.

Intent: {intent}
Entities: {entities}

Requirements:
1. Use parameterized queries with %(param_name)s format
2. Always include: AND status = 'active'
3. Use appropriate ORDER BY clauses
4. Include LIMIT for search queries (default 20)
5. Use array operators for topics/ministries: 'value' = ANY(array_column)
6. For full-text search: to_tsvector('hebrew', content) @@ to_tsquery('hebrew', 'search_term')

Return JSON with:
- "sql": The complete SQL query
- "parameters": Object with parameter names and values
- "explanation": Brief explanation of the query logic

Example for "החלטות ממשלה 37 בנושא חינוך":
{
  "sql": "SELECT id, government_number, decision_number, decision_date, title, summary FROM government_decisions WHERE government_number = %(government_number)s AND %(topic)s = ANY(topics) AND status = 'active' ORDER BY decision_date DESC LIMIT %(limit)s;",
  "parameters": {"government_number": 37, "topic": "חינוך", "limit": 20},
  "explanation": "Search for education decisions from government 37, ordered by date"
}
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


def generate_sql_from_template(intent: str, entities: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Generate SQL using predefined templates."""
    template = get_template_by_intent(intent, entities)
    if not template:
        return None
    
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
        # Try template-based generation first
        template_result = generate_sql_from_template(request.intent, request.entities)
        
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
            
            logger.info(f"SQL generated using template: {template_used}", extra={
                "conv_id": request.conv_id,
                "template": template_used
            })
        
        else:
            # Fallback to GPT generation
            logger.info("Falling back to GPT SQL generation", extra={
                "conv_id": request.conv_id
            })
            
            gpt_response = await call_gpt_for_sql(request.intent, request.entities)
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
            token_usage=token_usage
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