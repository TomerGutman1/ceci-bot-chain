#!/usr/bin/env python3
"""
Comprehensive Token Usage Test - All Bots
Tests various scenarios to trigger different bots and verify token reporting
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration
API_URL = 'http://localhost:5001/api/chat'
HEALTH_URL = 'http://localhost:5001/api/chat/health'

# Test queries designed to trigger different bots
TEST_SCENARIOS = [
    {
        "name": "Simple Query with Template",
        "query": "החלטות בנושא חינוך",
        "expected_bots": ["REWRITE", "SQLGEN"],
        "description": "Should use template for SQL, minimal token usage"
    },
    {
        "name": "Query with Ranking",
        "query": "10 החלטות חשובות בנושא כלכלה מהשנתיים האחרונות",
        "expected_bots": ["REWRITE", "SQLGEN", "RANKER"],
        "description": "Should trigger RANKER with GPT-4 (expensive)"
    },
    {
        "name": "Ambiguous Query for Clarification",
        "query": "החלטות",
        "expected_bots": ["REWRITE", "CLARIFY"],
        "description": "Too vague, should trigger clarification"
    },
    {
        "name": "Context Reference Query",
        "query": "עוד החלטות כמו שהצגת קודם",
        "expected_bots": ["REWRITE", "CONTEXT_ROUTER"],
        "description": "References previous context"
    },
    {
        "name": "EVAL Query (Single, Expensive)",
        "query": "נתח את החלטה 2983 של ממשלה 37",
        "expected_bots": ["REWRITE", "SQLGEN", "EVALUATOR"],
        "description": "Deep analysis with EVALUATOR (GPT-4, expensive)"
    },
    {
        "name": "Complex Query Needing GPT SQL",
        "query": "השווה בין החלטות בנושא חינוך לבין החלטות בנושא בריאות בממשלה 37",
        "expected_bots": ["REWRITE", "SQLGEN"],
        "description": "Complex query that might need GPT for SQL generation"
    }
]

class TokenTestRunner:
    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0
        self.bot_totals = {}
        self.results = []
        
    def check_health(self) -> bool:
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

    def parse_sse_response(self, response_text: str) -> Dict[str, Any]:
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

    def print_bot_token_usage(self, bot_breakdown: Dict[str, Dict[str, float]], expected_bots: List[str]):
        """Print token usage per bot with validation"""
        print("\n🤖 Bot Token Usage:")
        
        # Sort by tokens used
        sorted_bots = sorted(bot_breakdown.items(), key=lambda x: x[1]['tokens'], reverse=True)
        
        for bot_name, usage in sorted_bots:
            tokens = usage['tokens']
            cost = usage['cost_usd']
            status = "✅" if bot_name in expected_bots else "❓"
            
            # Update totals
            if bot_name not in self.bot_totals:
                self.bot_totals[bot_name] = {"tokens": 0, "cost": 0}
            self.bot_totals[bot_name]["tokens"] += tokens
            self.bot_totals[bot_name]["cost"] += cost
            
            print(f"  {bot_name:<15} {status} {tokens:>6} tokens  ${cost:.6f}")
        
        # Check for expected bots
        print("\n🔍 Expected Bots Check:")
        for expected_bot in expected_bots:
            if expected_bot in bot_breakdown:
                print(f"  ✅ {expected_bot}: {bot_breakdown[expected_bot]['tokens']} tokens")
            else:
                # Special cases
                if expected_bot == "INTENT":
                    print(f"  ℹ️  {expected_bot}: Using deterministic engine (0 tokens)")
                elif expected_bot == "FORMATTER":
                    print(f"  ℹ️  {expected_bot}: Code-only, no GPT usage")
                elif expected_bot == "CONTEXT_ROUTER" and "ROUTE" not in bot_breakdown:
                    print(f"  ❓ {expected_bot}: Expected but not found")
                else:
                    print(f"  ❌ {expected_bot}: Expected but not reported")

    def test_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single scenario"""
        print(f"\n{'='*60}")
        print(f"📋 Test: {scenario['name']}")
        print(f"🔍 Query: \"{scenario['query']}\"")
        print(f"📝 {scenario['description']}")
        print('='*60)
        
        session_id = f"test-all-bots-{int(time.time())}"
        
        try:
            # Make the request
            start_time = time.time()
            response = requests.post(API_URL, json={
                'message': scenario['query'],
                'sessionId': session_id
            })
            duration = (time.time() - start_time) * 1000
            
            if response.status_code != 200:
                print(f"❌ Request failed: {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
            
            # Parse SSE response
            final_data = self.parse_sse_response(response.text)
            
            if not final_data:
                print("❌ No final response received")
                return {"error": "No final response"}
            
            # Extract metadata
            metadata = final_data.get('metadata', {})
            token_usage = metadata.get('token_usage', {})
            
            # Display results
            print(f"\n📊 Summary:")
            print(f"  Intent: {metadata.get('intent', 'unknown')}")
            print(f"  Confidence: {metadata.get('confidence', 0):.2f}")
            print(f"  Processing Time: {duration:.0f}ms")
            
            if metadata.get('service') == 'bot-chain-clarification':
                print(f"  ⚠️  Clarification requested - query was ambiguous")
            
            if token_usage:
                total_tokens = token_usage.get('total_tokens', 0)
                total_cost = token_usage.get('estimated_cost_usd', 0)
                
                print(f"  Total Tokens: {total_tokens}")
                print(f"  Total Cost: ${total_cost:.6f}")
                
                self.total_tokens += total_tokens
                self.total_cost += total_cost
                
                # Display bot breakdown
                if 'bot_breakdown' in token_usage:
                    self.print_bot_token_usage(token_usage['bot_breakdown'], scenario['expected_bots'])
                
                # Warnings for expensive operations
                if total_cost > 0.01:
                    print(f"\n⚠️  WARNING: High cost query! ${total_cost:.4f}")
                if 'EVALUATOR' in token_usage.get('bot_breakdown', {}):
                    eval_cost = token_usage['bot_breakdown']['EVALUATOR']['cost_usd']
                    print(f"⚠️  EVALUATOR used GPT-4: ${eval_cost:.4f}")
                if 'RANKER' in token_usage.get('bot_breakdown', {}):
                    ranker_cost = token_usage['bot_breakdown']['RANKER']['cost_usd']
                    print(f"⚠️  RANKER used GPT-4: ${ranker_cost:.4f}")
            else:
                print("  ❌ No token usage data")
            
            result = {
                "scenario": scenario['name'],
                "tokens": token_usage.get('total_tokens', 0),
                "cost": token_usage.get('estimated_cost_usd', 0),
                "intent": metadata.get('intent'),
                "duration_ms": duration,
                "bot_breakdown": token_usage.get('bot_breakdown', {})
            }
            self.results.append(result)
            return result
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return {"error": str(e)}

    def print_summary_report(self):
        """Print summary report of all tests"""
        print(f"\n{'='*60}")
        print("📈 SUMMARY REPORT")
        print('='*60)
        
        # Overall costs
        print(f"\n💰 Total Cost Analysis:")
        print(f"  Total Queries: {len(self.results)}")
        print(f"  Total Tokens: {self.total_tokens}")
        print(f"  Total Cost: ${self.total_cost:.6f}")
        print(f"  Avg Cost/Query: ${self.total_cost/len(self.results):.6f}" if self.results else "  Avg Cost/Query: N/A")
        
        # Cost by bot
        print(f"\n🤖 Cost by Bot:")
        sorted_bots = sorted(self.bot_totals.items(), key=lambda x: x[1]['cost'], reverse=True)
        for bot_name, totals in sorted_bots:
            percentage = (totals['cost'] / self.total_cost * 100) if self.total_cost > 0 else 0
            print(f"  {bot_name:<15} {totals['tokens']:>6} tokens  ${totals['cost']:.6f} ({percentage:.1f}%)")
        
        # Most expensive queries
        print(f"\n💸 Most Expensive Queries:")
        sorted_results = sorted(self.results, key=lambda x: x['cost'], reverse=True)[:3]
        for i, result in enumerate(sorted_results, 1):
            print(f"  {i}. {result['scenario']}: ${result['cost']:.6f}")
        
        # Optimization insights
        print(f"\n💡 Optimization Insights:")
        
        # Check REWRITE usage
        if 'REWRITE' in self.bot_totals:
            rewrite_percentage = (self.bot_totals['REWRITE']['cost'] / self.total_cost * 100) if self.total_cost > 0 else 0
            print(f"  • REWRITE is {rewrite_percentage:.0f}% of total cost")
            if rewrite_percentage > 50:
                print(f"    → Consider shorter prompts in REWRITE bot")
        
        # Check expensive bots
        if 'EVALUATOR' in self.bot_totals:
            print(f"  • EVALUATOR (GPT-4) used: ${self.bot_totals['EVALUATOR']['cost']:.4f}")
            print(f"    → Use EVAL queries sparingly")
        
        if 'RANKER' in self.bot_totals:
            print(f"  • RANKER (GPT-4) used: ${self.bot_totals['RANKER']['cost']:.4f}")
            print(f"    → Consider SKIP_RANKER for simple queries")
        
        # Check SQL Gen
        sqlgen_in_results = any('SQLGEN' in r.get('bot_breakdown', {}) for r in self.results)
        if sqlgen_in_results:
            sqlgen_with_tokens = sum(1 for r in self.results 
                                    if r.get('bot_breakdown', {}).get('SQLGEN', {}).get('tokens', 0) > 0)
            template_usage = len(self.results) - sqlgen_with_tokens
            print(f"  • SQL Gen template usage: {template_usage}/{len(self.results)} queries")
            if sqlgen_with_tokens > 0:
                print(f"    → Add more SQL templates to reduce GPT usage")

def main():
    """Main test runner"""
    print("\n🚀 Comprehensive Token Usage Test - All Bots")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    runner = TokenTestRunner()
    
    # Check health first
    if not runner.check_health():
        print("\n⚠️  Please make sure the bot chain is running:")
        print("   cd /path/to/project && docker-compose up -d")
        return
    
    print("\n⚠️  Note: This test includes EVAL queries which use GPT-4 and are expensive!")
    print("   Running only essential tests to minimize costs.")
    
    # Run tests
    for scenario in TEST_SCENARIOS:
        runner.test_scenario(scenario)
        time.sleep(2)  # Wait between queries to avoid rate limiting
    
    # Print summary
    runner.print_summary_report()
    
    print("\n✅ Test completed!")
    
    # Final warnings
    if runner.total_cost > 0.05:
        print(f"\n⚠️  ATTENTION: Total test cost was ${runner.total_cost:.4f}")
        print("   Consider reducing EVAL and complex queries in production")

if __name__ == "__main__":
    main()
