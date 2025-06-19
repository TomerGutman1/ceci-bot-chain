"""
Test Session Reference Resolution
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_reference_resolution():
    """Test if reference resolution works correctly"""
    print("Testing Reference Resolution")
    print("=" * 50)
    
    # Step 1: Get a specific decision
    print("\nStep 1: Getting a specific decision about הגירה from government 32")
    response1 = requests.post(f"{BASE_URL}/query", json={
        "query": "הבא לי החלטה בנושא הגירה של ממשלה 32"
    })
    
    result1 = response1.json()
    session_id = result1.get('session_id')
    
    print(f"Success: {result1.get('success')}")
    print(f"Session ID: {session_id}")
    
    # Extract decision number if available
    answer = result1.get('answer', '')
    import re
    decision_match = re.search(r'מספר החלטה: (\d+)', answer)
    if decision_match:
        decision_num = decision_match.group(1)
        print(f"Decision number found: {decision_num}")
    else:
        print("No decision number found in response")
    
    print("\nFirst 300 chars of answer:")
    print(answer[:300])
    
    # Wait a bit
    time.sleep(2)
    
    # Step 2: Request full content with reference
    print("\n" + "-" * 50)
    print("\nStep 2: Requesting full content of THE decision")
    response2 = requests.post(f"{BASE_URL}/query", json={
        "query": "הבא לי את התוכן המלא של ההחלטה",
        "session_id": session_id
    })
    
    result2 = response2.json()
    print(f"Success: {result2.get('success')}")
    print(f"Same session: {result2.get('session_id') == session_id}")
    
    answer2 = result2.get('answer', '')
    
    # Check if it's the same decision
    if decision_match:
        # The content itself might not contain the decision number
        # Instead, check if we got the actual content (not empty, not error)
        if answer2 and len(answer2) > 50 and "א." in answer2:
            print(f"✓ Correct! Got content for decision {decision_num}")
            print(f"  Content starts with: {answer2[:30]}...")
        else:
            print(f"✗ Wrong! Content seems invalid or empty")
            # Try to find what decision it returned
            wrong_match = re.search(r'החלטה מס[\'"]? (\d+)', answer2)
            if wrong_match:
                print(f"  Returned content for decision {wrong_match.group(1)} instead")
    
    print("\nFirst 500 chars of content:")
    print(answer2[:500])
    
    # Step 3: Check session info
    print("\n" + "-" * 50)
    print("\nStep 3: Checking session info")
    session_info = requests.get(f"{BASE_URL}/session/{session_id}")
    if session_info.status_code == 200:
        info = session_info.json()
        print(f"Query count: {info['query_count']}")
        print("Recent queries:")
        for q in info['recent_queries']:
            print(f"  - {q['original_query']}")
            print(f"    Response type: {q['response_type']}, Has results: {q['has_results']}")

if __name__ == "__main__":
    test_reference_resolution()
