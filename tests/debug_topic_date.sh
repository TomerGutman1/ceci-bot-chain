#!/bin/bash

# Debug specific failing test
API_URL="http://localhost:8002/api/process-query"

echo "=== Debugging Topic with Date Test ==="
echo ""

query="החלטות בנושא חינוך מ-2023"
echo "Query: $query"
echo ""

response=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$query\"}" 2>/dev/null)

echo "Full SQL:"
echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null
echo ""
echo "All params:"
echo "$response" | jq '.metadata.params' 2>/dev/null
echo ""
echo "Template used:"
echo "$response" | jq -r '.metadata.template_used' 2>/dev/null