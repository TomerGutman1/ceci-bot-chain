#!/usr/bin/env python3
"""
Test EVAL Query Token Usage
Tests the expensive EVALUATOR bot with GPT-4
"""

import requests
import json
import sys
import time

API_URL = 'http://localhost:5001/api/chat'

def test_eval_query():
    """Test a single EVAL query"""
    
    # Warning
    print("\n⚠️  WARNING: EVAL queries use GPT-4 and are expensive!")
    print("This test will run a deep analysis query that costs more.")
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Test cancelled.")
        sys.exit(0)
    
    # The EVAL query
    query = "נתח לעומק את החלטה 2983 של ממשלה 37 בנושא חינוך STEM"
    session_id = f"test-eval-{int(time.time())}"
    
    print(f"\n🔍 Testing EVAL Query:")
    print(f"📝 Query: {query}")
    print("="*60)
    
    try:
        # Make request
        print("\n⏳ Processing (this may take a few seconds)...")
        response = requests.post(API_URL, json={
            'message': query,
            'sessionId': session_id
        })
        
        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code}")
            return
        
        # Parse response
        lines = response.text.strip().split('\n')
        final_data = None
        
        for line in lines:
            if line.startswith('data: ') and '"final":true' in line:
                final_data = json.loads(line[6:])
                break
        
        if not final_data:
            print("❌ No final response received")
            return
        
        # Extract metadata
        metadata = final_data.get('metadata', {})
        token_usage = metadata.get('token_usage', {})
        
        print(f"\n📊 Results:")
        print(f"   Intent: {metadata.get('intent')}")
        print(f"   Service: {metadata.get('service')}")
        print(f"   Processing Time: {metadata.get('processing_time_ms', 0)}ms")
        
        if metadata.get('intent') != 'EVAL':
            print("\n⚠️  Query was not recognized as EVAL intent!")
            print("   EVALUATOR bot may not have been triggered.")
        
        if token_usage:
            print(f"\n💰 Token Usage:")
            print(f"   Total Tokens: {token_usage.get('total_tokens', 0)}")
            print(f"   Prompt Tokens: {token_usage.get('prompt_tokens', 0)}")
            print(f"   Completion Tokens: {token_usage.get('completion_tokens', 0)}")
            print(f"   Total Cost: ${token_usage.get('estimated_cost_usd', 0):.6f}")
            
            # Bot breakdown
            breakdown = token_usage.get('bot_breakdown', {})
            if breakdown:
                print(f"\n🤖 Cost by Bot:")
                sorted_bots = sorted(breakdown.items(), 
                                   key=lambda x: x[1]['cost_usd'], 
                                   reverse=True)
                
                for bot, usage in sorted_bots:
                    tokens = usage['tokens']
                    cost = usage['cost_usd']
                    model_indicator = ""
                    
                    # Indicate expensive bots
                    if bot == 'EVALUATOR':
                        model_indicator = " (GPT-4 🔥)"
                    elif bot == 'RANKER' and tokens > 0:
                        model_indicator = " (GPT-4)"
                    elif bot == 'REWRITE':
                        model_indicator = " (GPT-3.5)"
                    
                    print(f"   {bot:<15}{model_indicator:<12} {tokens:>6} tokens  ${cost:.6f}")
                
                # Check if EVALUATOR was used
                if 'EVALUATOR' in breakdown:
                    eval_cost = breakdown['EVALUATOR']['cost_usd']
                    print(f"\n✅ EVALUATOR was triggered!")
                    print(f"   EVALUATOR alone cost: ${eval_cost:.6f}")
                else:
                    print(f"\n❌ EVALUATOR was NOT triggered!")
                    print("   The query may not have been recognized as EVAL intent.")
            
            # Cost warnings
            total_cost = token_usage.get('estimated_cost_usd', 0)
            if total_cost > 0.01:
                print(f"\n💸 EXPENSIVE QUERY: ${total_cost:.4f}")
                print("   This is normal for EVAL queries, but use sparingly!")
        else:
            print("\n❌ No token usage data in response")
        
        # Show a sample of the analysis
        if final_data.get('response'):
            print(f"\n📄 Analysis Preview (first 500 chars):")
            print("-"*60)
            print(final_data['response'][:500] + "...")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🚀 EVAL Query Token Usage Test")
    print("="*60)
    
    # Check health
    try:
        health_response = requests.get('http://localhost:5001/api/chat/health')
        if health_response.status_code == 200:
            print("✅ API is healthy")
        else:
            print("❌ API health check failed")
            sys.exit(1)
    except:
        print("❌ Cannot connect to API")
        sys.exit(1)
    
    # Run test
    test_eval_query()
    
    print("\n✅ Test completed!")
    print("\n💡 EVAL Query Optimization Tips:")
    print("   - EVAL queries are expensive (GPT-4)")
    print("   - Use only for deep analysis of specific decisions")
    print("   - Consider caching EVAL results")
    print("   - Typical cost: $0.01-0.05 per EVAL query")
