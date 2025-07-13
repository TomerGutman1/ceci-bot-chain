#!/usr/bin/env python3
"""
Test script to diagnose context handling issues in the bot chain.
Tests various scenarios to understand the entity persistence bug.
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "http://localhost:5001"
BOT_CHAIN_URL = f"{BACKEND_URL}/api/chat"
CONTEXT_ROUTER_URL = "http://localhost:8013"

# Test conversation ID
TEST_CONV_ID = f"test_context_{uuid.uuid4()}"

def make_query(message: str, session_id: str = None) -> Dict[str, Any]:
    """Make a query to the bot chain."""
    payload = {
        "message": message,
        "sessionId": session_id or TEST_CONV_ID,
        "includeMetadata": True,
        "includeScores": True
    }
    
    try:
        response = requests.post(BOT_CHAIN_URL, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error making query: {e}")
        return {"success": False, "error": str(e)}

def test_entity_persistence():
    """Test if entities persist incorrectly across queries."""
    print("\n=== Testing Entity Persistence Bug ===")
    
    # Query 1: Specific decision
    print("\n1. Querying decision 2989...")
    result1 = make_query("החלטה 2989")
    print(f"Success: {result1.get('success')}")
    if result1.get('metadata'):
        print(f"Entities: {result1['metadata'].get('entities')}")
    
    time.sleep(2)
    
    # Query 2: Different decision  
    print("\n2. Querying decision 1234...")
    result2 = make_query("החלטה 1234")
    print(f"Success: {result2.get('success')}")
    if result2.get('metadata'):
        print(f"Entities: {result2['metadata'].get('entities')}")
    
    # Check if decision 2989 appears in the second response
    if "2989" in str(result2.get('response', '')):
        print("\n❌ BUG CONFIRMED: Decision 2989 appears in response for decision 1234!")
    else:
        print("\n✅ No entity persistence detected in this test")

def test_context_router_directly():
    """Test context router API directly."""
    print("\n=== Testing Context Router Directly ===")
    
    # Test 1: Basic routing decision
    payload = {
        "conv_id": TEST_CONV_ID,
        "current_query": "תן לי את זה",
        "intent": "RESULT_REF",
        "entities": {},
        "confidence_score": 0.9,
        "route_flags": {"needs_context": True}
    }
    
    try:
        response = requests.post(f"{CONTEXT_ROUTER_URL}/route", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        print(f"\nRoute decision: {result.get('route')}")
        print(f"Needs clarification: {result.get('needs_clarification')}")
        print(f"Reasoning: {result.get('reasoning')}")
        print(f"Context summary: {json.dumps(result.get('context_summary'), indent=2)}")
    except Exception as e:
        print(f"Error testing context router: {e}")

def test_unclear_route():
    """Test if UNCLEAR intent triggers clarification."""
    print("\n=== Testing UNCLEAR Route ===")
    
    # Ambiguous query that should trigger clarification
    queries = [
        "מה?",
        "תראה לי החלטות",
        "איפה ההחלטה?"
    ]
    
    for query in queries:
        print(f"\nTesting query: '{query}'")
        result = make_query(query)
        
        if result.get('success'):
            response_text = result.get('response', '')
            metadata = result.get('metadata', {})
            
            print(f"Intent: {metadata.get('intent')}")
            print(f"Response preview: {response_text[:200]}...")
            
            # Check if it's a clarification response
            if any(word in response_text for word in ["זקוק לפרטים", "אפשרויות", "הצעות", "מה הייתם"]):
                print("✅ Clarification response detected")
            else:
                print("❌ No clarification - might be returning recent decisions instead")

def test_reference_resolution():
    """Test reference resolution in multi-turn conversation."""
    print("\n=== Testing Reference Resolution ===")
    
    session_id = f"ref_test_{uuid.uuid4()}"
    
    # Turn 1: Query specific decision
    print("\n1. Initial query about decision 2989...")
    result1 = make_query("החלטה 2989 של ממשלה 37", session_id)
    time.sleep(2)
    
    # Turn 2: Reference to previous
    print("\n2. Reference query...")
    result2 = make_query("תן לי את התוכן המלא של זה", session_id)
    
    if result2.get('success'):
        response = result2.get('response', '')
        metadata = result2.get('metadata', {})
        
        print(f"Intent: {metadata.get('intent')}")
        print(f"Entities: {metadata.get('entities')}")
        
        # Check if reference was resolved
        if "2989" in str(metadata.get('entities', {})) or "2989" in response:
            print("✅ Reference resolution appears to work")
        else:
            print("❌ Reference not resolved - entities missing decision number")

def test_conversation_memory():
    """Test if conversation memory is properly stored and retrieved."""
    print("\n=== Testing Conversation Memory ===")
    
    session_id = f"memory_test_{uuid.uuid4()}"
    
    # Make several queries to build conversation history
    queries = [
        "החלטות בנושא חינוך",
        "מה לגבי תקציב?",
        "תן לי עוד פרטים על ההחלטה הראשונה"
    ]
    
    for i, query in enumerate(queries):
        print(f"\nTurn {i+1}: {query}")
        result = make_query(query, session_id)
        
        if result.get('metadata'):
            entities = result['metadata'].get('entities', {})
            print(f"Entities: {entities}")
        
        time.sleep(2)

def test_cache_invalidation():
    """Test cache invalidation on entity changes."""
    print("\n=== Testing Cache Invalidation ===")
    
    session_id = f"cache_inv_{uuid.uuid4()}"
    
    # Query 1: General topic search
    print("\n1. Initial topic search...")
    result1 = make_query("החלטות בנושא תחבורה", session_id)
    
    time.sleep(2)
    
    # Query 2: Add specific entity (should invalidate cache)
    print("\n2. Adding specific decision number...")
    result2 = make_query("החלטה 2989 בנושא תחבורה", session_id)
    
    time.sleep(2)
    
    # Query 3: Repeat first query (should get fresh results)
    print("\n3. Repeating initial search...")
    result3 = make_query("החלטות בנושא תחבורה", session_id)
    
    if result1.get('success') and result3.get('success'):
        # In a properly working system, cache should be invalidated
        print("✅ Cache invalidation test completed")
    else:
        print("❌ One or more queries failed")

def test_session_isolation():
    """Test that different sessions maintain separate contexts."""
    print("\n=== Testing Session Isolation ===")
    
    session1 = f"session1_{uuid.uuid4()}"
    session2 = f"session2_{uuid.uuid4()}"
    
    # Session 1: Decision 1000
    print("\n1. Session 1 - Decision 1000...")
    result1 = make_query("החלטה 1000", session1)
    
    # Session 2: Decision 2000
    print("\n2. Session 2 - Decision 2000...")
    result2 = make_query("החלטה 2000", session2)
    
    time.sleep(2)
    
    # Session 1: Reference query
    print("\n3. Session 1 - Reference query...")
    ref1 = make_query("תן לי את התוכן של זה", session1)
    
    # Session 2: Reference query
    print("\n4. Session 2 - Reference query...")
    ref2 = make_query("תן לי את התוכן של זה", session2)
    
    # Check if correct decisions are referenced
    if ref1.get('success') and ref2.get('success'):
        response1 = ref1.get('response', '')
        response2 = ref2.get('response', '')
        
        if "1000" in response1 and "2000" in response2:
            print("✅ Sessions properly isolated")
        else:
            print("❌ Session isolation failed - contexts mixed")

def test_ordinal_references():
    """Test ordinal reference handling."""
    print("\n=== Testing Ordinal References ===")
    
    session_id = f"ordinal_{uuid.uuid4()}"
    
    # Setup: Get multiple results
    print("\n1. Getting list of decisions...")
    result = make_query("החלטות ממשלה 37 בנושא חינוך", session_id)
    
    time.sleep(2)
    
    # Test ordinal references
    ordinals = [
        ("מה ההחלטה הראשונה?", "first"),
        ("והשנייה?", "second"),
        ("תן לי את השלישית", "third")
    ]
    
    for query, position in ordinals:
        print(f"\n2. Testing ordinal: {position}...")
        result = make_query(query, session_id)
        
        if result.get('success'):
            metadata = result.get('metadata', {})
            print(f"Intent: {metadata.get('intent')}")
            print(f"Response preview: {result.get('response', '')[:100]}...")

def test_entity_accumulation():
    """Test gradual entity accumulation across queries."""
    print("\n=== Testing Entity Accumulation ===")
    
    session_id = f"accumulation_{uuid.uuid4()}"
    
    queries = [
        ("ממשלה 37", "Set government"),
        ("בנושא בריאות", "Add topic"),
        ("משנת 2024", "Add year"),
        ("כמה יש?", "Count with all filters")
    ]
    
    accumulated = {}
    for i, (query, description) in enumerate(queries):
        print(f"\n{i+1}. {description}: '{query}'")
        result = make_query(query, session_id)
        
        if result.get('metadata'):
            entities = result['metadata'].get('entities', {})
            print(f"Current entities: {entities}")
            
            # Check if entities accumulate
            if i > 0 and len(entities) >= len(accumulated):
                print("✅ Entities maintained/accumulated")
            accumulated.update(entities)
        
        time.sleep(1)

def main():
    """Run all context handling tests."""
    print("Starting Context Handling Diagnostics")
    print("=" * 50)
    
    # Check if services are running
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health.status_code != 200:
            print("❌ Backend is not healthy!")
            return
    except:
        print("❌ Cannot connect to backend at http://localhost:5001")
        return
    
    # Run original tests
    test_entity_persistence()
    test_context_router_directly()
    test_unclear_route()
    test_reference_resolution()
    test_conversation_memory()
    
    # Run new tests
    test_cache_invalidation()
    test_session_isolation()
    test_ordinal_references()
    test_entity_accumulation()
    
    print("\n" + "=" * 50)
    print("Context Handling Diagnostics Complete")

if __name__ == "__main__":
    main()