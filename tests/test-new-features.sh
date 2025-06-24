#!/bin/bash

echo "===================================================="
echo "🧪 Testing New Features"
echo "===================================================="

# Function to test a query
test_query() {
    local query="$1"
    local test_name="$2"
    
    echo ""
    echo "📝 Testing: $test_name"
    echo "Query: \"$query\""
    
    # Make API request
    response=$(curl -s -X POST http://localhost:8002/api/process-query \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    # Extract success and row count
    success=$(echo "$response" | grep -o '"success":[^,}]*' | grep -o '[^:]*$')
    
    if [[ "$success" == "true" ]]; then
        # Extract row_count from metadata
        row_count=$(echo "$response" | grep -o '"row_count":[0-9]*' | grep -o '[0-9]*$')
        # Also check if it's a count query
        count=$(echo "$response" | grep -o '"count":[0-9]*' | grep -o '[0-9]*$' | head -1)
        
        if [[ ! -z "$count" ]]; then
            echo "✅ SUCCESS - Count: $count"
        elif [[ ! -z "$row_count" ]]; then
            echo "✅ SUCCESS - Rows returned: $row_count"
        else
            echo "✅ SUCCESS"
        fi
    else
        # Extract error message
        error=$(echo "$response" | grep -o '"message":"[^"]*"' | sed 's/"message":"//;s/"$//')
        echo "❌ FAILED - Error: $error"
    fi
}

# Test specific number of decisions
echo "1️⃣ === TESTING SPECIFIC NUMBER OF DECISIONS ==="
test_query "הבא 20 החלטות" "Request 20 decisions"
test_query "תן לי 50 החלטות אחרונות" "Request 50 recent decisions"
test_query "הצג 15 החלטות" "Display 15 decisions"

# Test count by topic and year
echo ""
echo "2️⃣ === TESTING COUNT BY TOPIC AND YEAR ==="
test_query "כמה החלטות בנושא רפואה היו ב2022?" "Medical decisions in 2022"
test_query "כמה החלטות בנושא חינוך היו ב2021?" "Education decisions in 2021"

# Test contextual year query
echo ""
echo "3️⃣ === TESTING CONTEXTUAL YEAR QUERY ==="
test_query "כמה החלטות בנושא תחבורה היו ב2022?" "Transport decisions in 2022"
test_query "וב2021?" "And in 2021? (contextual)"

# Test date range with topic
echo ""
echo "4️⃣ === TESTING DATE RANGE WITH TOPIC ==="
test_query "כמה החלטות בנושא רפואה היו מפברואר 2000 עד מרץ 2010?" "Medical decisions Feb 2000 - Mar 2010"
test_query "כמה החלטות בנושא חינוך היו מפברואר 2000 עד מרץ 2010?" "Education decisions Feb 2000 - Mar 2010"

echo ""
echo "===================================================="
echo "🏁 Tests completed!"
echo "===================================================="
