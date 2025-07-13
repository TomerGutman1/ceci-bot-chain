#!/usr/bin/env python3
"""
Test configuration and environment settings.
Centralizes all test-related configuration.
"""

import os
from typing import Dict, Any

# Test environment settings
TEST_ENV = {
    "BACKEND_URL": os.getenv("TEST_BACKEND_URL", "http://localhost:5001"),
    "CONTEXT_ROUTER_URL": os.getenv("TEST_CONTEXT_ROUTER_URL", "http://localhost:8013"),
    "UNIFIED_INTENT_URL": os.getenv("TEST_UNIFIED_INTENT_URL", "http://localhost:8011"),
    "SQL_GEN_URL": os.getenv("TEST_SQL_GEN_URL", "http://localhost:8012"),
    "EVALUATOR_URL": os.getenv("TEST_EVALUATOR_URL", "http://localhost:8014"),
    "CLARIFY_URL": os.getenv("TEST_CLARIFY_URL", "http://localhost:8015"),
    "LLM_FORMATTER_URL": os.getenv("TEST_LLM_FORMATTER_URL", "http://localhost:8017"),
    
    # Database
    "DB_HOST": os.getenv("TEST_DB_HOST", "localhost"),
    "DB_PORT": int(os.getenv("TEST_DB_PORT", "5433")),
    "DB_NAME": os.getenv("TEST_DB_NAME", "ceci_bot_chain"),
    "DB_USER": os.getenv("TEST_DB_USER", "postgres"),
    "DB_PASSWORD": os.getenv("TEST_DB_PASSWORD", "postgres"),
    
    # Redis
    "REDIS_URL": os.getenv("TEST_REDIS_URL", "redis://localhost:6380"),
    
    # Test settings
    "DEFAULT_TIMEOUT": int(os.getenv("TEST_TIMEOUT", "30")),
    "RETRY_COUNT": int(os.getenv("TEST_RETRY_COUNT", "3")),
    "RETRY_DELAY": float(os.getenv("TEST_RETRY_DELAY", "1.0")),
}

# API endpoints
API_ENDPOINTS = {
    "chat": f"{TEST_ENV['BACKEND_URL']}/api/chat",
    "health": f"{TEST_ENV['BACKEND_URL']}/health",
    "statistics": f"{TEST_ENV['BACKEND_URL']}/api/statistics",
    "context_route": f"{TEST_ENV['CONTEXT_ROUTER_URL']}/route",
    "context_health": f"{TEST_ENV['CONTEXT_ROUTER_URL']}/health",
}

# Test timeouts for different query types
QUERY_TIMEOUTS = {
    "simple": 5.0,
    "search": 10.0,
    "analysis": 30.0,
    "count": 5.0,
    "reference": 8.0,
    "unclear": 5.0,
    "comparison": 15.0
}

# Cache TTL settings for tests
CACHE_TTL = {
    "response_cache": 14400,      # 4 hours
    "sql_template_cache": 86400,  # 24 hours
    "intent_pattern_cache": 86400 # 24 hours
}

# Feature flags for testing
FEATURE_FLAGS = {
    "USE_UNIFIED_INTENT": os.getenv("USE_UNIFIED_INTENT", "true").lower() == "true",
    "USE_LLM_FORMATTER": os.getenv("USE_LLM_FORMATTER", "true").lower() == "true",
    "SKIP_RANKER": os.getenv("SKIP_RANKER", "true").lower() == "true",
    "SKIP_EVALUATOR": os.getenv("SKIP_EVALUATOR", "false").lower() == "true",
}

# Session configuration
SESSION_CONFIG = {
    "id_prefix": "test_",
    "max_history_length": 20,
    "context_window_size": 10,
    "session_timeout": 3600  # 1 hour
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "max_response_time": {
        "simple_query": 3.0,
        "search_query": 8.0,
        "analysis_query": 20.0,
        "count_query": 3.0
    },
    "min_cache_hit_rate": 0.7,
    "max_error_rate": 0.05,
    "min_success_rate": 0.95,
    "max_concurrent_sessions": 100,
    "target_qps": 10
}

# Hebrew test patterns
HEBREW_PATTERNS = {
    "clarification_indicators": [
        "זקוק לפרטים",
        "אפשרויות",
        "הצעות",
        "מה הייתם",
        "איזה",
        "לא ברור",
        "תוכל להבהיר",
        "למה התכוונת"
    ],
    "reference_patterns": [
        "זה", "זו", "זאת",
        "האחרון", "הקודם", "הנ\"ל",
        "שאמרת", "ההחלטה", "אותה"
    ],
    "count_patterns": [
        "כמה", "מספר", "סך הכל",
        "כמות", "סה\"כ"
    ]
}

# Logging configuration
LOGGING_CONFIG = {
    "level": os.getenv("TEST_LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.getenv("TEST_LOG_FILE", "tests/test_results.log")
}

def get_service_url(service: str) -> str:
    """Get URL for a specific service."""
    return TEST_ENV.get(f"{service.upper()}_URL", "")

def get_timeout_for_query(query_type: str) -> float:
    """Get timeout for specific query type."""
    return QUERY_TIMEOUTS.get(query_type, TEST_ENV["DEFAULT_TIMEOUT"])

def is_feature_enabled(feature: str) -> bool:
    """Check if a feature flag is enabled."""
    return FEATURE_FLAGS.get(feature, False)

def get_performance_threshold(metric: str, sub_metric: str = None) -> float:
    """Get performance threshold value."""
    if sub_metric:
        return PERFORMANCE_THRESHOLDS.get(metric, {}).get(sub_metric, 0)
    return PERFORMANCE_THRESHOLDS.get(metric, 0)

def get_db_connection_string() -> str:
    """Get database connection string."""
    return (
        f"postgresql://{TEST_ENV['DB_USER']}:{TEST_ENV['DB_PASSWORD']}"
        f"@{TEST_ENV['DB_HOST']}:{TEST_ENV['DB_PORT']}/{TEST_ENV['DB_NAME']}"
    )

# Export configuration
__all__ = [
    'TEST_ENV',
    'API_ENDPOINTS',
    'QUERY_TIMEOUTS',
    'CACHE_TTL',
    'FEATURE_FLAGS',
    'SESSION_CONFIG',
    'PERFORMANCE_THRESHOLDS',
    'HEBREW_PATTERNS',
    'LOGGING_CONFIG',
    'get_service_url',
    'get_timeout_for_query',
    'is_feature_enabled',
    'get_performance_threshold',
    'get_db_connection_string'
]