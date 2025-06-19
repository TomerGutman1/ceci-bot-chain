"""
Test PandasAI hallucination
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_hallucination():
    """Test if PandasAI is hallucinating decisions"""
    print("Testing PandasAI Hallucination")
    print("=" * 50)
    
    # Query 1: Ask for decisions that don't exist
    print("\nTest 1: Asking for decisions from 2018 (we know there are none)")
    response1 = requests.post(f"{BASE_URL}/query", json={
        "query": "הבא לי החלטה מ-2018"
    })
    
    result1 = response1.json()
    print(f"Success: {result1.get('success')}")
    if result1.get('metadata', {}).get('raw_data'):
        print("⚠️ WARNING: PandasAI returned data for non-existent year!")
        print(f"Returned decision: {result1.get('metadata', {}).get('raw_data', [])[0].get('decision_number', 'N/A')}")
    else:
        print("✓ Correctly returned no results")
    
    # Query 2: Direct code to check 2018 decisions
    print("\n" + "-" * 50)
    print("\nTest 2: Direct code to list 2018 decisions")
    response2 = requests.post(f"{BASE_URL}/query", json={
        "query": "result = {'type': 'dataframe', 'value': df[df['year'] == 2018]}"
    })
    
    result2 = response2.json()
    print(f"Success: {result2.get('success')}")
    print(f"Answer: {result2.get('answer', 'No answer')}")
    
    # Query 3: Ask for the latest decision
    print("\n" + "-" * 50)
    print("\nTest 3: Ask for the latest decision (to see what years we have)")
    response3 = requests.post(f"{BASE_URL}/query", json={
        "query": "הבא לי את ההחלטה האחרונה שהתקבלה"
    })
    
    result3 = response3.json()
    if result3.get('success'):
        answer = result3.get('answer', '')
        import re
        year_match = re.search(r'(\d{4})', answer)
        if year_match:
            print(f"Latest decision is from year: {year_match.group(1)}")
        else:
            print("Could not extract year from response")
    
    # Query 4: Check year range in database
    print("\n" + "-" * 50)
    print("\nTest 4: Check year range in database")
    response4 = requests.post(f"{BASE_URL}/query", json={
        "query": "print(f'Min year: {df[\"year\"].min()}, Max year: {df[\"year\"].max()}')"
    })
    
    result4 = response4.json()
    print(f"Year range: {result4.get('answer', 'No answer')}")
    
    # Query 5: Force PandasAI to be honest
    print("\n" + "-" * 50)
    print("\nTest 5: Force PandasAI to check if data exists")
    response5 = requests.post(f"{BASE_URL}/query", json={
        "query": "אם len(df[df['year'] == 2018]) == 0, תחזיר 'אין החלטות מ-2018'. אחרת, הבא החלטה מ-2018"
    })
    
    result5 = response5.json()
    print(f"Answer: {result5.get('answer', 'No answer')}")

if __name__ == "__main__":
    test_hallucination()
