"""
Comprehensive test cases for Reference Resolution in Context Router Bot.
Tests the scenarios from the specification plus edge cases.
"""

import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from uuid import uuid4

from reference_config import reference_config

# Import reference resolver without memory service dependency
import sys
import os
import importlib.util

# Load reference resolver manually to avoid Redis dependency
spec = importlib.util.spec_from_file_location("reference_resolver", "reference_resolver.py")
reference_resolver_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference_resolver_module)
ReferenceResolver = reference_resolver_module.ReferenceResolver


class MockMemoryService:
    """Mock memory service for testing without Redis dependency."""
    
    def __init__(self):
        self.conversations = {}
    
    def append(self, conv_id: str, turn_data: Dict[str, Any]) -> bool:
        """Add a turn to conversation history."""
        if conv_id not in self.conversations:
            self.conversations[conv_id] = []
        
        self.conversations[conv_id].append(turn_data)
        
        # Keep only last 20 turns
        if len(self.conversations[conv_id]) > 20:
            self.conversations[conv_id] = self.conversations[conv_id][-20:]
        
        return True
    
    def fetch(self, conv_id: str) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.conversations.get(conv_id, [])
    
    def clear(self, conv_id: str) -> bool:
        """Clear conversation history."""
        if conv_id in self.conversations:
            del self.conversations[conv_id]
        return True


class ReferenceResolutionTester:
    """Test suite for reference resolution functionality."""
    
    def __init__(self):
        self.mock_memory = MockMemoryService()
        self.resolver = ReferenceResolver(memory_service=self.mock_memory)
        self.test_results = []
    
    def setup_conversation_history(self, conv_id: str, history: List[Dict[str, str]]):
        """Setup conversation history for testing."""
        for i, turn in enumerate(history):
            turn_data = {
                'turn_id': str(uuid4()),
                'speaker': turn['speaker'],
                'clean_text': turn['text'],
                'timestamp': datetime.utcnow().isoformat()
            }
            self.mock_memory.append(conv_id, turn_data)
    
    def run_test_case(self, test_name: str, conv_id: str, user_text: str, 
                      current_entities: Dict[str, Any], intent: str,
                      history: List[Dict[str, str]], expected_outcome: str):
        """Run a single test case."""
        print(f"\n🧪 Running Test: {test_name}")
        print(f"Input: '{user_text}'")
        print(f"Current entities: {current_entities}")
        print(f"Intent: {intent}")
        
        # Setup history
        self.setup_conversation_history(conv_id, history)
        
        # Run reference resolution
        result = self.resolver.resolve_references(
            conv_id=conv_id,
            user_text=user_text,
            current_entities=current_entities,
            intent=intent
        )
        
        print(f"📊 Result:")
        print(f"  - Route: {result['route']}")
        print(f"  - Enriched Query: '{result['enriched_query']}'")
        print(f"  - Resolved Entities: {result['resolved_entities']}")
        print(f"  - Needs Clarification: {result['needs_clarification']}")
        if result['clarification_prompt']:
            print(f"  - Clarification: '{result['clarification_prompt']}'")
        print(f"  - Reasoning: {result['reasoning']}")
        
        # Check if result matches expected outcome
        success = result['route'] == expected_outcome
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - Expected: {expected_outcome}, Got: {result['route']}")
        
        self.test_results.append({
            'test_name': test_name,
            'success': success,
            'expected': expected_outcome,
            'actual': result['route'],
            'result': result
        })
        
        # Clear conversation for next test
        self.mock_memory.clear(conv_id)
        
        return result
    
    def test_scenario_1_direct_government_decision(self):
        """Test: Direct government+decision reference."""
        return self.run_test_case(
            test_name="Direct Government + Decision",
            conv_id="test_conv_1",
            user_text="החלטה 276",
            current_entities={},
            intent="QUERY",
            history=[
                {"speaker": "user", "text": "ממשלה 36"}
            ],
            expected_outcome="enriched"
        )
    
    def test_scenario_2_missing_government_from_input(self):
        """Test: Missing government from input, found in history (with bot response in between)."""
        return self.run_test_case(
            test_name="Missing Government from Input",
            conv_id="test_conv_2", 
            user_text="החלטה 100",
            current_entities={},
            intent="QUERY",
            history=[
                {"speaker": "user", "text": "אני מחפש על ממשלה 35"},
                {"speaker": "bot", "text": "מה אתה רוצה לדעת על ממשלה 35?"},
                {"speaker": "user", "text": "משהו אחר"},
                {"speaker": "bot", "text": "אוקיי, מה עוד?"}
            ],
            expected_outcome="enriched"
        )
    
    def test_scenario_3_date_range_only(self):
        """Test: Date range only - should request clarification."""
        return self.run_test_case(
            test_name="Date Range Only",
            conv_id="test_conv_3",
            user_text="בין 1/5/2022 - 30/6/2022",
            current_entities={},
            intent="QUERY",
            history=[],
            expected_outcome="clarify"
        )
    
    def test_scenario_4_decision_with_date_in_history(self):
        """Test: Decision only, date range in history (with bot response in between)."""
        return self.run_test_case(
            test_name="Decision with Date in History",
            conv_id="test_conv_4",
            user_text="החלטה 50",
            current_entities={},
            intent="QUERY", 
            history=[
                {"speaker": "user", "text": "בין 1/1/2023 - 31/1/2023"},
                {"speaker": "bot", "text": "איזה החלטה אתה מחפש בתקופה הזו?"}
            ],
            expected_outcome="enriched"
        )
    
    def test_scenario_5_government_with_decision_in_history(self):
        """Test: Government only, decision in history (with bot response in between)."""
        return self.run_test_case(
            test_name="Government with Decision in History", 
            conv_id="test_conv_5",
            user_text="ממשלה 34",
            current_entities={},
            intent="QUERY",
            history=[
                {"speaker": "user", "text": "אני רוצה החלטה 88"},
                {"speaker": "bot", "text": "איזה ממשלה? אני צריך לדעת מאיזה ממשלה החלטה 88"}
            ],
            expected_outcome="enriched"
        )
    
    def test_scenario_6_multiple_candidates_in_history(self):
        """Test: Multiple candidates - should use most recent (with bot responses in between).""" 
        return self.run_test_case(
            test_name="Multiple Candidates - Recency",
            conv_id="test_conv_6",
            user_text="תן לי את התוכן המלא",
            current_entities={},
            intent="ANALYSIS",
            history=[
                {"speaker": "user", "text": "החלטה 12"},
                {"speaker": "bot", "text": "נמצאה החלטה 12, איזה ממשלה?"},
                {"speaker": "user", "text": "החלטה 12 של ממשלה 30"},
                {"speaker": "bot", "text": "נמצאה החלטה 12 של ממשלה 30"}
            ],
            expected_outcome="enriched"
        )
    
    def test_scenario_7_fuzzy_match_threshold(self):
        """Test: Fuzzy matching for Hebrew text variations."""
        return self.run_test_case(
            test_name="Fuzzy Match Threshold",
            conv_id="test_conv_7", 
            user_text="החלטה תשעים",
            current_entities={},
            intent="QUERY",
            history=[
                {"speaker": "user", "text": "החלטה 90"}
            ],
            expected_outcome="enriched"
        )
    
    def test_scenario_8_near_limit_history(self):
        """Test: History search within configured limit."""
        # Create 21 turns, with relevant info at position 19
        history = []
        for i in range(18):
            history.append({"speaker": "user", "text": f"הודעה {i}"})
        
        history.append({"speaker": "user", "text": "ממשלה 41"})  # Position 19
        history.append({"speaker": "user", "text": "משהו אחר"})  # Position 20
        history.append({"speaker": "user", "text": "ממשלה 40"})  # Position 21 (should be ignored)
        
        return self.run_test_case(
            test_name="Near Limit History",
            conv_id="test_conv_8",
            user_text="החלטה 200", 
            current_entities={},
            intent="QUERY",
            history=history,
            expected_outcome="enriched"
        )
    
    def test_scenario_9_ambiguous_reference(self):
        """Test: Ambiguous reference - should clarify."""
        return self.run_test_case(
            test_name="Ambiguous Reference",
            conv_id="test_conv_9",
            user_text="החלטה X",
            current_entities={},
            intent="QUERY", 
            history=[],
            expected_outcome="clarify"
        )
    
    def test_scenario_10_complex_combination(self):
        """Test: User refers to multiple slots from history."""
        return self.run_test_case(
            test_name="Complex Combination",
            conv_id="test_conv_10",
            user_text="בין 10/2/2024 - 15/2/2024",
            current_entities={},
            intent="QUERY",
            history=[
                {"speaker": "user", "text": "החלטה 15 של ממשלה 39"}
            ],
            expected_outcome="enriched"
        )
    
    def test_scenario_11_partial_reference_user_case(self):
        """Test: יוזר מרפרנס להודעה קודמת בצורה לא שקופה - זה המקרה שהמשתמש ציין."""
        return self.run_test_case(
            test_name="Partial Reference - Real User Case",
            conv_id="test_conv_11",
            user_text="תן לי את זה",
            current_entities={},
            intent="QUERY",
            history=[
                {"speaker": "user", "text": "החלטה 2989 של ממשלה 37"},
                {"speaker": "bot", "text": "נמצאה החלטה 2989 של ממשלה 37. הנה התקציר: ..."}
            ],
            expected_outcome="enriched"
        )
    
    def test_scenario_12_implicit_continuation(self):
        """Test: המשך שיחה בצורה לא מפורשת - עם תגובת בוט ביניהן."""
        return self.run_test_case(
            test_name="Implicit Continuation with Bot Response",
            conv_id="test_conv_12", 
            user_text="תוכן מלא",
            current_entities={},
            intent="ANALYSIS",
            history=[
                {"speaker": "user", "text": "החלטה 1234"},
                {"speaker": "bot", "text": "נמצאה החלטה 1234. הנה תקציר קצר: ..."}
            ],
            expected_outcome="enriched"
        )
    
    def test_scenario_13_contextual_follow_up(self):
        """Test: שאלת המשך שתלויה בהקשר - עם תגובת בוט ביניהן."""
        return self.run_test_case(
            test_name="Contextual Follow-up with Bot Response",
            conv_id="test_conv_13",
            user_text="נתח את התוכן",
            current_entities={},
            intent="ANALYSIS", 
            history=[
                {"speaker": "user", "text": "החלטה 2766 ממשלה 36"},
                {"speaker": "bot", "text": "הנה תקציר החלטה 2766 של ממשלה 36: פרטי החלטה..."}
            ],
            expected_outcome="enriched"
        )
    
    def test_scenario_14_realistic_conversation_flow(self):
        """Test: תרחיש מציאותי - משתמש ובוט עם תגובות ביניהן."""
        return self.run_test_case(
            test_name="Realistic Conversation Flow",
            conv_id="test_conv_14",
            user_text="תן לי עוד פרטים",
            current_entities={},
            intent="ANALYSIS", 
            history=[
                {"speaker": "user", "text": "החלטה 2989 של ממשלה 37"},
                {"speaker": "bot", "text": "נמצאה החלטה 2989 של ממשלה 37. הנה תקציר: החלטה בנושא תקציב..."},
                {"speaker": "user", "text": "איך זה קשור לחינוך?"},
                {"speaker": "bot", "text": "החלטה זו משפיעה על תקציב החינוך באופן הבא..."}
            ],
            expected_outcome="enriched"
        )
    
    def test_scenario_15_multiple_user_bot_exchanges(self):
        """Test: מספר חילופי דברים בין משתמש לבוט."""
        return self.run_test_case(
            test_name="Multiple User-Bot Exchanges",
            conv_id="test_conv_15",
            user_text="החלטה 456",
            current_entities={},
            intent="QUERY", 
            history=[
                {"speaker": "user", "text": "ממשלה 35"},
                {"speaker": "bot", "text": "מה אתה רוצה לדעת על ממשלה 35?"},
                {"speaker": "user", "text": "מה עם התקציב?"},
                {"speaker": "bot", "text": "איזה החלטה תקציבית? צריך מספר החלטה"},
                {"speaker": "user", "text": "רגע אני בודק"},
                {"speaker": "bot", "text": "בסדר, אני מחכה"}
            ],
            expected_outcome="enriched"
        )
    
    def run_all_tests(self):
        """Run all test scenarios."""
        print("🚀 Starting Reference Resolution Test Suite")
        print("=" * 60)
        
        test_methods = [
            self.test_scenario_1_direct_government_decision,
            self.test_scenario_2_missing_government_from_input, 
            self.test_scenario_3_date_range_only,
            self.test_scenario_4_decision_with_date_in_history,
            self.test_scenario_5_government_with_decision_in_history,
            self.test_scenario_6_multiple_candidates_in_history,
            self.test_scenario_7_fuzzy_match_threshold,
            self.test_scenario_8_near_limit_history,
            self.test_scenario_9_ambiguous_reference,
            self.test_scenario_10_complex_combination,
            self.test_scenario_11_partial_reference_user_case,
            self.test_scenario_12_implicit_continuation,
            self.test_scenario_13_contextual_follow_up,
            self.test_scenario_14_realistic_conversation_flow,
            self.test_scenario_15_multiple_user_bot_exchanges
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                self.test_results.append({
                    'test_name': test_method.__name__,
                    'success': False,
                    'error': str(e)
                })
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Show resolver metrics
        print("\n📈 REFERENCE RESOLVER METRICS:")
        metrics = self.resolver.get_metrics()
        for key, value in metrics.items():
            print(f"  {key}: {value}")
        
        return self.test_results


if __name__ == "__main__":
    # Run the test suite
    tester = ReferenceResolutionTester()
    results = tester.run_all_tests()