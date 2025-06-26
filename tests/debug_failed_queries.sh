#!/bin/bash

# Debug specific queries to see what SQL is generated

SQL_ENGINE_URL="http://localhost:8002/api/process-query"

echo "Debugging Failed Queries - SQL Generation"
echo "========================================"

test_sql() {
    local query="$1"
    echo -e "\n🔍 Query: $query"
    
    response=$(curl -s -X POST "$SQL_ENGINE_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    # Extract SQL
    sql=$(echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null | head -c 300)
    echo "📝 SQL: $sql"
    
    # Extract parameters
    params=$(echo "$response" | jq -r '.formatted' 2>/dev/null | grep -o "Parameters:.*" | head -1)
    echo "🔧 $params"
    
    # Count results
    count=$(echo "$response" | grep -o '"decision_number"' | wc -l)
    echo "📊 Results: $count"
    
    # If 0 results, let's check why
    if [ "$count" -eq 0 ]; then
        echo "❌ No results - checking extracted parameters:"
        echo "$response" | jq '.metadata.extracted_params' 2>/dev/null || echo "No extracted_params"
    fi
}

# Test the failing queries
test_sql "החלטות מאז 2022 בנושא בריאות"
test_sql "החלטות משנת 2023 שעוסקות בתחבורה"

# Also test a working one for comparison
echo -e "\n--- For comparison, a working query: ---"
test_sql "תמצא לי את כל ההחלטות מאז ה-1.1.2023 שעוסקות בחינוך"

# Let's try different phrasings
echo -e "\n--- Testing alternative phrasings: ---"
test_sql "החלטות בנושא בריאות מ2022"
test_sql "תמצא החלטות מ2022 שעוסקות בבריאות"
