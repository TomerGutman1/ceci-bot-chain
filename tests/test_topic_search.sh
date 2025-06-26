#!/bin/bash

# Test improved search
API_URL="http://localhost:8002/api/process-query"

echo "=== Testing Improved Topic Search ==="
echo ""

queries=(
    "החלטות בנושא החברה הערבית"
    "החלטות על מיעוטים"
    "מיעוטים"
    "ערבים"
    "דרוזים"
    "בדואים"
)

for query in "${queries[@]}"; do
    echo "Query: $query"
    
    response=$(curl -s -X POST "$API_URL" \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"$query\"}" 2>/dev/null)
    
    echo "Row count: $(echo "$response" | jq '.metadata.row_count')"
    echo "First result title: $(echo "$response" | jq -r '.data[0].decision_title // "N/A"' 2>/dev/null | head -c 80)..."
    echo "---"
done