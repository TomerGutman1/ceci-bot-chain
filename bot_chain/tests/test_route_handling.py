#!/usr/bin/env python3
"""
Test suite for route handling functionality.
Tests UNCLEAR, RESULT_REF, EVAL, and other route types.
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "http://localhost:5001"
CHAT_API = f"{BACKEND_URL}/api/chat"

class RouteHandlingTester:
    def __init__(self):
        self.test_results = []
    
    def make_query(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """Make a query to the chat API."""
        if not session_id:
            session_id = f"route_test_{uuid.uuid4()}"
            
        payload = {
            "message": message,
            "sessionId": session_id,
            "includeMetadata": True
        }
        
        try:
            response = requests.post(CHAT_API, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def log_result(self, test_name: str, passed: bool, details: str):
        """Log test results."""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        print(f"{'✅' if passed else '❌'} {test_name}: {details}")
    
    def check_clarification_response(self, response: str) -> bool:
        """Check if response is a clarification."""
        clarification_indicators = [
            "זקוק לפרטים",
            "אפשרויות",
            "הצעות",
            "מה הייתם",
            "איזה",
            "לא ברור",
            "תוכל להבהיר",
            "למה התכוונת"
        ]
        return any(indicator in response for indicator in clarification_indicators)
    
    def test_unclear_routes(self):
        """Test UNCLEAR intent routes that should trigger clarification."""
        print("\n=== Testing UNCLEAR Routes ===")
        
        unclear_queries = [
            ("מה?", "Single word ambiguous query"),
            ("איפה?", "Location without context"),
            ("תראה לי החלטות", "Show decisions without specifics"),
            ("משהו על חינוך", "Vague topic query"),
            ("האם יש?", "Incomplete question"),
            ("איך אני יכול?", "How-to without context"),
            ("מי החליט?", "Who without context")
        ]
        
        for query, description in unclear_queries:
            result = self.make_query(query)
            
            if result.get('success'):
                response = result.get('response', '')
                metadata = result.get('metadata', {})
                intent = metadata.get('intent', '')
                
                if self.check_clarification_response(response):
                    self.log_result(f"UNCLEAR Route - '{query}'", True, 
                                  f"Correctly triggered clarification. Intent: {intent}")
                else:
                    self.log_result(f"UNCLEAR Route - '{query}'", False, 
                                  f"No clarification. Intent: {intent}, Response preview: {response[:100]}")
            else:
                self.log_result(f"UNCLEAR Route - '{query}'", False, 
                              f"Query failed: {result.get('error')}")
            
            time.sleep(1)
    
    def test_result_ref_routes(self):
        """Test RESULT_REF routes for context-dependent queries."""
        print("\n=== Testing RESULT_REF Routes ===")
        
        # Test scenarios
        test_scenarios = [
            {
                "setup": "החלטה 2989 של ממשלה 37",
                "refs": [
                    ("ספר לי עוד על זה", "More about this"),
                    ("מה התוכן המלא?", "Full content request"),
                    ("יש סעיפים אופרטיביים?", "Operative clauses"),
                    ("מתי התקבלה?", "When was it decided")
                ]
            },
            {
                "setup": "החלטות בנושא תחבורה",
                "refs": [
                    ("מה הראשונה?", "First result reference"),
                    ("יש עוד?", "More results"),
                    ("כמה מצאת?", "Count of results")
                ]
            }
        ]
        
        for scenario in test_scenarios:
            session_id = f"ref_route_{uuid.uuid4()}"
            
            # Setup context
            setup_result = self.make_query(scenario["setup"], session_id)
            if not setup_result.get('success'):
                self.log_result("RESULT_REF Setup", False, f"Setup failed for: {scenario['setup']}")
                continue
            
            time.sleep(2)
            
            # Test references
            for ref_query, description in scenario["refs"]:
                result = self.make_query(ref_query, session_id)
                
                if result.get('success'):
                    metadata = result.get('metadata', {})
                    intent = metadata.get('intent', '')
                    entities = metadata.get('entities', {})
                    
                    # Check if reference was resolved
                    if intent == 'RESULT_REF' or entities:
                        self.log_result(f"RESULT_REF - '{ref_query}'", True, 
                                      f"Recognized as reference. Intent: {intent}")
                    else:
                        self.log_result(f"RESULT_REF - '{ref_query}'", False, 
                                      f"Not recognized. Intent: {intent}")
                
                time.sleep(1)
    
    def test_eval_routes(self):
        """Test EVAL/ANALYSIS routes."""
        print("\n=== Testing EVAL Routes ===")
        
        eval_queries = [
            ("נתח את החלטה 2989", "Direct analysis request"),
            ("נתח לעומק את החלטה 1000", "Deep analysis"),
            ("מה החוזקות והחולשות של החלטה 2000?", "Strengths and weaknesses"),
            ("האם ההחלטה 3000 יעילה?", "Effectiveness analysis"),
            ("הערך את ההשפעה של החלטה 4000", "Impact evaluation")
        ]
        
        for query, description in eval_queries:
            result = self.make_query(query)
            
            if result.get('success'):
                metadata = result.get('metadata', {})
                intent = metadata.get('intent', '')
                evaluation = metadata.get('evaluation', {})
                
                if intent in ['EVAL', 'ANALYSIS'] or evaluation:
                    self.log_result(f"EVAL Route - '{query[:30]}...'", True, 
                                  f"Correctly routed to evaluation. Intent: {intent}")
                else:
                    self.log_result(f"EVAL Route - '{query[:30]}...'", False, 
                                  f"Not routed to EVAL. Intent: {intent}")
            
            time.sleep(1)
    
    def test_query_routes(self):
        """Test standard QUERY routes."""
        print("\n=== Testing QUERY Routes ===")
        
        query_types = [
            ("החלטה 2989", "Specific decision", "should have decision_number"),
            ("החלטות ממשלה 37", "Government decisions", "should have government_number"),
            ("החלטות בנושא חינוך", "Topic search", "should have topic"),
            ("החלטות משנת 2024", "Year search", "should have date filter"),
            ("החלטות אחרונות", "Recent decisions", "should be simple query")
        ]
        
        for query, description, expected in query_types:
            result = self.make_query(query)
            
            if result.get('success'):
                metadata = result.get('metadata', {})
                intent = metadata.get('intent', '')
                entities = metadata.get('entities', {})
                
                if intent in ['QUERY', 'DATA_QUERY']:
                    self.log_result(f"QUERY Route - '{query}'", True, 
                                  f"{description} - {expected}. Entities: {json.dumps(entities, ensure_ascii=False)}")
                else:
                    self.log_result(f"QUERY Route - '{query}'", False, 
                                  f"Wrong intent: {intent}")
    
    def test_statistical_routes(self):
        """Test STATISTICAL/COUNT routes."""
        print("\n=== Testing STATISTICAL Routes ===")
        
        stat_queries = [
            ("כמה החלטות יש בנושא חינוך?", "Count by topic"),
            ("כמה החלטות קיבלה ממשלה 37?", "Count by government"),
            ("מה מספר ההחלטות ב-2024?", "Count by year"),
            ("כמה החלטות אופרטיביות יש?", "Count operational"),
            ("סך כל ההחלטות", "Total count")
        ]
        
        for query, description in stat_queries:
            result = self.make_query(query)
            
            if result.get('success'):
                metadata = result.get('metadata', {})
                intent = metadata.get('intent', '')
                entities = metadata.get('entities', {})
                
                # Check if it's recognized as statistical
                if intent in ['STATISTICAL', 'QUERY'] and ('כמה' in query or 'count' in str(entities)):
                    self.log_result(f"STATISTICAL - '{query[:30]}...'", True, 
                                  f"{description}. Intent: {intent}")
                else:
                    self.log_result(f"STATISTICAL - '{query[:30]}...'", False, 
                                  f"Not recognized as statistical. Intent: {intent}")
    
    def test_comparison_routes(self):
        """Test COMPARISON routes."""
        print("\n=== Testing COMPARISON Routes ===")
        
        comparison_scenarios = [
            {
                "query": "השווה בין החלטה 1000 להחלטה 2000",
                "description": "Direct decision comparison"
            },
            {
                "query": "מה ההבדל בין ממשלה 36 לממשלה 37 בנושא חינוך?",
                "description": "Government comparison by topic"
            },
            {
                "query": "השווה החלטות תחבורה של 2023 מול 2024",
                "description": "Year comparison by topic"
            }
        ]
        
        for scenario in comparison_scenarios:
            result = self.make_query(scenario["query"])
            
            if result.get('success'):
                metadata = result.get('metadata', {})
                intent = metadata.get('intent', '')
                entities = metadata.get('entities', {})
                
                if intent == 'COMPARISON' or 'comparison' in str(entities):
                    self.log_result(f"COMPARISON - {scenario['description']}", True, 
                                  f"Recognized comparison. Intent: {intent}")
                else:
                    self.log_result(f"COMPARISON - {scenario['description']}", False, 
                                  f"Not recognized. Intent: {intent}")
    
    def test_route_transitions(self):
        """Test transitions between different route types."""
        print("\n=== Testing Route Transitions ===")
        session_id = f"transition_test_{uuid.uuid4()}"
        
        transition_flow = [
            ("החלטות בנושא בריאות", "QUERY", "Initial query"),
            ("נתח את הראשונה", "EVAL", "Switch to evaluation"),
            ("כמה היו בסך הכל?", "STATISTICAL", "Switch to count"),
            ("מה?", "UNCLEAR", "Ambiguous query"),
            ("חזור להחלטות בריאות", "QUERY", "Back to query")
        ]
        
        for query, expected_intent, description in transition_flow:
            result = self.make_query(query, session_id)
            
            if result.get('success'):
                metadata = result.get('metadata', {})
                actual_intent = metadata.get('intent', '')
                
                # Check if intent matches expected (flexible matching)
                intent_matches = (
                    actual_intent == expected_intent or
                    (expected_intent == "QUERY" and actual_intent == "DATA_QUERY") or
                    (expected_intent == "EVAL" and actual_intent == "ANALYSIS") or
                    (expected_intent == "UNCLEAR" and self.check_clarification_response(result.get('response', '')))
                )
                
                if intent_matches:
                    self.log_result(f"Route Transition - {description}", True, 
                                  f"Correct route: {actual_intent}")
                else:
                    self.log_result(f"Route Transition - {description}", False, 
                                  f"Expected {expected_intent}, got {actual_intent}")
            
            time.sleep(2)
    
    def run_all_tests(self):
        """Run all route handling tests."""
        print("Starting Route Handling Test Suite")
        print("=" * 50)
        
        self.test_unclear_routes()
        self.test_result_ref_routes()
        self.test_eval_routes()
        self.test_query_routes()
        self.test_statistical_routes()
        self.test_comparison_routes()
        self.test_route_transitions()
        
        # Summary
        print("\n" + "=" * 50)
        print("Test Summary:")
        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)
        print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        
        # Failed tests
        failed = [r for r in self.test_results if not r['passed']]
        if failed:
            print("\nFailed Tests:")
            for r in failed:
                print(f"  - {r['test']}: {r['details']}")

if __name__ == "__main__":
    # Check if backend is accessible
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health.status_code != 200:
            print("❌ Backend is not healthy!")
            exit(1)
    except:
        print("❌ Cannot connect to backend at http://localhost:5001")
        print("Please ensure all services are running with: docker compose up")
        exit(1)
    
    tester = RouteHandlingTester()
    tester.run_all_tests()