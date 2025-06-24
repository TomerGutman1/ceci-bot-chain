#!/bin/bash

# Comprehensive test script for unstable and failed queries
# This script tests all queries that have failed or shown instability
# Version: 2.3.2

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Test configuration
STABILITY_THRESHOLD=3  # Number of times a test should pass to be considered stable
MAX_RETRIES=5         # Maximum retries for flaky tests

# API endpoints
SQL_ENGINE_URL="http://localhost:8002/api/process-query"
BACKEND_URL="http://localhost:5173/api/chat/message"
NGINX_HTTPS_URL="https://localhost/api/chat/message"
NGINX_HTTP_URL="http://localhost/api/chat/message"

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
UNSTABLE_TESTS=0

# Arrays to track results
declare -A test_results
declare -A test_attempts
declare -A test_errors

echo "=================================================="
echo "🔍 Comprehensive Test Suite for Failed & Unstable Queries"
echo "=================================================="
echo "Stability threshold: $STABILITY_THRESHOLD consecutive passes"
echo "Max retries: $MAX_RETRIES attempts"
echo ""

# Function to test a query with retries
test_query_with_retry() {
    local endpoint="$1"
    local query="$2"
    local description="$3"
    local test_key="$4"
    
    echo -e "\n${BLUE}Testing: $description${NC}"
    echo "Query: \"$query\""
    echo "Endpoint: $endpoint"
    
    local passes=0
    local fails=0
    local last_error=""
    
    for attempt in $(seq 1 $MAX_RETRIES); do
        echo -n "Attempt $attempt/$MAX_RETRIES: "
        
        local response
        local success=false
        
        # Make request based on endpoint
        case "$endpoint" in
            "sql-direct")
                response=$(curl -s -X POST "$SQL_ENGINE_URL" \
                    -H "Content-Type: application/json" \
                    -d "{\"query\": \"$query\"}" 2>&1)
                
                if echo "$response" | jq -e '.success == true' >/dev/null 2>&1; then
                    success=true
                fi
                ;;
                
            "backend-direct")
                response=$(curl -s -X POST "$BACKEND_URL" \
                    -H "Content-Type: application/json" \
                    -d "{\"message\": \"$query\", \"sessionId\": \"test-stability\"}" 2>&1)
                
                if echo "$response" | jq -e '.intent == "data_query"' >/dev/null 2>&1; then
                    success=true
                fi
                ;;
                
            "nginx-https")
                response=$(curl -sk -X POST "$NGINX_HTTPS_URL" \
                    -H "Content-Type: application/json" \
                    -d "{\"message\": \"$query\", \"sessionId\": \"test-stability\"}" 2>&1)
                
                if echo "$response" | jq -e '.intent == "data_query"' >/dev/null 2>&1; then
                    success=true
                fi
                ;;
                
            "nginx-http")
                response=$(curl -s -X POST "$NGINX_HTTP_URL" \
                    -H "Content-Type: application/json" \
                    -d "{\"message\": \"$query\", \"sessionId\": \"test-stability\"}" 2>&1)
                
                if echo "$response" | jq -e '.intent == "data_query"' >/dev/null 2>&1; then
                    success=true
                fi
                ;;
        esac
        
        if [ "$success" = true ]; then
            echo -e "${GREEN}✓${NC}"
            ((passes++))
            
            # Check if we've reached stability threshold
            if [ $passes -ge $STABILITY_THRESHOLD ]; then
                echo -e "${GREEN}✅ STABLE - Passed $passes times consecutively${NC}"
                test_results["$test_key"]="STABLE"
                ((PASSED_TESTS++))
                return 0
            fi
        else
            echo -e "${RED}✗${NC}"
            ((fails++))
            
            # Extract error
            if echo "$response" | jq -e . >/dev/null 2>&1; then
                last_error=$(echo "$response" | jq -r '.error // .message // "Unknown error"' 2>&1)
            else
                last_error="Invalid response: ${response:0:100}..."
            fi
            
            # Reset consecutive passes counter
            passes=0
        fi
        
        # Small delay between attempts
        [ $attempt -lt $MAX_RETRIES ] && sleep 1
    done
    
    # Determine final status
    if [ $passes -gt 0 ]; then
        echo -e "${YELLOW}⚠️  UNSTABLE - Passed $passes/$MAX_RETRIES times${NC}"
        test_results["$test_key"]="UNSTABLE"
        test_errors["$test_key"]="$last_error"
        ((UNSTABLE_TESTS++))
    else
        echo -e "${RED}❌ FAILED - Never passed in $MAX_RETRIES attempts${NC}"
        echo "Last error: $last_error"
        test_results["$test_key"]="FAILED"
        test_errors["$test_key"]="$last_error"
        ((FAILED_TESTS++))
    fi
    
    ((TOTAL_TESTS++))
}

# Function to test across all endpoints
test_query_all_endpoints() {
    local query="$1"
    local description="$2"
    local test_base_key="$3"
    
    echo -e "\n${PURPLE}=== Testing: $description ===${NC}"
    
    # Test on each endpoint
    test_query_with_retry "sql-direct" "$query" "$description (SQL Direct)" "${test_base_key}_sql"
    test_query_with_retry "backend-direct" "$query" "$description (Backend)" "${test_base_key}_backend"
    test_query_with_retry "nginx-https" "$query" "$description (NGINX HTTPS)" "${test_base_key}_nginx_https"
    test_query_with_retry "nginx-http" "$query" "$description (NGINX HTTP)" "${test_base_key}_nginx_http"
}

# Check services health first
echo "🏥 Checking services health..."

# SQL Engine
if curl -s "$SQL_ENGINE_URL" -X POST -d '{"query":"test"}' | jq -e . >/dev/null 2>&1; then
    echo -e "SQL Engine: ${GREEN}✓ Running${NC}"
else
    echo -e "SQL Engine: ${RED}✗ Not responding${NC}"
fi

# Backend
if curl -s "$BACKEND_URL" -X POST -d '{"message":"test"}' | jq -e . >/dev/null 2>&1; then
    echo -e "Backend: ${GREEN}✓ Running${NC}"
else
    echo -e "Backend: ${RED}✗ Not responding${NC}"
fi

# NGINX
if curl -sk "$NGINX_HTTPS_URL" >/dev/null 2>&1; then
    echo -e "NGINX: ${GREEN}✓ Running${NC}"
else
    echo -e "NGINX: ${RED}✗ Not responding${NC}"
fi

echo ""
echo "=================================================="
echo "Starting comprehensive tests..."
echo "=================================================="

# 1. Previously failed queries from nginx/API tests
echo -e "\n${YELLOW}1️⃣ === QUERIES THAT FAILED IN NGINX/API TESTS ===${NC}"

test_query_all_endpoints \
    "החלטות הממשלה האחרונה בנושא תחבורה" \
    "Last government + topic" \
    "last_gov_topic"

test_query_all_endpoints \
    "החלטות מ-1.1.2024 עד 31.12.2024" \
    "Date range with dots" \
    "date_range_dots"

test_query_all_endpoints \
    "החלטות בנושא חינוך מהשנה האחרונה" \
    "Complex: topic + last year" \
    "complex_topic_year"

# 2. Queries that sometimes fail (based on logs)
echo -e "\n${YELLOW}2️⃣ === INTERMITTENTLY FAILING QUERIES ===${NC}"

test_query_all_endpoints \
    "החלטות לגבי תל אביב מ-2022" \
    "Tel Aviv decisions (failed once)" \
    "tel_aviv"

test_query_all_endpoints \
    "מה עשה נתניהו בנושא חינוך?" \
    "PM + Topic (parameter issues)" \
    "pm_topic"

test_query_all_endpoints \
    "'קורונה' בין 2020-2021" \
    "Content search with dates (text search)" \
    "content_search"

# 3. Edge cases that might be unstable
echo -e "\n${YELLOW}3️⃣ === EDGE CASES & POTENTIAL INSTABILITIES ===${NC}"

test_query_all_endpoints \
    "וב2021?" \
    "Contextual query" \
    "contextual"

test_query_all_endpoints \
    "החלטה 660" \
    "Decision without government" \
    "decision_no_gov"

test_query_all_endpoints \
    "החלטות על מאדים מ-2025" \
    "Empty result handling" \
    "empty_result"

test_query_all_endpoints \
    "החלטות בנושא טכהבורה" \
    "Typo handling (fuzzy search)" \
    "typo_fuzzy"

# 4. Complex aggregations that might timeout
echo -e "\n${YELLOW}4️⃣ === COMPLEX AGGREGATIONS ===${NC}"

test_query_all_endpoints \
    "כמה החלטות קיבלה כל ממשלה?" \
    "All governments statistics" \
    "all_gov_stats"

test_query_all_endpoints \
    "מה ההחלטות החשובות ביותר של 2024?" \
    "Important decisions (subjective)" \
    "important_decisions"

# 5. New query types that haven't been tested enough
echo -e "\n${YELLOW}5️⃣ === NEW QUERY TYPES (STABILITY CHECK) ===${NC}"

test_query_all_endpoints \
    "כמה החלטות בנושא רפואה היו מפברואר 2000 עד מרץ 2010?" \
    "Hebrew month in date range" \
    "hebrew_month_range"

test_query_all_endpoints \
    "5 הוועדות שהנפיקו הכי הרבה החלטות" \
    "Top N committees" \
    "top_committees"

test_query_all_endpoints \
    "החלטות מ-7 הימים האחרונים" \
    "Relative date (depends on current date)" \
    "relative_date"

# 6. Concurrent request stability
echo -e "\n${YELLOW}6️⃣ === CONCURRENT REQUEST STABILITY ===${NC}"

echo "Testing 5 concurrent requests..."
for i in {1..5}; do
    (
        response=$(curl -s -X POST "$SQL_ENGINE_URL" \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"כמה החלטות יש?\"}")
        
        if echo "$response" | jq -e '.success == true' >/dev/null 2>&1; then
            echo -e "Concurrent request $i: ${GREEN}✓${NC}"
        else
            echo -e "Concurrent request $i: ${RED}✗${NC}"
        fi
    ) &
done
wait

# Print summary
echo ""
echo "=================================================="
echo "📊 TEST SUMMARY"
echo "=================================================="
echo -e "Total tests run: ${TOTAL_TESTS}"
echo -e "Stable (passed $STABILITY_THRESHOLD+ times): ${GREEN}${PASSED_TESTS}${NC}"
echo -e "Unstable (passed some times): ${YELLOW}${UNSTABLE_TESTS}${NC}"
echo -e "Failed (never passed): ${RED}${FAILED_TESTS}${NC}"

# Detailed breakdown by endpoint
echo ""
echo "📈 Breakdown by endpoint:"
for key in "${!test_results[@]}"; do
    status="${test_results[$key]}"
    endpoint=$(echo "$key" | awk -F'_' '{print $NF}')
    query=$(echo "$key" | sed 's/_[^_]*$//')
    
    case "$status" in
        "STABLE")
            echo -e "  ${GREEN}✓${NC} $query ($endpoint)"
            ;;
        "UNSTABLE")
            echo -e "  ${YELLOW}⚠${NC}  $query ($endpoint) - ${test_errors[$key]}"
            ;;
        "FAILED")
            echo -e "  ${RED}✗${NC} $query ($endpoint) - ${test_errors[$key]}"
            ;;
    esac
done

# Generate recommendations
echo ""
echo "=================================================="
echo "🔧 RECOMMENDATIONS"
echo "=================================================="

if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}Critical issues found:${NC}"
    echo "1. Check nginx configuration - most failures are on nginx endpoints"
    echo "2. Verify backend-to-SQL-engine connectivity"
    echo "3. Check for missing SQL functions or templates"
fi

if [ $UNSTABLE_TESTS -gt 0 ]; then
    echo -e "\n${YELLOW}Stability issues found:${NC}"
    echo "1. Add retry logic to production code"
    echo "2. Implement connection pooling"
    echo "3. Add circuit breakers for external calls"
    echo "4. Consider caching for frequently accessed data"
fi

# Save results to file
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_FILE="test_results_${TIMESTAMP}.json"

echo ""
echo "💾 Saving detailed results to: $RESULTS_FILE"

# Generate JSON report
{
    echo "{"
    echo "  \"timestamp\": \"$(date -Iseconds)\","
    echo "  \"summary\": {"
    echo "    \"total\": $TOTAL_TESTS,"
    echo "    \"stable\": $PASSED_TESTS,"
    echo "    \"unstable\": $UNSTABLE_TESTS,"
    echo "    \"failed\": $FAILED_TESTS"
    echo "  },"
    echo "  \"results\": {"
    
    first=true
    for key in "${!test_results[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        
        echo -n "    \"$key\": {"
        echo -n "\"status\": \"${test_results[$key]}\""
        if [ -n "${test_errors[$key]}" ]; then
            echo -n ", \"error\": \"${test_errors[$key]//\"/\\\"}\""
        fi
        echo -n "}"
    done
    
    echo ""
    echo "  }"
    echo "}"
} > "$RESULTS_FILE"

echo ""
echo "✅ Test suite completed!"
echo ""

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ] && [ $UNSTABLE_TESTS -eq 0 ]; then
    echo -e "${GREEN}All queries are stable! 🎉${NC}"
    exit 0
else
    echo -e "${YELLOW}Some queries need attention${NC}"
    exit 1
fi
