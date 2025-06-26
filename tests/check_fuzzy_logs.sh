#!/bin/bash

# Check if fuzzy matcher is working
API_URL="http://localhost:8002/api/process-query"

echo "=== Checking Fuzzy Matcher Logs ==="
echo ""

# Make a request and capture logs
query="החלטות בנושא החברה הערבית"
echo "Sending query: $query"

# First, clear logs
docker compose logs sql-engine --tail=0 -f > /tmp/sql-logs.txt &
LOG_PID=$!

sleep 1

# Make the request
curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$query\"}" > /dev/null

sleep 2

# Kill the log capture
kill $LOG_PID 2>/dev/null

# Show relevant logs
echo ""
echo "=== Fuzzy Matcher Logs ==="
grep -E "(FuzzyMatcher|החברה הערבית|מיעוטים)" /tmp/sql-logs.txt || echo "No fuzzy matcher logs found"