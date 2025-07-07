#!/usr/bin/env python3
"""
Test script for the Unified Intent Bot.
Tests various Hebrew queries to ensure proper normalization and intent detection.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init()

# Test configuration
BOT_URL = "http://localhost:8011"
ENDPOINT = "/intent"

# Test cases covering various scenarios
TEST_CASES = [
    # Typos and corrections
    {
        "name": "Typo correction",
        "input": {
            "raw_user_text": "החלתה 2983 ממשלת 37 נתח לעומק",
            "conv_id": "test-001"
        },
        "expected": {
            "clean_query": "החלטה 2983 של ממשלה 37 - ניתוח מעמיק",
            "intent": "ANALYSIS",
            "params": {
                "decision_number": 2983,
                "government_number": 37
            }
        }
    },
    
    # Statistical queries
    {
        "name": "Count query",
        "input": {
            "raw_user_text": "כמה החלטות בנושא חינוך היו ב-2024?",
            "conv_id": "test-002"
        },
        "expected": {
            "intent": "DATA_QUERY",
            "params": {
                "topic": "חינוך",
                "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
                "count_only": True
            }
        }
    },
    
    # Hebrew numbers
    {
        "name": "Hebrew number conversion",
        "input": {
            "raw_user_text": "החלטות ממשלה שלושים ושבע",
            "conv_id": "test-003"
        },
        "expected": {
            "clean_query": "החלטות ממשלה 37",
            "intent": "DATA_QUERY",
            "params": {
                "government_number": 37
            }
        }
    },
    
    # Reference queries
    {
        "name": "Reference to previous",
        "input": {
            "raw_user_text": "תן לי את ההחלטה השלישית ששלחת",
            "conv_id": "test-004"
        },
        "expected": {
            "intent": "RESULT_REF",
            "params": {
                "index_in_previous": 3,
                "reference_type": "sent"
            }
        }
    },
    
    # Date range queries
    {
        "name": "Date range",
        "input": {
            "raw_user_text": "החלטות בין 2020 ל-2023",
            "conv_id": "test-005"
        },
        "expected": {
            "intent": "DATA_QUERY",
            "params": {
                "date_range": {"start": "2020-01-01", "end": "2023-12-31"}
            }
        }
    },
    
    # Mixed Hebrew-English
    {
        "name": "Mixed language",
        "input": {
            "raw_user_text": "תן לי decision 2983 של government 37",
            "conv_id": "test-006"
        },
        "expected": {
            "clean_query": "תן לי החלטה 2983 של ממשלה 37",
            "intent": "DATA_QUERY",
            "params": {
                "decision_number": 2983,
                "government_number": 37
            }
        }
    },
    
    # Unclear queries
    {
        "name": "Unclear query",
        "input": {
            "raw_user_text": "מה?",
            "conv_id": "test-007"
        },
        "expected": {
            "intent": "UNCLEAR",
            "params": {}
        }
    },
    
    # Complex queries
    {
        "name": "Complex query with multiple params",
        "input": {
            "raw_user_text": "5 החלטות אחרונות בנושא בריאות של ממשלה 37",
            "conv_id": "test-008"
        },
        "expected": {
            "intent": "DATA_QUERY",
            "params": {
                "limit": 5,
                "topic": "בריאות",
                "government_number": 37
            }
        }
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
    
    # Make request
    try:
        print(f"Input: {json.dumps(test_case['input']['raw_user_text'], ensure_ascii=False)}")
        
        response = requests.post(
            f"{BOT_URL}{ENDPOINT}",
            json=test_case["input"],
            timeout=10
        )
        
        if response.status_code != 200:
            print_error(f"Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        
        # Print results
        print(f"\nResponse:")
        print(f"  Clean Query: {result.get('clean_query', 'N/A')}")
        print(f"  Intent: {result.get('intent', 'N/A')}")
        print(f"  Params: {json.dumps(result.get('params', {}), ensure_ascii=False, indent=2)}")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
        
        # Check expectations
        passed = True
        expected = test_case.get("expected", {})
        
        # Check clean_query if expected
        if "clean_query" in expected:
            if result.get("clean_query") != expected["clean_query"]:
                print_warning(f"Clean query mismatch: expected '{expected['clean_query']}', got '{result.get('clean_query')}'")
                passed = False
        
        # Check intent
        if "intent" in expected:
            if result.get("intent") != expected["intent"]:
                print_error(f"Intent mismatch: expected '{expected['intent']}', got '{result.get('intent')}'")
                passed = False
        
        # Check params
        if "params" in expected:
            result_params = result.get("params", {})
            for key, value in expected["params"].items():
                if key not in result_params:
                    print_warning(f"Missing param '{key}'")
                    passed = False
                elif result_params[key] != value:
                    print_warning(f"Param '{key}' mismatch: expected {value}, got {result_params[key]}")
                    passed = False
        
        # Check token usage
        if "token_usage" in result:
            usage = result["token_usage"]
            print(f"\n  Token Usage: {usage.get('total_tokens', 0)} tokens (${usage.get('total_tokens', 0) * 0.00003:.4f})")
        
        if passed:
            print_success("Test passed")
        else:
            print_error("Test failed")
        
        return passed
        
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        return False


def main():
    """Run all tests."""
    print(f"{Fore.MAGENTA}{'=' * 60}")
    print(f"Unified Intent Bot Test Suite")
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