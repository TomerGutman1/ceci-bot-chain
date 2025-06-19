"""
Test what PandasAI actually returns
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_raw_response():
    """Test what PandasAI actually returns"""
    print("Testing Raw PandasAI Response")
    print("=" * 50)
    
    # Query 1: Get raw response for תחבורה ציבורית מ2018
    print("\nStep 1: Getting raw response for תחבורה ציבורית מ2018")
    response1 = requests.post(f"{BASE_URL}/query", json={
        "query": "הבא לי החלטה בנושא תחבורה ציבורית מ2018"
    })
    
    result1 = response1.json()
    print(f"Success: {result1.get('success')}")
    print(f"Query type: {result1.get('query_type')}")
    print(f"Error: {result1.get('error')}")
    
    # Print full metadata
    metadata = result1.get('metadata', {})
    print(f"\nMetadata:")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    
    # Check what's in the answer
    answer = result1.get('answer', '')
    if '4272' in answer:
        print("\n4272 appears in the answer!")
        print("But we know this decision doesn't exist in the database.")
    
    # Query 2: Check what decisions exist about תחבורה
    print("\n" + "-" * 50)
    print("\nStep 2: Checking what תחבורה decisions exist")
    response2 = requests.post(f"{BASE_URL}/query", json={
        "query": "print(df[df['tags_policy_area'].str.contains('תחבורה', na=False)]['decision_number'].head(20).tolist())"
    })
    
    result2 = response2.json()
    print(f"Success: {result2.get('success')}")
    print("Decision numbers with תחבורה:")
    print(result2.get('answer', 'No answer'))
    
    # Query 3: Check decisions from 2018
    print("\n" + "-" * 50)
    print("\nStep 3: Checking decisions from 2018")
    response3 = requests.post(f"{BASE_URL}/query", json={
        "query": "print(f'Total decisions from 2018: {len(df[df[\"year\"] == 2018])}')"
    })
    
    result3 = response3.json()
    print(result3.get('answer', 'No answer'))
    
    # Query 4: Get any decision from 2018
    print("\nStep 4: Getting any decision from 2018")
    response4 = requests.post(f"{BASE_URL}/query", json={
        "query": "הראה לי את df[df['year'] == 2018][['decision_number', 'decision_title', 'tags_policy_area']].head(5)"
    })
    
    result4 = response4.json()
    print(f"Success: {result4.get('success')}")
    print("Sample decisions from 2018:")
    print(result4.get('answer', 'No answer'))

if __name__ == "__main__":
    test_raw_response()
