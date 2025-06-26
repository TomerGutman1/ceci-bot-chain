#!/bin/bash

# Debug version - Test script for "decisions since date + topic" queries
# Shows the actual response from the server

API_URL="http://localhost:8080/api/chat"

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Testing 'Since Date + Topic' Pattern - DEBUG MODE${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to test a query with debug info
test_query_debug() {
    local query="$1"
    local expected_desc="$2"
    
    echo -e "\n${YELLOW}Testing:${NC} $query"
    echo "Expected: $expected_desc"
    
    # Make the API call
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$query\", \"sessionId\": \"test-session\"}")
    
    # Show response structure (first 500 chars)
    echo -e "${MAGENTA}Response preview:${NC}"
    echo "$response" | head -c 500
    echo "..."
    
    # Check if response has error
    if echo "$response" | grep -q '"error"'; then
        error=$(echo "$response" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
        echo -e "${RED}Error found: $error${NC}"
    fi
    
    # Check if response has success=false
    if echo "$response" | grep -q '"success":false'; then
        echo -e "${RED}Success: false${NC}"
    fi
    
    # Check if response has data
    if echo "$response" | grep -q '"data"'; then
        echo -e "${GREEN}Data field found${NC}"
        # Count decisions
        count=$(echo "$response" | grep -o '"decision_number"' | wc -l)
        echo "Decision count: $count"
    else
        echo -e "${RED}No data field found${NC}"
    fi
    
    # Check what pattern was matched (if any)
    if echo "$response" | grep -q '"template_used"'; then
        template=$(echo "$response" | grep -o '"template_used":"[^"]*"' | cut -d'"' -f4)
        echo -e "${CYAN}Template used: $template${NC}"
    fi
    
    echo "---"
}

# Test just a few queries to debug
echo -e "\n${CYAN}=== Testing Basic Queries First ===${NC}"

# Test a simple query that should work
test_query_debug "החלטות בנושא חינוך" \
                 "Simple topic query (should work)"

# Test a year + topic query that works
test_query_debug "החלטות בנושא חינוך מ2023" \
                 "Topic + Year (existing pattern)"

# Test our new pattern
test_query_debug "תמצא לי את כל ההחלטות מאז ה-1.1.2023 שעוסקות בחינוך" \
                 "Since date + topic (new pattern)"

# Test another new pattern
test_query_debug "החלטות מ2023 שעוסקות בחינוך" \
                 "Since year + topic (new pattern)"

# Test comprehensive search
test_query_debug "תמצא לי החלטות שעוסקות בחינוך" \
                 "Comprehensive search (new pattern)"

echo -e "\n${BLUE}=== Debug Summary ===${NC}"
echo "Check the responses above to see:"
echo "1. Are we getting any response from the server?"
echo "2. Is there an error message?"
echo "3. Which template (if any) is being matched?"
echo "4. Is the data structure what we expect?"
