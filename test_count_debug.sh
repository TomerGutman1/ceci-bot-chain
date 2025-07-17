#!/bin/bash

echo "Testing count query with debug..."

response=$(curl -s -X POST https://ceci-ai.ceci.org.il/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "כמה החלטות בנושא ביטחון קיבלה ממשלה 37",
    "conversationId": "count-debug-test"
  }')

echo "Raw response (first 500 chars):"
echo "${response:0:500}"

echo -e "\n\nExtracting data chunks..."
echo "$response" | grep "^data: " | head -5

echo -e "\n\nChecking backend logs..."
ssh root@178.62.39.248 "cd /root/CECI-W-BOTS && docker compose logs backend --tail 100 | grep -E 'count-debug-test|COUNT QUERY|count_only' | head -20"