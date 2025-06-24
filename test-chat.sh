#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# API endpoint
API_URL="http://localhost:5173/api/chat"
SESSION_ID="test-session-$(date +%s)"

echo -e "${YELLOW}🧪 CECI-AI Test Suite${NC}"
echo "========================="
echo "Session ID: $SESSION_ID"
echo ""

# Function to send message and display response
send_message() {
    local message="$1"
    local test_name="$2"
    
    echo -e "\n${GREEN}Test: $test_name${NC}"
    echo "Message: $message"
    echo -n "Response: "
    
    # Send request and capture response
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$message\", \"history\": [], \"sessionId\": \"$SESSION_ID\"}" \
        2>/dev/null)
    
    # Extract content from SSE response
    if [ $? -eq 0 ]; then
        # Parse SSE data and extract content
        content=$(echo "$response" | grep "^data:" | head -1 | sed 's/^data: //' | jq -r '.content' 2>/dev/null)
        
        if [ -n "$content" ] && [ "$content" != "null" ]; then
            echo -e "${GREEN}✓${NC} $content" | head -3
        else
            # Try to get error message
            error=$(echo "$response" | grep "^data:" | grep "error" | head -1 | sed 's/^data: //' | jq -r '.content' 2>/dev/null)
            if [ -n "$error" ] && [ "$error" != "null" ]; then
                echo -e "${RED}✗ Error:${NC} $error"
            else
                echo -e "${RED}✗ No valid response${NC}"
                echo "Raw response: $response" | head -100
            fi
        fi
    else
        echo -e "${RED}✗ Failed to connect${NC}"
    fi
    
    sleep 2 # Wait between requests
}

# Health check first
echo -e "${YELLOW}🔍 Health Check${NC}"
health=$(curl -s "http://localhost:5173/health")
echo "Backend Health: $health"
echo ""

echo -e "${YELLOW}🏃 Running Tests...${NC}"

# Test 1: General question about capabilities
send_message "מה אתה יודע לעשות?" "General Question - Capabilities"

# Test 2: Simple greeting
send_message "שלום" "Greeting"

# Test 3: Search for decision by topic
send_message "הבא לי החלטה בנושא חינוך" "Search by Topic"

# Test 4: Search for specific decision
send_message "החלטה מספר 660" "Specific Decision"

# Test 5: Statistical query
send_message "כמה החלטות יש משנת 2023?" "Statistical Query"

# Test 6: Spelling error correction
send_message "הבא ליי החלתה בנושה בריאות" "Spelling Error Test"

# Test 7: Unclear query
send_message "xyz123" "Unclear Query"

echo -e "\n${YELLOW}✅ Test Suite Complete${NC}"
echo "========================="

# Optional: Test PandasAI directly
echo -e "\n${YELLOW}🐼 Direct PandasAI Test${NC}"
pandas_health=$(curl -s "http://localhost:8001/")
echo "PandasAI Health: $pandas_health"
