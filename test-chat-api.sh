#!/bin/bash

# CECI-AI Chat API Test Script
# Tests various types of queries to ensure the system works correctly

API_URL="https://localhost/api/chat"
SESSION_ID=$(uuidgen 2>/dev/null || echo "test-session-$(date +%s)")

echo "🧪 CECI-AI Chat API Test Suite"
echo "================================"
echo "Session ID: $SESSION_ID"
echo ""

# Function to send a chat message and parse response
send_message() {
    local message="$1"
    local test_name="$2"
    
    echo "📤 Test: $test_name"
    echo "   Message: \"$message\""
    echo -n "   Response: "
    
    # Send request and capture response
    response=$(curl -k -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$message\", \"history\": [], \"sessionId\": \"$SESSION_ID\"}" \
        --no-buffer 2>/dev/null)
    
    # Extract content from SSE stream
    content=$(echo "$response" | grep "^data: " | head -1 | sed 's/^data: //' | jq -r '.content // empty' 2>/dev/null)
    
    if [ -n "$content" ]; then
        # Truncate long responses
        if [ ${#content} -gt 150 ]; then
            echo "${content:0:150}..."
        else
            echo "$content"
        fi
        echo "   ✅ Success"
    else
        echo "❌ Failed to get response"
        echo "   Raw response: ${response:0:100}..."
    fi
    echo ""
    
    # Small delay between requests
    sleep 2
}

echo "🏃 Running Tests..."
echo ""

# Test 1: General question about system capabilities
send_message "מה אתה יודע לעשות?" "System Capabilities Question"

# Test 2: Greeting (should not go to PandasAI)
send_message "שלום" "Simple Greeting"

# Test 3: Specific decision request
send_message "הבא לי החלטה בנושא חינוך" "Topic Search - Education"

# Test 4: Decision with spelling errors
send_message "הבא ליי החלתה בנושה בריאות" "Spelling Error Correction"

# Test 5: Decision by number with government
send_message "החלטה 660 של ממשלה 35" "Specific Decision with Government"

# Test 6: Current government decisions
send_message "הבא לי החלטה מהממשלה הנוכחית בנושא תחבורה" "Current Government Query"

# Test 7: Statistical query
send_message "כמה החלטות יש משנת 2023?" "Statistical Query"

# Test 8: Unclear query
send_message "xyzabc" "Unclear Query"

echo ""
echo "✅ Test Suite Completed!"
echo ""

# Summary
echo "📊 Test Summary:"
echo "- Tested various query types: general, greetings, searches, statistics"
echo "- Tested spelling correction capabilities"
echo "- Tested government-specific queries"
echo "- Session ID: $SESSION_ID"
echo ""
echo "💡 Check the backend logs for detailed processing information:"
echo "   docker compose logs -f backend"
echo ""