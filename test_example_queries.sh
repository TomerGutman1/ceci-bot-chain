#!/bin/bash

# Test all example queries from the sidebar

echo "Testing Example Queries from Sidebar"
echo "===================================="
echo ""

API_URL="https://ceci-ai.ceci.org.il/api/chat"

# Function to test a query
test_query() {
    local query="$1"
    local description="$2"
    local timestamp=$(date +%s)
    
    echo "🔍 Testing: $description"
    echo "   Query: $query"
    echo ""
    
    # Make the request and capture response
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"message\": \"$query\",
            \"conversationId\": \"test-example-$timestamp\"
        }" \
        --max-time 30)
    
    # Check if response is empty
    if [ -z "$response" ]; then
        echo "   ❌ ERROR: Empty response or timeout"
    else
        # Try to extract key information
        # Since response is SSE, we need to parse it differently
        if echo "$response" | grep -q "data: {"; then
            echo "   ✅ Response received (SSE format)"
            
            # Extract first few data chunks
            echo "$response" | grep "^data: " | head -3 | while read -r line; do
                echo "   $line"
            done
        else
            echo "   ⚠️  Unexpected response format"
            echo "   First 200 chars: ${response:0:200}"
        fi
    fi
    
    echo ""
    echo "---"
    echo ""
    sleep 2  # Rate limiting
}

# Test all queries
test_query "החלטות בנושא חינוך ממשלה 37" "חיפוש פשוט"
test_query "החלטה 2989" "החלטה ספציפית"
test_query "כמה החלטות בנושא ביטחון קיבלה ממשלה 37" "ספירת החלטות"
test_query "הראה החלטות אחרונות בנושא סביבה" "החלטות אחרונות"
test_query "החלטות של משרד החינוך" "החלטות לפי משרד"
test_query "החלטות ממשלה ב2024 בנושא בריאות" "חיפוש לפי תאריך"

echo ""
echo "Testing completed!"