#!/bin/bash

# Debug search for Arab society
API_URL="http://localhost:8002/api/process-query"

echo "=== Testing Arab Society Search ==="
echo ""

queries=(
    "החלטות בנושא החברה הערבית"
    "החלטות על מיעוטים"
    "החלטות בנושא מיעוטים ואוכלוסיות ייחודיות"
)

for query in "${queries[@]}"; do
    echo "Query: $query"
    echo "---"
    
    response=$(curl -s -X POST "$API_URL" \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"$query\"}" 2>/dev/null)
    
    echo "SQL Query:"
    echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null | head -5
    
    echo "Parameters:"
    echo "$response" | jq '.metadata.params' 2>/dev/null
    
    echo "Row count:"
    echo "$response" | jq '.metadata.row_count' 2>/dev/null
    
    echo "========================================="
    echo ""
done