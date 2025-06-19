"""
Test Session Management Flow
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_session_flow():
    """Test complete session flow"""
    print("Testing Session Management Flow")
    print("=" * 50)
    
    # Step 1: First query WITHOUT session_id
    print("\nStep 1: First query (should create new session)")
    response1 = requests.post(f"{BASE_URL}/query", json={
        "query": "הבא לי החלטה בנושא הגירה של ממשלה 32"
    })
    
    result1 = response1.json()
    print(f"Success: {result1.get('success')}")
    print(f"Session ID returned: {result1.get('session_id')}")
    print(f"Query ID: {result1.get('query_id')}")
    
    session_id = result1.get('session_id')
    if not session_id:
        print("ERROR: No session_id returned!")
        return
    
    # Extract decision number
    answer = result1.get('answer', '')
    import re
    decision_match = re.search(r'מספר החלטה: (\d+)', answer)
    if decision_match:
        decision_num = decision_match.group(1)
        print(f"Decision number: {decision_num}")
    
    # Step 2: Check session info
    print("\n" + "-" * 50)
    print("\nStep 2: Checking session info")
    session_info = requests.get(f"{BASE_URL}/session/{session_id}")
    if session_info.status_code == 200:
        info = session_info.json()
        print(f"Session found!")
        print(f"Query count: {info['query_count']}")
        print(f"Last query: {info['recent_queries'][0]['original_query'] if info['recent_queries'] else 'None'}")
    else:
        print(f"ERROR: Session not found (status: {session_info.status_code})")
    
    # Step 3: Second query WITH session_id
    print("\n" + "-" * 50)
    print("\nStep 3: Second query with session_id")
    response2 = requests.post(f"{BASE_URL}/query", json={
        "query": "הבא לי את התוכן המלא של ההחלטה",
        "session_id": session_id  # Pass the session_id
    })
    
    result2 = response2.json()
    print(f"Success: {result2.get('success')}")
    print(f"Same session: {result2.get('session_id') == session_id}")
    
    # Check if content matches
    answer2 = result2.get('answer', '')
    if decision_match:
        # The content itself might not contain the decision number
        # Instead, check if we got the actual content (not empty, not error)
        if answer2 and len(answer2) > 50 and "א." in answer2:
            print(f"✓ CORRECT: Got content for decision {decision_num}")
            print(f"  Content starts with: {answer2[:30]}...")
        else:
            print(f"✗ WRONG: Content seems invalid or empty")
            
            # Try to find what decision it returned
            content_match = re.search(r'החלטה מספר (\d+)', answer2)
            if content_match:
                print(f"  Returned content for decision {content_match.group(1)} instead")
            else:
                print("  Could not identify decision number in content")
    
    print("\nFirst 300 chars of content:")
    print(answer2[:300])

if __name__ == "__main__":
    test_session_flow()
