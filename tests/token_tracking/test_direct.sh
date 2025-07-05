#!/bin/bash

# Test using the direct test endpoint

echo "🔍 Testing Bot Chain Direct Endpoint"
echo "===================================="
echo ""

# Test the direct endpoint
echo "📡 Calling /api/chat/test-bot-chain..."
echo ""

RESPONSE=$(curl -s -X POST http://localhost:5001/api/chat/test-bot-chain \
  -H "Content-Type: application/json" \
  -d '{
    "query": "3 החלטות בנושא חינוך",
    "sessionId": "test-direct",
    "preferences": {}
  }')

echo "📄 Raw Response:"
echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"

echo ""
echo "📊 Metadata:"
echo "$RESPONSE" | jq '.metadata' 2>/dev/null || echo "No metadata"

echo ""
echo "💰 Token Usage:"
echo "$RESPONSE" | jq '.metadata.token_usage' 2>/dev/null || echo "No token usage"

echo ""
echo "📈 Bot Breakdown:"
echo "$RESPONSE" | jq '.metadata.token_usage.bot_breakdown' 2>/dev/null || echo "No breakdown"

# Also try the health endpoint
echo ""
echo "🏥 Health Check:"
curl -s http://localhost:5001/api/chat/health | jq '.' 2>/dev/null
