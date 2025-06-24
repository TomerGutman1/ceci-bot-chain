#!/bin/bash

echo "=================================================="
echo "🔍 Testing Remaining Failed Queries"
echo "=================================================="

# Function to test a query with detailed output
test_query_detailed() {
    local query="$1"
    local description="$2"
    
    echo -e "\n📝 Testing: $description"
    echo "Query: \"$query\""
    
    # Make the request and capture full response
    local response=$(curl -sk -X POST "https://localhost/api/chat/test-sql" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" 2>&1)
    
    echo "Full response:"
    echo "$response" | head -200
    
    # Try to parse as JSON
    echo -e "\nParsed response:"
    echo "$response" | jq . 2>/dev/null || echo "Failed to parse as JSON"
}

# Test each failing query
echo "1️⃣ === GOVERNMENT + TOPIC (האחרונה) ==="
test_query_detailed "החלטות הממשלה האחרונה בנושא תחבורה" \
                   "Last government transport decisions"

echo -e "\n2️⃣ === DATE RANGE 1 ==="
test_query_detailed "החלטות מ-1.1.2024 עד 31.12.2024" \
                   "Decisions from 1.1.2024 to 31.12.2024"

echo -e "\n3️⃣ === DATE RANGE 2 ==="
test_query_detailed "החלטות בין 1.1.2023 ל-31.12.2023" \
                   "Decisions between 1.1.2023 and 31.12.2023"

echo -e "\n4️⃣ === COMPLEX QUERY ==="
test_query_detailed "החלטות בנושא חינוך מהשנה האחרונה" \
                   "Education decisions from last year"

echo -e "\n=================================================="
echo "📊 Checking SQL Engine logs for these queries:"
docker logs ceci-ai-testing-main-sql-engine-1 --tail 50 2>&1 | grep -A5 -B5 "האחרונה\|2024\|2023\|השנה האחרונה" || echo "No relevant logs found"

echo -e "\n=================================================="
