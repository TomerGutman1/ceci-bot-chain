"""
Test Query Optimizer functionality
"""

import requests
import json

BASE_URL = "http://localhost:8001"

test_queries = [
    # Should work well with optimization
    "הבא לי החלטה בנושא חינוך משנת 2022",
    "הבא לי 3 החלטות בנושא בריאות",
    "החלטות ממשלה 36 בנושא תחבורה",
    
    # Statistical queries (should sample)
    "כמה החלטות יש בנושא חינוך",
    "מה ההתפלגות של החלטות לפי שנים",
    
    # Complex queries
    "הבא לי את כל ההחלטות בנושא חינוך מ-2020",
    "תן לי סטטיסטיקה של החלטות לפי ממשלה",
]

def test_queries_with_optimization():
    print("Testing queries with optimization...")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 30)
        
        try:
            response = requests.post(f"{BASE_URL}/query", json={
                "query": query
            }, timeout=30)
            
            result = response.json()
            
            if result['success']:
                print("✓ Success")
                # Print first 200 chars of answer
                answer = result['answer']
                if isinstance(answer, str):
                    print(f"Answer preview: {answer[:200]}...")
                else:
                    print(f"Answer type: {type(answer)}")
            else:
                print("✗ Failed")
                print(f"Error: {result.get('error', 'Unknown error')}")
                
        except requests.exceptions.Timeout:
            print("✗ Timeout (30s)")
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("Query Optimizer Test")
    print("Make sure PandasAI service is running on port 8001")
    print("-" * 50)
    
    # Check if service is healthy
    try:
        health = requests.get(f"{BASE_URL}/")
        if health.status_code != 200:
            print("PandasAI service is not responding!")
            exit(1)
        
        test_queries_with_optimization()
        
    except Exception as e:
        print(f"Error: {e}")
