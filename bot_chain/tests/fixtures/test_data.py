#!/usr/bin/env python3
"""
Test data fixtures for consistent testing across all test suites.
Provides standardized test data for decisions, queries, and expected responses.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta

# Standard test decision numbers
TEST_DECISIONS = {
    "basic": [1000, 1234, 2000, 2989, 3000],
    "government_36": [1000, 1001, 1002, 1003, 1004],
    "government_37": [2000, 2001, 2002, 2003, 2004, 2989],
    "government_38": [3000, 3001, 3002, 3003, 3004],
    "education": [1001, 2001, 2989, 3001],
    "health": [1002, 2002, 3002],
    "transport": [1003, 2003, 3003],
    "security": [1004, 2004, 3004],
    "recent": [2989, 3000, 3001, 3002, 3003, 3004]
}

# Standard test queries with expected behavior
TEST_QUERIES = {
    "specific_decision": {
        "queries": [
            "החלטה 2989",
            "החלטה 1234 של ממשלה 36",
            "תן לי את החלטה 3000"
        ],
        "expected_intent": "QUERY",
        "expected_entities": ["decision_number"],
        "cache_safe": False
    },
    
    "government_search": {
        "queries": [
            "החלטות ממשלה 37",
            "כל ההחלטות של ממשלה 36",
            "מה החליטה ממשלה 38?"
        ],
        "expected_intent": "QUERY",
        "expected_entities": ["government_number"],
        "cache_safe": True
    },
    
    "topic_search": {
        "queries": [
            "החלטות בנושא חינוך",
            "החלטות על בריאות",
            "תחבורה ציבורית החלטות"
        ],
        "expected_intent": "QUERY",
        "expected_entities": ["topic"],
        "cache_safe": True
    },
    
    "statistical": {
        "queries": [
            "כמה החלטות יש בנושא חינוך?",
            "מה מספר ההחלטות של ממשלה 37?",
            "כמה החלטות התקבלו ב-2024?"
        ],
        "expected_intent": "STATISTICAL",
        "expected_entities": ["count_only"],
        "cache_safe": True
    },
    
    "unclear": {
        "queries": [
            "מה?",
            "איפה?",
            "תראה לי החלטות",
            "משהו על חינוך"
        ],
        "expected_intent": "UNCLEAR",
        "expected_entities": [],
        "cache_safe": False
    },
    
    "reference": {
        "queries": [
            "תן לי את זה",
            "ספר לי עוד",
            "מה היה שם?",
            "ההחלטה האחרונה"
        ],
        "expected_intent": "RESULT_REF",
        "expected_entities": [],
        "cache_safe": False
    },
    
    "analysis": {
        "queries": [
            "נתח את החלטה 2989",
            "מה החוזקות והחולשות של החלטה 1000?",
            "הערך את ההשפעה של החלטה 3000"
        ],
        "expected_intent": "EVAL",
        "expected_entities": ["decision_number"],
        "cache_safe": False
    },
    
    "comparison": {
        "queries": [
            "השווה בין החלטה 1000 להחלטה 2000",
            "מה ההבדל בין ממשלה 36 לממשלה 37?",
            "השווה החלטות חינוך של 2023 מול 2024"
        ],
        "expected_intent": "COMPARISON",
        "expected_entities": ["comparison"],
        "cache_safe": False
    }
}

# Mock decision data for testing
MOCK_DECISIONS = {
    1000: {
        "decision_number": "1000",
        "government_number": 36,
        "title": "החלטה בנושא תשתיות חינוך",
        "topics": ["חינוך", "תשתיות"],
        "ministries": ["משרד החינוך", "משרד האוצר"],
        "budget": 500000000,
        "decision_date": "2023-01-15",
        "decision_url": "https://www.gov.il/he/departments/policies/dec1000_2023",
        "summary": "הקצאת תקציב לבניית בתי ספר חדשים",
        "operative_clauses": ["בניית 50 בתי ספר", "הקצאת 500 מיליון ש\"ח"],
        "is_operational": True
    },
    
    2000: {
        "decision_number": "2000",
        "government_number": 37,
        "title": "תכנית לאומית לבריאות דיגיטלית",
        "topics": ["בריאות", "טכנולוגיה"],
        "ministries": ["משרד הבריאות", "משרד החדשנות"],
        "budget": 300000000,
        "decision_date": "2024-03-20",
        "decision_url": "https://www.gov.il/he/departments/policies/dec2000_2024",
        "summary": "קידום דיגיטציה במערכת הבריאות",
        "operative_clauses": ["הקמת מערכת רשומות רפואיות", "חיבור כל בתי החולים"],
        "is_operational": True
    },
    
    2989: {
        "decision_number": "2989",
        "government_number": 37,
        "title": "רפורמה בחינוך הגבוה",
        "topics": ["חינוך", "השכלה גבוהה"],
        "ministries": ["משרד החינוך", "המועצה להשכלה גבוהה"],
        "budget": 1000000000,
        "decision_date": "2024-06-15",
        "decision_url": "https://www.gov.il/he/departments/policies/dec2989_2024",
        "summary": "הגדלת הנגישות להשכלה גבוהה",
        "operative_clauses": ["הקמת 5 מכללות חדשות", "מלגות ל-10,000 סטודנטים"],
        "is_operational": True
    },
    
    3000: {
        "decision_number": "3000",
        "government_number": 38,
        "title": "תכנית חירום לתחבורה ציבורית",
        "topics": ["תחבורה", "תשתיות"],
        "ministries": ["משרד התחבורה", "משרד האוצר"],
        "budget": 2000000000,
        "decision_date": "2024-07-01",
        "decision_url": "https://www.gov.il/he/departments/policies/dec3000_2024",
        "summary": "שיפור התחבורה הציבורית במטרופולינים",
        "operative_clauses": ["רכישת 500 אוטובוסים", "הקמת 20 קווי BRT"],
        "is_operational": True
    }
}

# Expected responses for common scenarios
EXPECTED_RESPONSES = {
    "specific_decision": {
        "pattern": r"החלטה מספר \d+ של ממשלה \d+",
        "must_contain": ["החלטה", "ממשלה", "תאריך"],
        "must_not_contain": ["לא נמצא", "שגיאה"]
    },
    
    "count_response": {
        "pattern": r"\d+ החלטות",
        "must_contain": ["החלטות"],
        "must_not_contain": ["רשימת", "הנה", "להלן"]
    },
    
    "clarification": {
        "pattern": r"(מה הייתם רוצים|אנא הבהירו|איזה)",
        "must_contain": ["?"],
        "must_not_contain": ["החלטה מספר", "ממשלה"]
    },
    
    "analysis": {
        "pattern": r"ניתוח החלטה",
        "must_contain": ["חוזקות", "חולשות", "ציון"],
        "must_not_contain": ["לא נמצא"]
    }
}

# Test conversation flows
TEST_CONVERSATIONS = {
    "research_flow": [
        ("החלטות בנושא חינוך מ-2024", "initial_search"),
        ("כמה החלטות מצאת?", "count_results"),
        ("נתח את הראשונה", "analyze_first"),
        ("יש החלטות דומות משנים קודמות?", "historical_comparison")
    ],
    
    "decision_exploration": [
        ("החלטה 2989", "find_decision"),
        ("תן לי את התוכן המלא", "full_content"),
        ("מה הסעיפים האופרטיביים?", "operative_clauses"),
        ("כמה תקציב הוקצה?", "budget_info"),
        ("נתח את ההחלטה", "analysis")
    ],
    
    "entity_accumulation": [
        ("ממשלה 37", "set_government"),
        ("בנושא בריאות", "add_topic"),
        ("משנת 2024", "add_year"),
        ("כמה יש?", "count_with_filters")
    ]
}

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "response_times": {
        "simple_query": 3.0,      # seconds
        "search_query": 5.0,
        "analysis_query": 15.0,
        "count_query": 3.0,
        "reference_query": 4.0
    },
    
    "cache_hit_rates": {
        "general_queries": 0.8,   # 80% hit rate expected
        "specific_queries": 0.0,  # Should not cache
        "statistical_queries": 0.9
    },
    
    "concurrent_sessions": {
        "max_sessions": 100,
        "queries_per_second": 10,
        "error_rate_threshold": 0.05  # 5% max
    }
}

# Error scenarios
ERROR_SCENARIOS = {
    "non_existent_decision": {
        "query": "החלטה 99999999",
        "expected_response": "לא נמצאה החלטה",
        "should_fail_gracefully": True
    },
    
    "invalid_syntax": {
        "query": "🦄🌈✨",
        "expected_response": "לא הצלחתי להבין",
        "should_fail_gracefully": True
    },
    
    "timeout_simulation": {
        "query": "נתח את כל ההחלטות של כל הממשלות",
        "expected_response": "timeout",
        "should_fail_gracefully": True
    }
}

def get_test_decision(decision_number: int) -> Dict[str, Any]:
    """Get mock decision data by number."""
    return MOCK_DECISIONS.get(decision_number, {
        "decision_number": str(decision_number),
        "government_number": 37,
        "title": f"החלטת מבחן {decision_number}",
        "topics": ["כללי"],
        "ministries": ["משרד ראש הממשלה"],
        "budget": 0,
        "decision_date": datetime.now().strftime("%Y-%m-%d"),
        "decision_url": f"https://www.gov.il/he/departments/policies/test{decision_number}",
        "summary": "החלטת מבחן לצורכי בדיקה",
        "operative_clauses": [],
        "is_operational": False
    })

def get_test_queries_by_type(query_type: str) -> List[str]:
    """Get test queries by type."""
    return TEST_QUERIES.get(query_type, {}).get("queries", [])

def get_expected_intent(query_type: str) -> str:
    """Get expected intent for query type."""
    return TEST_QUERIES.get(query_type, {}).get("expected_intent", "QUERY")

def is_cache_safe(query_type: str) -> bool:
    """Check if query type should be cached."""
    return TEST_QUERIES.get(query_type, {}).get("cache_safe", True)

def get_conversation_flow(flow_name: str) -> List[tuple]:
    """Get predefined conversation flow."""
    return TEST_CONVERSATIONS.get(flow_name, [])

def get_performance_benchmark(metric_type: str, sub_metric: str = None) -> float:
    """Get performance benchmark value."""
    benchmarks = PERFORMANCE_BENCHMARKS.get(metric_type, {})
    if sub_metric:
        return benchmarks.get(sub_metric, 0)
    return benchmarks

def validate_response(response: str, response_type: str) -> bool:
    """Validate if response matches expected pattern."""
    expected = EXPECTED_RESPONSES.get(response_type, {})
    
    # Check must contain
    for term in expected.get("must_contain", []):
        if term not in response:
            return False
    
    # Check must not contain
    for term in expected.get("must_not_contain", []):
        if term in response:
            return False
    
    return True

# Export all fixtures
__all__ = [
    'TEST_DECISIONS',
    'TEST_QUERIES',
    'MOCK_DECISIONS',
    'EXPECTED_RESPONSES',
    'TEST_CONVERSATIONS',
    'PERFORMANCE_BENCHMARKS',
    'ERROR_SCENARIOS',
    'get_test_decision',
    'get_test_queries_by_type',
    'get_expected_intent',
    'is_cache_safe',
    'get_conversation_flow',
    'get_performance_benchmark',
    'validate_response'
]