#!/bin/bash

echo "=== Testing Direct RPC Call ==="
echo

# Test 1: Simple query without parameters
echo "1. Testing simple query (no parameters):"
curl -s -X POST "https://djkpmgxxvsklrtvoofcp.supabase.co/rest/v1/rpc/execute_simple_sql" \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRqa3BtZ3h4dnNrbHJ0dm9vZmNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTAyMjk1NzQsImV4cCI6MjAyNTgwNTU3NH0.kK1svcodt4qktdIE4Z6n_vcc81l2cMcWJdECMcKr4OM" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM israeli_government_decisions LIMIT 1"}' | jq '.[0].result | keys'
echo

# Test 2: Query with parameters (the way it's being sent)
echo "2. Testing query with parameters (current method):"
curl -s -X POST "https://djkpmgxxvsklrtvoofcp.supabase.co/rest/v1/rpc/execute_simple_sql" \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRqa3BtZ3h4dnNrbHJ0dm9vZmNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTAyMjk1NzQsImV4cCI6MjAyNTgwNTU3NH0.kK1svcodt4qktdIE4Z6n_vcc81l2cMcWJdECMcKr4OM" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM israeli_government_decisions WHERE (tags_policy_area ILIKE '\''%בריאות%'\'' OR summary ILIKE '\''%בריאות%'\'') AND EXTRACT(YEAR FROM decision_date) = '\''2024'\'' ORDER BY decision_date DESC LIMIT 1"}' | jq '.[0].result | {decision_number, decision_date, tags_policy_area}'
echo

# Test 3: Check if we should use query builder instead
echo "3. Checking USE_SUPABASE_RPC environment variable:"
docker compose exec sql-engine printenv USE_SUPABASE_RPC
echo

# Test 4: Direct query builder test
echo "4. Testing with query builder (set USE_SUPABASE_RPC=false):"
docker compose exec sql-engine sh -c 'USE_SUPABASE_RPC=false node -e "
const { QueryExecutor } = require(\"./dist/services/executor.js\");
const executor = new QueryExecutor();
executor.executeDirectQuery(
  \"israeli_government_decisions\",
  {},
  { limit: 1, select: \"decision_number,decision_date\" }
).then(console.log).catch(console.error);
"'
