#!/bin/bash

# Quick Token Usage Test Script
# Tests a simple query and displays token usage

echo "🚀 Testing Token Usage Reporting..."
echo "=================================="
echo ""

# Test query
QUERY="3 החלטות בנושא חינוך"
SESSION_ID="test-tokens-$(date +%s)"

echo "📝 Query: $QUERY"
echo "🆔 Session: $SESSION_ID"
echo ""

# Make the API call and capture response
echo "🔄 Sending request..."
RESPONSE=$(curl -s -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"$QUERY\", \"sessionId\": \"$SESSION_ID\"}")

# Extract the final response
FINAL_DATA=$(echo "$RESPONSE" | grep "data: " | tail -1 | sed 's/data: //')

# Check if we got a response
if [ -z "$FINAL_DATA" ]; then
  echo "❌ No response received"
  echo "Raw response:"
  echo "$RESPONSE"
  exit 1
fi

# Extract and display token usage using jq
echo ""
echo "📊 Token Usage Report:"
echo "====================="

# Check if token_usage exists
if echo "$FINAL_DATA" | jq -e '.metadata.token_usage' > /dev/null 2>&1; then
  echo "✅ Token usage found!"
  echo ""
  
  # Display summary
  echo "Summary:"
  echo "$FINAL_DATA" | jq -r '.metadata.token_usage | 
    "  Total Tokens: \(.total_tokens)
  Prompt Tokens: \(.prompt_tokens)
  Completion Tokens: \(.completion_tokens)
  Estimated Cost: $\(.estimated_cost_usd)"'
  
  echo ""
  echo "Bot Breakdown:"
  echo "$FINAL_DATA" | jq -r '.metadata.token_usage.bot_breakdown | 
    to_entries | 
    sort_by(.value.tokens) | 
    reverse | 
    .[] | 
    "  \(.key): \(.value.tokens) tokens ($\(.value.cost_usd))"'
    
  # Also show metadata
  echo ""
  echo "Query Metadata:"
  echo "$FINAL_DATA" | jq -r '.metadata | 
    "  Intent: \(.intent)
  Confidence: \(.confidence)
  Processing Time: \(.processing_time_ms)ms
  Service: \(.service)"'
    
else
  echo "❌ No token usage in response!"
  echo ""
  echo "Response metadata:"
  echo "$FINAL_DATA" | jq '.metadata'
fi

echo ""
echo "✅ Test completed!"
