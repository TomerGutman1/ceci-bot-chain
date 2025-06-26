#!/bin/bash

echo "=== Checking Services Status ==="
echo

echo "1. Docker Compose Status:"
docker compose ps
echo

echo "2. Testing SQL Engine Health:"
curl -s http://localhost:8002/health || echo "SQL Engine not responding"
echo

echo "3. Testing Backend Health:"
curl -s http://localhost:8080/api/health || echo "Backend not responding"
echo

echo "4. Checking SQL Engine Logs (last 20 lines):"
docker compose logs sql-engine --tail=20
echo

echo "5. Testing a simple query directly to SQL Engine:"
curl -s -X POST http://localhost:8002/api/process-query \
  -H "Content-Type: application/json" \
  -d '{"query": "כמה החלטות יש?", "sessionId": "test"}' | jq . || echo "Failed to query SQL Engine"
