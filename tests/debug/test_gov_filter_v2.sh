#!/bin/bash

# Government Filter Test - Improved Version
API_URL="http://localhost:8002/api/process-query"

echo "======================================"
echo "Government Filter Test (v2)"
echo "======================================"

# Test 1: Simple query WITHOUT government mention
echo -n "1. Query without government: "
response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"query": "החלטות בנושא חינוך"}' 2>/dev/null)

sql=$(echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null)
success=$(echo "$response" | jq -r '.success' 2>/dev/null)

if [ "$success" = "true" ]; then
    if echo "$sql" | grep -q "government_number.*37"; then
        echo "❌ FAILED - Found government_number = '37'"
        echo "   SQL snippet: $(echo "$sql" | grep -o "government_number[^,]*" | head -1)"
    else
        echo "✅ PASSED - No default government filter"
    fi
else
    echo "❌ ERROR: $(echo "$response" | jq -r '.error' | cut -c1-50)..."
fi

# Test 2: Query WITH explicit government mention
echo -n "2. Query with government 37: "
response2=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"query": "החלטות בנושא חינוך של ממשלה 37"}' 2>/dev/null)

sql2=$(echo "$response2" | jq -r '.metadata.sql_query' 2>/dev/null)
success2=$(echo "$response2" | jq -r '.success' 2>/dev/null)

if [ "$success2" = "true" ]; then
    # Check if SQL contains government_number filter (as parameter)
    if echo "$sql2" | grep -q "government_number.*\$"; then
        # Extract the actual data from response to verify results
        count=$(echo "$response2" | jq -r '.data | length' 2>/dev/null)
        echo "✅ PASSED - Found government filter"
        echo "   SQL uses parameters, found $count results"
    else
        echo "❌ FAILED - No government filter when explicitly requested"
        echo "   SQL: $(echo "$sql2" | cut -c1-100)..."
    fi
else
    echo "❌ ERROR: $(echo "$response2" | jq -r '.error' | cut -c1-50)..."
fi

# Test 3: Different government
echo -n "3. Query with government 36: "
response3=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"query": "החלטות של ממשלה 36"}' 2>/dev/null)

sql3=$(echo "$response3" | jq -r '.metadata.sql_query' 2>/dev/null)
success3=$(echo "$response3" | jq -r '.success' 2>/dev/null)

if [ "$success3" = "true" ]; then
    if echo "$sql3" | grep -q "government_number.*\$"; then
        count=$(echo "$response3" | jq -r '.data | length' 2>/dev/null)
        echo "✅ PASSED - Found government filter"
        echo "   SQL uses parameters, found $count results"
    else
        echo "❌ FAILED - Wrong or missing government filter"
        echo "   SQL: $(echo "$sql3" | cut -c1-100)..."
    fi
else
    echo "❌ ERROR: $(echo "$response3" | jq -r '.error' | cut -c1-50)..."
fi

# Test 4: Mixed query without government mention
echo -n "4. Mixed query (no government): "
response4=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"query": "20 החלטות בנושא בריאות מ2023"}' 2>/dev/null)

sql4=$(echo "$response4" | jq -r '.metadata.sql_query' 2>/dev/null)

if echo "$sql4" | grep -q "government_number"; then
    echo "❌ FAILED - Added government filter when not requested"
else
    echo "✅ PASSED - No government filter"
fi

echo "======================================"
