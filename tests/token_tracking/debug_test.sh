#!/bin/bash

# Debug Token Usage Test
# Tests the API and shows raw response

echo "🔍 Debug Token Usage Test"
echo "========================"
echo ""

# First check health
echo "1️⃣ Checking API health..."
curl -s http://localhost:5001/api/chat/health | jq '.' || echo "❌ Health check failed"

echo ""
echo "2️⃣ Sending test query..."
echo ""

# Make the request and save raw response
RESPONSE=$(curl -s -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "החלטות בנושא חינוך", "sessionId": "debug-test"}' \
  2>&1)

echo "📄 Raw response:"
echo "================"
echo "$RESPONSE" | head -20
echo ""

# Try to extract data lines
echo "📊 Extracting data lines:"
echo "========================"
echo "$RESPONSE" | grep "^data: " | head -5

echo ""
echo "📋 Extracting final response:"
echo "============================"
FINAL=$(echo "$RESPONSE" | grep "^data: " | grep '"final":true' | sed 's/^data: //')

if [ -z "$FINAL" ]; then
  echo "❌ No final response found"
  echo ""
  echo "All data lines:"
  echo "$RESPONSE" | grep "^data: "
else
  echo "✅ Found final response"
  echo ""
  echo "Pretty printed:"
  echo "$FINAL" | jq '.' 2>/dev/null || echo "$FINAL"
  
  echo ""
  echo "Checking metadata:"
  echo "$FINAL" | jq '.metadata' 2>/dev/null || echo "No metadata found"
  
  echo ""
  echo "Checking token_usage:"
  echo "$FINAL" | jq '.metadata.token_usage' 2>/dev/null || echo "No token_usage found"
fi
