#!/bin/bash

echo "Testing government filter issue..."
echo "================================"

API_URL="http://localhost:8002/api/process-query"

# Test simple query without government mention
echo -e "\n1. Testing: החלטות בנושא חינוך"
response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"query": "החלטות בנושא חינוך"}')

echo "Full response:"
echo "$response" | jq '.'

echo -e "\n2. Checking SQL for government filter:"
sql=$(echo "$response" | jq -r '.metadata.sql_query')
echo "SQL: $sql"

if echo "$sql" | grep -q "government_number.*37"; then
    echo "❌ FAILED: Found government_number = '37' in SQL"
else
    echo "✅ PASSED: No government filter found"
fi

echo -e "\n3. Testing query WITH government mention:"
response2=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"query": "החלטות בנושא חינוך של ממשלה 37"}')

sql2=$(echo "$response2" | jq -r '.metadata.sql_query')
echo "SQL: $sql2"

if echo "$sql2" | grep -q "government_number.*37"; then
    echo "✅ PASSED: Found government filter when explicitly mentioned"
else
    echo "❌ FAILED: No government filter when explicitly mentioned"
fi
