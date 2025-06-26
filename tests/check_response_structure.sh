#!/bin/bash

# Quick debug to see actual response structure
API_URL="http://localhost:8002/api/process-query"

echo "=== Testing actual response structure ==="
echo ""

# Test a simple query
query="כמה החלטות"
echo "Query: $query"
echo ""

response=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$query\"}" 2>/dev/null)

echo "Full response:"
echo "$response" | jq '.' 2>/dev/null | head -50
echo ""
echo "Metadata structure:"
echo "$response" | jq '.metadata' 2>/dev/null | head -30
echo ""
echo "Success field:"
echo "$response" | jq '.success' 2>/dev/null
echo ""
echo "Data field:"
echo "$response" | jq '.data' 2>/dev/null | head -10