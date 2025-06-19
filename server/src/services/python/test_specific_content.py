"""
Test specific decision content retrieval
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_specific_decision_content():
    """Test getting content of a specific decision"""
    print("Testing Specific Decision Content Retrieval")
    print("=" * 50)
    
    # Create a new session
    session_id = None
    
    # Query 1: Get decision 4272
    print("\nStep 1: Getting decision 4272 directly")
    response1 = requests.post(f"{BASE_URL}/query", json={
        "query": "הבא לי את החלטה מספר 4272"
    })
    
    result1 = response1.json()
    session_id = result1.get('session_id')
    
    print(f"Success: {result1.get('success')}")
    print(f"Session ID: {session_id}")
    
    answer1 = result1.get('answer', '')
    print("\nFirst 500 chars of answer:")
    print(answer1[:500])
    
    # Query 2: Get content directly by number
    print("\n" + "-" * 50)
    print("\nStep 2: Getting content of decision 4272 directly")
    response2 = requests.post(f"{BASE_URL}/query", json={
        "query": "הבא לי את התוכן המלא של החלטה מספר 4272",
        "session_id": session_id
    })
    
    result2 = response2.json()
    answer2 = result2.get('answer', '')
    
    print(f"Success: {result2.get('success')}")
    
    # Check if content matches decision 4272
    if '4272' in answer1 and 'נמל' in answer1:
        if 'נמל' in answer2 or 'תמ"א' in answer2:
            print("✓ Content matches decision 4272 (about נמל הדרום)")
        else:
            print("✗ Content does NOT match decision 4272")
            if 'קו האופק' in answer2:
                print("  Got content about 'קו האופק' instead!")
    
    print("\nContent preview:")
    print(answer2[:500])
    
    # Query 3: Try with explicit instruction
    print("\n" + "-" * 50)
    print("\nStep 3: Getting content with explicit instruction")
    response3 = requests.post(f"{BASE_URL}/query", json={
        "query": "תן לי את df[df['decision_number'] == '4272'].iloc[0]['decision_content']",
        "session_id": session_id
    })
    
    result3 = response3.json()
    answer3 = result3.get('answer', '')
    
    print(f"Success: {result3.get('success')}")
    
    if 'נמל' in answer3 or 'תמ"א' in answer3:
        print("✓ Explicit query worked!")
    else:
        print("✗ Even explicit query failed")
    
    print("\nContent preview:")
    print(answer3[:300])

if __name__ == "__main__":
    test_specific_decision_content()
