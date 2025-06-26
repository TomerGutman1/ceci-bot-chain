#!/bin/bash

# === Comprehensive Test Suite for All Improvements ===
# Tests fuzzy matching, confidence gates, and new templates

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# API endpoints
CHAT_API="http://localhost:8080/api/chat"
SQL_API="http://localhost:8002/api/process-query"

# Counters
total_tests=0
passed_tests=0
failed_tests=0

# === Header ===
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Comprehensive Test Suite - Version 2.4.6${NC}"
echo -e "${BLUE}================================================${NC}"
echo "Testing:"
echo "- Fuzzy Matching"
echo "- Date Normalization"
echo "- Confidence Gates"
echo "- New Templates"

# === Generic Test Function ===
test_query() {
    local query="$1"
    local expected_pattern="$2"
    local description="$3"
    local endpoint="${4:-$SQL_API}"
    
    ((total_tests++))
    
    echo -e "\n${YELLOW}Test $total_tests:${NC} $description"
    echo "Query: \"$query\""
    
    # Choose endpoint
    if [ "$endpoint" = "$CHAT_API" ]; then
        response=$(curl -s -X POST "$CHAT_API" \
            -H "Content-Type: application/json" \
            -d "{\"message\": \"$query\", \"sessionId\": \"test-comprehensive\"}" \
            --no-buffer 2>/dev/null)
        
        # Extract content from streaming response
        content=$(echo "$response" | grep '^data:' | tail -1 | sed 's/^data: //')
    else
        response=$(curl -s -X POST "$SQL_API" \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"$query\"}" 2>/dev/null)
        content="$response"
    fi
    
    # Check for expected pattern
    if echo "$content" | grep -q "$expected_pattern"; then
        echo -e "Result: ${GREEN}✓${NC} Found expected: $expected_pattern"
        ((passed_tests++))
    else
        echo -e "Result: ${RED}✗${NC} Did not find: $expected_pattern"
        echo "Response snippet: $(echo "$content" | head -c 300)..."
        ((failed_tests++))
    fi
}

# === Test Section 1: Fuzzy Matching ===
echo -e "\n${CYAN}=== Section 1: Fuzzy Matching Tests ===${NC}"

test_query \
    "החלטות בנושא איכות הסביבה" \
    "סביבה" \
    "Should fuzzy match 'איכות הסביבה' to 'סביבה'"

test_query \
    "החלטות בנושא מדע" \
    "מחקר\|השכלה גבוהה" \
    "Should fuzzy match 'מדע' to research/higher education"

test_query \
    "החלטות בנושא חנוך" \
    "חינוך" \
    "Should fuzzy match typo 'חנוך' to 'חינוך'"

# === Test Section 2: Date Normalization ===
echo -e "\n${CYAN}=== Section 2: Date Normalization Tests ===${NC}"

test_query \
    "החלטות מאז 15/03/2023" \
    "2023-03-15" \
    "Should normalize DD/MM/YYYY format"

test_query \
    "החלטות מאז 1.1.2023" \
    "2023-01-01" \
    "Should normalize D.M.YYYY format with padding"

test_query \
    "החלטות מאז מרץ 2023" \
    "2023-03" \
    "Should normalize Hebrew month format"

# === Test Section 3: Confidence Gates ===
echo -e "\n${CYAN}=== Section 3: Confidence Gate Tests ===${NC}"

test_query \
    "xyz123" \
    "לא ברור\|לא הבנתי\|unclear" \
    "Gibberish should trigger UNCLEAR" \
    "$CHAT_API"

test_query \
    "משהו לא ברור" \
    "נסה\|פרט\|guidance" \
    "Vague query should get guidance" \
    "$CHAT_API"

# === Test Section 4: New Templates ===
echo -e "\n${CYAN}=== Section 4: New Template Tests ===${NC}"

test_query \
    "כמה החלטות בנושא חינוך בשנת 2023" \
    "count.*WHERE.*tags_policy_area.*2023\|\"success\":true" \
    "COUNT_BY_TAG_AND_YEAR template"

test_query \
    "הבא החלטות של נתניהו בנושא ביטחון" \
    "prime_minister.*ILIKE.*נתניהו.*ביטחון\|\"success\":true" \
    "LIST_BY_PM_AND_TOPIC template"

test_query \
    "תמצא לי את כל ההחלטות מאז 1.1.2023 שעוסקות בחינוך" \
    "decision_date >= .*2023-01-01.*חינוך\|\"success\":true" \
    "DECISIONS_SINCE_DATE_BY_TOPIC template"

# === Test Section 5: Complex Queries ===
echo -e "\n${CYAN}=== Section 5: Complex Query Tests ===${NC}"

test_query \
    "החלטה אחת בנושא איכות הסביבה מ2023" \
    "סביבה.*2023.*LIMIT 1\|\"success\":true" \
    "Fuzzy match + year + single result"

test_query \
    "כמה החלטות קיבל נתניהו בנושא קורונה" \
    "נתניהו.*בריאות\|קורונה.*COUNT" \
    "PM + fuzzy topic (קורונה→בריאות) + count"

# === Test Section 6: Edge Cases ===
echo -e "\n${CYAN}=== Section 6: Edge Case Tests ===${NC}"

test_query \
    "החלטות בנושא נושא_שלא_קיים_במערכת" \
    "summary ILIKE\|decision_content ILIKE" \
    "Non-existent topic should search in content"

test_query \
    "5 החלטות בנושא חינוך מ2023" \
    "LIMIT 5.*חינוך.*2023" \
    "Specific count + topic + year"

# === Summary ===
echo -e "\n${BLUE}================================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "Total tests: ${total_tests}"
echo -e "Passed: ${GREEN}${passed_tests}${NC}"
echo -e "Failed: ${RED}${failed_tests}${NC}"

# Calculate percentage
if [ $total_tests -gt 0 ]; then
    percentage=$(( passed_tests * 100 / total_tests ))
    echo -e "Success rate: ${percentage}%"
fi

# Final status
echo ""
if [ $failed_tests -eq 0 ]; then
    echo -e "${GREEN}✨ All tests passed! The improvements are working correctly. ✨${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please check the implementation. ⚠️${NC}"
    echo -e "\n${MAGENTA}Debug tip:${NC} Check the response snippets above for error messages"
    echo -e "${MAGENTA}Common issues:${NC}"
    echo "- Services not rebuilt after changes"
    echo "- Database connection issues"
    echo "- Syntax errors in new code"
    exit 1
fi
