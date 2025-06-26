#!/bin/bash

# Test template matching directly

API_URL="http://localhost:8002/api/process-query"

echo "=================================="
echo "Template Matching Debug Test"
echo "=================================="
echo ""

test_queries=(
    "הבא 5 החלטות בנושא חינוך"
    "תן לי 5 החלטות בנושא חינוך"
    "הבא 20 החלטות בנושא תחבורה"
    "החלטות ממרץ 2023"
    "החלטה 660"
)

for query in "${test_queries[@]}"; do
    echo "Query: $query"
    echo "-------------------"
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    # Extract key fields
    success=$(echo "$response" | jq -r '.success' 2>/dev/null)
    template_used=$(echo "$response" | jq -r '.metadata.template_used' 2>/dev/null)
    sql_query=$(echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null | head -5)
    
    echo "Success: $success"
    
    if [ -n "$template_used" ] && [ "$template_used" != "null" ]; then
        echo "✅ Template matched: $template_used"
    else
        echo "❌ No template matched (using GPT)"
    fi
    
    # Check for LIMIT in SQL
    if echo "$sql_query" | grep -i "LIMIT" > /dev/null; then
        limit_line=$(echo "$sql_query" | grep -i "LIMIT")
        echo "Found LIMIT: $limit_line"
    else
        echo "No LIMIT found in query"
    fi
    
    echo ""
done

# Also test the exact regex patterns
echo "=================================="
echo "Direct Regex Pattern Tests"
echo "=================================="
echo ""

# Test X_DECISIONS_BY_TOPIC pattern
pattern='(?:הבא|תן)\s+(?:לי\s+)?(\d+)\s+החלטות\s+בנושא\s+([\u0590-\u05FF\s]+)'
test_string="הבא 5 החלטות בנושא חינוך"

echo "Testing pattern matching in Node.js:"
cat > /tmp/test_regex.js << 'EOF'
const pattern = /(?:הבא|תן)\s+(?:לי\s+)?(\d+)\s+החלטות\s+בנושא\s+([\u0590-\u05FF\s]+)/;
const testCases = [
    "הבא 5 החלטות בנושא חינוך",
    "תן לי 5 החלטות בנושא חינוך",
    "הבא 20 החלטות בנושא תחבורה"
];

testCases.forEach(test => {
    const match = test.match(pattern);
    if (match) {
        console.log(`✅ "${test}" matches!`);
        console.log(`   Count: ${match[1]}, Topic: ${match[2]}`);
    } else {
        console.log(`❌ "${test}" does NOT match`);
    }
});

// Test Hebrew month pattern
const monthPattern = /החלטות\s+(?:מ|מחודש)\s*(ינואר|פברואר|מרץ|מרס|אפריל|מאי|יוני|יולי|אוגוסט|ספטמבר|אוקטובר|נובמבר|דצמבר)\s+(\d{4})/;
const monthTest = "החלטות ממרץ 2023";
const monthMatch = monthTest.match(monthPattern);
if (monthMatch) {
    console.log(`\n✅ "${monthTest}" matches month pattern!`);
    console.log(`   Month: ${monthMatch[1]}, Year: ${monthMatch[2]}`);
} else {
    console.log(`\n❌ "${monthTest}" does NOT match month pattern`);
}
EOF

node /tmp/test_regex.js
