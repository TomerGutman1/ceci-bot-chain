#!/bin/bash

echo "=== Rebuilding SQL Engine ==="
cd /mnt/c/Users/tomer/Downloads/INTEGRATION/FRONTEND_NEW/ceci-ai-testing-main
docker compose up -d --build sql-engine

echo ""
echo "=== Waiting for services to start ==="
sleep 5

echo ""
echo "=== Running Date Diagnostic Test ==="
bash TESTS/debug/test_date_diagnostic.sh
