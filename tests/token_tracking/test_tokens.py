#!/usr/bin/env python3
"""
Test Token Usage Reporting
Simple Python script to test token usage tracking
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_URL = 'http://localhost:5001/api/chat'
HEALTH_URL = 'http://localhost:5001/api/chat/health'

# Test queries
TEST_QUERIES = [
    {
        "name": "Simple search",
        "query": "החלטות בנושא חינוך",
        "description": "Should use REWRITE, INTENT (deterministic), SQLGEN (template), FORMATTER"
    },
    {
        "name": "Government + topic",
        "query": "החלטות ממשלה 37 בנושא בריאות",
        "description": "Should use templates for SQL"
    },
    {
        "name": "Limited results with ranking",
        "query": "5 החלטות אחרונות בנושא תחבורה",
        "description": "May trigger RANKER bot with GPT-4"
    }
]

def check_health():
    """Check if the API is healthy"""
    try:
        response = requests.get(HEALTH_URL)
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def parse_sse_response(response_text):
    """Parse SSE response and extract final data"""
    lines = response_text.strip().split('\n')
    final_data = None
    
    for line in lines:
        if line.startswith('data: '):
            try:
                data = json.loads(line[6:])
                if data.get('final'):
                    final_data = data
            except json.JSONDecodeError:
                pass
    
    return final_data

def format_token_report(token_usage):
    """Format token usage report"""
    if not token_usage:
        return "❌ No token usage data"
    
    report = []
    report.append("📊 Token Usage Summary:")
    report.append(f"   Total Tokens: {token_usage.get('total_tokens', 0)}")
    report.append(f"   Prompt Tokens: {token_usage.get('prompt_tokens', 0)}")
    report.append(f"   Completion Tokens: {token_usage.get('completion_tokens', 0)}")
    report.append(f"   Estimated Cost: ${token_usage.get('estimated_cost_usd', 0):.4f}")
    
    if 'bot_breakdown' in token_usage:
        report.append("\n📈 Token Usage by Bot:")
        breakdown = token_usage['bot_breakdown']
        
        # Sort by tokens used
        sorted_bots = sorted(breakdown.items(), key=lambda x: x[1]['tokens'], reverse=True)
        
        for bot_name, usage in sorted_bots:
            tokens = usage['tokens']
            cost = usage['cost_usd']
            report.append(f"   {bot_name:<15} {tokens:>6} tokens  ${cost:.4f}")
    
    return "\n".join(report)

def test_query(query_info):
    """Test a single query"""
    print(f"\n{'='*60}")
    print(f"🔍 Testing: {query_info['name']}")
    print(f"📝 Query: \"{query_info['query']}\"")
    print(f"ℹ️  {query_info['description']}")
    print('='*60)
    
    session_id = f"test-token-{int(time.time())}"
    
    try:
        # Make the request
        start_time = time.time()
        response = requests.post(API_URL, json={
            'message': query_info['query'],
            'sessionId': session_id
        })
        duration = (time.time() - start_time) * 1000
        
        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code}")
            print(response.text)
            return
        
        # Parse SSE response
        final_data = parse_sse_response(response.text)
        
        if not final_data:
            print("❌ No final response received")
            return
        
        # Check metadata
        metadata = final_data.get('metadata', {})
        if not metadata:
            print("❌ No metadata in response")
            return
        
        # Display query info
        print(f"\n✅ Query processed successfully")
        print(f"   Intent: {metadata.get('intent', 'unknown')}")
        print(f"   Confidence: {metadata.get('confidence', 0):.2f}")
        print(f"   Processing Time: {duration:.0f}ms")
        print(f"   Service: {metadata.get('service', 'unknown')}")
        
        # Display token usage
        token_usage = metadata.get('token_usage')
        if token_usage:
            print(f"\n{format_token_report(token_usage)}")
            
            # Check which bots reported tokens
            if 'bot_breakdown' in token_usage:
                print("\n🔍 Bot Coverage:")
                expected_bots = ['REWRITE', 'INTENT', 'SQLGEN', 'FORMATTER']
                if 'אחרונות' in query_info['query'] or 'limit' in query_info['query'].lower():
                    expected_bots.append('RANKER')
                
                breakdown = token_usage['bot_breakdown']
                for bot in expected_bots:
                    if bot in breakdown:
                        print(f"   ✅ {bot}: {breakdown[bot]['tokens']} tokens")
                    else:
                        if bot == 'INTENT':
                            print(f"   ℹ️  {bot}: Using deterministic engine (0 tokens)")
                        elif bot == 'SQLGEN' and breakdown.get('SQLGEN', {}).get('tokens', 0) == 0:
                            print(f"   ℹ️  {bot}: Using template (0 tokens)")
                        else:
                            print(f"   ❓ {bot}: No token usage reported")
        else:
            print("\n❌ No token usage in metadata!")
            print("Metadata keys:", list(metadata.keys()))
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test runner"""
    print("\n🚀 Token Usage Reporting Test")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check health first
    if not check_health():
        print("\n⚠️  Please make sure the bot chain is running:")
        print("   cd /path/to/project && docker-compose up -d")
        return
    
    # Run tests
    for query_info in TEST_QUERIES:
        test_query(query_info)
        time.sleep(2)  # Wait between queries
    
    print("\n✅ All tests completed!")
    print("\n💡 Tips for optimization:")
    print("   - If costs are high, check which bots use the most tokens")
    print("   - Consider adding more SQL templates to reduce GPT usage")
    print("   - Monitor RANKER usage - it can be expensive with GPT-4")
    print("   - REWRITE bot tokens can be reduced with shorter prompts")

if __name__ == "__main__":
    main()
