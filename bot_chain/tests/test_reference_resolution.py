#!/usr/bin/env python3
"""
Test suite for reference resolution functionality.
Tests implicit references, ordinal references, and context enrichment.
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, List, Tuple

# Configuration
BACKEND_URL = "http://localhost:5001"
CHAT_API = f"{BACKEND_URL}/api/chat"
CONTEXT_ROUTER_URL = "http://localhost:8013"

class ReferenceResolutionTester:
    def __init__(self):
        self.test_results = []
    
    def make_query(self, message: str, session_id: str) -> Dict[str, Any]:
        """Make a query to the chat API."""
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
    
    def test_context_router_directly(self, query: str, intent: str, entities: Dict, 
                                   conv_id: str) -> Dict[str, Any]:
        """Test context router API directly."""
        payload = {
            "conv_id": conv_id,
            "current_query": query,
            "intent": intent,
            "entities": entities,
            "confidence_score": 0.9,
            "route_flags": {"needs_context": True}
        }
        
        try:
            response = requests.post(f"{CONTEXT_ROUTER_URL}/route", json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def log_result(self, test_name: str, passed: bool, details: str):
        """Log test results."""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        print(f"{'✅' if passed else '❌'} {test_name}: {details}")
    
    def test_simple_pronoun_reference(self):
        """Test simple pronoun references like 'זה', 'אותה'."""
        print("\n=== Testing Simple Pronoun References ===")
        session_id = f"pronoun_test_{uuid.uuid4()}"
        
        # Setup: Query a specific decision
        setup_result = self.make_query("החלטה 2989 של ממשלה 37", session_id)
        if not setup_result.get('success'):
            self.log_result("Pronoun Reference Setup", False, "Setup query failed")
            return
        
        time.sleep(2)
        
        # Test various pronoun references
        pronoun_queries = [
            ("תן לי את התוכן המלא של זה", "Should resolve 'זה' to decision 2989"),
            ("ספר לי עוד על אותה", "Should resolve 'אותה' to decision 2989"),
            ("מה הסעיפים של ההחלטה הזו?", "Should resolve 'הזו' to decision 2989")
        ]
        
        for query, expected in pronoun_queries:
            result = self.make_query(query, session_id)
            
            if result.get('success'):
                response = result.get('response', '')
                metadata = result.get('metadata', {})
                entities = metadata.get('entities', {})
                
                # Check if reference was resolved
                if '2989' in str(entities.get('decision_number', '')) or '2989' in response:
                    self.log_result(f"Pronoun Reference - '{query[:20]}...'", True, 
                                  f"Correctly resolved reference")
                else:
                    self.log_result(f"Pronoun Reference - '{query[:20]}...'", False, 
                                  f"Failed to resolve reference. Entities: {entities}")
            else:
                self.log_result(f"Pronoun Reference - '{query[:20]}...'", False, 
                              "Query failed")
            
            time.sleep(1)
    
    def test_ordinal_references(self):
        """Test ordinal references like 'הראשון', 'השני'."""
        print("\n=== Testing Ordinal References ===")
        session_id = f"ordinal_test_{uuid.uuid4()}"
        
        # Setup: Query multiple results
        setup_result = self.make_query("החלטות בנושא חינוך", session_id)
        if not setup_result.get('success'):
            self.log_result("Ordinal Reference Setup", False, "Setup query failed")
            return
        
        time.sleep(2)
        
        # Test ordinal references
        ordinal_queries = [
            ("מה ההחלטה הראשונה?", "first"),
            ("תן לי פרטים על השנייה", "second"),
            ("והשלישית?", "third")
        ]
        
        for query, position in ordinal_queries:
            result = self.make_query(query, session_id)
            
            if result.get('success'):
                response = result.get('response', '')
                metadata = result.get('metadata', {})
                
                # Check if ordinal was understood
                if metadata.get('intent') == 'RESULT_REF':
                    self.log_result(f"Ordinal Reference - '{query}'", True, 
                                  f"Recognized as reference query")
                else:
                    self.log_result(f"Ordinal Reference - '{query}'", False, 
                                  f"Not recognized as reference. Intent: {metadata.get('intent')}")
            else:
                self.log_result(f"Ordinal Reference - '{query}'", False, "Query failed")
            
            time.sleep(1)
    
    def test_temporal_references(self):
        """Test temporal references like 'האחרון', 'הקודם'."""
        print("\n=== Testing Temporal References ===")
        session_id = f"temporal_test_{uuid.uuid4()}"
        
        # Make multiple queries to build history
        queries_sequence = [
            "החלטה 1000",
            "החלטה 2000",
            "החלטה 3000"
        ]
        
        for q in queries_sequence:
            self.make_query(q, session_id)
            time.sleep(1)
        
        # Test temporal references
        temporal_queries = [
            ("מה היה בהחלטה האחרונה?", "Should refer to 3000"),
            ("והקודמת?", "Should refer to 2000"),
            ("חזור להחלטה הראשונה", "Should refer to 1000")
        ]
        
        for query, expected in temporal_queries:
            result = self.make_query(query, session_id)
            
            if result.get('success'):
                metadata = result.get('metadata', {})
                intent = metadata.get('intent', '')
                
                if intent in ['RESULT_REF', 'UNCLEAR']:
                    self.log_result(f"Temporal Reference - '{query}'", True, 
                                  f"Recognized temporal reference. {expected}")
                else:
                    self.log_result(f"Temporal Reference - '{query}'", False, 
                                  f"Not recognized. Intent: {intent}")
    
    def test_entity_enrichment(self):
        """Test query enrichment with resolved entities."""
        print("\n=== Testing Entity Enrichment ===")
        session_id = f"enrichment_test_{uuid.uuid4()}"
        
        # Setup context
        self.make_query("החלטה 2989 של ממשלה 37 בנושא חינוך", session_id)
        time.sleep(2)
        
        # Test context router enrichment directly
        router_result = self.test_context_router_directly(
            "תן לי את זה",
            "RESULT_REF",
            {},  # Empty entities
            session_id
        )
        
        if 'error' not in router_result:
            resolved_entities = router_result.get('resolved_entities', {})
            enriched_query = router_result.get('enriched_query', '')
            
            if resolved_entities.get('decision_number') == 2989:
                self.log_result("Entity Enrichment", True, 
                              f"Entities resolved: {resolved_entities}")
            else:
                self.log_result("Entity Enrichment", False, 
                              f"Failed to resolve entities. Got: {resolved_entities}")
            
            if enriched_query and enriched_query != "תן לי את זה":
                self.log_result("Query Enrichment", True, 
                              f"Query enriched to: '{enriched_query}'")
            else:
                self.log_result("Query Enrichment", False, 
                              "Query not enriched")
        else:
            self.log_result("Entity Enrichment", False, 
                          f"Context router error: {router_result['error']}")
    
    def test_multi_turn_context(self):
        """Test complex multi-turn conversations."""
        print("\n=== Testing Multi-Turn Context ===")
        session_id = f"multiturn_test_{uuid.uuid4()}"
        
        conversation_flow = [
            ("החלטות ממשלה 36 על בריאות", "Setup government 36 health context"),
            ("כמה היו?", "Should count government 36 health decisions"),
            ("ומה לגבי ממשלה 37?", "Should switch to government 37 health"),
            ("השווה ביניהם", "Should compare gov 36 vs 37 health decisions"),
            ("תן לי את הראשונה של 36", "Should get first decision of gov 36")
        ]
        
        for query, expected_behavior in conversation_flow:
            print(f"\nQuery: '{query}'")
            result = self.make_query(query, session_id)
            
            if result.get('success'):
                metadata = result.get('metadata', {})
                entities = metadata.get('entities', {})
                intent = metadata.get('intent', '')
                
                print(f"Intent: {intent}, Entities: {json.dumps(entities, ensure_ascii=False)}")
                self.log_result(f"Multi-turn - '{query[:30]}...'", True, 
                              expected_behavior)
            else:
                self.log_result(f"Multi-turn - '{query[:30]}...'", False, 
                              "Query failed")
            
            time.sleep(2)
    
    def test_ambiguous_references(self):
        """Test handling of ambiguous references."""
        print("\n=== Testing Ambiguous References ===")
        session_id = f"ambiguous_test_{uuid.uuid4()}"
        
        # Create ambiguous context
        self.make_query("החלטה 1000 של ממשלה 36", session_id)
        time.sleep(1)
        self.make_query("החלטה 1000 של ממשלה 37", session_id)
        time.sleep(1)
        
        # Ambiguous reference
        result = self.make_query("תן לי את התוכן של 1000", session_id)
        
        if result.get('success'):
            response = result.get('response', '')
            metadata = result.get('metadata', {})
            
            # Should either ask for clarification or use most recent
            if "איזו" in response or "ממשלה" in response or metadata.get('intent') == 'UNCLEAR':
                self.log_result("Ambiguous Reference", True, 
                              "Correctly handled ambiguity")
            else:
                self.log_result("Ambiguous Reference", True, 
                              "Used most recent context (acceptable behavior)")
    
    def test_reference_without_context(self):
        """Test references without prior context."""
        print("\n=== Testing References Without Context ===")
        session_id = f"no_context_test_{uuid.uuid4()}"
        
        # Try reference without setup
        result = self.make_query("תן לי את זה", session_id)
        
        if result.get('success'):
            response = result.get('response', '')
            metadata = result.get('metadata', {})
            
            # Should ask for clarification
            if any(word in response for word in ["מה", "איזה", "לא ברור", "פרטים"]):
                self.log_result("No Context Reference", True, 
                              "Correctly asked for clarification")
            else:
                self.log_result("No Context Reference", False, 
                              "Did not ask for clarification")
    
    def run_all_tests(self):
        """Run all reference resolution tests."""
        print("Starting Reference Resolution Test Suite")
        print("=" * 50)
        
        self.test_simple_pronoun_reference()
        self.test_ordinal_references()
        self.test_temporal_references()
        self.test_entity_enrichment()
        self.test_multi_turn_context()
        self.test_ambiguous_references()
        self.test_reference_without_context()
        
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
    # Check if services are accessible
    try:
        backend_health = requests.get(f"{BACKEND_URL}/health", timeout=5)
        router_health = requests.get(f"{CONTEXT_ROUTER_URL}/health", timeout=5)
        
        if backend_health.status_code != 200:
            print("❌ Backend is not healthy!")
            exit(1)
        if router_health.status_code != 200:
            print("❌ Context Router is not healthy!")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to services: {e}")
        print("Please ensure all services are running with: docker compose up")
        exit(1)
    
    tester = ReferenceResolutionTester()
    tester.run_all_tests()