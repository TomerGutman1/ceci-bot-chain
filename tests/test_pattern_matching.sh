#!/bin/bash

# Quick test to check if our patterns are being matched

echo "Testing pattern matching directly with SQL engine..."

SQL_ENGINE_URL="http://localhost:8002/api/process-query"

# Test a few queries and see what template is matched
test_pattern() {
    local query="$1"
    echo -e "\n🔍 Testing: $query"
    
    response=$(curl -s -X POST "$SQL_ENGINE_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    # Extract template used
    template=$(echo "$response" | grep -o '"template_used":"[^"]*"' | cut -d'"' -f4)
    
    # Extract SQL preview
    sql=$(echo "$response" | grep -o '"sql_query":"[^"]*"' | cut -d'"' -f4 | sed 's/\\n/ /g' | cut -c1-100)
    
    # Check success
    if echo "$response" | grep -q '"success":true'; then
        echo "✅ Success"
        echo "📋 Template: ${template:-'No template (GPT generated)'}"
        echo "🔧 SQL preview: $sql..."
        
        # Count results
        count=$(echo "$response" | grep -o '"decision_number"' | wc -l)
        echo "📊 Results: $count"
    else
        echo "❌ Failed"
        error=$(echo "$response" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
        echo "Error: $error"
    fi
}

echo "=== Testing our new patterns ==="

# Test patterns that should match DECISIONS_SINCE_DATE_BY_TOPIC
test_pattern "תמצא לי את כל ההחלטות מאז ה-1.1.2023 שעוסקות בחינוך"
test_pattern "החלטות מאז 15.6.2022 בנושא בריאות"
test_pattern "חפש החלטות החל מ-1/7/2021 שקשורות לתחבורה"

# Test patterns that should match DECISIONS_SINCE_YEAR_BY_TOPIC
test_pattern "תמצא החלטות מ2023 שעוסקות בחינוך"
test_pattern "החלטות משנת 2022 ואילך בנושא בריאות"

# Test patterns that should match TOPIC_SEARCH_COMPREHENSIVE
test_pattern "תמצא לי החלטות שעוסקות בחינוך"
test_pattern "חפש החלטות על תחבורה משנת 2023"

# Test existing pattern that we know works
echo -e "\n=== Testing existing patterns (should work) ==="
test_pattern "החלטות בנושא חינוך"
test_pattern "5 החלטות בנושא חינוך מ2023"
