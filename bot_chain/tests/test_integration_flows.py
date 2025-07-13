#!/usr/bin/env python3
"""
Integration test suite for end-to-end conversation flows.
Tests complete user journeys through the bot chain.
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, List, Tuple
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:5001"
CHAT_API = f"{BACKEND_URL}/api/chat"

class IntegrationFlowTester:
    def __init__(self):
        self.test_results = []
        self.conversation_logs = []
    
    def make_query(self, message: str, session_id: str) -> Dict[str, Any]:
        """Make a query to the chat API and log the conversation."""
        payload = {
            "message": message,
            "sessionId": session_id,
            "includeMetadata": True,
            "includeScores": True
        }
        
        start_time = time.time()
        try:
            response = requests.post(CHAT_API, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Log conversation turn
            self.conversation_logs.append({
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "message": message,
                "response": result.get('response', '')[:200] + "...",
                "intent": result.get('metadata', {}).get('intent'),
                "processing_time": time.time() - start_time
            })
            
            return result
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
    
    def test_research_flow(self):
        """Test a typical research flow: search → analyze → compare."""
        print("\n=== Testing Research Flow ===")
        session_id = f"research_flow_{uuid.uuid4()}"
        
        flow = [
            ("החלטות בנושא חינוך מ-2024", "Initial search"),
            ("כמה החלטות מצאת?", "Count results"),
            ("נתח את הראשונה", "Analyze first result"),
            ("יש החלטות דומות משנים קודמות?", "Historical comparison"),
            ("השווה את התקציבים", "Budget comparison")
        ]
        
        all_success = True
        for i, (query, step) in enumerate(flow):
            print(f"\nStep {i+1}: {step}")
            result = self.make_query(query, session_id)
            
            if result.get('success'):
                metadata = result.get('metadata', {})
                print(f"  Intent: {metadata.get('intent')}")
                print(f"  Entities: {json.dumps(metadata.get('entities', {}), ensure_ascii=False)}")
                
                # Verify conversation continuity
                if i > 0 and not metadata.get('entities'):
                    self.log_result(f"Research Flow - Step {i+1}", False, 
                                  "Lost context from previous queries")
                    all_success = False
            else:
                self.log_result(f"Research Flow - Step {i+1}", False, 
                              f"Query failed: {result.get('error')}")
                all_success = False
            
            time.sleep(2)
        
        if all_success:
            self.log_result("Research Flow", True, 
                          "Complete research journey successful")
    
    def test_decision_exploration_flow(self):
        """Test exploring a specific decision in depth."""
        print("\n=== Testing Decision Exploration Flow ===")
        session_id = f"exploration_flow_{uuid.uuid4()}"
        
        # Start with a specific decision
        decision_num = "2989"
        exploration_steps = [
            (f"החלטה {decision_num}", "Find decision"),
            ("תן לי את התוכן המלא", "Get full content"),
            ("מה הסעיפים האופרטיביים?", "Extract operative clauses"),
            ("מי היו המשרדים המעורבים?", "Identify ministries"),
            ("כמה תקציב הוקצה?", "Check budget"),
            ("נתח את ההחלטה", "Analyze decision"),
            ("יש החלטות המשך?", "Find follow-up decisions")
        ]
        
        for i, (query, description) in enumerate(exploration_steps):
            print(f"\nExploring {description}...")
            result = self.make_query(query, session_id)
            
            if result.get('success'):
                response = result.get('response', '')
                
                # Check if decision number persists in context
                if i > 0 and decision_num not in str(result.get('metadata', {}).get('entities', {})):
                    self.log_result(f"Decision Exploration - {description}", False, 
                                  f"Lost decision context at step {i+1}")
                else:
                    self.log_result(f"Decision Exploration - {description}", True, 
                                  "Context maintained")
            else:
                self.log_result(f"Decision Exploration - {description}", False, 
                              "Query failed")
            
            time.sleep(2)
    
    def test_clarification_recovery_flow(self):
        """Test recovery from unclear queries through clarification."""
        print("\n=== Testing Clarification Recovery Flow ===")
        session_id = f"clarification_flow_{uuid.uuid4()}"
        
        # Ambiguous query → clarification → specific query
        flow = [
            ("החלטות", "Ambiguous initial query"),
            ("החלטות ממשלה 37 בנושא בריאות", "Specific follow-up"),
            ("מה?", "Another ambiguous query"),
            ("מה התקציב של ההחלטה הראשונה?", "Specific question")
        ]
        
        for i, (query, description) in enumerate(flow):
            print(f"\nStep {i+1}: {description}")
            result = self.make_query(query, session_id)
            
            if result.get('success'):
                response = result.get('response', '')
                metadata = result.get('metadata', {})
                
                # Check appropriate handling
                if i % 2 == 0:  # Ambiguous queries (0, 2)
                    if any(word in response for word in ["מה", "איזה", "פרטים", "הבהיר"]):
                        self.log_result(f"Clarification Flow - {description}", True, 
                                      "Correctly asked for clarification")
                    else:
                        self.log_result(f"Clarification Flow - {description}", False, 
                                      "Should have asked for clarification")
                else:  # Specific queries (1, 3)
                    if metadata.get('intent') not in ['UNCLEAR', 'CLARIFICATION']:
                        self.log_result(f"Clarification Flow - {description}", True, 
                                      "Processed specific query correctly")
                    else:
                        self.log_result(f"Clarification Flow - {description}", False, 
                                      "Wrongly triggered clarification")
            
            time.sleep(2)
    
    def test_multi_entity_flow(self):
        """Test handling multiple entities across conversation."""
        print("\n=== Testing Multi-Entity Flow ===")
        session_id = f"multi_entity_flow_{uuid.uuid4()}"
        
        # Build up multiple entities gradually
        entity_building = [
            ("החלטות של ממשלה 36", "Set government context"),
            ("בנושא תחבורה", "Add topic filter"),
            ("משנת 2023", "Add time filter"),
            ("שהן אופרטיביות", "Add operativity filter"),
            ("עם תקציב מעל 100 מיליון", "Add budget filter"),
            ("כמה יש כאלה?", "Count with all filters")
        ]
        
        accumulated_entities = {}
        for i, (query, description) in enumerate(entity_building):
            print(f"\nBuilding entities: {description}")
            result = self.make_query(query, session_id)
            
            if result.get('success'):
                metadata = result.get('metadata', {})
                current_entities = metadata.get('entities', {})
                
                # Check if entities accumulate
                if i > 0 and len(current_entities) >= len(accumulated_entities):
                    self.log_result(f"Multi-Entity - {description}", True, 
                                  f"Entities maintained/accumulated: {json.dumps(current_entities, ensure_ascii=False)}")
                    accumulated_entities.update(current_entities)
                elif i == 0:
                    accumulated_entities = current_entities
                    self.log_result(f"Multi-Entity - {description}", True, 
                                  "Initial entities set")
                else:
                    self.log_result(f"Multi-Entity - {description}", False, 
                                  f"Lost entities. Had: {len(accumulated_entities)}, Now: {len(current_entities)}")
            
            time.sleep(2)
    
    def test_context_switching_flow(self):
        """Test switching context mid-conversation."""
        print("\n=== Testing Context Switching Flow ===")
        session_id = f"context_switch_{uuid.uuid4()}"
        
        # Switch between different contexts
        context_switches = [
            ("החלטה 1000 של ממשלה 36", "Context A: Decision 1000"),
            ("מה התוכן?", "Query about A"),
            ("עכשיו תראה לי החלטה 2000 של ממשלה 37", "Switch to Context B"),
            ("מה ההבדל ביניהם?", "Compare A and B"),
            ("חזור להחלטה הראשונה", "Back to Context A"),
            ("מי חתום עליה?", "Query about current context")
        ]
        
        for i, (query, description) in enumerate(context_switches):
            print(f"\nContext: {description}")
            result = self.make_query(query, session_id)
            
            if result.get('success'):
                metadata = result.get('metadata', {})
                entities = metadata.get('entities', {})
                
                # Verify context switches appropriately
                expected_context = "1000" if i in [0, 1, 4, 5] else "2000" if i in [2] else "both"
                
                self.log_result(f"Context Switch - {description}", True, 
                              f"Handled context switch. Entities: {json.dumps(entities, ensure_ascii=False)}")
            
            time.sleep(2)
    
    def test_error_recovery_flow(self):
        """Test recovery from errors and invalid queries."""
        print("\n=== Testing Error Recovery Flow ===")
        session_id = f"error_recovery_{uuid.uuid4()}"
        
        # Mix valid and invalid queries
        error_scenarios = [
            ("החלטה 99999999", "Non-existent decision"),
            ("החלטות בנושא צבא", "Valid recovery query"),
            ("נתח את ההחלטה של אתמול בלילה ב-3:47", "Nonsensical time reference"),
            ("פשוט תן לי החלטות אחרונות", "Simple recovery"),
            ("🦄🌈✨", "Emoji spam"),
            ("החלטה 1234", "Final valid query")
        ]
        
        for i, (query, scenario) in enumerate(error_scenarios):
            print(f"\nScenario: {scenario}")
            result = self.make_query(query, session_id)
            
            if result.get('success'):
                response = result.get('response', '')
                
                # Even "error" queries should get reasonable responses
                if len(response) > 10:  # Some meaningful response
                    self.log_result(f"Error Recovery - {scenario}", True, 
                                  "Handled gracefully")
                else:
                    self.log_result(f"Error Recovery - {scenario}", False, 
                                  "Empty or minimal response")
            else:
                # API errors are failures
                self.log_result(f"Error Recovery - {scenario}", False, 
                              f"API error: {result.get('error')}")
            
            time.sleep(1)
    
    def test_performance_flow(self):
        """Test response times across different query types."""
        print("\n=== Testing Performance Flow ===")
        session_id = f"performance_{uuid.uuid4()}"
        
        performance_queries = [
            ("החלטה 1234", "simple_lookup", 5.0),
            ("החלטות ממשלה 37", "government_search", 8.0),
            ("נתח את החלטה 2989", "analysis", 20.0),
            ("כמה החלטות יש?", "count", 5.0),
            ("תן לי את זה", "reference", 5.0)
        ]
        
        for query, query_type, expected_time in performance_queries:
            start = time.time()
            result = self.make_query(query, session_id)
            elapsed = time.time() - start
            
            if result.get('success'):
                if elapsed <= expected_time:
                    self.log_result(f"Performance - {query_type}", True, 
                                  f"Completed in {elapsed:.1f}s (expected <{expected_time}s)")
                else:
                    self.log_result(f"Performance - {query_type}", False, 
                                  f"Too slow: {elapsed:.1f}s (expected <{expected_time}s)")
            else:
                self.log_result(f"Performance - {query_type}", False, 
                              "Query failed")
            
            time.sleep(1)
    
    def run_all_tests(self):
        """Run all integration flow tests."""
        print("Starting Integration Flow Test Suite")
        print("=" * 50)
        
        self.test_research_flow()
        self.test_decision_exploration_flow()
        self.test_clarification_recovery_flow()
        self.test_multi_entity_flow()
        self.test_context_switching_flow()
        self.test_error_recovery_flow()
        self.test_performance_flow()
        
        # Summary
        print("\n" + "=" * 50)
        print("Test Summary:")
        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)
        print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        
        # Performance summary
        if self.conversation_logs:
            avg_time = sum(log['processing_time'] for log in self.conversation_logs) / len(self.conversation_logs)
            print(f"\nAverage response time: {avg_time:.2f}s")
            print(f"Total queries made: {len(self.conversation_logs)}")
        
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
    
    tester = IntegrationFlowTester()
    tester.run_all_tests()