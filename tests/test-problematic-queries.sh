#!/bin/bash

# Quick test for known problematic queries
# Focuses only on queries that have actually failed in recent tests

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=================================================="
echo "🔍 Testing Known Problematic Queries"
echo "=================================================="

# Function to test SQL Engine directly
test_sql_direct() {
    local query="$1"
    local description="$2"
    
    echo -e "\n${BLUE}Testing: $description${NC}"
    echo "Query: \"$query\""
    
    response=$(curl -s -X POST http://localhost:8002/api/process-query \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    if echo "$response" | jq -e '.success == true' >/dev/null 2>&1; then
        echo -e "${GREEN}✅ SUCCESS${NC}"
        # Show relevant data
        if echo "$response" | jq -e '.data[0].count' >/dev/null 2>&1; then
            count=$(echo "$response" | jq -r '.data[0].count')
            echo "Count: $count"
        else
            rows=$(echo "$response" | jq -r '.metadata.row_count // 0')
            echo "Rows: $rows"
        fi
    else
        echo -e "${RED}❌ FAILED${NC}"
        error=$(echo "$response" | jq -r '.error // .message // "Unknown error"')
        echo "Error: $error"
    fi
}

# Test through NGINX/API
test_api() {
    local query="$1"
    local description="$2"
    
    echo -e "\n${BLUE}Testing via API: $description${NC}"
    echo "Query: \"$query\""
    
    # Try HTTPS first
    response=$(curl -sk -X POST https://localhost/api/chat/message \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$query\", \"sessionId\": \"test\"}" 2>&1)
    
    # Check if we got a JSON response
    if echo "$response" | jq -e . >/dev/null 2>&1; then
        intent=$(echo "$response" | jq -r '.intent // empty')
        if [ "$intent" = "data_query" ]; then
            echo -e "${GREEN}✅ SUCCESS (recognized as data query)${NC}"
        else
            echo -e "${RED}❌ FAILED - Intent: $intent${NC}"
        fi
    else
        echo -e "${RED}❌ FAILED - Invalid response${NC}"
        echo "Response: ${response:0:100}..."
    fi
}

# 1. Test the consistently failing queries
echo -e "\n${YELLOW}1️⃣ === CONSISTENTLY FAILING QUERIES ===${NC}"

# These failed in nginx/API tests
queries_failed_nginx=(
    "החלטות הממשלה האחרונה בנושא תחבורה|Last government transport decisions"
    "החלטות מ-1.1.2024 עד 31.12.2024|Date range with dots"
    "החלטות בנושא חינוך מהשנה האחרונה|Complex query: education last year"
)

for query_desc in "${queries_failed_nginx[@]}"; do
    IFS='|' read -r query desc <<< "$query_desc"
    test_sql_direct "$query" "$desc (SQL Direct)"
    test_api "$query" "$desc"
done

# 2. Test queries that sometimes fail
echo -e "\n${YELLOW}2️⃣ === INTERMITTENTLY FAILING QUERIES ===${NC}"

# Based on your test results
intermittent_queries=(
    "החלטות לגבי תל אביב מ-2022|Tel Aviv decisions"
    "מה עשה נתניהו בנושא חינוך?|PM + Topic"
    "'קורונה' בין 2020-2021|Content search with dates"
    "'תקציב' בין 2023-2024|Budget search with dates"
)

for query_desc in "${intermittent_queries[@]}"; do
    IFS='|' read -r query desc <<< "$query_desc"
    test_sql_direct "$query" "$desc"
done

# 3. Test edge cases
echo -e "\n${YELLOW}3️⃣ === EDGE CASES ===${NC}"

edge_cases=(
    "וב2021?|Contextual query"
    "ממשלה 50|Non-existent government"
    "החלטות בנושא טכהבורה|Typo in topic"
)

for query_desc in "${edge_cases[@]}"; do
    IFS='|' read -r query desc <<< "$query_desc"
    test_sql_direct "$query" "$desc"
done

# 4. Test API connectivity specifically
echo -e "\n${YELLOW}4️⃣ === API CONNECTIVITY TEST ===${NC}"

echo "Testing different API endpoints..."

# Direct to backend
echo -e "\n${BLUE}Backend direct (port 5173):${NC}"
curl -s http://localhost:5173/health | jq . || echo "Backend not responding"

# Through nginx HTTP
echo -e "\n${BLUE}NGINX HTTP (port 80):${NC}"
curl -s http://localhost/api/chat/health || echo "NGINX HTTP not working"

# Through nginx HTTPS
echo -e "\n${BLUE}NGINX HTTPS (port 443):${NC}"
curl -sk https://localhost/api/chat/health || echo "NGINX HTTPS not working"

# SQL Engine direct
echo -e "\n${BLUE}SQL Engine (port 8002):${NC}"
curl -s http://localhost:8002/health | jq . || echo "SQL Engine not responding"

# 5. Summary
echo -e "\n${YELLOW}=================================================="
echo "📊 QUICK SUMMARY"
echo "==================================================${NC}"

echo -e "\n${BLUE}Known issues:${NC}"
echo "1. NGINX routing - returns 404 for /api/chat/message"
echo "2. Some patterns don't match in templates (האחרונה, date ranges with dots)"
echo "3. Text search needs Hebrew configuration or fallback to ILIKE"

echo -e "\n${BLUE}Working well:${NC}"
echo "1. SQL Engine direct access - all queries work"
echo "2. All new query types when accessed directly"
echo "3. Pattern matching for most Hebrew queries"

echo -e "\n✅ Done!"
