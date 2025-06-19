"""
Test script to check if specific decisions exist in the database
Specifically checking decision 4272 which is causing issues
"""

import requests
import json

# PandasAI service URL
BASE_URL = "http://localhost:8001"

def check_decision(decision_number):
    """Check if a specific decision exists"""
    try:
        response = requests.get(f"{BASE_URL}/decision/{decision_number}")
        data = response.json()
        
        print(f"\n=== Checking Decision {decision_number} ===")
        print(f"Found: {data.get('found', False)}")
        
        if data.get('found'):
            print(f"Title: {data['data'].get('title', 'N/A')}")
            print(f"Date: {data['data'].get('date', 'N/A')}")
            print(f"Government: {data['data'].get('government_number', 'N/A')}")
            print(f"Has content: {data['data'].get('has_content', False)}")
        else:
            print(f"Message: {data.get('message', '')}")
            if data.get('similar_decisions'):
                print(f"Similar decisions: {data['similar_decisions']}")
                
    except Exception as e:
        print(f"Error checking decision {decision_number}: {e}")

def validate_decision(decision_number):
    """Quick validation check"""
    try:
        response = requests.get(f"{BASE_URL}/validate-decision/{decision_number}")
        data = response.json()
        
        print(f"\n=== Validation Check for {decision_number} ===")
        print(f"Exists: {data.get('exists', False)}")
        print(f"Total valid decisions: {data.get('total_valid_decisions', 0)}")
        
    except Exception as e:
        print(f"Error validating decision {decision_number}: {e}")

def test_query(query, session_id=None):
    """Test a specific query"""
    try:
        payload = {"query": query}
        if session_id:
            payload["session_id"] = session_id
            
        response = requests.post(f"{BASE_URL}/query", json=payload)
        data = response.json()
        
        print(f"\n=== Query Test: {query} ===")
        print(f"Success: {data.get('success', False)}")
        print(f"Query type: {data.get('query_type', 'N/A')}")
        
        if data.get('session_id'):
            print(f"Session ID: {data['session_id']}")
            
        if data.get('answer'):
            print(f"\nAnswer preview (first 500 chars):")
            print(data['answer'][:500] + "..." if len(data['answer']) > 500 else data['answer'])
            
        return data.get('session_id')
        
    except Exception as e:
        print(f"Error with query: {e}")
        return None

def main():
    print("Testing CECI-AI Decision Validation")
    print("====================================")
    
    # Check service health
    try:
        response = requests.get(BASE_URL)
        status = response.json()
        print(f"Service status: {status.get('status', 'unknown')}")
        print(f"Total records: {status.get('records', 0)}")
    except Exception as e:
        print(f"Service not running or error: {e}")
        return
    
    # Test problematic decision 4272
    check_decision("4272")
    validate_decision("4272")
    
    # Test some other decisions
    print("\n\nChecking other decisions for comparison:")
    for decision_num in ["1234", "5678", "100", "4270", "4280"]:
        validate_decision(decision_num)
    
    # Test queries
    print("\n\n=== Testing Queries ===")
    
    # First query
    session_id = test_query("הבא לי החלטה בנושא חינוך")
    
    if session_id:
        # Follow-up query for content
        print("\n\nTesting follow-up query for content:")
        test_query("הבא לי את תוכן ההחלטה", session_id)

if __name__ == "__main__":
    main()
