#!/bin/bash

# Production API endpoint
API_URL="https://ceci-ai.ceci.org.il/api/chat"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test a query
test_query() {
    local query="$1"
    local test_name="$2"
    local conv_id="$3"
    
    echo -e "\n${YELLOW}Testing: $test_name${NC}"
    echo "Query: $query"
    echo "Conversation ID: $conv_id"
    echo "---"
    
    # Make the request and capture the response
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"message\": \"$query\",
            \"conversationId\": \"$conv_id\"
        }" \
        --max-time 60)
    
    # Check if we got a response
    if [ -z "$response" ]; then
        echo -e "${RED}❌ No response received (timeout or error)${NC}"
        return
    fi
    
    # Extract key information from the response
    if echo "$response" | grep -q '"type":"response"'; then
        # Extract content
        content=$(echo "$response" | grep -o '"content":"[^"]*' | head -1 | sed 's/"content":"//g' | sed 's/\\n/ /g')
        
        # Extract metadata
        intent=$(echo "$response" | grep -o '"intent":"[^"]*' | head -1 | sed 's/"intent":"//g')
        processing_time=$(echo "$response" | grep -o '"processing_time_ms":[0-9]*' | head -1 | sed 's/"processing_time_ms"://g')
        
        # Check if it's a count query
        if echo "$response" | grep -q '"count_only":true'; then
            query_type="COUNT"
        else
            query_type="LIST"
        fi
        
        echo -e "${GREEN}✅ Response received${NC}"
        echo "Intent: $intent"
        echo "Query Type: $query_type"
        echo "Processing Time: ${processing_time}ms"
        echo "Content Preview: ${content:0:200}..."
        
        # Check for specific issues
        if echo "$content" | grep -q "נמצאו 1 החלטות" && [ "$query_type" = "COUNT" ]; then
            echo -e "${RED}⚠️  Issue: Count query returning '1 החלטות'${NC}"
        fi
        
        if echo "$content" | grep -q "לא נמצאו"; then
            echo -e "${YELLOW}⚠️  No results found${NC}"
        fi
    else
        echo -e "${RED}❌ Invalid response format${NC}"
        echo "Raw response: ${response:0:200}..."
    fi
}

# Main test execution
echo "========================================="
echo "Testing All Example Queries on Production"
echo "API: $API_URL"
echo "Time: $(date)"
echo "========================================="

# Test 1: Basic search query
test_query "החלטות בנושא חינוך ממשלה 37" "Basic Search - Education Gov 37" "test-basic-001"
sleep 2

# Test 2: Count query
test_query "כמה החלטות בנושא ביטחון קיבלה ממשלה 37" "Count Query - Security Gov 37" "test-count-001"
sleep 2

# Test 3: Specific decision
test_query "החלטה 2989" "Specific Decision 2989" "test-specific-001"
sleep 2

# Test 4: Recent decisions
test_query "הראה החלטות אחרונות בנושא סביבה" "Recent Environment Decisions" "test-recent-001"
sleep 2

# Test 5: Ministry search
test_query "החלטות של משרד החינוך" "Ministry of Education Decisions" "test-ministry-001"
sleep 2

# Test 6: Date range query
test_query "החלטות בנושא בריאות משנת 2023" "Health Decisions from 2023" "test-date-001"
sleep 2

# Test 7: Operational decisions
test_query "החלטות אופרטיביות בנושא תחבורה" "Operational Transport Decisions" "test-operational-001"
sleep 2

# Test 8: Analysis query
test_query "נתח את החלטה 1000 של ממשלה 37" "Analyze Decision 1000 Gov 37" "test-analysis-001"
sleep 2

# Test 9: Comparison query  
test_query "השווה בין ממשלה 36 לממשלה 37 בנושא כלכלה" "Compare Gov 36 vs 37 Economy" "test-compare-001"
sleep 2

# Test 10: Multi-topic search
test_query "החלטות בנושא חינוך וביטחון" "Multi-topic Education & Security" "test-multi-001"

echo -e "\n========================================="
echo "Test Summary Complete"
echo "========================================="