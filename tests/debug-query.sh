#!/bin/bash

# Debug script to see what's actually happening with queries

echo "Testing a simple query directly to SQL Engine..."
echo ""

# Test basic query
echo "1. Testing: 'מה עשה נתניהו בנושא חינוך?'"
echo "Request being sent:"
echo '{"query": "מה עשה נתניהו בנושא חינוך?"}'
echo ""
echo "Full response:"
curl -s -X POST "http://localhost:8002/api/process-query" \
    -H "Content-Type: application/json" \
    -d '{"query": "מה עשה נתניהו בנושא חינוך?"}' | jq '.'

echo ""
echo "===================="
echo ""

# Test if SQL Engine is even running
echo "2. Checking SQL Engine health:"
curl -s http://localhost:8002/health | jq '.'

echo ""
echo "===================="
echo ""

# Test with the old test script format
echo "3. Testing with test-sql endpoint (if exists):"
curl -s -X POST "http://localhost:8002/test-sql" \
    -H "Content-Type: application/json" \
    -d '{"query": "מה עשה נתניהו בנושא חינוך?"}' | jq '.'

echo ""
echo "===================="
echo ""

# Check what endpoints are available
echo "4. Checking root endpoint:"
curl -s http://localhost:8002/ | head -20

echo ""
echo "===================="
echo ""

# Test a simpler query
echo "5. Testing simpler query: 'כמה החלטות יש?'"
curl -s -X POST "http://localhost:8002/api/process-query" \
    -H "Content-Type: application/json" \
    -d '{"query": "כמה החלטות יש?"}' | jq '.'
