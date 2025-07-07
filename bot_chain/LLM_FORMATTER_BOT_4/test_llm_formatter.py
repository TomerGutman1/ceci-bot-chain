#!/usr/bin/env python3
"""
Test script for the LLM Formatter Bot.
Tests various formatting scenarios including decision cards, analysis, counts, and comparisons.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any
from colorama import init, Fore, Style

# Initialize colorama
init()

# Test configuration
BOT_URL = "http://localhost:8017"
ENDPOINT = "/format"

# Test cases
TEST_CASES = [
    # Decision cards formatting
    {
        "name": "Format decision cards",
        "input": {
            "data_type": "ranked_rows",
            "content": {
                "results": [
                    {
                        "id": 1,
                        "decision_title": "תוכנית לאומית לחינוך דיגיטלי",
                        "government_number": 37,
                        "decision_number": 2983,
                        "decision_date": "2024-05-15",
                        "decision_url": "https://www.gov.il/he/departments/policies/dec2983_2024",
                        "summary": "הקמת תוכנית לאומית להטמעת כלים דיגיטליים במערכת החינוך",
                        "tags_policy_area": "חינוך;טכנולוגיה",
                        "tags_government_body": "משרד החינוך;משרד הדיגיטל",
                        "status": "בתוקף"
                    },
                    {
                        "id": 2,
                        "decision_title": "רפורמה בבריאות הציבור",
                        "government_number": 37,
                        "decision_number": 2984,
                        "decision_date": "2024-05-16",
                        "summary": "שיפור שירותי הבריאות הציבוריים ברחבי הארץ",
                        "tags_policy_area": "בריאות",
                        "tags_government_body": "משרד הבריאות",
                        "status": "בתוקף"
                    }
                ]
            },
            "original_query": "החלטות אחרונות",
            "presentation_style": "card",
            "conv_id": "test-format-001"
        },
        "expected_contains": ["תוכנית לאומית לחינוך דיגיטלי", "רפורמה בבריאות הציבור", "✅"]
    },
    
    # Count formatting
    {
        "name": "Format count result",
        "input": {
            "data_type": "count",
            "content": {
                "count": 42,
                "topic": "חינוך",
                "year": 2024
            },
            "original_query": "כמה החלטות בנושא חינוך ב-2024",
            "presentation_style": "brief",
            "conv_id": "test-format-002"
        },
        "expected_contains": ["42", "חינוך", "2024", "📊"]
    },
    
    # Analysis formatting
    {
        "name": "Format analysis result",
        "input": {
            "data_type": "analysis",
            "content": {
                "evaluation": {
                    "overall_score": 0.75,
                    "relevance_level": "high",
                    "explanation": "ההחלטה מציגה תוכנית מפורטת עם לוחות זמנים ברורים ותקציב מוגדר."
                },
                "decision": {
                    "decision_title": "תוכנית לאומית לחינוך דיגיטלי",
                    "decision_number": 2983
                }
            },
            "original_query": "נתח את החלטה 2983",
            "presentation_style": "detailed",
            "conv_id": "test-format-003"
        },
        "expected_contains": ["ניתוח החלטה", "75", "ציון ישימות", "תוכנית מפורטת"]
    },
    
    # Empty results
    {
        "name": "Format empty results",
        "input": {
            "data_type": "ranked_rows",
            "content": {
                "results": []
            },
            "original_query": "החלטות בנושא חלל",
            "presentation_style": "card",
            "conv_id": "test-format-004"
        },
        "expected_contains": ["לא נמצאו תוצאות"]
    }
]


def print_test_header(name: str):
    """Print a formatted test header."""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"Test: {name}")
    print(f"{'=' * 60}{Style.RESET_ALL}")


def print_success(message: str):
    """Print a success message."""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")


def check_health():
    """Check if the bot is healthy."""
    try:
        response = requests.get(f"{BOT_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print_success(f"Bot is healthy - Model: {health_data.get('model', 'unknown')}")
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


def run_test(test_case: Dict[str, Any]) -> bool:
    """Run a single test case."""
    print_test_header(test_case["name"])
    
    try:
        print(f"Data Type: {test_case['input']['data_type']}")
        print(f"Style: {test_case['input']['presentation_style']}")
        
        response = requests.post(
            f"{BOT_URL}{ENDPOINT}",
            json=test_case["input"],
            timeout=15
        )
        
        if response.status_code != 200:
            print_error(f"Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        
        # Print formatted response
        print(f"\n{Fore.YELLOW}Formatted Response:{Style.RESET_ALL}")
        print("-" * 40)
        print(result.get("formatted_response", "N/A"))
        print("-" * 40)
        
        # Check metadata
        metadata = result.get("metadata", {})
        print(f"\nMetadata:")
        print(f"  Format Type: {metadata.get('format_type', 'N/A')}")
        print(f"  Cards Generated: {metadata.get('cards_generated', 0)}")
        print(f"  Word Count: {metadata.get('word_count', 0)}")
        
        # Check token usage
        if "token_usage" in result:
            usage = result["token_usage"]
            print(f"\n  Token Usage: {usage.get('total_tokens', 0)} tokens")
            print(f"  Model: {usage.get('model', 'N/A')}")
        
        # Check expected content
        passed = True
        formatted_response = result.get("formatted_response", "")
        expected_contains = test_case.get("expected_contains", [])
        
        for expected in expected_contains:
            if expected not in formatted_response:
                print_warning(f"Expected content not found: '{expected}'")
                passed = False
        
        if passed:
            print_success("Test passed")
        else:
            print_error("Test failed - missing expected content")
        
        return passed
        
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        return False


def main():
    """Run all tests."""
    print(f"{Fore.MAGENTA}{'=' * 60}")
    print(f"LLM Formatter Bot Test Suite")
    print(f"Bot URL: {BOT_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'=' * 60}{Style.RESET_ALL}")
    
    # Check health first
    if not check_health():
        print_error("Bot is not healthy. Exiting.")
        sys.exit(1)
    
    # Run tests
    passed = 0
    failed = 0
    
    for test_case in TEST_CASES:
        if run_test(test_case):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{Fore.MAGENTA}{'=' * 60}")
    print(f"Test Summary")
    print(f"{'=' * 60}{Style.RESET_ALL}")
    print(f"Total tests: {len(TEST_CASES)}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    
    # Calculate success rate
    success_rate = (passed / len(TEST_CASES)) * 100 if TEST_CASES else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    # Exit code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()