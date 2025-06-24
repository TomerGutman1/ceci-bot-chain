#!/bin/bash

echo "===================================================="
echo "🧪 Testing New Query Types - SQL Engine Direct"
echo "===================================================="

# Function to test a query
test_query() {
    local query="$1"
    local test_name="$2"
    
    echo ""
    echo "📝 Testing: $test_name"
    echo "Query: \"$query\""
    
    # Make API request directly to SQL Engine
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

# Test 1: Decisions by Committee
echo "1️⃣ === TESTING DECISIONS BY COMMITTEE ==="
test_query "החלטות ועדת השרים לענייני חקיקה ב-2023" "Committee decisions in 2023"
test_query "החלטות של ועדת הכספים" "Finance committee decisions"

# Test 2: Count by Operativity
echo ""
echo "2️⃣ === TESTING COUNT BY OPERATIVITY ==="
test_query "כמה החלטות דקלרטיביות היו ב-2024?" "Declarative decisions 2024"
test_query "כמה החלטות אופרטיביות?" "Operative decisions count"

# Test 3: Decisions by Location
echo ""
echo "3️⃣ === TESTING DECISIONS BY LOCATION ==="
test_query "החלטות על ירושלים שהתקבלו מאז 2020" "Jerusalem decisions since 2020"
test_query "החלטות לגבי תל אביב מ-2022" "Tel Aviv decisions from 2022"

# Test 4: Monthly Trend
echo ""
echo "4️⃣ === TESTING MONTHLY TREND ==="
test_query "כמה החלטות היו בכל חודש ב-2023?" "Monthly trend 2023"

# Test 5: PM + Topic
echo ""
echo "5️⃣ === TESTING PM + TOPIC ==="
test_query "מה עשה נתניהו בנושא חינוך?" "Netanyahu education decisions"
test_query "מה עשה נתניהו בנושא ביטחון?" "Netanyahu security decisions"

# Test 6: Recent Decisions
echo ""
echo "6️⃣ === TESTING RECENT DECISIONS ==="
test_query "החלטות מה-7 הימים האחרונים" "Decisions last 7 days"
test_query "החלטות מ-30 הימים האחרונים" "Decisions last 30 days"

# Test 7: Compare Topics
echo ""
echo "7️⃣ === TESTING COMPARE TOPICS ==="
test_query "כמה החלטות חינוך לעומת בריאות ב-2024?" "Education vs Health 2024"

# Test 8: Top Committees
echo ""
echo "8️⃣ === TESTING TOP COMMITTEES ==="
test_query "3 הוועדות שהנפיקו הכי הרבה החלטות" "Top 3 committees"

# Test 9: Content Search with Date Range
echo ""
echo "9️⃣ === TESTING CONTENT SEARCH WITH DATE RANGE ==="
test_query "'קורונה' בין 2020-2021" "Corona between 2020-2021"
test_query "'תקציב' בין 2023-2024" "Budget between 2023-2024"

echo ""
echo "===================================================="
echo "🏁 Tests completed!"
echo "===================================================="
