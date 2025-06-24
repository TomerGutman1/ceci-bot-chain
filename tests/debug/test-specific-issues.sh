#!/bin/bash
# test-specific-issues.sh - בדיקת 3 הבעיות הספציפיות

echo "========================================="
echo "🔍 בדיקת בעיות ספציפיות ב-SQL Engine"
echo "========================================="

# צבעים
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# URL בסיס
BASE_URL="http://localhost:8002/api"

# פונקציה לשליחת שאילתה
send_query() {
    local query="$1"
    local description="$2"
    
    echo -e "\n${YELLOW}Testing: ${description}${NC}"
    echo "Query: $query"
    echo "-------------------"
    
    response=$(curl -s -X POST "$BASE_URL/process-query" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    echo "$response" | jq '.'
    
    # כתיבת התוצאה לקובץ
    echo -e "\n### ${description}" >> debug_results.md
    echo "Query: $query" >> debug_results.md
    echo '```json' >> debug_results.md
    echo "$response" | jq '.' >> debug_results.md
    echo '```' >> debug_results.md
}

# מחיקת קובץ תוצאות קודם
rm -f debug_results.md
echo "# תוצאות בדיקת בעיות SQL Engine" > debug_results.md
echo "תאריך: $(date)" >> debug_results.md

echo -e "\n${GREEN}=== בעיה 1: ממשלה 37 מחזיר רק החלטה אחת ===${NC}"
send_query "כמה החלטות קיבלה ממשלה 37?" "ספירת החלטות ממשלה 37"
send_query "סטטיסטיקה של ממשלה 37" "סטטיסטיקה ממשלה 37"

echo -e "\n${GREEN}=== בעיה 2: שאילתות מורכבות (ממשלה + נושא) ===${NC}"
send_query "כמה החלטות בנושא ביטחון קיבלה ממשלה 37?" "ממשלה 37 + ביטחון"
send_query "כמה החלטות בנושא חינוך קיבלה ממשלה 37?" "ממשלה 37 + חינוך"
send_query "כמה החלטות בנושא בריאות קיבלה ממשלה 37?" "ממשלה 37 + בריאות"

echo -e "\n${GREEN}=== בעיה 3: תצוגה מוגבלת ל-10 תוצאות ===${NC}"
send_query "ובנושא רפואה?" "שאילתת המשך - רפואה"
send_query "הבא 20 החלטות בנושא תחבורה" "20 החלטות תחבורה"
send_query "הבא 50 החלטות" "50 החלטות אחרונות"

echo -e "\n${GREEN}=== בדיקות נוספות לאבחון ===${NC}"
# בדיקה ישירה של ה-SQL
send_query "החלטות של ממשלה 37" "כל החלטות ממשלה 37"

echo -e "\n${YELLOW}בדיקת SQL ישיר דרך execute-sql:${NC}"
# בדיקת SQL ישיר לספירת ממשלה 37
sql_query="SELECT COUNT(*) as count FROM israeli_government_decisions WHERE government_number = '37' OR government_number = '37.0'"
echo "SQL: $sql_query"
curl -s -X POST "$BASE_URL/execute-sql" \
    -H "Content-Type: application/json" \
    -d "{\"sql\": \"$sql_query\"}" | jq '.'

echo -e "\n${GREEN}=== סיום בדיקות ===${NC}"
echo "התוצאות נשמרו ב-debug_results.md"
