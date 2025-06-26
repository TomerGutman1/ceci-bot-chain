#!/bin/bash

# Date Normalizer Focused Test
API_URL="http://localhost:8002/api/process-query"

echo "======================================"
echo "Date Normalizer Focused Test"
echo "======================================"

# Test 1: DD/MM/YYYY with context "מאז"
echo -n "1. DD/MM/YYYY with 'מאז': "
response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"query": "החלטות מאז 15/03/2023 בנושא חינוך"}' 2>/dev/null)

sql=$(echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null)
success=$(echo "$response" | jq -r '.success' 2>/dev/null)

if [ "$success" = "true" ]; then
    # Check if SQL contains the normalized date
    if echo "$sql" | grep -q "2023-03-15\|decision_date >= \$"; then
        echo "✅ PASSED"
        # Let's see what date was actually used
        echo "   SQL uses: $(echo "$sql" | grep -o "decision_date >= \$[0-9]" || echo "date parameter")"
    else
        echo "❌ FAILED - Date not normalized"
        echo "   SQL: $(echo "$sql" | cut -c1-100)..."
    fi
else
    echo "❌ ERROR: $(echo "$response" | jq -r '.error' | cut -c1-50)..."
fi

# Test 2: DD.MM.YYYY with context "מאז"
echo -n "2. DD.MM.YYYY with 'מאז': "
response2=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"query": "החלטות מאז 1.1.2023 בנושא בריאות"}' 2>/dev/null)

sql2=$(echo "$response2" | jq -r '.metadata.sql_query' 2>/dev/null)
formatted2=$(echo "$response2" | jq -r '.formatted' 2>/dev/null | head -1)

if echo "$sql2" | grep -q "decision_date >= \$"; then
    echo "✅ PASSED - Date parameter found"
    # Check the actual results to see if it's working
    count=$(echo "$response2" | jq -r '.data | length' 2>/dev/null)
    echo "   Found $count results"
else
    echo "❌ FAILED"
    echo "   SQL: $(echo "$sql2" | cut -c1-100)..."
fi

# Test 3: Let's debug what happens to the date
echo -e "\n3. Debug date normalization:"
echo -n "   Testing direct template match: "
response3=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"query": "תמצא לי את כל ההחלטות מאז ה-1.1.2023 שעוסקות בחינוך"}' 2>/dev/null)

template_used=$(echo "$response3" | jq -r '.metadata.template_used' 2>/dev/null)
if [ "$template_used" != "null" ]; then
    echo "✅ Template: $template_used"
else
    echo "❌ No template matched"
fi

# Test 4: Different date formats
echo -e "\n4. Testing various date formats:"
date_formats=(
    "15/03/2023"
    "15.03.2023"
    "15-03-2023"
    "1/1/2023"
    "01/01/2023"
)

for date in "${date_formats[@]}"; do
    echo -n "   Format $date: "
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"החלטות מאז $date\"}" 2>/dev/null)
    
    sql=$(echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null)
    if echo "$sql" | grep -q "decision_date >= \$"; then
        echo "✅ Recognized as date"
    else
        echo "❌ Not recognized"
    fi
done

# Test 5: Check if the problem is in the template or in the normalizer
echo -e "\n5. Direct date in query:"
echo -n "   Query with YYYY-MM-DD format: "
response5=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"query": "החלטות מאז 2023-03-15 בנושא חינוך"}' 2>/dev/null)

sql5=$(echo "$response5" | jq -r '.metadata.sql_query' 2>/dev/null)
if echo "$sql5" | grep -q "2023-03-15\|decision_date >= \$"; then
    echo "✅ PASSED"
else
    echo "❌ FAILED"
fi

echo "======================================"
