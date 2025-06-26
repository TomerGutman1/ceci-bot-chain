#!/bin/bash

# Test simple patterns that should work
echo "=== Testing Simple Patterns ==="
echo

echo "1. Testing: החלטה אחת בנושא בריאות מ2024"
curl -s -X POST http://localhost:8002/api/process-query \
  -H "Content-Type: application/json" \
  -d '{"query": "החלטה אחת בנושא בריאות מ2024", "sessionId": "test"}' | jq '.data[] | {decision_number, decision_date, tags_policy_area}'
echo

echo "2. Testing SQL generation only:"
curl -s -X POST http://localhost:8002/api/process-query \
  -H "Content-Type: application/json" \
  -d '{"query": "החלטה אחת בנושא בריאות מ2024", "sessionId": "test", "debug": true}' | jq '.debug'
echo

echo "3. Testing direct SQL execution:"
curl -s -X POST http://localhost:8002/api/execute-sql \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM israeli_government_decisions WHERE (tags_policy_area ILIKE $1 OR summary ILIKE $1) AND EXTRACT(YEAR FROM decision_date) = $2 ORDER BY decision_date DESC LIMIT 1",
    "params": ["%בריאות%", 2024]
  }' | jq '.data[] | {decision_number, decision_date, tags_policy_area, summary}'
