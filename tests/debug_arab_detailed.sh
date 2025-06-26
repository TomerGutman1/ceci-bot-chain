#!/bin/bash

# More detailed debug
API_URL="http://localhost:8002/api/process-query"

echo "=== Detailed Arab Society Debug ==="
echo ""

query="החלטות בנושא החברה הערבית"
echo "Query: $query"
echo ""

# Clear logs first
docker compose logs sql-engine --tail=0 -f > /tmp/detailed-logs.txt &
LOG_PID=$!
sleep 1

# Make request
response=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$query\"}" 2>/dev/null)

sleep 3
kill $LOG_PID 2>/dev/null

echo "=== Full Flow Logs ==="
grep -E "(NLToSQL|FuzzyMatcher|buildNormalizedQuery|SQL generated)" /tmp/detailed-logs.txt

echo ""
echo "=== Response Analysis ==="
echo "SQL Query:"
echo "$response" | jq -r '.metadata.sql_query' 2>/dev/null

echo ""
echo "Parameters:"
echo "$response" | jq '.metadata.params' 2>/dev/null

echo ""
echo "Row count:"
echo "$response" | jq '.metadata.row_count' 2>/dev/null