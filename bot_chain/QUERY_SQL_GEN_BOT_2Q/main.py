"""
2Q_QUERY_SQL_GEN_BOT - SQL query generation service.
"""
import os
import sys
import json
import asyncio
import sqlparse
from typing import Dict, Any, List, Optional, Tuple
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
from synonym_mapper import (
    expand_topic_synonyms, expand_ministry_synonyms, correct_typos,
    get_all_synonyms_for_topic, build_topic_sql_condition
)
from date_interpreter import (
    interpret_hebrew_date, extract_date_from_entities, 
    normalize_date_format, validate_date_range
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
    
    # New enhanced fields
    query_type: str = Field(default="list", description="Type of query: count, list, comparison, analysis, specific")
    synonym_expansions: Dict[str, List[str]] = Field(default_factory=dict, description="Topics expanded with synonyms")
    date_interpretations: Dict[str, str] = Field(default_factory=dict, description="How dates were interpreted")
    validation_warnings: List[str] = Field(default_factory=list, description="Non-fatal validation warnings")
    fallback_applied: bool = Field(default=False, description="Whether fallback logic was used")
    confidence_score: float = Field(default=1.0, ge=0, le=1, description="Confidence in the generated query")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    layer: str
    version: str
    uptime_seconds: int
    timestamp: datetime


# Global variables
start_time = datetime.utcnow()

SQL_GENERATION_PROMPT = """You are an expert SQL query generator for the Israeli government decisions database.

## Your Core Task:
Transform Hebrew natural language queries into precise PostgreSQL queries while understanding:
- Synonyms and related terms (חינוך = השכלה = חנוך)
- Date/time expressions (השנה, החודש, ב-3 השנים האחרונות)
- Numeric ranges (בין 100 ל-500 מיליון)
- Boolean flags (רק אופרטיביות, ללא ביטולים)
- Statistical vs. List queries (כמה vs. אילו)

## Database Schema:
israeli_government_decisions(
  id BIGINT PRIMARY KEY,
  decision_date DATE NOT NULL,
  decision_number TEXT NOT NULL,
  government_number TEXT NOT NULL,
  prime_minister TEXT NOT NULL,
  committee TEXT,
  decision_title TEXT NOT NULL,
  summary TEXT NOT NULL,
  decision_content TEXT NOT NULL,
  operativity TEXT NOT NULL, -- 'אופרטיבית' or 'דקלרטיבית'
  tags_policy_area TEXT,
  tags_government_body TEXT,
  tags_location TEXT,
  all_tags TEXT NOT NULL,
  decision_url TEXT NOT NULL,
  decision_key TEXT UNIQUE NOT NULL,
  embedding VECTOR(768),
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL
)

## Query Types:
1. COUNT: Return count only (כמה, מספר, סך הכל)
2. LIST: Return full rows (אילו, מה, תן לי, הצג)
3. COMPARISON: Compare between entities
4. ANALYSIS: Deep dive into specific decisions
5. SPECIFIC: Search for exact decision number in exact government (e.g. "החלטה 100 של ממשלה 35")

Intent: {intent}
Entities: {entities}

## Examples:

### Example 1: Statistical/Count Query
If entities contain "count_only": true or intent suggests counting:
{{
  "sql": "SELECT COUNT(*) as count FROM israeli_government_decisions WHERE tags_policy_area ILIKE '%%חינוך%%' AND decision_date BETWEEN %(start_date)s AND %(end_date)s",
  "parameters": {{"start_date": "2020-01-01", "end_date": "2024-12-31"}},
  "query_type": "count"
}}

### Example 1b: Count Query with Government Filter
IMPORTANT: When counting with government_number, ALWAYS include it in WHERE clause:
{{
  "sql": "SELECT COUNT(*) as count FROM israeli_government_decisions WHERE tags_policy_area ILIKE '%%ביטחון%%' AND government_number = %(government_number)s",
  "parameters": {{"government_number": "37"}},
  "query_type": "count",
  "description": "ספירת החלטות בנושא ביטחון של ממשלה 37"
}}

### Example 2: Fetch/List Query with Synonyms
For topic queries, expand synonyms AND search in multiple fields:
{{
  "sql": "SELECT id, government_number, decision_number, decision_date, decision_title, summary, tags_policy_area, tags_government_body, decision_url FROM israeli_government_decisions WHERE (tags_policy_area ILIKE '%%חינוך%%' OR tags_policy_area ILIKE '%%השכלה%%' OR all_tags ILIKE '%%חינוך%%' OR all_tags ILIKE '%%השכלה%%' OR decision_title ILIKE '%%חינוך%%' OR decision_title ILIKE '%%השכלה%%' OR summary ILIKE '%%חינוך%%' OR summary ILIKE '%%השכלה%%' OR decision_content ILIKE '%%חינוך%%' OR decision_content ILIKE '%%השכלה%%') ORDER BY decision_date DESC LIMIT %(limit)s",
  "parameters": {{"limit": 5}},
  "query_type": "list",
  "synonym_expansion": {{"השכלה": ["חינוך", "השכלה"]}}
}}

### Example 3: Specific Decision Query with Government
When both government_number and decision_number are specified, search for EXACTLY that decision:
{{
  "sql": "SELECT * FROM israeli_government_decisions WHERE government_number = %(government_number)s AND decision_number = %(decision_number)s",
  "parameters": {{"government_number": "35", "decision_number": "100"}},
  "query_type": "specific"
}}

### Example 4: Specific Decision Query without Government
When only decision_number is specified (e.g. "החלטה 2989"), search for EXACTLY that decision:
{{
  "sql": "SELECT * FROM israeli_government_decisions WHERE decision_number = %(decision_number)s ORDER BY decision_date DESC",
  "parameters": {{"decision_number": "2989"}},
  "query_type": "specific"
}}
IMPORTANT: For specific decision queries, use EXACT match (=) not similarity or LIKE. Do NOT return similar numbers.

### Example 5: Ministry Search Query
For ministry queries, search in tags_government_body:
{{
  "sql": "SELECT id, government_number, decision_number, decision_date, decision_title, summary, tags_policy_area, tags_government_body, decision_url FROM israeli_government_decisions WHERE tags_government_body ILIKE '%%משרד החינוך%%' ORDER BY decision_date DESC LIMIT %(limit)s",
  "parameters": {{"limit": 20}},
  "query_type": "list",
  "description": "החלטות של משרד החינוך"
}}

### Example 6: Topic Search in Content (not in standard tags)
For topics like "ענן הממשלתי", "מחשוב ענן", "תשתיות דיגיטליות" that might not be in tags:
{{
  "sql": "SELECT id, government_number, decision_number, decision_date, decision_title, summary, tags_policy_area, tags_government_body, decision_url FROM israeli_government_decisions WHERE (decision_title ILIKE '%%ענן%%' OR summary ILIKE '%%ענן%%' OR decision_content ILIKE '%%ענן%%' OR all_tags ILIKE '%%ענן%%') ORDER BY decision_date DESC LIMIT %(limit)s",
  "parameters": {{"limit": 20}},
  "query_type": "list",
  "search_note": "Searching in title, summary and content since 'ענן' is not a standard policy tag"
}}

## Topic Synonym Mapping:
{{
  "חינוך": ["חינוך", "השכלה", "חנוך", "מערכת החינוך", "חינוך פורמלי"],
  "ביטחון": ["ביטחון", "בטחון", "ביטחון לאומי", "הגנה", "צבא"],
  "בריאות": ["בריאות", "רפואה", "בראות", "שירותי בריאות"],
  "כלכלה": ["כלכלה", "כלכלי", "מסחר", "תעשייה", "עסקים"],
  "תחבורה": ["תחבורה", "תיחבורה", "כבישים", "תחבורה ציבורית"]
}}

## Parameter Validation:
- government_number: convert to TEXT
- decision_number: convert to TEXT
- limit: 1-100 (default 20)
- dates: validate format YYYY-MM-DD

Always return JSON with: sql, parameters, query_type, validation_notes

CRITICAL RULES:
1. When user asks for a specific decision (e.g. "החלטה X של ממשלה Y"), ALWAYS use WHERE government_number = Y AND decision_number = X
2. When user asks for just "החלטה X" without government, search WHERE decision_number = X (exact match)
3. NEVER fallback to listing all decisions of a government when a specific decision is requested
4. NEVER use similarity search, LIKE, or approximate matching for decision numbers - use exact equality (=)
5. If user asks for "החלטה 2989", the SQL must be: WHERE decision_number = '2989' (exact match)
6. Do NOT return decisions with similar numbers (2998, 2996, etc.) when an exact number is requested
7. For topic searches: ALWAYS search in multiple fields (tags_policy_area, all_tags, decision_title, summary, decision_content)
8. If a topic is not in the standard synonym mapping, still search for it in title, summary and content fields
9. COUNT queries must ONLY return COUNT(*) as count - no other fields
10. When count_only=true AND government_number exists, ALWAYS filter by government_number
11. For "כמה החלטות בנושא X קיבלה ממשלה Y", generate: SELECT COUNT(*) as count WHERE topic AND government_number = Y
"""


def detect_query_type(intent: str, entities: Dict[str, Any]) -> str:
    """
    Detect the type of query based on intent and entities.
    
    Returns: 'count', 'list', 'comparison', 'analysis', or 'specific'
    """
    # Check for explicit count_only flag
    if entities.get("count_only"):
        return "count"
    
    # Check for count operation
    if entities.get("operation") == "count":
        return "count"
    
    # Check intent types
    if intent == "count":
        return "count"
    
    if intent == "comparison" or entities.get("comparison_target"):
        return "comparison"
    
    if intent in ["ANALYSIS", "EVAL"]:
        return "analysis"
    
    if intent == "specific_decision" or (entities.get("government_number") and entities.get("decision_number")):
        return "specific"
    
    # Check for count keywords in topic or original query
    count_keywords = ["כמה", "מספר", "סך הכל", "סה\"כ", "ספירה"]
    topic = entities.get("topic", "").lower()
    for keyword in count_keywords:
        if keyword in topic:
            return "count"
    
    # Default to list query
    return "list"


async def call_gpt_for_sql(intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
    """Call GPT-4o for SQL generation."""
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
        
        # Calculate cost for GPT-4o-turbo: $0.01/$0.03 per 1K tokens  
        cost_usd = (usage.prompt_tokens * 0.01 / 1000) + (usage.completion_tokens * 0.03 / 1000)
        
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


async def generate_enhanced_sql(intent: str, entities: Dict[str, Any], use_enhanced: bool = True) -> Dict[str, Any]:
    """
    Generate SQL using enhanced GPT-4o capabilities with all new features.
    
    Returns dict with sql, parameters, and all enhanced metadata
    """
    validation_warnings = []
    synonym_expansions = {}
    date_interpretations = {}
    confidence_score = 1.0
    
    # Step 1: Correct typos in entities
    if entities.get("topic"):
        original_topic = entities["topic"]
        corrected_topic = correct_typos(original_topic)
        if corrected_topic != original_topic:
            entities["topic"] = corrected_topic
            validation_warnings.append(f"תוקן: '{original_topic}' → '{corrected_topic}'")
    
    # Step 2: Extract and interpret dates
    date_range = extract_date_from_entities(entities)
    if date_range:
        # Validate date range
        is_valid, error_msg = validate_date_range(date_range["start"], date_range["end"])
        if not is_valid:
            validation_warnings.append(f"בעיה בתאריכים: {error_msg}")
            confidence_score *= 0.8
        else:
            entities["date_range"] = date_range
            date_interpretations["extracted"] = f"{date_range['start']} עד {date_range['end']}"
    
    # Step 3: Expand synonyms for topics
    if entities.get("topic"):
        topic = entities["topic"]
        synonyms = list(get_all_synonyms_for_topic(topic))
        if len(synonyms) > 1:
            synonym_expansions[topic] = synonyms
            entities["expanded_topics"] = synonyms
    
    # Step 4: Expand ministry synonyms
    if entities.get("ministries"):
        for i, ministry in enumerate(entities["ministries"]):
            ministry_synonyms = expand_ministry_synonyms(ministry)
            if len(ministry_synonyms) > 1:
                synonym_expansions[ministry] = ministry_synonyms
                entities["ministries"][i] = ministry_synonyms[0]  # Use canonical form
    
    # Step 5: Detect query type
    query_type = detect_query_type(intent, entities)
    entities["query_type"] = query_type
    
    # Step 6: Add boolean flag detection
    if entities.get("decision_type") == "אופרטיבית":
        entities["operativity_filter"] = "אופרטיבית"
    
    # Step 7: Call GPT with enhanced prompt
    if use_enhanced:
        gpt_response = await call_gpt_for_sql(intent, entities)
        result = gpt_response["result"]
        
        # Extract enhanced metadata from GPT response
        if "query_type" in result:
            query_type = result["query_type"]
        
        if "synonym_expansion" in result:
            synonym_expansions.update(result["synonym_expansion"])
        
        if "validation_notes" in result:
            validation_warnings.extend(result["validation_notes"])
        
        # Validate count queries
        sql = result["sql"]
        is_valid, error_msg = validate_count_query(sql, entities, query_type)
        if not is_valid:
            validation_warnings.append(f"SQL validation error: {error_msg}")
            confidence_score *= 0.7
            logger.warning(f"Count query validation failed: {error_msg}", extra={
                "sql": sql,
                "entities": entities,
                "query_type": query_type
            })
        
        # Log the generated SQL for debugging
        logger.info("Enhanced SQL generated", extra={
            "sql": sql,
            "parameters": result.get("parameters", {}),
            "query_type": query_type,
            "token_usage": gpt_response["usage"],
            "validation_passed": is_valid
        })
        
        return {
            "sql": sql,
            "parameters": result.get("parameters", {}),
            "query_type": query_type,
            "synonym_expansions": synonym_expansions,
            "date_interpretations": date_interpretations,
            "validation_warnings": validation_warnings,
            "confidence_score": confidence_score,
            "token_usage": gpt_response["usage"],
            "method": "enhanced_gpt"
        }
    else:
        # Fallback to template system
        template_result = generate_sql_from_template(intent, entities)
        if template_result:
            return {
                "sql": template_result["sql"],
                "parameters": template_result["parameters"],
                "query_type": query_type,
                "synonym_expansions": synonym_expansions,
                "date_interpretations": date_interpretations,
                "validation_warnings": validation_warnings,
                "confidence_score": confidence_score * 0.9,  # Slightly lower confidence for templates
                "template_used": template_result["template_used"],
                "method": "template"
            }
        else:
            validation_warnings.append("לא נמצאה תבנית מתאימה, משתמש ב-GPT")
            return await generate_enhanced_sql(intent, entities, use_enhanced=True)


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


def validate_count_query(sql: str, entities: Dict[str, Any], query_type: str) -> Tuple[bool, str]:
    """
    Validate that count queries are properly formatted.
    Returns (is_valid, error_message)
    """
    sql_lower = sql.lower().strip()
    
    # If it's marked as a count query or has count_only flag
    if query_type == "count" or entities.get("count_only", False):
        # Must have COUNT(*) in the SELECT clause
        if "count(*)" not in sql_lower:
            return False, "Count query must use COUNT(*)"
        
        # Should not select other columns (except for aliased count)
        select_part = sql_lower.split("from")[0].replace("select", "").strip()
        # Remove COUNT(*) as count or COUNT(*)
        select_clean = select_part.replace("count(*) as count", "").replace("count(*)", "").strip()
        if select_clean and select_clean != ",":
            return False, "Count query should only select COUNT(*)"
        
        # If government_number is in entities, ensure it's in WHERE clause
        if entities.get("government_number"):
            if "government_number" not in sql_lower:
                return False, "Count query with government filter must include government_number in WHERE clause"
        
        # If topic is in entities, ensure some filtering is applied
        if entities.get("topic") or entities.get("expanded_topics"):
            if "where" not in sql_lower:
                return False, "Count query with topic filter must have WHERE clause"
            
            # Check for topic-related filtering
            topic_found = False
            for field in ["tags_policy_area", "decision_content", "title", "summary"]:
                if field in sql_lower:
                    topic_found = True
                    break
            if not topic_found:
                return False, "Count query with topic must filter on policy area or content fields"
    
    # For non-count queries, ensure they don't have COUNT(*)
    elif "count(*)" in sql_lower and "count" not in query_type.lower():
        return False, "Non-count query should not use COUNT(*)"
    
    return True, ""


def should_use_template(intent: str, entities: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Determine if a query should use template-based SQL generation.
    Returns (should_use_template, reason)
    
    Templates are preferred for:
    1. Simple, well-defined queries
    2. Queries that match exact template patterns
    3. Performance-critical queries
    """
    # Always use templates for these simple cases
    if entities.get("count_only") and entities.get("government_number") and entities.get("topic"):
        # Count with government and topic - template is reliable
        return True, "Simple count query with filters"
    
    if entities.get("decision_number") and not entities.get("topic"):
        # Single decision lookup - template is perfect
        return True, "Single decision lookup"
    
    # Check if we have a complex date interpretation
    if entities.get("relative_date") or entities.get("date_context"):
        # Complex date queries benefit from GPT
        return False, "Complex date interpretation needed"
    
    # Check for typos or non-standard terms
    topic = entities.get("topic", "")
    if topic:
        # Common typos that need GPT correction
        typo_indicators = ["חנוך", "בראות", "תיחבורה", "בטחון"]
        for typo in typo_indicators:
            if typo in topic:
                return False, f"Typo correction needed: {typo}"
    
    # Check for ministry queries
    if entities.get("ministries"):
        # Ministry queries often need synonym expansion
        return False, "Ministry query needs synonym expansion"
    
    # Check for complex filtering
    complex_filters = 0
    for field in ["topic", "government_number", "committee_id", "policy_area", "date_range"]:
        if entities.get(field):
            complex_filters += 1
    
    if complex_filters >= 3:
        # Too many filters, GPT can optimize better
        return False, "Complex multi-filter query"
    
    # Default: try template first
    return True, "Default to template for efficiency"


async def generate_hybrid_sql(intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate SQL using hybrid approach: template first, then enhanced if needed.
    """
    validation_warnings = []
    
    # Step 1: Decide whether to use template
    use_template, reason = should_use_template(intent, entities)
    
    logger.info(f"Hybrid SQL decision: {'template' if use_template else 'enhanced'}", extra={
        "reason": reason,
        "intent": intent,
        "entities": entities
    })
    
    # Step 2: Try template approach first if recommended
    if use_template:
        template_result = generate_sql_from_template(intent, entities)
        if template_result:
            # Template succeeded
            query_type = detect_query_type(intent, entities)
            
            # Validate count queries even from templates
            is_valid, error_msg = validate_count_query(
                template_result["sql"], 
                entities, 
                query_type
            )
            
            if is_valid:
                logger.info("Template SQL validated successfully", extra={
                    "sql": template_result["sql"],
                    "parameters": template_result["parameters"],
                    "template": template_result["template_used"],
                    "query_type": query_type,
                    "hybrid_reason": reason
                })
                
                return {
                    "sql": template_result["sql"],
                    "parameters": template_result["parameters"],
                    "query_type": query_type,
                    "synonym_expansions": {},
                    "date_interpretations": {},
                    "validation_warnings": validation_warnings,
                    "confidence_score": 0.95,  # High confidence for validated templates
                    "template_used": template_result["template_used"],
                    "method": "hybrid_template",
                    "hybrid_reason": reason
                }
            else:
                validation_warnings.append(f"Template validation failed: {error_msg}")
                logger.warning(f"Template SQL failed validation, falling back to enhanced", extra={
                    "template": template_result["template_used"],
                    "error": error_msg
                })
    
    # Step 3: Fall back to enhanced generation
    result = await generate_enhanced_sql(intent, entities, use_enhanced=True)
    result["method"] = "hybrid_enhanced"
    result["hybrid_reason"] = f"Fallback from: {reason}"
    
    return result


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
        # Check feature flag
        use_enhanced = os.getenv("USE_ENHANCED_SQL_GEN", "true").lower() == "true"
        
        # Enhance entities with conversation context
        enhanced_entities = enhance_entities_with_context(
            request.entities,
            request.conversation_history
        )
        
        if use_enhanced:
            # Use hybrid SQL generation (template first, then enhanced)
            logger.info("Using hybrid SQL generation", extra={
                "conv_id": request.conv_id
            })
            
            result = await generate_hybrid_sql(request.intent, enhanced_entities)
            
            sql_query = result["sql"]
            params = result["parameters"]
            
            # Convert parameters to response format
            parameters = []
            for name, value in params.items():
                parameters.append(SQLParameter(
                    name=name,
                    value=value,
                    type=type(value).__name__
                ))
            
            # Validate SQL syntax
            validation_passed = validate_sql_syntax(sql_query)
            
            if not validation_passed:
                logger.error(f"Generated SQL failed validation", extra={
                    "conv_id": request.conv_id,
                    "sql": sql_query
                })
                result["validation_warnings"].append("SQL syntax validation failed")
                result["confidence_score"] *= 0.5
            
            # Create enhanced response
            response = SQLGenResponse(
                conv_id=request.conv_id,
                sql_query=sql_query,
                parameters=parameters,
                template_used=result.get("template_used"),
                validation_passed=validation_passed,
                timestamp=datetime.utcnow(),
                token_usage=result.get("token_usage") and TokenUsage(**result["token_usage"]),
                context_used=len(request.conversation_history) > 0,
                enhanced_entities=enhanced_entities,
                # New enhanced fields
                query_type=result.get("query_type", "list"),
                synonym_expansions=result.get("synonym_expansions", {}),
                date_interpretations=result.get("date_interpretations", {}),
                validation_warnings=result.get("validation_warnings", []),
                fallback_applied=result.get("method") == "template",
                confidence_score=result.get("confidence_score", 1.0)
            )
        else:
            # Use legacy template-based approach
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
            
            # Create legacy response
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
            "method": result.get("method", "enhanced") if use_enhanced else ("template" if template_used else "gpt"),
            "parameter_count": len(parameters),
            "query_type": response.query_type if use_enhanced else "unknown",
            "sql_query": sql_query[:200] + "..." if len(sql_query) > 200 else sql_query,
            "validation_passed": response.validation_passed,
            "confidence_score": response.confidence_score if hasattr(response, 'confidence_score') else None
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