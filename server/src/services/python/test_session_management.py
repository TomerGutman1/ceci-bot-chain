"""
Test script for Session Management functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_basic_session():
    """Test basic session functionality"""
    print("=== Testing Basic Session Functionality ===")
    
    # First query - should create new session
    response1 = requests.post(f"{BASE_URL}/query", json={
        "query": "הבא לי 3 החלטות בנושא חינוך"
    })
    result1 = response1.json()
    print(f"Query 1 Success: {result1['success']}")
    print(f"Session ID: {result1.get('session_id')}")
    print(f"Query ID: {result1.get('query_id')}")
    
    session_id = result1.get('session_id')
    
    # Second query - reference to previous
    time.sleep(1)
    response2 = requests.post(f"{BASE_URL}/query", json={
        "query": "תן לי את התוכן המלא של ההחלטה הראשונה",
        "session_id": session_id
    })
    result2 = response2.json()
    print(f"\nQuery 2 Success: {result2['success']}")
    print(f"Same Session: {result2.get('session_id') == session_id}")
    
    # Third query - relative reference
    time.sleep(1)
    response3 = requests.post(f"{BASE_URL}/query", json={
        "query": "עכשיו 3 החלטות כאלה משנת 1999",
        "session_id": session_id
    })
    result3 = response3.json()
    print(f"\nQuery 3 Success: {result3['success']}")
    
    # Get session info
    session_info = requests.get(f"{BASE_URL}/session/{session_id}")
    if session_info.status_code == 200:
        info = session_info.json()
        print(f"\nSession Info:")
        print(f"  Created: {info['created_at']}")
        print(f"  Queries: {info['query_count']}")
        print(f"  State: {info['state']}")
        print("\n  Recent Queries:")
        for q in info['recent_queries']:
            print(f"    - {q['original_query'][:50]}...")

def test_reference_types():
    """Test different types of references"""
    print("\n\n=== Testing Reference Types ===")
    
    # Get some decisions first
    response1 = requests.post(f"{BASE_URL}/query", json={
        "query": "הבא לי 5 החלטות בנושא בריאות מ-2023"
    })
    result1 = response1.json()
    session_id = result1.get('session_id')
    print(f"Initial query success: {result1['success']}")
    
    # Test ordinal reference
    time.sleep(1)
    response2 = requests.post(f"{BASE_URL}/query", json={
        "query": "הראה לי את ההחלטה השלישית בפירוט",
        "session_id": session_id
    })
    print(f"Ordinal reference success: {response2.json()['success']}")
    
    # Test content reference
    time.sleep(1)
    response3 = requests.post(f"{BASE_URL}/query", json={
        "query": "תן לי את התוכן המלא של ההחלטה האחרונה",
        "session_id": session_id
    })
    print(f"Content reference success: {response3.json()['success']}")
    
    # Test relative reference
    time.sleep(1)
    response4 = requests.post(f"{BASE_URL}/query", json={
        "query": "עוד כמו זה",
        "session_id": session_id
    })
    print(f"Relative reference success: {response4.json()['success']}")

def test_session_stats():
    """Test session statistics"""
    print("\n\n=== Testing Session Statistics ===")
    
    response = requests.get(f"{BASE_URL}/sessions/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"Total Sessions: {stats['total_sessions']}")
        print(f"Active Sessions: {stats['active_sessions']}")
        print(f"Total Queries: {stats['total_queries']}")
        print(f"Average Queries per Session: {stats['average_queries_per_session']:.2f}")

def test_cleanup():
    """Test session cleanup"""
    print("\n\n=== Testing Session Cleanup ===")
    
    response = requests.post(f"{BASE_URL}/sessions/cleanup")
    if response.status_code == 200:
        result = response.json()
        print(f"Cleanup Success: {result['success']}")
        print(f"Removed Sessions: {result['removed_sessions']}")

if __name__ == "__main__":
    print("Starting Session Management Tests...")
    print("Make sure PandasAI service is running on port 8001")
    print("-" * 50)
    
    try:
        # Check if service is healthy
        health = requests.get(f"{BASE_URL}/")
        if health.status_code != 200:
            print("PandasAI service is not responding!")
            exit(1)
        
        test_basic_session()
        test_reference_types()
        test_session_stats()
        test_cleanup()
        
        print("\n\nAll tests completed!")
        
    except Exception as e:
        print(f"\nError during tests: {e}")
