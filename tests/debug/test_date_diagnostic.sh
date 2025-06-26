#!/bin/bash

# Date Normalizer Diagnostic Test
API_URL="http://localhost:8002/api/process-query"

echo "======================================"
echo "Date Normalizer Diagnostic Test"
echo "======================================"

# Function to analyze response
analyze_response() {
    local test_name="$1"
    local query="$2"
    local expected_date="$3"
    
    echo -e "\n🔍 Test: $test_name"
    echo "   Query: \"$query\""
    echo "   Expected normalized date: $expected_date"
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" 2>/dev/null)
    
    # Extract all relevant info
    success=$(echo "$response" | jq -r '.success' 2>/dev/null)
    sql=$(echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null)
    template_used=$(echo "$response" | jq -r '.metadata.template_used // "null"' 2>/dev/null)
    confidence=$(echo "$response" | jq -r '.metadata.confidence // "null"' 2>/dev/null)
    error=$(echo "$response" | jq -r '.error // "null"' 2>/dev/null)
    params=$(echo "$response" | jq -r '.metadata.params // "[]"' 2>/dev/null)
    
    echo "   Success: $success"
    echo "   Template: $template_used"
    echo "   Confidence: $confidence"
    
    if [ "$success" = "true" ]; then
        # Check if SQL contains date parameter
        if echo "$sql" | grep -q "decision_date >= \$"; then
            echo "   ✅ Date filter found in SQL"
            # Show the actual parameter values
            echo "   Parameters: $params"
            
            # Check if the normalized date is in params
            if echo "$params" | grep -q "$expected_date"; then
                echo "   ✅ Expected date found in parameters!"
            else
                echo "   ❌ Expected date NOT found in parameters"
            fi
        else
            echo "   ❌ No date filter in SQL"
        fi
        
        # Show first 150 chars of SQL
        echo "   SQL: $(echo "$sql" | head -c 150)..."
    else
        echo "   ❌ Query failed"
        echo "   Error: $error"
    fi
    
    echo "   ---"
}

# Test 1: Basic date formats
echo "=== Testing Basic Date Formats ==="
analyze_response "DD/MM/YYYY with מאז" "החלטות מאז 15/03/2023 בנושא חינוך" "2023-03-15"
analyze_response "DD.MM.YYYY with מאז" "החלטות מאז 1.1.2023 בנושא בריאות" "2023-01-01"
analyze_response "DD-MM-YYYY with מאז" "החלטות מאז 15-03-2023 בנושא תחבורה" "2023-03-15"

# Test 2: Date formats with different contexts
echo -e "\n=== Testing Different Contexts ==="
analyze_response "החל מ- with date" "החלטות החל מ-1.1.2023" "2023-01-01"
analyze_response "מ- with date" "החלטות מ-15/03/2023" "2023-03-15"
analyze_response "Date with ה-" "החלטות מאז ה-1.1.2023" "2023-01-01"

# Test 3: Template that should match
echo -e "\n=== Testing Known Template Match ==="
analyze_response "Template DECISIONS_SINCE_DATE_BY_TOPIC" \
    "תמצא לי את כל ההחלטות מאז ה-1.1.2023 שעוסקות בחינוך" \
    "2023-01-01"

# Test 4: Check if date normalizer is being called at all
echo -e "\n=== Direct Date Format Test ==="
analyze_response "YYYY-MM-DD format" "החלטות מאז 2023-03-15" "2023-03-15"
analyze_response "Just year" "החלטות מאז 2023" "2023-01-01"

# Test 5: Debug what the system sees
echo -e "\n=== Debug Query Processing ==="
echo "Testing simple date query to see how it's processed:"
simple_response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"query": "15/03/2023"}' 2>/dev/null)

echo "Response for just '15/03/2023':"
echo "$simple_response" | jq '.' 2>/dev/null | head -20

echo "======================================"
echo "Summary:"
echo "If dates are not being normalized, check:"
echo "1. Is normalizeQuery() being called?"
echo "2. Are the regex patterns in normalizeQuery() correct?"
echo "3. Is the normalizeDateString() function working?"
echo "======================================"
