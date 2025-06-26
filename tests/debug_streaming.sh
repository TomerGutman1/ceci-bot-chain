#!/bin/bash

# Debug streaming response

API_URL="http://localhost:8080/api/chat"

echo "Testing streaming response parsing..."

query="תמצא לי את כל ההחלטות מאז ה-1.1.2023 שעוסקות בחינוך"

echo -e "\n🔍 Query: $query"

# Get raw response
echo -e "\n📡 Raw streaming response:"
response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"$query\", \"sessionId\": \"test-session\"}" \
    --no-buffer)

# Show first 1000 chars
echo "$response" | head -c 1000
echo "..."

# Try different patterns to find the count
echo -e "\n\n🔢 Trying to extract count:"

# Pattern 1: "נמצאו X החלטות"
count1=$(echo "$response" | grep -o 'נמצאו [0-9]* החלטות' | head -1)
echo "Pattern 'נמצאו X החלטות': $count1"

# Pattern 2: Look for any number before "החלטות"
count2=$(echo "$response" | grep -o '[0-9]* החלטות' | head -1)
echo "Pattern 'X החלטות': $count2"

# Pattern 3: Look in the last data line
last_data=$(echo "$response" | grep '^data:' | tail -1)
echo -e "\nLast data line:"
echo "$last_data" | head -c 500

# Extract just the content
content=$(echo "$last_data" | sed 's/^data: //' | jq -r '.content' 2>/dev/null || echo "Failed to parse JSON")
echo -e "\nExtracted content:"
echo "$content" | head -c 500

# Try to find count in content
if [[ "$content" != "Failed to parse JSON" ]]; then
    count3=$(echo "$content" | grep -o 'נמצאו [0-9]* החלטות' | head -1)
    echo -e "\nCount from content: $count3"
fi
