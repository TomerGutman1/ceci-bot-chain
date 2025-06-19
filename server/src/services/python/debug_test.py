"""
Debug test for Query Optimizer
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

# Start with simple queries
test_queries = [
    # Very simple query first
    "הבא לי החלטה אחת",
    
    # Then with filter
    "הבא לי החלטה בנושא חינוך",
    
    # Then with year
    "הבא לי החלטה משנת 2022",
    
    # Then combined
    "הבא לי החלטה בנושא חינוך משנת 2022",
]

def test_single_query(query):
    """Test a single query with detailed output"""
    print(f"\nTesting: {query}")
    print("-" * 50)
    
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/query", json={
            "query": query
        }, timeout=60)
        
        elapsed = time.time() - start_time
        print(f"Response time: {elapsed:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            
            if result.get('success'):
                print(f"Query type: {result.get('query_type', 'unknown')}")
                
                # Show answer preview
                answer = result.get('answer', '')
                if isinstance(answer, str):
                    lines = answer.split('\n')
                    print("\nAnswer preview:")
                    for line in lines[:5]:  # First 5 lines
                        print(f"  {line}")
                    if len(lines) > 5:
                        print(f"  ... ({len(lines) - 5} more lines)")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out (60s)")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")

def main():
    print("Debug Test for Query Optimizer")
    print("=" * 50)
    
    # Check health first
    try:
        print("Checking service health...")
        health = requests.get(f"{BASE_URL}/", timeout=5)
        if health.status_code == 200:
            health_data = health.json()
            print(f"✓ Service is {health_data.get('status', 'unknown')}")
            print(f"  Records: {health_data.get('records', 0)}")
        else:
            print("✗ Service is not healthy")
            return
    except Exception as e:
        print(f"✗ Cannot connect to service: {e}")
        return
    
    # Test each query
    for query in test_queries:
        test_single_query(query)
        time.sleep(2)  # Wait between queries
    
    print("\n" + "=" * 50)
    print("Debug test completed")

if __name__ == "__main__":
    main()
