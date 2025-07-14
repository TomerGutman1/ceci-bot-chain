#!/usr/bin/env python3
"""
Test script for enhanced SQL generation capabilities.
"""
import asyncio
import json
from datetime import datetime
from uuid import uuid4
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from QUERY_SQL_GEN_BOT_2Q.main import (
    generate_enhanced_sql, detect_query_type, 
    clean_topic_entity, enhance_entities_with_context
)
from QUERY_SQL_GEN_BOT_2Q.synonym_mapper import (
    expand_topic_synonyms, get_all_synonyms_for_topic
)
from QUERY_SQL_GEN_BOT_2Q.date_interpreter import (
    interpret_hebrew_date, extract_date_from_entities
)


# Test cases for enhanced SQL generation
TEST_CASES = [
    {
        "name": "Count query with synonym",
        "intent": "DATA_QUERY",
        "entities": {
            "topic": "השכלה",  # Should expand to include חינוך
            "count_only": True,
            "date_range": {"start": "2024-01-01", "end": "2024-12-31"}
        },
        "expected": {
            "query_type": "count",
            "has_synonyms": True,
            "synonym_for": "השכלה"
        }
    },
    {
        "name": "Typo correction",
        "intent": "DATA_QUERY", 
        "entities": {
            "topic": "חנוך",  # Typo for חינוך
            "limit": 5
        },
        "expected": {
            "query_type": "list",
            "has_correction": True,
            "corrected_to": "חינוך"
        }
    },
    {
        "name": "Hebrew date interpretation",
        "intent": "DATA_QUERY",
        "entities": {
            "topic": "ביטחון השנה",  # Should extract current year
            "count_only": True
        },
        "expected": {
            "query_type": "count",
            "has_date": True,
            "date_extracted": True
        }
    },
    {
        "name": "Boolean flag query",
        "intent": "DATA_QUERY",
        "entities": {
            "topic": "תחבורה",
            "decision_type": "אופרטיבית",
            "count_only": True
        },
        "expected": {
            "query_type": "count",
            "has_operativity_filter": True
        }
    },
    {
        "name": "Comparison query",
        "intent": "comparison",
        "entities": {
            "government_numbers": [36, 37],
            "topic": "דיור"
        },
        "expected": {
            "query_type": "comparison"
        }
    },
    {
        "name": "Ministry synonym expansion",
        "intent": "DATA_QUERY",
        "entities": {
            "ministries": ["החינוך"],  # Should expand to משרד החינוך
            "limit": 10
        },
        "expected": {
            "query_type": "list",
            "has_ministry_synonyms": True
        }
    },
    {
        "name": "Relative date expression",
        "intent": "DATA_QUERY",
        "entities": {
            "topic": "כלכלה ב-3 השנים האחרונות"
        },
        "expected": {
            "query_type": "list",
            "has_date": True,
            "relative_date": True
        }
    },
    {
        "name": "Specific decision query",
        "intent": "specific_decision",
        "entities": {
            "government_number": 37,
            "decision_number": 2080
        },
        "expected": {
            "query_type": "specific"
        }
    }
]


def print_test_result(test_name: str, result: dict, expected: dict):
    """Print formatted test result."""
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"{'='*60}")
    
    # Check query type
    query_type_match = result.get("query_type") == expected.get("query_type")
    print(f"Query Type: {result.get('query_type')} {'✓' if query_type_match else '✗'}")
    
    # Check synonyms
    if expected.get("has_synonyms"):
        has_synonyms = len(result.get("synonym_expansions", {})) > 0
        print(f"Synonym Expansion: {has_synonyms} {'✓' if has_synonyms else '✗'}")
        if has_synonyms:
            print(f"  Synonyms: {result['synonym_expansions']}")
    
    # Check corrections
    if expected.get("has_correction"):
        has_warnings = any("תוקן" in w for w in result.get("validation_warnings", []))
        print(f"Typo Correction: {has_warnings} {'✓' if has_warnings else '✗'}")
        if has_warnings:
            print(f"  Warnings: {result['validation_warnings']}")
    
    # Check date interpretation
    if expected.get("has_date"):
        has_dates = len(result.get("date_interpretations", {})) > 0
        print(f"Date Interpretation: {has_dates} {'✓' if has_dates else '✗'}")
        if has_dates:
            print(f"  Dates: {result['date_interpretations']}")
    
    # Print SQL
    print(f"\nGenerated SQL:")
    print(f"  {result.get('sql', 'No SQL generated')}")
    
    # Print parameters
    if result.get("parameters"):
        print(f"\nParameters:")
        for k, v in result["parameters"].items():
            print(f"  {k}: {v}")
    
    # Print confidence
    print(f"\nConfidence Score: {result.get('confidence_score', 0):.2f}")
    
    # Print method
    print(f"Method: {result.get('method', 'unknown')}")


async def run_tests():
    """Run all test cases."""
    print("Enhanced SQL Generation Test Suite")
    print("="*60)
    
    for test_case in TEST_CASES:
        try:
            # Run enhanced SQL generation
            result = await generate_enhanced_sql(
                test_case["intent"],
                test_case["entities"].copy(),
                use_enhanced=True
            )
            
            # Print results
            print_test_result(
                test_case["name"],
                result,
                test_case["expected"]
            )
            
        except Exception as e:
            print(f"\n❌ Test Failed: {test_case['name']}")
            print(f"   Error: {str(e)}")
    
    print("\n" + "="*60)
    print("Test Suite Complete")


def test_synonym_expansion():
    """Test synonym expansion functionality."""
    print("\nTesting Synonym Expansion")
    print("-"*40)
    
    test_topics = ["חינוך", "השכלה", "חנוך", "ביטחון", "בטחון"]
    
    for topic in test_topics:
        synonyms = list(get_all_synonyms_for_topic(topic))
        print(f"{topic} → {synonyms}")


def test_date_interpretation():
    """Test date interpretation functionality."""
    print("\nTesting Date Interpretation")
    print("-"*40)
    
    test_dates = [
        "השנה",
        "החודש",
        "השנה שעברה",
        "3 השנים האחרונות",
        "בין 2020 ל-2023",
        "ינואר 2024"
    ]
    
    for date_text in test_dates:
        result = interpret_hebrew_date(date_text)
        print(f"{date_text} → {result}")


def test_query_type_detection():
    """Test query type detection."""
    print("\nTesting Query Type Detection")
    print("-"*40)
    
    test_queries = [
        ("count", {"count_only": True}, "count"),
        ("DATA_QUERY", {"topic": "כמה החלטות"}, "count"),
        ("comparison", {"comparison_target": True}, "comparison"),
        ("ANALYSIS", {}, "analysis"),
        ("DATA_QUERY", {"government_number": 37, "decision_number": 100}, "specific"),
        ("search", {"topic": "חינוך"}, "list")
    ]
    
    for intent, entities, expected in test_queries:
        result = detect_query_type(intent, entities)
        status = "✓" if result == expected else "✗"
        print(f"Intent: {intent}, Entities: {entities} → {result} {status}")


if __name__ == "__main__":
    # Set environment to use enhanced SQL
    os.environ["USE_ENHANCED_SQL_GEN"] = "true"
    
    # Run unit tests
    print("Running Unit Tests...")
    test_synonym_expansion()
    test_date_interpretation()
    test_query_type_detection()
    
    # Run integration tests
    print("\n\nRunning Integration Tests...")
    asyncio.run(run_tests())