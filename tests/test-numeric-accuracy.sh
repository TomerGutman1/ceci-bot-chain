#!/bin/bash

# Test script for numeric accuracy in SQL Engine
# Ensures no numeric answers are limited to 50 or any arbitrary number

API_URL="https://localhost/api/chat"

echo "=================================================="
echo "🔢 Testing Numeric Accuracy - No LIMIT on COUNT Queries"
echo "=================================================="

# Function to test a query with SSE
test_sse_query() {
    local query="$1"
    local description="$2"
    local session_id="numeric-test-$(date +%s)-$$"
    
    echo ""
    echo "📝 Test: $description"
    echo "Query: \"$query\""
    echo "Session: $session_id"
    echo "---"
    
    # Make SSE request
    response=$(curl -s -k -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -H "Accept: text/event-stream" \
        -d "{\"message\": \"$query\", \"sessionId\": \"$session_id\"}" \
        --max-time 10)
    
    # Extract numeric result from response
    if echo "$response" | grep -q "data:"; then
        echo "✅ Response received"
        
        # Look for numeric results
        numeric_result=$(echo "$response" | grep -o '"data_count":[0-9]*' | cut -d: -f2 | head -1)
        if [ -n "$numeric_result" ]; then
            echo "📊 Numeric result: $numeric_result"
            
            # Check if it's exactly 50 (suspicious)
            if [ "$numeric_result" = "50" ]; then
                echo "⚠️  WARNING: Result is exactly 50 - might be limited!"
            fi
        fi
        
        # Extract formatted response
        formatted=$(echo "$response" | grep "^data:" | head -1 | sed 's/^data: //' | jq -r '.content' 2>/dev/null | head -20)
        if [ -n "$formatted" ]; then
            echo "Formatted response:"
            echo "$formatted"
        fi
        
        # Show SQL query if available
        sql_query=$(echo "$response" | grep -o '"sql_query":"[^"]*"' | cut -d'"' -f4 | head -1)
        if [ -n "$sql_query" ]; then
            echo ""
            echo "SQL Query used:"
            echo "$sql_query"
        fi
    else
        echo "❌ No valid response"
        echo "Raw response: $response"
    fi
    
    echo "=================================================="
}

# Test 1: Count all decisions (should be 24,716)
test_sse_query "כמה החלטות יש בסך הכל?" "Total decisions count"

# Test 2: Count by topic - Education
test_sse_query "כמה החלטות יש בנושא חינוך?" "Count education decisions"

# Test 3: Count by topic - Transportation  
test_sse_query "כמה החלטות יש בנושא תחבורה?" "Count transportation decisions"

# Test 4: Count by topic - Health
test_sse_query "כמה החלטות יש בנושא בריאות?" "Count health decisions"

# Test 5: Count by government
test_sse_query "כמה החלטות קיבלה ממשלה 37?" "Count government 37 decisions"

# Test 6: Count by year
test_sse_query "כמה החלטות היו ב-2023?" "Count 2023 decisions"

# Test 7: Count operativity
test_sse_query "כמה החלטות אופרטיביות?" "Count operative decisions"

# Test 8: Count declarative
test_sse_query "כמה החלטות דקלרטיביות?" "Count declarative decisions"

# Test 9: Government and topic count
test_sse_query "כמה החלטות בנושא ביטחון קיבלה ממשלה 37?" "Count security decisions by gov 37"

# Test 10: Date range count
test_sse_query "כמה החלטות בנושא חינוך היו בין 2020 ל-2023?" "Count education 2020-2023"

# Test 11: Committee count - check if returns all
test_sse_query "החלטות של ועדת השרים" "Committee decisions (should be all, not 50)"

# Test 12: Location count - check if returns all
test_sse_query "החלטות על תל אביב מאז 2020" "Tel Aviv decisions since 2020"

# Test 13: PM decisions - check if returns all
test_sse_query "החלטות של נתניהו" "Netanyahu decisions (should be all)"

# Test 14: Topic decisions - check if returns all  
test_sse_query "הבא החלטות בנושא כלכלה" "Economy decisions (should be all)"

# Test 15: Monthly trend
test_sse_query "כמה החלטות היו בכל חודש ב-2023?" "Monthly trend 2023"

echo ""
echo "🎯 === SUMMARY ==="
echo ""
echo "Check for the following:"
echo "1. No count should be exactly 50 (unless coincidence)"
echo "2. Total decisions should be 24,716"
echo "3. All numeric queries should return exact counts"
echo "4. Non-count queries should return all relevant results"
echo ""
echo "⚠️  If you see many results with exactly 50, there's still a LIMIT problem!"
