#!/bin/bash

echo "🧪 Phase 1: Individual Bot Testing with Token Metrics"
echo "===================================================="

# Test 1: MAIN_REWRITE_BOT_0
echo -e "\n📍 Test 1: MAIN_REWRITE_BOT_0 (Port 8010)"
echo "Testing Hebrew text normalization and cost tracking..."
response=$(curl -s -X POST http://localhost:8010/rewrite \
  -H "Content-Type: application/json" \
  -d '{
    "text": "נתח לי את החלטה מספר שלושים ושבע של ממשלה 37",
    "conv_id": "test-rewrite-001",
    "trace_id": "trace-001"
  }')

echo "Response:"
echo "$response" | jq '{clean_text, token_usage}'
echo ""

# Test 2: QUERY_SQL_GEN_BOT_2Q
echo -e "\n📍 Test 2: QUERY_SQL_GEN_BOT_2Q (Port 8012)"
echo "Testing SQL generation with template/GPT fallback..."
response=$(curl -s -X POST http://localhost:8012/sqlgen \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "analyze_decision",
    "entities": {
      "decision_number": "37",
      "government_number": "37"
    },
    "conv_id": "test-sql-001",
    "trace_id": "trace-004"
  }')

echo "Response:"
echo "$response" | jq '{sql_query, template_used, token_usage}'
echo ""

# Test 3: UNIFIED_INTENT_BOT (Port 8019 external)
echo -e "\n📍 Test 3: UNIFIED_INTENT_BOT_1 (Port 8019)"
echo "Testing unified rewrite + intent with GPT-4o..."
response=$(curl -s -X POST http://localhost:8019/intent \
  -H "Content-Type: application/json" \
  -d '{
    "raw_user_text": "נתח לי את החלטה מספר שלושים ושבע של ממשלה 37",
    "conv_id": "test-unified-001",
    "chat_history": []
  }')

echo "Response:"
echo "$response" | jq '{clean_query, intent, entities, token_usage}' 2>/dev/null || echo "$response"
echo ""

# Test 4: LLM_FORMATTER_BOT_4 (Port 8018 external)
echo -e "\n📍 Test 4: LLM_FORMATTER_BOT_4 (Port 8018)"
echo "Testing LLM formatting with GPT-4o-mini..."
response=$(curl -s -X POST http://localhost:8018/format \
  -H "Content-Type: application/json" \
  -d '{
    "data_type": "ranked_rows",
    "content": {
      "results": [
        {
          "title": "החלטה בנושא חינוך",
          "decision_number": 37,
          "government_number": 37,
          "topics": ["חינוך", "תקציב"],
          "summary": "החלטה לקידום החינוך בישראל"
        }
      ],
      "query_info": {
        "intent": "search_decisions",
        "entities": {"topic": "חינוך"}
      }
    },
    "original_query": "החלטות בנושא חינוך",
    "conv_id": "test-format-001"
  }')

echo "Response:"
echo "$response" | jq '{formatted_response, token_usage}' 2>/dev/null || echo "$response"
echo ""

# Summary
echo -e "\n📊 Summary:"
echo "==========="
echo "- Rewrite Bot: Uses GPT-3.5-turbo, ~$0.0003 per request"
echo "- SQL Gen Bot: Uses templates (free) or GPT-3.5-turbo fallback"
echo "- Unified Intent Bot: Uses GPT-4o-turbo, ~$0.015-$0.045 per request"
echo "- LLM Formatter Bot: Uses GPT-4o-mini, ~$0.0001-$0.0006 per request"