#!/usr/bin/env python3
"""Test script to debug specific decision queries"""

import requests
import json

# Test the unified intent bot
intent_url = "http://localhost:8011/rewrite-and-detect"
intent_payload = {
    "original_query": "החלטה 100 של ממשלה 35",
    "conv_id": "test-123",
    "trace_id": "test-trace"
}

print("Testing Unified Intent Bot:")
print(f"Query: {intent_payload['original_query']}")
print("-" * 50)

try:
    response = requests.post(intent_url, json=intent_payload)
    if response.status_code == 200:
        result = response.json()
        print(f"Intent: {result.get('intent')}")
        print(f"Entities: {json.dumps(result.get('entities', {}), ensure_ascii=False, indent=2)}")
        print(f"Full content: {result.get('full_content', False)}")
        
        # Now test SQL generation
        if result.get('entities'):
            sql_url = "http://localhost:8012/sqlgen"
            sql_payload = {
                "intent": result['intent'],
                "entities": result['entities'],
                "conv_id": "test-123",
                "trace_id": "test-trace",
                "conversation_history": []
            }
            
            print("\n" + "="*50)
            print("Testing SQL Generation Bot:")
            print("-" * 50)
            
            sql_response = requests.post(sql_url, json=sql_payload)
            if sql_response.status_code == 200:
                sql_result = sql_response.json()
                print(f"SQL Query: {sql_result.get('sql_query')}")
                print(f"Parameters: {json.dumps(sql_result.get('parameters', []), ensure_ascii=False, indent=2)}")
                print(f"Query Type: {sql_result.get('query_type')}")
                print(f"Enhanced Entities: {json.dumps(sql_result.get('enhanced_entities', {}), ensure_ascii=False, indent=2)}")
            else:
                print(f"SQL Gen Error: {sql_response.status_code} - {sql_response.text}")
    else:
        print(f"Intent Bot Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test another query for comparison
print("\n" + "="*70)
print("\nTesting a general government query for comparison:")
intent_payload2 = {
    "original_query": "החלטות של ממשלה 35",
    "conv_id": "test-456",
    "trace_id": "test-trace-2"
}

try:
    response2 = requests.post(intent_url, json=intent_payload2)
    if response2.status_code == 200:
        result2 = response2.json()
        print(f"Query: {intent_payload2['original_query']}")
        print(f"Intent: {result2.get('intent')}")
        print(f"Entities: {json.dumps(result2.get('entities', {}), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"Error: {e}")