#!/bin/bash

# Check what LIMIT is being applied

SQL_ENGINE_URL="http://localhost:8002/api/process-query"

echo "Checking LIMIT in SQL queries"
echo "============================="

test_sql() {
    local query="$1"
    echo -e "\n🔍 Query: $query"
    
    response=$(curl -s -X POST "$SQL_ENGINE_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    # Extract SQL and look for LIMIT
    sql=$(echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null)
    echo "📝 SQL:"
    echo "$sql" | grep -E "(LIMIT|limit)" --color=always || echo "(No LIMIT found)"
    
    # Count actual results
    count=$(echo "$response" | grep -o '"decision_number"' | wc -l)
    echo "📊 Actual results returned: $count"
}

# Test queries with "כל" (all)
test_sql "תמצא לי את כל ההחלטות מאז ה-1.1.2023 שעוסקות בחינוך"
test_sql "כל ההחלטות בנושא חינוך"
test_sql "הבא את כל ההחלטות משנת 2023"

# Compare with queries without "כל"
echo -e "\n--- Compare with queries WITHOUT 'כל' ---"
test_sql "החלטות מאז 2022 בנושא בריאות"
test_sql "החלטות בנושא חינוך"

# Test explicit number request
echo -e "\n--- Explicit number request ---"
test_sql "תן לי 50 החלטות בנושא חינוך"
test_sql "100 החלטות משנת 2023"
