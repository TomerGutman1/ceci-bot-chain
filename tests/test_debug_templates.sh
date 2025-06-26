#!/bin/bash

# Test simple pattern to verify our templates are loaded

echo "Testing if our templates are loaded..."

SQL_ENGINE_URL="http://localhost:8002/api/process-query"

# Add a very simple test pattern
test_simple() {
    local query="$1"
    echo -e "\n🔍 Testing: $query"
    
    # First, let's check what patterns are available
    response=$(curl -s -X POST "$SQL_ENGINE_URL" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}")
    
    # Show full response for debugging
    echo "Full response:"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
}

# Test the simplest possible version
test_simple "מאז 2023 חינוך"

# Also test a pattern we know works
test_simple "5 החלטות בנושא חינוך מ2023"

# Check if service is responding
echo -e "\n🏥 Health check:"
curl -s http://localhost:8002/health | jq '.' 2>/dev/null || echo "No JSON response"
