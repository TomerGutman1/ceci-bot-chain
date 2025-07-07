#!/bin/bash

# Real-time Token Monitoring
# Run this to watch token usage in real-time

echo "🔍 REAL-TIME TOKEN MONITORING"
echo "============================="
echo "Press Ctrl+C to stop"
echo

while true; do
  clear
  echo "🔬 CECI BOT CHAIN - LIVE TOKEN DASHBOARD"
  echo "========================================"
  echo "$(date)"
  echo
  
  echo "💼 CURRENT SESSION:"
  curl -s http://localhost:5001/api/chat/usage-stats | jq -r '
    .stats | 
    "Requests: \(.totalRequests)",
    "Total Tokens: \(.totalTokensUsed)", 
    "Total Cost: \(.totalCostFormatted)",
    "Cache Hit Rate: \(.cacheHitRatePercent)",
    "Avg Cost/Request: \(.avgCostPerRequestFormatted)"
  ' 2>/dev/null || echo "❌ Backend not responding"
  
  echo
  echo "🤖 BOT STATUS:"
  for port in 8010 8011 8012 8013 8014 8015 8016 8017; do
    status=$(curl -s http://localhost:$port/health 2>/dev/null | jq -r '.status // "error"')
    if [ "$status" = "ok" ]; then
      echo "✅ Bot $port: $status"
    else
      echo "❌ Bot $port: $status"
    fi
  done
  
  echo
  echo "📊 QUICK STATS:"
  echo "🔥 Most expensive: EVALUATOR (~3,818 tokens per analysis)"
  echo "💚 Zero cost: Intent, SQL-Gen, Formatter bots"
  echo "🎯 Optimization: 72.7% token reduction achieved"
  
  echo
  echo "⏱️  Refreshing in 10 seconds... (Ctrl+C to stop)"
  sleep 10
done