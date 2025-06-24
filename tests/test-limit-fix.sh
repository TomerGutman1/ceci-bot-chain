#!/bin/bash

# Test script to verify LIMIT fixes
# Tests statistical queries that should return ALL results

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "🔍 Testing LIMIT Fix for Statistical Queries"
echo "=========================================="
echo ""

# SQL Engine endpoint
SQL_ENGINE_URL="http://localhost:8002"

# Function to test a query and count results
test_query() {
    local query="$1"
    local description="$2"
    
    echo -e "\n${BLUE}Testing: ${description}${NC}"
    echo "Query: \"$query\""
    
    # Send request to SQL Engine
    response=$(curl -s -X POST "$SQL_ENGINE_URL/api/process-query" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    # Extract row count and check if it's exactly 50 or 100
    if [ -n "$response" ]; then
        # First try row_count field directly
        count=$(echo "$response" | jq '.row_count' 2>/dev/null)
        
        # If not found, try metadata.row_count
        if [ "$count" = "null" ] || [ -z "$count" ]; then
            count=$(echo "$response" | jq '.metadata.row_count' 2>/dev/null)
        fi
        
        # If still not found, try counting data array
        if [ "$count" = "null" ] || [ -z "$count" ]; then
            count=$(echo "$response" | jq '.data | length' 2>/dev/null)
        fi
        
        # Last resort - try formatted response
        if [ "$count" = "null" ] || [ -z "$count" ]; then
            count=$(echo "$response" | jq -r '.formatted' 2>/dev/null | grep -oE "נמצאו [0-9]+ החלטות" | grep -oE "[0-9]+" | head -1)
        fi
        
        if [ -n "$count" ]; then
            echo "Results count: $count"
            
            # Check for suspicious limits
            if [ "$count" = "50" ]; then
                echo -e "${RED}❌ EXACTLY 50 RESULTS - STILL LIMITED!${NC}"
            elif [ "$count" = "100" ]; then
                echo -e "${RED}❌ EXACTLY 100 RESULTS - STILL LIMITED!${NC}"
            elif [ "$count" = "0" ]; then
                echo -e "${YELLOW}⚠️  WARNING: Zero results - might be an error${NC}"
            else
                echo -e "${GREEN}✓ Result count: $count (not a round limit)${NC}"
            fi
        else
            echo -e "${RED}❌ Could not extract result count${NC}"
        fi
    else
        echo -e "${RED}❌ No response${NC}"
    fi
}

echo -e "${YELLOW}=== 1. PM + TOPIC QUERIES (Previously limited to 50) ===${NC}"
test_query "מה עשה נתניהו בנושא חינוך?" "Netanyahu education decisions"
test_query "מה עשה נתניהו בנושא ביטחון?" "Netanyahu security decisions"
test_query "מה עשתה גולדה בנושא כלכלה?" "Golda economy decisions"
test_query "מה עשה בנט בנושא בריאות?" "Bennett health decisions"

echo -e "\n${YELLOW}=== 2. CONTENT SEARCH WITH DATES (Previously limited to 50) ===${NC}"
test_query "'קורונה' בין 2020-2021" "Corona between 2020-2021"
test_query "'תקציב' בין 2023-2024" "Budget between 2023-2024"
test_query "'חינוך' בין 2022-2023" "Education between 2022-2023"

echo -e "\n${YELLOW}=== 3. LOCATION QUERIES (Previously limited to 100) ===${NC}"
test_query "החלטות על ירושלים שהתקבלו מאז 2020" "Jerusalem decisions since 2020"
test_query "החלטות לגבי תל אביב מ-2022" "Tel Aviv decisions from 2022"

echo -e "\n${YELLOW}=== 4. COMMITTEE QUERIES (Previously limited to 50) ===${NC}"
test_query "החלטות ועדת השרים לענייני חקיקה ב-2023" "Legislation committee 2023"
test_query "החלטות של ועדת הכספים" "Finance committee all time"

echo -e "\n${YELLOW}=== 5. CONTROL GROUP (Should have varying counts) ===${NC}"
test_query "הבא 20 החלטות" "Explicitly requesting 20"
test_query "הבא 75 החלטות" "Explicitly requesting 75"
test_query "כמה החלטות יש בנושא חינוך?" "Count query (should be one number)"

echo -e "\n${YELLOW}=========================================="
echo "📊 SUMMARY"
echo "==========================================${NC}"
echo ""
echo "If you see many results with exactly 50 or 100,"
echo "the LIMIT issue is still present."
echo ""
echo "Expected behavior:"
echo "- Statistical queries should return ALL matching results"
echo "- Only display queries should have reasonable limits"
echo "- Count queries should return actual counts, not limited samples"

# Test NGINX routing fix
echo -e "\n${YELLOW}=== TESTING NGINX ROUTING FIX ===${NC}"
echo "Testing /api/health endpoint through different ports..."
echo ""

# Test direct backend
echo -n "Backend direct (5173): "
curl -s http://localhost:5173/api/health | jq -r '.status' 2>/dev/null || echo "FAILED"

# Test through NGINX HTTP
echo -n "NGINX HTTP (80): "
curl -s http://localhost/api/health | jq -r '.status' 2>/dev/null || echo "FAILED"

# Test through NGINX HTTPS
echo -n "NGINX HTTPS (443): "
curl -sk https://localhost/api/health | jq -r '.status' 2>/dev/null || echo "FAILED"

echo -e "\n${GREEN}✅ Test complete!${NC}"
