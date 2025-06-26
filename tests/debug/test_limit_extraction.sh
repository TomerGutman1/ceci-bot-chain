#!/bin/bash

# Test limit extraction specifically

API_URL="http://localhost:8002/api/process-query"

echo "=================================="
echo "Limit Extraction Debug Test"
echo "=================================="
echo ""

queries=(
    "הבא 5 החלטות בנושא חינוך"
    "תן לי 10 החלטות בנושא בריאות"
    "הבא 20 החלטות בנושא תחבורה"
)

for query in "${queries[@]}"; do
    echo "Query: $query"
    echo "-------------------"
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    # Extract all relevant fields
    success=$(echo "$response" | jq -r '.success' 2>/dev/null)
    template_used=$(echo "$response" | jq -r '.metadata.template_used' 2>/dev/null)
    sql_query=$(echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null)
    
    echo "Success: $success"
    echo "Template: $template_used"
    echo "SQL Query:"
    echo "$sql_query" | head -10
    
    # Check for LIMIT
    if echo "$sql_query" | grep -i "LIMIT" > /dev/null; then
        limit_line=$(echo "$sql_query" | grep -i "LIMIT")
        echo "✅ Found LIMIT: $limit_line"
    else
        echo "❌ No LIMIT found"
    fi
    
    echo ""
    echo "=================================="
    echo ""
done

# Test if the regex pattern works
echo "Testing regex pattern directly:"
echo "------------------------------"
cat > /tmp/test_limit_regex.js << 'EOF'
const patterns = {
    X_DECISIONS_BY_TOPIC: /(?:הבא|תן)\s+(?:לי\s+)?(\d+)\s+החלטות\s+בנושא\s+([\u0590-\u05FF\s]+)/,
    X_RECENT_DECISIONS: /(?:הבא|תן)\s+(?:לי\s+)?(\d+)\s+החלטות(?:\s+אחרונות)?$/
};

const testCases = [
    "הבא 5 החלטות בנושא חינוך",
    "תן לי 10 החלטות בנושא בריאות",
    "הבא 20 החלטות בנושא תחבורה",
    "הבא 50 החלטות"
];

for (const [name, pattern] of Object.entries(patterns)) {
    console.log(`\nTesting pattern: ${name}`);
    testCases.forEach(test => {
        const match = test.match(pattern);
        if (match) {
            console.log(`✅ "${test}" matches!`);
            if (match[1]) console.log(`   Count: ${match[1]}`);
            if (match[2]) console.log(`   Topic: ${match[2]}`);
        } else {
            console.log(`❌ "${test}" does NOT match`);
        }
    });
}
EOF

node /tmp/test_limit_regex.js
