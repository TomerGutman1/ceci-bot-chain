#!/bin/bash

# Debug single decision queries
# Check what's happening with "החלטה אחת" queries

SQL_ENGINE_URL="http://localhost:8002/api"

echo "Testing single decision query patterns..."
echo "========================================="

test_query() {
    local query="$1"
    echo -e "\nQuery: $query"
    echo "Response:"
    curl -s -X POST "$SQL_ENGINE_URL/process-query" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" | jq '.'
}

# Test different variations
test_query "החלטה אחת בנושא בריאות מ2024"
test_query "החלטה בנושא חינוך משנת 2023"
test_query "הבא החלטה אחת בנושא תחבורה מ2022"
test_query "תן לי החלטה בנושא ביטחון משנת 2021"

# Test what works
echo -e "\n\nCompare with working queries:"
echo "============================="
test_query "2 החלטות בנושא כלכלה מ2024"
test_query "הבא 1 החלטה בנושא בריאות מ2024"

# Test specific template
echo -e "\n\nDirect template test:"
echo "===================="
test_query "החלטה אחת בנושא בריאות מ2024"
