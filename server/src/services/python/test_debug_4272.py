"""
Debug why we can't find decision 4272
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def debug_decision_4272():
    """Debug why we can't find decision 4272"""
    print("Debugging Decision 4272")
    print("=" * 50)
    
    # Query 1: Check decision_number data type
    print("\nStep 1: Check decision_number column data type")
    response1 = requests.post(f"{BASE_URL}/query", json={
        "query": "print(f'decision_number dtype: {df[\"decision_number\"].dtype}')"
    })
    
    result1 = response1.json()
    print(result1.get('answer', 'No answer'))
    
    # Query 2: Check for '4272' as string
    print("\n" + "-" * 50)
    print("\nStep 2: Check for '4272' as string")
    response2 = requests.post(f"{BASE_URL}/query", json={
        "query": "print(f'Decisions with 4272 as string: {len(df[df[\"decision_number\"] == \"4272\"])}')"
    })
    
    result2 = response2.json()
    print(result2.get('answer', 'No answer'))
    
    # Query 3: Check for 4272 as number
    print("\nStep 3: Check for 4272 as number")
    response3 = requests.post(f"{BASE_URL}/query", json={
        "query": "print(f'Decisions with 4272 as int: {len(df[df[\"decision_number\"] == 4272])}')"
    })
    
    result3 = response3.json()
    print(result3.get('answer', 'No answer'))
    
    # Query 4: Check with str conversion
    print("\n" + "-" * 50)
    print("\nStep 4: Check with str conversion")
    response4 = requests.post(f"{BASE_URL}/query", json={
        "query": "print(f'Decisions with str 4272: {len(df[df[\"decision_number\"].astype(str) == \"4272\"])}')"
    })
    
    result4 = response4.json()
    print(result4.get('answer', 'No answer'))
    
    # Query 5: Get the actual decision 4272
    print("\n" + "-" * 50)
    print("\nStep 5: Get decision 4272 data")
    response5 = requests.post(f"{BASE_URL}/query", json={
        "query": "result = {'type': 'dataframe', 'value': df[df['decision_number'].astype(str) == '4272'][['decision_number', 'year', 'decision_title', 'tags_policy_area']]}"
    })
    
    result5 = response5.json()
    print(f"Success: {result5.get('success')}")
    if result5.get('metadata', {}).get('raw_data'):
        data = result5.get('metadata', {}).get('raw_data', [])[0]
        print(f"Decision found!")
        print(f"  Number: {data.get('decision_number')}")
        print(f"  Year: {data.get('year')}")
        print(f"  Title: {data.get('decision_title')}")
        print(f"  Tags: {data.get('tags_policy_area')}")
    
    # Query 6: Check actual year of decision 4272
    print("\n" + "-" * 50)
    print("\nStep 6: Check what year decision 4272 is from")
    response6 = requests.post(f"{BASE_URL}/query", json={
        "query": "הראה את df[df['decision_number'].astype(str) == '4272']['year']"
    })
    
    result6 = response6.json()
    print(f"Answer: {result6.get('answer', 'No answer')}")

if __name__ == "__main__":
    debug_decision_4272()
