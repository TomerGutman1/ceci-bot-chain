"""
Debug decision data
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def debug_decisions():
    """Debug what decisions exist in the database"""
    print("Debugging Decision Data")
    print("=" * 50)
    
    # Query 1: Check decisions from 2018 about תחבורה
    print("\nStep 1: Checking decisions from 2018 about תחבורה")
    response1 = requests.post(f"{BASE_URL}/query", json={
        "query": "הראה לי את df[(df['year'] == 2018) & (df['tags_policy_area'].str.contains('תחבורה', na=False))][['decision_number', 'decision_title', 'decision_content']].head()"
    })
    
    result1 = response1.json()
    print(f"Success: {result1.get('success')}")
    print("Answer:")
    print(result1.get('answer', 'No answer'))
    
    # Query 2: Check if decision 4272 exists
    print("\n" + "-" * 50)
    print("\nStep 2: Checking if decision 4272 exists")
    response2 = requests.post(f"{BASE_URL}/query", json={
        "query": "print(len(df[df['decision_number'] == '4272']))"
    })
    
    result2 = response2.json()
    print(f"Success: {result2.get('success')}")
    print("Answer:")
    print(result2.get('answer', 'No answer'))
    
    # Query 3: Get decision numbers around 4272
    print("\n" + "-" * 50)
    print("\nStep 3: Checking decision numbers around 4272")
    response3 = requests.post(f"{BASE_URL}/query", json={
        "query": "הראה לי את df[(df['decision_number'].astype(int) >= 4270) & (df['decision_number'].astype(int) <= 4275)][['decision_number', 'decision_title', 'year']]"
    })
    
    result3 = response3.json()
    print(f"Success: {result3.get('success')}")
    print("Answer:")
    print(result3.get('answer', 'No answer'))
    
    # Query 4: Check the actual decision that was returned
    print("\n" + "-" * 50)
    print("\nStep 4: What decision was actually returned for תחבורה ציבורית מ2018?")
    response4 = requests.post(f"{BASE_URL}/query", json={
        "query": "הבא לי החלטה בנושא תחבורה ציבורית מ2018"
    })
    
    result4 = response4.json()
    answer = result4.get('answer', '')
    
    # Extract the decision number from the response
    import re
    decision_match = re.search(r'מספר החלטה: (\d+)', answer)
    if decision_match:
        actual_decision = decision_match.group(1)
        print(f"Decision returned: {actual_decision}")
        
        # Now check if this decision has content
        print("\nStep 5: Checking if this decision has content")
        response5 = requests.post(f"{BASE_URL}/query", json={
            "query": f"print(df[df['decision_number'] == '{actual_decision}']['decision_content'].iloc[0][:200] if not df[df['decision_number'] == '{actual_decision}']['decision_content'].isna().iloc[0] else 'No content')"
        })
        
        result5 = response5.json()
        print(f"Content exists: {result5.get('success')}")
        print("Content preview:")
        print(result5.get('answer', 'No answer'))

if __name__ == "__main__":
    debug_decisions()
