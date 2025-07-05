#!/usr/bin/env python3
"""
Selective Bot Token Testing
Test specific expensive bots with minimal queries
"""

import requests
import json
import time

API_URL = 'http://localhost:5001/api/chat'

def test_bot(query, bot_name, session_id=None):
    """Test a single query and report token usage"""
    if not session_id:
        session_id = f"test-{bot_name}-{int(time.time())}"
    
    print(f"\n{'='*50}")
    print(f"🤖 Testing: {bot_name}")
    print(f"📝 Query: {query}")
    print('='*50)
    
    try:
        # Make request
        response = requests.post(API_URL, json={
            'message': query,
            'sessionId': session_id
        })
        
        # Parse response
        lines = response.text.strip().split('\n')
        for line in lines:
            if line.startswith('data: ') and '"final":true' in line:
                data = json.loads(line[6:])
                metadata = data.get('metadata', {})
                token_usage = metadata.get('token_usage', {})
                
                if token_usage:
                    print(f"\n✅ Token Usage:")
                    print(f"   Total: {token_usage.get('total_tokens', 0)} tokens")
                    print(f"   Cost: ${token_usage.get('estimated_cost_usd', 0):.6f}")
                    
                    # Bot breakdown
                    breakdown = token_usage.get('bot_breakdown', {})
                    if breakdown:
                        print(f"\n   Bot Breakdown:")
                        for bot, usage in breakdown.items():
                            print(f"   - {bot}: {usage['tokens']} tokens (${usage['cost_usd']:.6f})")
                    
                    # Check if target bot was triggered
                    if bot_name in breakdown:
                        print(f"\n✅ {bot_name} was triggered!")
                    else:
                        print(f"\n❌ {bot_name} was NOT triggered")
                else:
                    print("\n❌ No token usage data")
                    
                return token_usage
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

# Test scenarios
print("🚀 Selective Bot Token Testing")
print("="*50)

# 1. Test CLARIFY bot with ambiguous query
print("\n1️⃣ Testing CLARIFY Bot (Ambiguous Query)")
test_bot("החלטות חשובות", "CLARIFY")
time.sleep(2)

# 2. Test RANKER with limited results
print("\n2️⃣ Testing RANKER Bot (Limited Results)")
test_bot("10 החלטות אחרונות בנושא כלכלה", "RANKER")
time.sleep(2)

# 3. Test EVALUATOR with EVAL query (expensive!)
print("\n3️⃣ Testing EVALUATOR Bot (EVAL Query - GPT-4!)")
print("⚠️  WARNING: This uses GPT-4 and is expensive!")
response = input("Continue? (y/n): ")
if response.lower() == 'y':
    test_bot("נתח לעומק את החלטה 2983 של ממשלה 37", "EVALUATOR")
else:
    print("Skipped EVALUATOR test")

# 4. Test SQL Gen with complex query (should use GPT)
print("\n4️⃣ Testing SQLGEN with GPT (Complex Query)")
test_bot("השווה בין כל ההחלטות של ממשלה 36 ו-37 בנושאי חינוך וכלכלה", "SQLGEN")

print("\n✅ Testing completed!")
print("\n💡 Tips:")
print("   - CLARIFY triggers on vague queries")
print("   - RANKER triggers with many results")
print("   - EVALUATOR only on EVAL intent")
print("   - SQLGEN uses GPT for complex queries without templates")
