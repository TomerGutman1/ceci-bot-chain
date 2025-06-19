"""
Advanced Test for Reference Resolution
Tests specific content to ensure we're getting the right decision
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_advanced_reference_resolution():
    """Test if reference resolution returns the correct content"""
    print("Testing Advanced Reference Resolution")
    print("=" * 50)
    
    # Step 1: Get a specific decision about הגירה from government 32
    print("\nStep 1: Getting decision about הגירה from government 32")
    response1 = requests.post(f"{BASE_URL}/query", json={
        "query": "הבא לי החלטה בנושא הגירה של ממשלה 32"
    })
    
    result1 = response1.json()
    session_id = result1.get('session_id')
    
    print(f"Success: {result1.get('success')}")
    print(f"Session ID: {session_id}")
    
    # Extract decision details
    answer1 = result1.get('answer', '')
    import re
    
    # Extract decision number
    decision_match = re.search(r'מספר החלטה: (\d+)', answer1)
    decision_num = decision_match.group(1) if decision_match else None
    
    # Extract key content identifiers
    content_markers = {}
    if 'מולדובה' in answer1:
        content_markers['moldova'] = True
        print("✓ Found 'מולדובה' in first response")
    
    if 'אשרור הסכם' in answer1:
        content_markers['agreement'] = True
        print("✓ Found 'אשרור הסכם' in first response")
    
    print(f"\nDecision number: {decision_num}")
    print(f"Key markers found: {list(content_markers.keys())}")
    
    # Wait a bit
    time.sleep(1)
    
    # Step 2: Request full content
    print("\n" + "-" * 50)
    print("\nStep 2: Requesting full content of THE decision")
    response2 = requests.post(f"{BASE_URL}/query", json={
        "query": "הבא לי את התוכן המלא של ההחלטה",
        "session_id": session_id
    })
    
    result2 = response2.json()
    answer2 = result2.get('answer', '')
    
    print(f"Success: {result2.get('success')}")
    print(f"Same session: {result2.get('session_id') == session_id}")
    
    # Verify content
    print("\nContent verification:")
    
    # Check basic content structure
    if answer2 and len(answer2) > 50:
        print("✓ Content has sufficient length")
    else:
        print("✗ Content is too short or empty")
    
    # Check for decision structure
    if "א." in answer2 or "א " in answer2:
        print("✓ Content has decision structure (starts with א.)")
    else:
        print("✗ Missing decision structure")
    
    # Check for key content markers
    if content_markers.get('moldova') and 'מולדובה' in answer2:
        print("✓ Content contains 'מולדובה' - matches original decision!")
    elif content_markers.get('moldova'):
        print("✗ Content missing 'מולדובה' - might be wrong decision")
    
    if content_markers.get('agreement') and 'הסכם' in answer2:
        print("✓ Content contains 'הסכם' - matches theme")
    
    # Check for common decision elements
    if 'ההחלטה התקבלה' in answer2:
        print("✓ Content has standard decision footer")
    
    print("\nContent preview:")
    print(answer2[:200] + "...")
    
    # Step 3: Test another reference type
    print("\n" + "-" * 50)
    print("\nStep 3: Testing 'more details' reference")
    response3 = requests.post(f"{BASE_URL}/query", json={
        "query": "פרטים נוספים על ההחלטה",
        "session_id": session_id
    })
    
    result3 = response3.json()
    answer3 = result3.get('answer', '')
    
    if answer3 and (decision_num in answer3 or 'מולדובה' in answer3):
        print("✓ 'More details' reference worked correctly")
    else:
        print("✗ 'More details' reference failed")
    
    # Final summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    
    session_info = requests.get(f"{BASE_URL}/session/{session_id}")
    if session_info.status_code == 200:
        info = session_info.json()
        print(f"Total queries in session: {info['query_count']}")
        print(f"All queries tracked: {'✓' if info['query_count'] == 3 else '✗'}")
        
        # Check if all queries were resolved correctly
        resolved_count = sum(1 for q in info['recent_queries'] if 'השתמש ב:' in q.get('original_query', ''))
        print(f"Queries with reference resolution: {resolved_count}")

if __name__ == "__main__":
    test_advanced_reference_resolution()
