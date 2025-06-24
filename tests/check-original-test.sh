#!/bin/bash

# Let's run the previous test script that worked
# Testing the templates we know work

echo "Running the original test that returned 50 results..."
echo ""

# Direct SQL test
echo "Testing directly against SQL endpoint:"
curl -X POST http://localhost:8002/test-sql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "מה עשה נתניהו בנושא חינוך?"
  }' | jq -r '.rows' 2>/dev/null || echo "SQL endpoint failed"

echo ""
echo "Testing another one that returned 50:"
curl -X POST http://localhost:8002/test-sql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "'"'"'קורונה'"'"' בין 2020-2021"
  }' | jq -r '.rows' 2>/dev/null || echo "SQL endpoint failed"

echo ""
echo "Let's check the services are running:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(sql-engine|backend|nginx)"
