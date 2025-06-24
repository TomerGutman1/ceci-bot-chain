#!/bin/bash

# SQL Query Engine - Quick Test Suite for Working Queries
# This script tests only queries that are known to work consistently
# Last verified: 22/06/2025

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Server URL
API_URL="https://localhost"

echo "=================================================="
echo "🚀 Testing SQL Query Engine - Working Queries Only"
echo "=================================================="

# Check if server is running
echo "🔍 Checking if server is running..."
if curl -sk -o /dev/null -w "%{http_code}" "$API_URL/api/chat/health" | grep -q "200"; then
    echo -e "${GREEN}✅ Server is running${NC}"
else
    echo -e "${RED}❌ Server is not running. Please start the server first.${NC}"
    exit 1
fi

# Function to test a query
test_query() {
    local query="$1"
    local description="$2"
    local expected_type="${3:-}"
    
    echo ""
    echo -e "${BLUE}📝 Test: $description${NC}"
    echo "Query: \"$query\""
    
    # Make API request
    local response=$(curl -sk -X POST "$API_URL/api/chat/test-sql" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    # Check if successful
    if echo "$response" | jq -e '.success' > /dev/null 2>&1; then
        local success=$(echo "$response" | jq -r '.success')
        
        if [ "$success" = "true" ]; then
            echo -e "${GREEN}✅ Success!${NC}"
            
            # Show type if available
            local type=$(echo "$response" | jq -r '.type // empty')
            if [ -n "$type" ]; then
                echo "Type: $type"
            fi
            
            # Show formatted response (first 100 chars)
            local formatted=$(echo "$response" | jq -r '.formatted // empty')
            if [ -n "$formatted" ]; then
                echo "Response preview: ${formatted:0:100}..."
            fi
        else
            echo -e "${RED}❌ Failed!${NC}"
            local error=$(echo "$response" | jq -r '.error // "Unknown error"')
            echo "Error: $error"
        fi
    else
        echo -e "${RED}❌ Invalid response format${NC}"
    fi
}

# Test categories with working queries only

echo ""
echo -e "${YELLOW}🔢 === BASIC COUNT QUERIES ===${NC}"
test_query "כמה החלטות יש בסך הכל?" "Total count"
test_query "כמה החלטות יש משנת 2023?" "Count by year 2023"
test_query "כמה החלטות התקבלו בשנת 2024?" "Count by year 2024"

echo ""
echo -e "${YELLOW}🎯 === SPECIFIC DECISION QUERIES ===${NC}"
test_query "החלטה 660 של ממשלה 35" "Specific decision 660/35"
test_query "החלטה 100 של ממשלה 37" "Specific decision 100/37"
test_query "החלטה 1" "Decision 1 (any government)"

echo ""
echo -e "${YELLOW}🏷️ === TOPIC-BASED QUERIES ===${NC}"
test_query "הבא לי החלטה בנושא תחבורה" "Single decision about transportation"
test_query "הבא לי החלטה בנושא חינוך" "Single decision about education"
test_query "הבא 5 החלטות בנושא ביטחון" "5 decisions about security"

echo ""
echo -e "${YELLOW}🏛️ === GOVERNMENT STATISTICS ===${NC}"
test_query "סטטיסטיקה של ממשלה 37" "Statistics for government 37"
test_query "סטטיסטיקה של ממשלה 36" "Statistics for government 36"

echo ""
echo -e "${YELLOW}🕐 === RECENT DECISIONS ===${NC}"
test_query "ההחלטות האחרונות" "Most recent decisions"
test_query "החלטות אחרונות" "Recent decisions (short)"

echo ""
echo -e "${YELLOW}🆕 === NEW COMPLEX COUNT QUERIES (Testing) ===${NC}"
test_query "כמה החלטות בנושא חינוך החליטה ממשלה מס 37" "Count by government 37 and education"
test_query "כמה החלטות בנושא חינוך עברו בין 2020 ל2022?" "Count education 2020-2022"

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 Quick test suite completed!${NC}"
echo "=================================================="

# Show summary of untested queries
echo ""
echo -e "${YELLOW}📊 === QUERIES THAT NEED NEW SQL FUNCTIONS ===${NC}"
echo "The following queries are not tested because they require SQL functions that haven't been deployed yet:"
echo ""
echo "1. Count by topic: \"כמה החלטות יש בנושא כלכלה?\""
echo "   - Needs: count_decisions_by_topic()"
echo ""
echo "2. Government + topic: \"החלטות מהממשלה הנוכחית בנושא חינוך\""
echo "   - Needs: get_decisions_by_government_and_topic()"
echo ""
echo "3. Date range: \"החלטות מ-1.1.2024 עד 31.12.2024\""
echo "   - Needs: get_decisions_by_date_range()"
echo ""
echo "4. Prime minister: \"החלטות של נתניהו\""
echo "   - Needs: get_decisions_by_prime_minister()"
echo ""
echo "5. Per government stats: \"כמה החלטות קיבלה כל ממשלה?\""
echo "   - Needs: count_decisions_per_government()"
echo ""
echo "6. Important decisions: \"מה ההחלטות החשובות ביותר של 2024?\""
echo "   - Needs: get_important_decisions_by_year()"
echo ""
echo "7. Content search: \"חפש קורונה\""
echo "   - Needs: search_decisions_hebrew()"
echo ""
echo -e "${BLUE}💡 To enable these queries, run the SQL functions from:${NC}"
echo "   server/db_load/sql_functions/additional_functions.sql"
