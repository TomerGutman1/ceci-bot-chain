#!/bin/bash
# apply-fixes.sh - החלת התיקונים

echo "========================================="
echo "🔧 החלת תיקונים ל-SQL Engine"
echo "========================================="

# צבעים
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# גיבוי הקובץ הקיים
echo -e "${YELLOW}1. יוצר גיבוי של queryTemplates.ts${NC}"
cp ../../sql-engine/src/services/queryTemplates.ts ../../sql-engine/src/services/queryTemplates.backup_$(date +%Y%m%d_%H%M%S).ts

# החלפת הקובץ
echo -e "${YELLOW}2. מחליף את queryTemplates.ts עם הגרסה המתוקנת${NC}"
cp ../../sql-engine/src/services/queryTemplates_fixed.ts ../../sql-engine/src/services/queryTemplates.ts

echo -e "${GREEN}✅ התיקון הוחל בהצלחה!${NC}"
echo ""
echo "השינויים העיקריים:"
echo "1. הוספת template חדש COUNT_BY_GOVERNMENT עם priority 15"
echo "2. הוספת templates ל-X_DECISIONS_BY_TOPIC ו-X_RECENT_DECISIONS"
echo "3. תיקון COUNT_BY_GOVERNMENT_AND_TOPIC עם priority 10"
echo "4. הוספת CONTEXTUAL_TOPIC לשאילתות המשך"
echo ""
echo -e "${YELLOW}הבא: הרץ מחדש את קונטיינר ה-SQL Engine${NC}"
echo "docker restart sql-engine"
