#!/bin/bash

# Test to see what nlToSql returns
API_URL="http://localhost:8002/api/process-query"

echo "=== Testing different queries to see extracted params ==="
echo ""

test_query() {
    local query="$1"
    echo "Query: $query"
    
    response=$(curl -s -X POST "$API_URL" \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"$query\"}" 2>/dev/null)
    
    echo "Metadata params:"
    echo "$response" | jq '.metadata.params' 2>/dev/null
    
    echo "Template used:"
    echo "$response" | jq '.metadata.template_used' 2>/dev/null
    
    echo "---"
}

# Test various queries
test_query "החלטות מ-15/03/2023"
test_query "החלטות על נושא סביבה"
test_query "החלטות של ממשלה 36"
test_query "כמה החלטות"
test_query "5 החלטות"
test_query "שמכילות תקציב"