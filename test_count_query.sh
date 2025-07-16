#!/bin/bash

echo "Testing count query..."
echo "====================="

# Make the request
response=$(curl -s -X POST https://ceci-ai.ceci.org.il/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "כמה החלטות בנושא ביטחון קיבלה ממשלה 37",
    "conversationId": "test-count-'$(date +%s)'"
  }')

echo "Response received:"
echo "$response" | jq '.'

# Extract key info
echo -e "\nKey information:"
echo "Number of results: $(echo "$response" | jq '.results | length')"
echo "First result title: $(echo "$response" | jq -r '.results[0].title // "N/A"')"
echo "Response message: $(echo "$response" | jq -r '.message // "N/A"')"