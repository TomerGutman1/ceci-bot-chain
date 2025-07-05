#!/bin/bash
# Integration test script for Intent Recognizer replacement

echo "==================================="
echo "Intent Recognizer Integration Test"
echo "==================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test configuration
BACKEND_URL="http://localhost:5001"
INTENT_BOT_URL="http://localhost:8011"

# Function to check service health
check_health() {
    local service_name=$1
    local health_url=$2
    
    echo -n "Checking $service_name health... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$health_url")
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED (HTTP $response)${NC}"
        return 1
    fi
}

# Function to test intent detection
test_intent() {
    local test_name=$1
    local query=$2
    local expected_intent=$3
    
    echo ""
    echo "Test: $test_name"
    echo "Query: \"$query\""
    
    # Call intent bot directly
    response=$(curl -s -X POST "$INTENT_BOT_URL/intent" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"$query\", \"conv_id\": \"test-$$\"}")
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to call intent bot${NC}"
        return 1
    fi
    
    # Extract intent_type from response
    intent_type=$(echo "$response" | grep -o '"intent_type":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$intent_type" = "$expected_intent" ]; then
        echo -e "${GREEN}✓ Intent detected correctly: $intent_type${NC}"
        
        # Extract some entities
        government=$(echo "$response" | grep -o '"government_number":[0-9]*' | cut -d':' -f2)
        topic=$(echo "$response" | grep -o '"topic":"[^"]*"' | cut -d'"' -f4)
        
        [ -n "$government" ] && echo "  - Government: $government"
        [ -n "$topic" ] && echo "  - Topic: $topic"
        
        return 0
    else
        echo -e "${RED}✗ Expected $expected_intent, got $intent_type${NC}"
        echo "Full response: $response"
        return 1
    fi
}

# Function to test full bot chain
test_bot_chain() {
    local test_name=$1
    local query=$2
    
    echo ""
    echo -e "${YELLOW}Testing full bot chain:${NC} $test_name"
    echo "Query: \"$query\""
    
    # Call bot chain through backend
    response=$(curl -s -X POST "$BACKEND_URL/api/chat/test-bot-chain" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\", \"sessionId\": \"test-$$\"}")
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to call bot chain${NC}"
        return 1
    fi
    
    # Check if response contains success
    if echo "$response" | grep -q '"success":true'; then
        echo -e "${GREEN}✓ Bot chain processed successfully${NC}"
        
        # Extract metadata
        intent=$(echo "$response" | grep -o '"intent":"[^"]*"' | cut -d'"' -f4)
        confidence=$(echo "$response" | grep -o '"confidence":[0-9.]*' | cut -d':' -f2)
        
        [ -n "$intent" ] && echo "  - Intent: $intent"
        [ -n "$confidence" ] && echo "  - Confidence: $confidence"
        
        return 0
    else
        echo -e "${RED}✗ Bot chain processing failed${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Main test sequence
echo "Starting integration tests..."
echo ""

# Check services health
echo "=== Health Checks ==="
all_healthy=true

check_health "Backend" "$BACKEND_URL/api/chat/health" || all_healthy=false
check_health "Intent Recognizer" "$INTENT_BOT_URL/health" || all_healthy=false

if [ "$all_healthy" = false ]; then
    echo ""
    echo -e "${RED}Some services are not healthy. Please ensure all services are running.${NC}"
    exit 1
fi

# Test intent detection directly
echo ""
echo "=== Direct Intent Detection Tests ==="
test_intent "Simple Query" "החלטות ממשלה 37" "QUERY"
test_intent "Statistical Query" "כמה החלטות יש בנושא חינוך?" "STATISTICAL"  
test_intent "Eval Query" "נתח את החלטה 2948" "EVAL"
test_intent "Topic Search" "החלטות בנושא בריאות" "QUERY"
test_intent "Limited Results" "3 החלטות אחרונות" "QUERY"

# Test full bot chain integration
echo ""
echo "=== Full Bot Chain Integration Tests ==="
test_bot_chain "Simple Search" "החלטות ממשלה 37 בנושא חינוך"
test_bot_chain "Statistical Query" "כמה החלטות התקבלו השנה?"
test_bot_chain "Recent Decisions" "5 החלטות אחרונות"

echo ""
echo "==================================="
echo "Integration test completed"
echo "==================================="
