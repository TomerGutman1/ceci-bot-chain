#!/bin/bash

# Date Parameter Debug Test
API_URL="http://localhost:8002/api/process-query"

echo "======================================"
echo "Date Parameter Debug Test"
echo "======================================"

# Function to check actual parameters
check_date_params() {
    local query="$1"
    local expected="$2"
    
    echo -e "\n🔍 Testing: \"$query\""
    echo "   Expected date: $expected"
    
    # Make request and save full response
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" 2>/dev/null)
    
    # Extract SQL and check for date parameter
    sql=$(echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null)
    
    if echo "$sql" | grep -q "decision_date >= \$1"; then
        echo "   ✅ SQL has date filter"
        
        # Let's execute a direct SQL query to debug
        direct_response=$(curl -s -X POST "$API_URL/execute-sql" \
            -H "Content-Type: application/json" \
            -d '{
                "sql": "SELECT $1::text as param1, $2::text as param2",
                "params": ["15/03/2023", "חינוך"]
            }' 2>/dev/null)
        
        echo "   Direct SQL test: $(echo "$direct_response" | jq -c '.data[0]' 2>/dev/null)"
        
        # Check result count to see if date filter is working
        count=$(echo "$response" | jq '.data | length' 2>/dev/null)
        echo "   Results count: $count"
        
        # Get first result date to see what dates we're getting
        if [ "$count" -gt 0 ]; then
            first_date=$(echo "$response" | jq -r '.data[0].decision_date' 2>/dev/null)
            echo "   First result date: $first_date"
        fi
    else
        echo "   ❌ No date filter in SQL"
    fi
}

# Test different date formats
echo "=== Testing Date Formats ==="
check_date_params "החלטות מאז 15/03/2023 בנושא חינוך" "2023-03-15"
check_date_params "החלטות מאז 1.1.2023 בנושא בריאות" "2023-01-01"
check_date_params "החלטות מאז 01/01/2023" "2023-01-01"

# Let's test if the date normalizer works at all
echo -e "\n=== Testing Date Normalizer Directly ==="
echo "Checking if backend is normalizing dates..."

# Test with a query that should definitely have a date
test_response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"query": "החלטות משנת 2023"}' 2>/dev/null)

year_sql=$(echo "$test_response" | jq -r '.metadata.sql_query' 2>/dev/null)
echo "Year query SQL: $(echo "$year_sql" | grep -o "EXTRACT.*2023" | head -1 || echo "No year filter found")"

# Let's check the actual template matching
echo -e "\n=== Checking Template DECISIONS_SINCE_DATE_BY_TOPIC ==="
template_query="תמצא לי את כל ההחלטות מאז ה-1.1.2023 שעוסקות בחינוך"
echo "Query: $template_query"

template_response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$template_query\"}" 2>/dev/null)

template_used=$(echo "$template_response" | jq -r '.metadata.template_used' 2>/dev/null)
echo "Template matched: $template_used"

if [ "$template_used" = "DECISIONS_SINCE_DATE_BY_TOPIC" ]; then
    echo "✅ Correct template matched!"
else
    echo "❌ Wrong template or no match"
fi

echo "======================================"
