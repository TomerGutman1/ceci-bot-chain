"""
Check what data is actually loaded
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def check_loaded_data():
    """Check what data is actually loaded in the system"""
    print("Checking Loaded Data")
    print("=" * 50)
    
    # Query 1: Total records
    print("\nStep 1: Total records loaded")
    response1 = requests.post(f"{BASE_URL}/query", json={
        "query": "print(f'Total records: {len(df)}')"
    })
    
    result1 = response1.json()
    print(result1.get('answer', 'No answer'))
    
    # Query 2: Sample of decision numbers
    print("\n" + "-" * 50)
    print("\nStep 2: Sample of decision numbers")
    response2 = requests.post(f"{BASE_URL}/query", json={
        "query": "print('Sample decision numbers:', df['decision_number'].head(20).tolist())"
    })
    
    result2 = response2.json()
    print(result2.get('answer', 'No answer'))
    
    # Query 3: Check max decision number
    print("\n" + "-" * 50)
    print("\nStep 3: Max decision number")
    response3 = requests.post(f"{BASE_URL}/query", json={
        "query": "print(f'Max decision number: {df[\"decision_number\"].astype(str).max()}')"
    })
    
    result3 = response3.json()
    print(result3.get('answer', 'No answer'))
    
    # Query 4: Check for decisions > 4000
    print("\n" + "-" * 50)
    print("\nStep 4: Decisions with number > 4000")
    response4 = requests.post(f"{BASE_URL}/query", json={
        "query": "high_nums = df[pd.to_numeric(df['decision_number'], errors='coerce') > 4000]['decision_number'].head(10).tolist(); print(f'Decisions > 4000: {high_nums}')"
    })
    
    result4 = response4.json()
    print(result4.get('answer', 'No answer'))
    
    # Query 5: Check decisions containing '427' in number
    print("\n" + "-" * 50)
    print("\nStep 5: Decisions containing '427' in number")
    response5 = requests.post(f"{BASE_URL}/query", json={
        "query": "containing_427 = df[df['decision_number'].astype(str).str.contains('427', na=False)]['decision_number'].head(10).tolist(); print(f'Decisions with 427: {containing_427}')"
    })
    
    result5 = response5.json()
    print(result5.get('answer', 'No answer'))
    
    # Query 6: Check if data is from DataProvider or Supabase
    print("\n" + "-" * 50)
    print("\nStep 6: Check data status")
    response6 = requests.get(f"{BASE_URL}/data-status")
    
    if response6.status_code == 200:
        status = response6.json()
        print(f"Data loaded: {status.get('data_loaded')}")
        print(f"Records: {status.get('records')}")
        print(f"PandasAI ready: {status.get('pandasai_ready')}")

if __name__ == "__main__":
    check_loaded_data()
