#!/bin/bash
# debug-government-37.sh - בדיקה ממוקדת לבעיה של ממשלה 37

echo "========================================="
echo "🔍 בדיקה ממוקדת: בעיית ממשלה 37"
echo "========================================="

# צבעים
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# URL בסיס
BASE_URL="http://localhost:8002/api"

echo -e "\n${YELLOW}1. בדיקת SQL ישיר - ספירת החלטות ממשלה 37:${NC}"
curl -s -X POST "$BASE_URL/execute-sql" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "SELECT COUNT(*) as count FROM israeli_government_decisions WHERE government_number = '\''37'\'' OR government_number = '\''37.0'\''"
    }' | jq '.'

echo -e "\n${YELLOW}2. בדיקת RPC Function - get_government_statistics:${NC}"
curl -s -X POST "$BASE_URL/execute-sql" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "SELECT * FROM get_government_statistics(37)"
    }' | jq '.'

echo -e "\n${YELLOW}3. בדיקת process-query - כמה החלטות קיבלה ממשלה 37:${NC}"
curl -s -X POST "$BASE_URL/process-query" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "כמה החלטות קיבלה ממשלה 37?"
    }' | jq '.'

echo -e "\n${YELLOW}4. בדיקת process-query - סטטיסטיקה של ממשלה 37:${NC}"
curl -s -X POST "$BASE_URL/process-query" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "סטטיסטיקה של ממשלה 37"
    }' | jq '.'

echo -e "\n${YELLOW}5. בדיקת SQL ישיר - דגימת החלטות ממשלה 37:${NC}"
curl -s -X POST "$BASE_URL/execute-sql" \
    -H "Content-Type: application/json" \
    -d '{
        "sql": "SELECT decision_number, government_number, decision_title FROM israeli_government_decisions WHERE government_number LIKE '\''37%'\'' LIMIT 5"
    }' | jq '.'
