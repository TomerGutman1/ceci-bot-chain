#!/bin/bash

# Check SQL engine logs
echo "Checking SQL engine logs..."
echo "=========================="

# Show last 50 lines of sql-engine logs
docker compose logs sql-engine --tail 50

echo -e "\n\nNow testing a problematic query..."
echo "=================================="

# Test with full output
curl -s -X POST "http://localhost:8002/api/process-query" \
    -H "Content-Type: application/json" \
    -d '{"query": "החלטה אחת בנושא בריאות מ2024"}' | jq '.'

echo -e "\n\nChecking logs again..."
echo "===================="
docker compose logs sql-engine --tail 20
