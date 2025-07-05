#!/usr/bin/env python3
"""
Comprehensive Token Usage Test
Tests multiple queries and analyzes token usage patterns
"""

import requests
import json
import time
from datetime import datetime
from collections import defaultdict

# Configuration
BASE_URL = 'http://localhost:5001'
TEST_ENDPOINT = f'{BASE_URL}/api/chat/test-bot-chain'
SSE_ENDPOINT = f'{BASE_URL}/api/chat'

# Test cases with expected behavior
TEST_CASES = [
    {
        "name": "Simple topic search",
        "query": "החלטות בנושא חינוך",
        "expected": {
            "uses_gpt": ["REWRITE"],
            "uses_template": ["SQLGEN"],
            "no_tokens": ["INTENT", "FORMATTER"]
        }
    },
    {
        "name": "Government + topic",
        "query": "החלטות ממשלה 37 בנושא בריאות", 
        "expected": {
            "uses_gpt": ["REWRITE"],
            "uses_template": ["SQLGEN"],
            "no_tokens": ["INTENT", "FORMATTER"]
        }
    },
    {
        "name": "Limited results",
        "query": "5 החלטות אחרונות",
        "expected": {
            "uses_gpt": ["REWRITE"],
            "uses_template": ["SQLGEN"],
            "no_tokens": ["INTENT", "FORMATTER"],
            "maybe_ranker": True
        }
    },
    {
        "name": "Complex query with typo",
        "query": "החלטות ממשלת ישראל בנושא חנוך מהשנה האחרונה",
        "expected": {
            "uses_gpt": ["REWRITE"],
            "uses_template": ["SQLGEN"],
            "no_tokens": ["INTENT", "FORMATTER"]
        }
    }
]

def test_direct_endpoint(query, session_id):
    """Test using the direct JSON endpoint"""
    try:
        response = requests.post(TEST_ENDPOINT, json={
            'query': query,
            'sessionId': session_id
        })
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def analyze_token_usage(result):
    """Analyze token usage from result"""
    if not result or not result.get('metadata'):
        return None
        
    metadata = result['metadata']
    token_usage = metadata.get('token_usage')
    
    if not token_usage:
        return None
        
    analysis = {
        'total_tokens': token_usage.get('total_tokens', 0),
        'total_cost': token_usage.get('estimated_cost_usd', 0),
        'bot_breakdown': token_usage.get('bot_breakdown', {}),
        'processing_time': metadata.get('processing_time_ms', 0),
        'intent': metadata.get('intent', 'unknown'),
        'confidence': metadata.get('confidence', 0)
    }
    
    return analysis

def print_test_result(test_case, analysis):
    """Print formatted test result"""
    print(f"\n{'='*60}")
    print(f"📋 Test: {test_case['name']}")
    print(f"🔍 Query: \"{test_case['query']}\"")
    print('='*60)
    
    if not analysis:
        print("❌ No token usage data available")
        return
        
    # Summary
    print(f"\n📊 Summary:")
    print(f"  Intent: {analysis['intent']}")
    print(f"  Confidence: {analysis['confidence']:.2f}")
    print(f"  Processing Time: {analysis['processing_time']}ms")
    print(f"  Total Tokens: {analysis['total_tokens']}")
    print(f"  Total Cost: ${analysis['total_cost']:.6f}")
    
    # Bot breakdown
    print(f"\n🤖 Bot Token Usage:")
    breakdown = analysis['bot_breakdown']
    
    # Expected bots
    expected = test_case['expected']
    all_bots = set()
    all_bots.update(expected.get('uses_gpt', []))
    all_bots.update(expected.get('uses_template', []))
    all_bots.update(expected.get('no_tokens', []))
    
    for bot in sorted(all_bots):
        if bot in breakdown:
            tokens = breakdown[bot]['tokens']
            cost = breakdown[bot]['cost_usd']
            print(f"  {bot:<15} {tokens:>6} tokens  ${cost:.6f}")
        else:
            if bot in expected.get('uses_gpt', []):
                print(f"  {bot:<15} ❌ Expected GPT usage but no tokens reported")
            elif bot in expected.get('uses_template', []):
                print(f"  {bot:<15} ✅ Template used (0 tokens expected)")
            elif bot in expected.get('no_tokens', []):
                print(f"  {bot:<15} ✅ No tokens expected")
    
    # Check for unexpected bots
    for bot in breakdown:
        if bot not in all_bots:
            tokens = breakdown[bot]['tokens']
            print(f"  {bot:<15} ⚠️  Unexpected: {tokens} tokens")

def run_comprehensive_test():
    """Run all test cases and summarize"""
    print("\n🚀 Comprehensive Token Usage Test")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check health
    try:
        health = requests.get(f'{BASE_URL}/api/chat/health').json()
        if health['status'] == 'healthy':
            print("✅ API is healthy")
        else:
            print("❌ API is unhealthy")
            return
    except:
        print("❌ Cannot connect to API")
        return
    
    # Run tests
    total_tokens = 0
    total_cost = 0
    bot_totals = defaultdict(lambda: {'tokens': 0, 'cost': 0})
    
    for test_case in TEST_CASES:
        session_id = f"test-{int(time.time())}"
        result = test_direct_endpoint(test_case['query'], session_id)
        analysis = analyze_token_usage(result)
        
        if analysis:
            print_test_result(test_case, analysis)
            total_tokens += analysis['total_tokens']
            total_cost += analysis['total_cost']
            
            # Aggregate by bot
            for bot, usage in analysis['bot_breakdown'].items():
                bot_totals[bot]['tokens'] += usage['tokens']
                bot_totals[bot]['cost'] += usage['cost_usd']
        else:
            print(f"\n❌ Test failed: {test_case['name']}")
            
        time.sleep(1)  # Rate limiting
    
    # Print summary
    print(f"\n{'='*60}")
    print("📈 SUMMARY REPORT")
    print('='*60)
    
    print(f"\n💰 Total Cost Analysis:")
    print(f"  Total Queries: {len(TEST_CASES)}")
    print(f"  Total Tokens: {total_tokens}")
    print(f"  Total Cost: ${total_cost:.6f}")
    print(f"  Avg Cost/Query: ${total_cost/len(TEST_CASES):.6f}")
    
    print(f"\n🤖 Cost by Bot:")
    sorted_bots = sorted(bot_totals.items(), key=lambda x: x[1]['cost'], reverse=True)
    for bot, totals in sorted_bots:
        pct = (totals['cost'] / total_cost * 100) if total_cost > 0 else 0
        print(f"  {bot:<15} {totals['tokens']:>8} tokens  ${totals['cost']:.6f} ({pct:>5.1f}%)")
    
    print(f"\n💡 Optimization Insights:")
    
    # Find most expensive bot
    if sorted_bots:
        top_bot = sorted_bots[0]
        print(f"  • {top_bot[0]} is the most expensive bot ({top_bot[1]['cost']/total_cost*100:.1f}% of total)")
    
    # Check if SQL templates are being used
    if 'SQLGEN' in bot_totals and bot_totals['SQLGEN']['tokens'] > 0:
        print(f"  • SQL Gen is using GPT instead of templates - consider adding more templates")
    else:
        print(f"  • SQL Gen is efficiently using templates")
    
    # Check for ranker usage
    if 'RANKER' in bot_totals:
        print(f"  • Ranker was used {bot_totals['RANKER']['tokens']} tokens - consider if necessary")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    run_comprehensive_test()
