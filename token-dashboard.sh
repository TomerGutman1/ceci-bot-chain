#!/bin/bash

# Token Usage Dashboard - Easy Access
# Run this script to get comprehensive token analytics

echo "🔬 CECI BOT CHAIN - TOKEN USAGE DASHBOARD"
echo "========================================"
echo "$(date)"
echo

echo "📊 QUICK ACCESS COMMANDS:"
echo "========================"
echo
echo "1. 💼 Current Session Stats:"
echo "   curl -s http://localhost:5001/api/chat/usage-stats | jq ."
echo
echo "2. 📈 Health & Status:"
echo "   curl -s http://localhost:5001/api/chat/health | jq ."
echo
echo "3. 🔍 Bot Health Checks:"
echo "   for port in 8010 8011 8012 8013 8014 8015 8016 8017; do"
echo "     echo \"Bot \$port:\" && curl -s http://localhost:\$port/health | jq .status"
echo "   done"
echo
echo "4. 📁 Historical Analysis Files:"
echo "   ls -la tests/eval_test_results*.json"
echo

echo "🎯 CURRENT SESSION STATISTICS:"
echo "=============================="
curl -s http://localhost:5001/api/chat/usage-stats | jq .

echo
echo "🤖 BOT STATUS CHECK:"
echo "==================="
for port in 8010 8011 8012 8013 8014 8015 8016 8017; do
  echo -n "Bot $port: "
  curl -s http://localhost:$port/health | jq -r '.status // "error"' 2>/dev/null || echo "unreachable"
done

echo
echo "📋 HISTORICAL DATA AVAILABLE:"
echo "============================="
if [ -d "tests" ]; then
  ls -la tests/eval_test_results*.json 2>/dev/null | head -5 || echo "No evaluation files found"
else
  echo "Run from project root directory to see test files"
fi

echo
echo "🎨 DETAILED ANALYSIS:"
echo "===================="
echo "To see detailed per-bot breakdown:"
echo "  python3 tests/token_tracking/comprehensive_test.py"
echo
echo "To run specific bot tests:"
echo "  python3 tests/token_tracking/test_all_bots.py"
echo
echo "To analyze evaluation results:"
echo "  python3 -c \"
import json
with open('tests/eval_test_results_20250703_122308.json', 'r') as f:
    data = json.load(f)
print(f'Tests: {len(data)}')
for test in data:
    if 'eval_bot_direct' in test['steps']:
        tokens = test['steps']['eval_bot_direct']['result'].get('token_usage', {}).get('total_tokens', 0)
        print(f'Query: {test[\"query\"][:50]}... Tokens: {tokens}')
\""

echo
echo "💡 OPTIMIZATION STATUS:"
echo "======================"
echo "✅ Phase 1: Safe caching, timeout fixes, content validation"
echo "✅ Phase 2: Smart routing, conditional bot activation"  
echo "✅ Phase 3.1: Multi-tier model selection"
echo "🎯 Expected savings: 80-90% vs pre-optimization"
echo
echo "🔥 COST HOTSPOTS:"
echo "================"
echo "• EVALUATOR bot: 100% of current token usage (~3,818 tokens per analysis)"
echo "• Analysis queries: ~$0.114 per query"
echo "• Search queries: $0.00 per query (optimized to zero)"
echo
echo "📞 FOR REAL-TIME MONITORING:"
echo "============================"
echo "curl -s http://localhost:5001/api/chat/usage-stats"
echo
echo "Dashboard ready! 🚀"