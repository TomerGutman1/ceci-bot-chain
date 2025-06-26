#!/bin/bash

# Debug test for date normalization issues

API_URL="http://localhost:8002/api/process-query"

echo "=================================="
echo "Date Normalization Debug Test"
echo "=================================="
echo ""

# Test queries that should normalize dates
test_queries=(
    "החלטות ממרץ 2023"
    "החלטות מאז 15/03/2023"
    "החלטות מאז 1.1.2023"
    "החלטות מאז 01-01-2023"
    "תמצא לי את כל ההחלטות מאז ה-1.1.2023 שעוסקות בחינוך"
)

for query in "${test_queries[@]}"; do
    echo "Testing: $query"
    echo "-------------------"
    
    # Make request and capture full response
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" 2>&1)
    
    # Extract metadata
    metadata=$(echo "$response" | jq -r '.metadata' 2>/dev/null)
    sql_query=$(echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null)
    success=$(echo "$response" | jq -r '.success' 2>/dev/null)
    error=$(echo "$response" | jq -r '.error' 2>/dev/null)
    
    echo "Success: $success"
    
    if [ "$success" = "true" ]; then
        echo "SQL Query:"
        echo "$sql_query" | head -10
        
        # Check for normalized dates
        if echo "$sql_query" | grep -E "20[0-9]{2}-[0-9]{2}-[0-9]{2}" > /dev/null; then
            echo "✅ Found normalized date format (YYYY-MM-DD)"
        else
            echo "❌ No normalized date found"
        fi
    else
        echo "Error: $error"
        echo "Full response:"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
    fi
    
    echo ""
    echo "=================================="
    echo ""
done

# Additional test to check template matching
echo "Template Matching Test:"
echo "====================="

test_template_query() {
    local query="$1"
    local expected="$2"
    
    echo "Query: $query"
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    template=$(echo "$response" | jq -r '.metadata.template_used' 2>/dev/null)
    
    if [ -n "$template" ] && [ "$template" != "null" ]; then
        echo "Template used: $template"
        if [ "$template" = "$expected" ]; then
            echo "✅ Correct template matched"
        else
            echo "⚠️  Different template than expected: $expected"
        fi
    else
        echo "❌ No template matched"
    fi
    echo ""
}

test_template_query "תמצא לי את כל ההחלטות מאז ה-1.1.2023 שעוסקות בחינוך" "DECISIONS_SINCE_DATE_BY_TOPIC"
test_template_query "החלטות ממרץ 2023" "DECISIONS_BY_MONTH" # This template might not exist
test_template_query "החלטה 660" "DECISION_BY_NUMBER_ANY_GOV"
