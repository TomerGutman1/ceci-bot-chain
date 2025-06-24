#!/bin/bash

# Quick test script
echo "🧪 Quick CECI-AI Test"
echo "===================="

# Test 1: Direct to API
echo -e "\n1️⃣ Testing Backend API..."
curl -X POST http://localhost:5173/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "הבא לי החלטה בנושא חינוך", "sessionId": "test-123"}' \
  -w "\n\nHTTP Status: %{http_code}\n"

# Test 2: PandasAI direct
echo -e "\n2️⃣ Testing PandasAI directly..."
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "הבא לי החלטה בנושא חינוך", "intent_type": "topic", "parameters": {}}' \
  -w "\n\nHTTP Status: %{http_code}\n"

# Test 3: Check services
echo -e "\n3️⃣ Service Status:"
echo "Backend: $(curl -s http://localhost:5173/health | jq -r '.status' 2>/dev/null || echo 'Not responding')"
echo "PandasAI: $(curl -s http://localhost:8001/ | jq -r '.status' 2>/dev/null || echo 'Not responding')"
