"""
SQL query templates for government decisions database.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re


@dataclass
class SQLTemplate:
    """SQL template with parameters and validation."""
    name: str
    description: str
    sql: str
    required_params: List[str]
    optional_params: List[str]
    example_params: Dict[str, Any]
    intent_match: List[str]  # Which intents this template supports


# SQL Templates for different query patterns
SQL_TEMPLATES = {
    "search_by_government_and_topic": SQLTemplate(
        name="search_by_government_and_topic",
        description="Search decisions by government number and topic",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries
        FROM government_decisions 
        WHERE government_number = %(government_number)s
        AND %(topic)s = ANY(topics)
        AND status = 'active'
        ORDER BY decision_date DESC, decision_number DESC
        LIMIT %(limit)s;
        """,
        required_params=["government_number", "topic"],
        optional_params=["limit"],
        example_params={
            "government_number": 37,
            "topic": "חינוך",
            "limit": 20
        },
        intent_match=["search"]
    ),
    
    "search_by_topic_only": SQLTemplate(
        name="search_by_topic_only",
        description="Search decisions by topic across all governments",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries
        FROM government_decisions 
        WHERE %(topic)s = ANY(topics)
        AND status = 'active'
        ORDER BY decision_date DESC, government_number DESC, decision_number DESC
        LIMIT %(limit)s;
        """,
        required_params=["topic"],
        optional_params=["limit"],
        example_params={
            "topic": "ביטחון",
            "limit": 50
        },
        intent_match=["search"]
    ),
    
    "specific_decision": SQLTemplate(
        name="specific_decision",
        description="Get a specific decision by government and decision number",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, content, summary, topics, ministries, decision_type
        FROM government_decisions 
        WHERE government_number = %(government_number)s
        AND decision_number = %(decision_number)s
        AND status = 'active';
        """,
        required_params=["government_number", "decision_number"],
        optional_params=[],
        example_params={
            "government_number": 37,
            "decision_number": 660
        },
        intent_match=["specific_decision"]
    ),
    
    "count_decisions_by_government": SQLTemplate(
        name="count_decisions_by_government",
        description="Count total decisions by government",
        sql="""
        SELECT 
            government_number,
            COUNT(*) as decision_count,
            MIN(decision_date) as first_decision,
            MAX(decision_date) as last_decision
        FROM government_decisions 
        WHERE government_number = %(government_number)s
        AND status = 'active'
        GROUP BY government_number;
        """,
        required_params=["government_number"],
        optional_params=[],
        example_params={
            "government_number": 37
        },
        intent_match=["count"]
    ),
    
    "count_decisions_by_topic": SQLTemplate(
        name="count_decisions_by_topic",
        description="Count decisions by topic and optionally government",
        sql="""
        SELECT 
            government_number,
            %(topic)s as topic,
            COUNT(*) as decision_count
        FROM government_decisions 
        WHERE %(topic)s = ANY(topics)
        AND status = 'active'
        {government_filter}
        GROUP BY government_number
        ORDER BY government_number DESC;
        """,
        required_params=["topic"],
        optional_params=["government_number"],
        example_params={
            "topic": "חינוך",
            "government_number": 37
        },
        intent_match=["count"]
    ),
    
    "search_by_date_range": SQLTemplate(
        name="search_by_date_range",
        description="Search decisions within a date range",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries
        FROM government_decisions 
        WHERE decision_date >= %(start_date)s
        AND decision_date <= %(end_date)s
        AND status = 'active'
        {topic_filter}
        {government_filter}
        ORDER BY decision_date DESC, government_number DESC, decision_number DESC
        LIMIT %(limit)s;
        """,
        required_params=["start_date", "end_date"],
        optional_params=["topic", "government_number", "limit"],
        example_params={
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "topic": "ביטחון",
            "limit": 30
        },
        intent_match=["search"]
    ),
    
    "search_by_ministry": SQLTemplate(
        name="search_by_ministry",
        description="Search decisions by ministry involvement",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries
        FROM government_decisions 
        WHERE %(ministry)s = ANY(ministries)
        AND status = 'active'
        {government_filter}
        {topic_filter}
        ORDER BY decision_date DESC, government_number DESC, decision_number DESC
        LIMIT %(limit)s;
        """,
        required_params=["ministry"],
        optional_params=["government_number", "topic", "limit"],
        example_params={
            "ministry": "משרד החינוך",
            "government_number": 37,
            "limit": 25
        },
        intent_match=["search"]
    ),
    
    "full_text_search": SQLTemplate(
        name="full_text_search",
        description="Full-text search in decision content",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries,
            ts_rank(to_tsvector('hebrew', content), to_tsquery('hebrew', %(search_term)s)) as relevance_score
        FROM government_decisions 
        WHERE to_tsvector('hebrew', content) @@ to_tsquery('hebrew', %(search_term)s)
        AND status = 'active'
        {government_filter}
        ORDER BY relevance_score DESC, decision_date DESC
        LIMIT %(limit)s;
        """,
        required_params=["search_term"],
        optional_params=["government_number", "limit"],
        example_params={
            "search_term": "חינוך & תקציב",
            "government_number": 37,
            "limit": 20
        },
        intent_match=["search"]
    ),
    
    "compare_governments": SQLTemplate(
        name="compare_governments",
        description="Compare decision counts between governments",
        sql="""
        SELECT 
            government_number,
            COUNT(*) as total_decisions,
            COUNT(CASE WHEN %(topic)s = ANY(topics) THEN 1 END) as topic_decisions,
            ROUND(
                100.0 * COUNT(CASE WHEN %(topic)s = ANY(topics) THEN 1 END) / COUNT(*), 
                2
            ) as topic_percentage
        FROM government_decisions 
        WHERE government_number IN %(government_list)s
        AND status = 'active'
        GROUP BY government_number
        ORDER BY government_number;
        """,
        required_params=["government_list", "topic"],
        optional_params=[],
        example_params={
            "government_list": [35, 36, 37],
            "topic": "ביטחון"
        },
        intent_match=["comparison"]
    ),
    
    "recent_decisions": SQLTemplate(
        name="recent_decisions",
        description="Get most recent decisions",
        sql="""
        SELECT 
            id, government_number, decision_number, decision_date,
            title, summary, topics, ministries
        FROM government_decisions 
        WHERE status = 'active'
        {government_filter}
        {topic_filter}
        ORDER BY decision_date DESC, government_number DESC, decision_number DESC
        LIMIT %(limit)s;
        """,
        required_params=[],
        optional_params=["government_number", "topic", "limit"],
        example_params={
            "limit": 10,
            "government_number": 37
        },
        intent_match=["search"]
    ),
    
    "topic_summary": SQLTemplate(
        name="topic_summary",
        description="Summarize decisions by topic across governments",
        sql="""
        SELECT 
            unnest(topics) as topic,
            COUNT(*) as decision_count,
            COUNT(DISTINCT government_number) as government_count,
            MIN(decision_date) as first_decision,
            MAX(decision_date) as last_decision
        FROM government_decisions 
        WHERE status = 'active'
        {government_filter}
        GROUP BY unnest(topics)
        HAVING COUNT(*) >= %(min_count)s
        ORDER BY decision_count DESC
        LIMIT %(limit)s;
        """,
        required_params=[],
        optional_params=["government_number", "min_count", "limit"],
        example_params={
            "min_count": 5,
            "limit": 20
        },
        intent_match=["search", "count"]
    )
}


def get_template_by_intent(intent: str, entities: Dict[str, Any]) -> Optional[SQLTemplate]:
    """Select the best template based on intent and available entities."""
    
    # For specific decisions
    if intent == "specific_decision":
        if entities.get("government_number") and entities.get("decision_number"):
            return SQL_TEMPLATES["specific_decision"]
    
    # For count queries
    if intent == "count":
        if entities.get("government_number") and not entities.get("topic"):
            return SQL_TEMPLATES["count_decisions_by_government"]
        elif entities.get("topic"):
            return SQL_TEMPLATES["count_decisions_by_topic"]
    
    # For search queries
    if intent == "search":
        # Date range search
        if entities.get("date_range"):
            return SQL_TEMPLATES["search_by_date_range"]
        
        # Ministry search
        if entities.get("ministries"):
            return SQL_TEMPLATES["search_by_ministry"]
        
        # Government + topic search
        if entities.get("government_number") and entities.get("topic"):
            return SQL_TEMPLATES["search_by_government_and_topic"]
        
        # Topic only search
        if entities.get("topic"):
            return SQL_TEMPLATES["search_by_topic_only"]
        
        # Recent decisions
        return SQL_TEMPLATES["recent_decisions"]
    
    # For comparison queries
    if intent == "comparison":
        return SQL_TEMPLATES["compare_governments"]
    
    # Default fallback
    return SQL_TEMPLATES["recent_decisions"]


def build_dynamic_filters(template: SQLTemplate, entities: Dict[str, Any]) -> str:
    """Build dynamic filter clauses for templates with optional parameters."""
    sql = template.sql
    
    # Government filter
    if "{government_filter}" in sql:
        if entities.get("government_number"):
            government_filter = "AND government_number = %(government_number)s"
        else:
            government_filter = ""
        sql = sql.replace("{government_filter}", government_filter)
    
    # Topic filter
    if "{topic_filter}" in sql:
        if entities.get("topic"):
            topic_filter = "AND %(topic)s = ANY(topics)"
        else:
            topic_filter = ""
        sql = sql.replace("{topic_filter}", topic_filter)
    
    return sql


def validate_parameters(template: SQLTemplate, params: Dict[str, Any]) -> List[str]:
    """Validate that all required parameters are present."""
    errors = []
    
    for required_param in template.required_params:
        if required_param not in params or params[required_param] is None:
            errors.append(f"Missing required parameter: {required_param}")
    
    return errors


def sanitize_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize parameters to prevent SQL injection."""
    sanitized = {}
    
    for key, value in params.items():
        if isinstance(value, str):
            # Remove potentially dangerous characters
            value = re.sub(r'[;\'\"\\]', '', value)
            # Limit length
            value = value[:200]
        elif isinstance(value, (int, float)):
            # Ensure reasonable bounds
            if key in ["government_number"]:
                value = max(1, min(50, int(value)))
            elif key in ["decision_number"]:
                value = max(1, min(9999, int(value)))
            elif key in ["limit"]:
                value = max(1, min(1000, int(value)))
        elif isinstance(value, list):
            # Sanitize list items
            value = [sanitize_parameters({key: item})[key] for item in value[:10]]
        
        sanitized[key] = value
    
    return sanitized


def get_template_coverage() -> Dict[str, Any]:
    """Get coverage statistics for SQL templates."""
    intent_coverage = {}
    total_templates = len(SQL_TEMPLATES)
    
    for template in SQL_TEMPLATES.values():
        for intent in template.intent_match:
            if intent not in intent_coverage:
                intent_coverage[intent] = 0
            intent_coverage[intent] += 1
    
    return {
        "total_templates": total_templates,
        "intent_coverage": intent_coverage,
        "template_names": list(SQL_TEMPLATES.keys()),
        "coverage_percentage": {
            intent: (count / total_templates) * 100 
            for intent, count in intent_coverage.items()
        }
    }


# Default parameters for common cases
DEFAULT_PARAMS = {
    "limit": 20,
    "min_count": 1,
    "start_date": "2020-01-01",
    "end_date": "2025-12-31"
}