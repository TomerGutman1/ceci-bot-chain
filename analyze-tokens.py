#!/usr/bin/env python3
"""
Quick Token Analysis Script
Run this for detailed historical token breakdown
"""

import json
import os
from collections import defaultdict

def analyze_historical_tokens():
    print("🔬 DETAILED TOKEN ANALYSIS")
    print("=" * 50)
    
    # Find latest evaluation file
    test_files = [f for f in os.listdir('tests') if f.startswith('eval_test_results_') and f.endswith('.json')]
    if not test_files:
        print("❌ No evaluation files found")
        return
    
    latest_file = f"tests/{sorted(test_files)[-1]}"
    print(f"📁 Analyzing: {latest_file}")
    print()
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    # Per-bot analysis
    bot_stats = defaultdict(lambda: {'tokens': 0, 'calls': 0, 'cost': 0, 'model': 'unknown'})
    total_tokens = 0
    total_cost = 0
    
    print("📊 PER-BOT BREAKDOWN:")
    print("-" * 30)
    
    for test in data:
        print(f"\n🔍 Query: {test['query']}")
        
        for step_name, step_data in test['steps'].items():
            if isinstance(step_data, dict) and step_data.get('success') and 'result' in step_data:
                result = step_data['result']
                if 'token_usage' in result:
                    usage = result['token_usage']
                    bot_name = result.get('layer', step_name)
                    model = usage.get('model', 'unknown')
                    tokens = usage.get('total_tokens', 0)
                    
                    # Calculate cost
                    cost = 0
                    if model == 'gpt-4-turbo':
                        prompt_tokens = usage.get('prompt_tokens', 0)
                        completion_tokens = usage.get('completion_tokens', 0)
                        cost = (prompt_tokens * 0.01 + completion_tokens * 0.03) / 1000
                    elif model == 'gpt-3.5-turbo':
                        prompt_tokens = usage.get('prompt_tokens', 0)
                        completion_tokens = usage.get('completion_tokens', 0)
                        cost = (prompt_tokens * 0.0005 + completion_tokens * 0.0015) / 1000
                    
                    bot_stats[bot_name]['tokens'] += tokens
                    bot_stats[bot_name]['calls'] += 1
                    bot_stats[bot_name]['cost'] += cost
                    bot_stats[bot_name]['model'] = model
                    
                    total_tokens += tokens
                    total_cost += cost
                    
                    if tokens > 0:
                        print(f"   🤖 {bot_name}: {tokens} tokens (${cost:.4f}) [{model}]")
    
    print(f"\n📈 SUMMARY:")
    print("=" * 30)
    
    for bot_name, stats in bot_stats.items():
        if stats['tokens'] > 0:
            avg_tokens = stats['tokens'] / stats['calls'] if stats['calls'] > 0 else 0
            print(f"{bot_name:20} | {stats['tokens']:6} tokens | {stats['calls']:2} calls | ${stats['cost']:7.4f} | {avg_tokens:6.0f} avg | {stats['model']}")
    
    print("-" * 80)
    print(f"{'TOTAL':20} | {total_tokens:6} tokens | {len(data):2} tests | ${total_cost:7.4f}")
    
    print(f"\n🎯 COST ANALYSIS:")
    print("=" * 30)
    
    if total_tokens > 0:
        for bot_name, stats in bot_stats.items():
            if stats['tokens'] > 0:
                percentage = (stats['tokens'] / total_tokens) * 100
                print(f"{bot_name:20}: {percentage:5.1f}% of total tokens")
    
    print(f"\n💰 ROUTE COSTS:")
    print("=" * 30)
    print(f"Search queries (QUERY): $0.00 (0 tokens)")
    print(f"Analysis queries (EVAL): ${total_cost/len([t for t in data if any('eval_bot' in step for step in t['steps'])]):7.4f} avg per query")
    
    print(f"\n🔮 OPTIMIZATION IMPACT:")
    print("=" * 30)
    estimated_pre_optimization = len(data) * 7000  # 7 bots * 1000 tokens each
    current_tokens = total_tokens
    savings_percentage = ((estimated_pre_optimization - current_tokens) / estimated_pre_optimization * 100) if estimated_pre_optimization > 0 else 0
    
    print(f"Pre-optimization estimate: {estimated_pre_optimization:,} tokens")
    print(f"Current usage: {current_tokens:,} tokens")
    print(f"Savings: {savings_percentage:.1f}%")
    
    print(f"\n✅ ZERO-TOKEN OPTIMIZATIONS:")
    print("=" * 30)
    zero_token_bots = [bot for bot, stats in bot_stats.items() if stats['tokens'] == 0 and stats['calls'] > 0]
    if zero_token_bots:
        for bot in zero_token_bots:
            print(f"✅ {bot}: {bot_stats[bot]['calls']} calls, 0 tokens ({bot_stats[bot]['model']})")
    else:
        print("🔍 No zero-token bots found in this dataset")

if __name__ == "__main__":
    try:
        analyze_historical_tokens()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("💡 Run from project root directory")
    except Exception as e:
        print(f"❌ Error analyzing tokens: {e}")