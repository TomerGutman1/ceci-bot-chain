#!/bin/bash

# Date Normalizer Test V2 - Focus on parameter extraction
API_URL="http://localhost:8002/api/process-query"

echo "======================================"
echo "Date Normalizer Test V2"
echo "======================================"

# Function to test query
test_query() {
    local test_name="$1"
    local query="$2"
    local expected_date="$3"
    
    echo -e "\n🔍 Test: $test_name"
    echo "   Query: \"$query\""
    echo "   Expected date: $expected_date"
    
    # Make the request and save full response
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" 2>/dev/null)
    
    # Extract key fields
    success=$(echo "$response" | jq -r '.success' 2>/dev/null)
    
    if [ "$success" = "true" ]; then
        # Extract metadata fields
        sql_query=$(echo "$response" | jq -r '.metadata.sql_query // ""' 2>/dev/null)
        params=$(echo "$response" | jq -r '.metadata.params // []' 2>/dev/null)
        confidence=$(echo "$response" | jq -r '.metadata.confidence // 0' 2>/dev/null)
        
        echo "   ✅ Query succeeded"
        echo "   Confidence: $confidence"
        
        # Check if SQL has date filter
        if echo "$sql_query" | grep -q "decision_date >=" ; then
            echo "   ✅ Date filter found in SQL"
            
            # Extract first parameter
            first_param=$(echo "$params" | jq -r '.[0] // ""' 2>/dev/null)
            echo "   First parameter: $first_param"
            
            if [ "$first_param" = "$expected_date" ]; then
                echo "   ✅ DATE NORMALIZED CORRECTLY!"
            else
                echo "   ❌ Date not normalized correctly"
                echo "      Expected: $expected_date"
                echo "      Got: $first_param"
            fi
        else
            echo "   ❌ No date filter in SQL"
        fi
        
        # Show all params for debugging
        echo "   All parameters: $params"
    else
        error=$(echo "$response" | jq -r '.error // "Unknown error"' 2>/dev/null)
        echo "   ❌ Query failed: $error"
    fi
}

# Run tests
echo "=== Basic Date Formats ==="
test_query "DD/MM/YYYY" "החלטות מאז 15/03/2023 בנושא חינוך" "2023-03-15"
test_query "DD.MM.YYYY" "החלטות מאז 1.1.2023 בנושא בריאות" "2023-01-01"
test_query "DD-MM-YYYY" "החלטות מאז 15-03-2023 בנושא תחבורה" "2023-03-15"

echo -e "\n=== Different Contexts ==="
test_query "החל מ-" "החלטות החל מ-1.1.2023" "2023-01-01"
test_query "Just date" "החלטות מאז 15/03/2023" "2023-03-15"
test_query "Year only" "החלטות מאז 2023" "2023-01-01"

echo -e "\n=== Complex Queries ==="
test_query "Full template" "תמצא לי את כל ההחלטות מאז ה-1.1.2023 שעוסקות בחינוך" "2023-01-01"

echo -e "\n======================================"
echo "Summary: Check if dates are being properly normalized to YYYY-MM-DD format"
echo "======================================"
