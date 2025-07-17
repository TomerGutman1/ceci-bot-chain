#!/bin/bash

# Production API endpoint
API_URL="https://ceci-ai.ceci.org.il/api/chat"

# Test queries
declare -a queries=(
  "החלטות בנושא חינוך ממשלה 37"
  "החלטה 2989"
  "כמה החלטות בנושא ביטחון קיבלה ממשלה 37"
  "הראה החלטות אחרונות בנושא סביבה"
  "החלטות של משרד החינוך"
  "החלטות ממשלה ב2024 בנושא בריאות"
)

echo "# Production Test Results - $(date)"
echo "Testing ${#queries[@]} example queries..."
echo ""

# Test each query
for i in "${!queries[@]}"; do
  query="${queries[$i]}"
  echo "## Test $((i+1)): \"$query\""
  
  # Make the request and capture response
  response=$(curl -s -w "\n\nRESPONSE_TIME: %{time_total}" -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"$query\", \"conversationId\": \"test-$((i+1))\"}")
  
  # Extract response time
  response_time=$(echo "$response" | grep -oP 'RESPONSE_TIME: \K[0-9.]+')
  
  # Check if response contains error
  if echo "$response" | grep -q '"error"'; then
    echo "❌ FAILED - Error in response"
  elif echo "$response" | grep -q '"type":"response"'; then
    echo "✅ SUCCESS - Response time: ${response_time}s"
    
    # Extract key information
    if echo "$response" | grep -q '"count_only":true'; then
      # Extract count from response
      count=$(echo "$response" | grep -oP '"content":"[^"]*(\d+)[^"]*"' | grep -oP '\d+')
      echo "   Count result: $count"
    else
      # Count number of decisions returned
      decisions=$(echo "$response" | grep -o "החלטה מס'" | wc -l)
      echo "   Decisions returned: $decisions"
    fi
  else
    echo "❌ FAILED - No valid response"
  fi
  
  echo ""
  sleep 1  # Small delay between requests
done

echo "Test completed!"