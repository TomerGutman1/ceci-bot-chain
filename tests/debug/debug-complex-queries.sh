#!/bin/bash
# debug-complex-queries.sh - בדיקת שאילתות מורכבות (ממשלה + נושא)

echo "========================================="
echo "🔍 בדיקה: שאילתות מורכבות ממשלה + נושא"
echo "========================================="

# צבעים
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# URL בסיס
BASE_URL="http://localhost:8002/api"

echo -e "\n${YELLOW}1. בדיקת SQL ישיר - החלטות ביטחון בממשלה 37:${NC}"
sql_query='SELECT COUNT(*) as count FROM israeli_government_decisions WHERE (government_number = '\''37'\'' OR government_number = '\''37.0'\'') AND tags_policy_area ILIKE '\''%ביטחון%'\'''
echo "SQL: $sql_query"
curl -s -X POST "$BASE_URL/execute-sql" \
    -H "Content-Type: application/json" \
    -d "{\"sql\": \"$sql_query\"}" | jq '.'

echo -e "\n${YELLOW}2. בדיקת process-query - כמה החלטות בנושא ביטחון קיבלה ממשלה 37?${NC}"
curl -s -X POST "$BASE_URL/process-query" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "כמה החלטות בנושא ביטחון קיבלה ממשלה 37?"
    }' | jq '.'

echo -e "\n${YELLOW}3. בדיקת הטמפלייט שמזוהה:${NC}"
curl -s -X POST "$BASE_URL/process-query" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "כמה החלטות בנושא ביטחון קיבלה ממשלה 37?",
        "debug": true
    }' | jq '.'

echo -e "\n${YELLOW}4. בדיקת שאילתות דומות:${NC}"
queries=(
    "כמה החלטות בנושא חינוך החליטה ממשלה מס 37"
    "כמה החלטות בנושא בריאות קיבלה ממשלה 37"
    "כמה החלטות ממשלה 37 בנושא כלכלה"
)

for query in "${queries[@]}"; do
    echo -e "\n${GREEN}Query: $query${NC}"
    curl -s -X POST "$BASE_URL/process-query" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" | jq '.response'
done
