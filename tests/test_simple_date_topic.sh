#!/bin/bash

# Simple test for our new date+topic queries
# Check if they work through backend

API_URL="http://localhost:8080/api/chat"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo "Testing Date + Topic Queries"
echo "============================"

test_query() {
    local query="$1"
    echo -e "\n${YELLOW}Query:${NC} $query"
    
    # Get response
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$query\", \"sessionId\": \"test\"}" \
        --no-buffer 2>/dev/null)
    
    # Check if we got any response
    if [ -z "$response" ]; then
        echo -e "${RED}✗ No response${NC}"
        return
    fi
    
    # Look for the count in Hebrew
    if echo "$response" | grep -q "נמצאו.*החלטות"; then
        count=$(echo "$response" | grep -o 'נמצאו [0-9]* החלטות' | grep -o '[0-9]*' | head -1)
        if [ "$count" -gt 0 ]; then
            echo -e "${GREEN}✓ Found $count decisions${NC}"
        else
            echo -e "${RED}✗ Found 0 decisions${NC}"
        fi
    else
        # Try English pattern
        if echo "$response" | grep -q "Found.*decisions"; then
            count=$(echo "$response" | grep -o 'Found [0-9]* decisions' | grep -o '[0-9]*' | head -1)
            echo -e "${GREEN}✓ Found $count decisions${NC}"
        else
            echo -e "${RED}✗ Could not parse response${NC}"
            # Show first 200 chars to debug
            echo "Response preview: $(echo "$response" | head -c 200)..."
        fi
    fi
}

# Test queries
test_query "תמצא לי את כל ההחלטות מאז ה-1.1.2023 שעוסקות בחינוך"
test_query "החלטות מאז 2022 בנושא בריאות"
test_query "החלטות משנת 2023 שעוסקות בתחבורה"
test_query "תמצא החלטות שעוסקות בחינוך"

echo -e "\n============================"
echo "Done"
