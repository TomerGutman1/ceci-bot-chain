# 🧪 Comprehensive Bot Chain Testing Plan

## Overview
This document outlines the comprehensive testing strategy for the CECI Bot Chain, with specific focus on token usage metrics verification and gradual downstream testing.

## 📋 Testing Phases

### Phase 1: Individual Bot Testing (Token Metrics Verification)

#### 1.1 MAIN_REWRITE_BOT_0 (Port 8010)
```bash
# Test rewrite functionality with token tracking
curl -X POST http://localhost:8010/rewrite \
  -H "Content-Type: application/json" \
  -d '{
    "text": "נתח לי את החלטה מספר שלושים ושבע של ממשלה 37",
    "conv_id": "test-rewrite-001",
    "trace_id": "trace-001"
  }'

# Expected response should include:
# - clean_text with normalized numbers
# - token_usage with cost_usd calculation
# - Model: gpt-3.5-turbo
# - Cost: ~$0.0005-$0.002 per request
```

#### 1.2 MAIN_INTENT_BOT_1 (Port 8011)
```bash
# Test intent detection with token tracking
curl -X POST http://localhost:8011/detect_intent \
  -H "Content-Type: application/json" \
  -d '{
    "query": "נתח לי את החלטה 37 של ממשלה 37",
    "conv_id": "test-intent-001",
    "trace_id": "trace-002"
  }'

# Expected response should include:
# - intent classification (analyze_decision)
# - entities extraction
# - token_usage with cost_usd
# - Model: gpt-3.5-turbo
# - Cost: ~$0.0008-$0.003 per request
```

#### 1.3 UNIFIED_INTENT_BOT_1 (Port 8011) - When Feature Flag Enabled
```bash
# Test unified rewrite + intent with token tracking
curl -X POST http://localhost:8011/unified_process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "נתח לי את החלטה מספר שלושים ושבע של ממשלה 37",
    "conv_id": "test-unified-001",
    "trace_id": "trace-003"
  }'

# Expected response should include:
# - clean_text (rewritten)
# - intent and entities
# - token_usage with cost_usd
# - Model: gpt-4o-turbo
# - Cost: ~$0.015-$0.045 per request (3x higher)
```

#### 1.4 QUERY_SQL_GEN_BOT_2Q (Port 8012)
```bash
# Test SQL generation with token tracking
curl -X POST http://localhost:8012/sqlgen \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "analyze_decision",
    "entities": {
      "decision_number": "37",
      "government_number": "37"
    },
    "conv_id": "test-sql-001",
    "trace_id": "trace-004"
  }'

# Expected response should include:
# - sql_query
# - parameters
# - token_usage (0 if template used, otherwise cost_usd)
# - Model: template or gpt-3.5-turbo
# - Cost: $0 (template) or ~$0.001-$0.004 (GPT)
```

#### 1.5 LLM_FORMATTER_BOT_4 (Port 8017) - When Feature Flag Enabled
```bash
# Test LLM formatting with token tracking
curl -X POST http://localhost:8017/format \
  -H "Content-Type: application/json" \
  -d '{
    "results": [
      {
        "title": "החלטה בנושא חינוך",
        "decision_number": 37,
        "government_number": 37,
        "topics": ["חינוך", "תקציב"]
      }
    ],
    "query_info": {
      "intent": "search_decisions",
      "entities": {"topic": "חינוך"}
    },
    "conv_id": "test-format-001"
  }'

# Expected response should include:
# - formatted_response (Hebrew text)
# - token_usage with cost_usd
# - Model: gpt-4o-mini
# - Cost: ~$0.0001-$0.0006 per request
```

### Phase 2: Pipeline Testing (Downstream Flow)

#### 2.1 Old Architecture Flow (Default)
```bash
# Test complete pipeline with old architecture
curl -X POST http://localhost:5001/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "כמה החלטות בנושא חינוך היו בממשלה 37?",
    "sessionId": "test-pipeline-old-001"
  }'

# Monitor token usage in response metadata:
# - Total cost should be ~$0.002-$0.008
# - Bot breakdown should show:
#   - rewrite: ~$0.001
#   - intent: ~$0.002
#   - sql_gen: ~$0.002
#   - formatter: $0 (code-based)
```

#### 2.2 Unified Architecture Flow (With Feature Flags)
```bash
# Enable feature flags first
export USE_UNIFIED_INTENT=true
export USE_LLM_FORMATTER=true

# Test complete pipeline with unified architecture
curl -X POST http://localhost:5001/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "נתח את החלטה 2989 של ממשלה 37",
    "sessionId": "test-pipeline-unified-001"
  }'

# Monitor token usage in response metadata:
# - Total cost should be ~$0.016-$0.031
# - Bot breakdown should show:
#   - unified_intent: ~$0.015-$0.030
#   - sql_gen: ~$0.001
#   - llm_formatter: ~$0.0003
```

### Phase 3: Comparative Testing

#### 3.1 Quality Comparison Script
```python
# test_quality_comparison.py
import requests
import json
from datetime import datetime

test_queries = [
    "כמה החלטות בנושא חינוך היו בממשלה 37?",
    "נתח את החלטה 2989",
    "מה היו ההחלטות בנושא תחבורה בשנת 2023?",
    "תן לי תוכן מלא של החלטה 1000"
]

def test_both_architectures(query):
    # Test old architecture
    old_response = requests.post(
        "http://localhost:5001/api/chat",
        json={"message": query, "sessionId": f"old-{datetime.now().timestamp()}"}
    ).json()
    
    # Test unified architecture
    headers = {"X-Use-Unified-Intent": "true", "X-Use-LLM-Formatter": "true"}
    new_response = requests.post(
        "http://localhost:5001/api/chat",
        json={"message": query, "sessionId": f"new-{datetime.now().timestamp()}"},
        headers=headers
    ).json()
    
    return {
        "query": query,
        "old": {
            "response": old_response.get("response"),
            "cost": old_response.get("metadata", {}).get("token_usage", {}).get("estimated_cost_usd", 0),
            "time_ms": old_response.get("metadata", {}).get("processing_time_ms", 0)
        },
        "new": {
            "response": new_response.get("response"),
            "cost": new_response.get("metadata", {}).get("token_usage", {}).get("estimated_cost_usd", 0),
            "time_ms": new_response.get("metadata", {}).get("processing_time_ms", 0)
        }
    }

# Run tests
results = []
for query in test_queries:
    results.append(test_both_architectures(query))
    
# Generate report
print("Quality & Cost Comparison Report")
print("=" * 50)
for result in results:
    print(f"\nQuery: {result['query']}")
    print(f"Old Architecture - Cost: ${result['old']['cost']:.4f}, Time: {result['old']['time_ms']}ms")
    print(f"New Architecture - Cost: ${result['new']['cost']:.4f}, Time: {result['new']['time_ms']}ms")
    print(f"Cost Increase: {(result['new']['cost'] / result['old']['cost'] - 1) * 100:.1f}%")
    print(f"Time Savings: {(1 - result['new']['time_ms'] / result['old']['time_ms']) * 100:.1f}%")
```

### Phase 4: Load Testing with Token Monitoring

#### 4.1 Concurrent Request Testing
```bash
# Create load test script
cat > load_test_tokens.sh << 'EOF'
#!/bin/bash

# Test concurrent requests and monitor token costs
echo "Starting load test with token monitoring..."

# Function to make request and extract cost
test_request() {
    local session_id=$1
    local query=$2
    
    response=$(curl -s -X POST http://localhost:5001/api/chat \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$query\", \"sessionId\": \"load-test-$session_id\"}")
    
    cost=$(echo $response | jq -r '.metadata.token_usage.estimated_cost_usd // 0')
    echo "Session $session_id - Cost: \$$cost"
}

# Run 10 concurrent requests
for i in {1..10}; do
    test_request $i "מה היו ההחלטות בנושא חינוך בממשלה 37?" &
done

wait
echo "Load test completed"
EOF

chmod +x load_test_tokens.sh
./load_test_tokens.sh
```

### Phase 5: Token Usage Analytics

#### 5.1 Create Token Usage Dashboard
```python
# token_usage_analytics.py
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="postgres",
    user="postgres",
    password="postgres"
)

# Query token usage data
query = """
SELECT 
    created_at,
    bot_name,
    model,
    total_tokens,
    cost_usd,
    route_type
FROM token_usage
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC
"""

df = pd.read_sql(query, conn)

# Generate analytics
print("\n=== Token Usage Summary (Last 24h) ===")
print(f"Total Requests: {len(df)}")
print(f"Total Cost: ${df['cost_usd'].sum():.4f}")
print(f"\nCost by Bot:")
print(df.groupby('bot_name')['cost_usd'].agg(['count', 'sum', 'mean']))
print(f"\nCost by Model:")
print(df.groupby('model')['cost_usd'].agg(['count', 'sum', 'mean']))

# Plot hourly costs
hourly_costs = df.set_index('created_at').resample('1H')['cost_usd'].sum()
hourly_costs.plot(kind='bar', title='Hourly Token Costs')
plt.ylabel('Cost (USD)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('token_costs_hourly.png')
print("\nHourly cost chart saved as token_costs_hourly.png")
```

### Phase 6: Automated Testing Suite

#### 6.1 Create Comprehensive Test Runner
```bash
# Create test runner script
cat > run_all_tests.sh << 'EOF'
#!/bin/bash

echo "🧪 Running Comprehensive Bot Chain Tests"
echo "========================================"

# Check if services are healthy
echo -n "Checking service health... "
docker-compose ps | grep -E "(rewrite|intent|sql-gen|formatter)" | grep -v "Up" && {
    echo "❌ Some services are not running!"
    exit 1
}
echo "✅"

# Run individual bot tests
echo -e "\n📍 Testing Individual Bots:"
echo "-------------------------"

# Test rewrite bot
echo -n "Testing MAIN_REWRITE_BOT_0... "
response=$(curl -s -X POST http://localhost:8010/rewrite \
    -H "Content-Type: application/json" \
    -d '{"text": "נתח את החלטה שלושים", "conv_id": "test-001"}')
cost=$(echo $response | jq -r '.token_usage.cost_usd // 0')
echo "✅ Cost: \$$cost"

# Test intent bot  
echo -n "Testing MAIN_INTENT_BOT_1... "
response=$(curl -s -X POST http://localhost:8011/detect_intent \
    -H "Content-Type: application/json" \
    -d '{"query": "נתח את החלטה 30", "conv_id": "test-002"}')
cost=$(echo $response | jq -r '.token_usage.cost_usd // 0')
echo "✅ Cost: \$$cost"

# Test SQL gen bot
echo -n "Testing QUERY_SQL_GEN_BOT_2Q... "
response=$(curl -s -X POST http://localhost:8012/sqlgen \
    -H "Content-Type: application/json" \
    -d '{"intent": "analyze_decision", "entities": {"decision_number": "30"}, "conv_id": "test-003"}')
cost=$(echo $response | jq -r '.token_usage.cost_usd // 0')
echo "✅ Cost: \$$cost"

# Run pipeline tests
echo -e "\n📍 Testing Full Pipeline:"
echo "----------------------"

# Test old architecture
echo -n "Testing old architecture pipeline... "
start_time=$(date +%s%N)
response=$(curl -s -X POST http://localhost:5001/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "כמה החלטות בנושא חינוך?", "sessionId": "test-pipeline-old"}')
end_time=$(date +%s%N)
duration=$((($end_time - $start_time) / 1000000))
cost=$(echo $response | jq -r '.metadata.token_usage.estimated_cost_usd // 0')
echo "✅ Cost: \$$cost, Time: ${duration}ms"

# Test unified architecture
echo -n "Testing unified architecture pipeline... "
export USE_UNIFIED_INTENT=true
export USE_LLM_FORMATTER=true
start_time=$(date +%s%N)
response=$(curl -s -X POST http://localhost:5001/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "כמה החלטות בנושא חינוך?", "sessionId": "test-pipeline-new"}')
end_time=$(date +%s%N)
duration=$((($end_time - $start_time) / 1000000))
cost=$(echo $response | jq -r '.metadata.token_usage.estimated_cost_usd // 0')
echo "✅ Cost: \$$cost, Time: ${duration}ms"

echo -e "\n✅ All tests completed successfully!"
EOF

chmod +x run_all_tests.sh
```

### Phase 7: Monitoring & Alerts

#### 7.1 Set Up Cost Alerts
```python
# cost_monitoring.py
import os
import requests
from datetime import datetime, timedelta

# Check hourly costs
def check_costs():
    # Query last hour costs from backend
    response = requests.get("http://localhost:5001/api/admin/token-usage/hourly")
    data = response.json()
    
    hourly_cost = data.get("total_cost_usd", 0)
    bot_breakdown = data.get("bot_breakdown", {})
    
    # Alert thresholds
    HOURLY_LIMIT = 1.0  # $1/hour
    DAILY_PROJECTION_LIMIT = 20.0  # $20/day
    
    # Check hourly limit
    if hourly_cost > HOURLY_LIMIT:
        print(f"⚠️ ALERT: Hourly cost ${hourly_cost:.2f} exceeds limit ${HOURLY_LIMIT}")
        
    # Project daily cost
    daily_projection = hourly_cost * 24
    if daily_projection > DAILY_PROJECTION_LIMIT:
        print(f"⚠️ ALERT: Projected daily cost ${daily_projection:.2f} exceeds limit ${DAILY_PROJECTION_LIMIT}")
    
    # Check for anomalies
    for bot, cost in bot_breakdown.items():
        if cost > hourly_cost * 0.5:  # Single bot using >50% of budget
            print(f"⚠️ ALERT: Bot {bot} using ${cost:.2f} ({cost/hourly_cost*100:.1f}% of total)")
    
    return {
        "hourly_cost": hourly_cost,
        "daily_projection": daily_projection,
        "bot_breakdown": bot_breakdown
    }

if __name__ == "__main__":
    costs = check_costs()
    print(f"\n📊 Current Costs:")
    print(f"Last Hour: ${costs['hourly_cost']:.4f}")
    print(f"Daily Projection: ${costs['daily_projection']:.2f}")
```

## 🚀 Testing Execution Plan

### Week 1: Individual Bot Testing
- Day 1-2: Test each bot endpoint individually
- Day 3-4: Verify token tracking accuracy
- Day 5: Document cost baselines

### Week 2: Pipeline Testing  
- Day 1-2: Test old architecture flow
- Day 3-4: Test unified architecture flow
- Day 5: Compare results and costs

### Week 3: Load & Performance Testing
- Day 1-2: Concurrent request testing
- Day 3-4: Peak load simulation
- Day 5: Performance optimization

### Week 4: Production Rollout
- Day 1: Enable 10% traffic split
- Day 2-3: Monitor metrics
- Day 4: Increase to 25%
- Day 5: Full rollout decision

## 📈 Success Metrics

1. **Token Tracking Accuracy**: 100% of requests have token usage data
2. **Cost Predictability**: Actual costs within 10% of estimates
3. **Performance**: p95 latency < 2s for both architectures
4. **Quality**: Unified architecture shows measurable improvement in response quality
5. **Reliability**: Zero token tracking failures during testing

## 🔧 Test Scripts

### Quick Test Script
```bash
#!/bin/bash
# quick_test.sh - Quick test of all bots

echo "Testing CECI Bot Chain..."

# Test rewrite bot
echo -n "1. Rewrite Bot: "
curl -s http://localhost:8010/health | jq -r '.status'

# Test intent bot
echo -n "2. Intent Bot: "
curl -s http://localhost:8011/health | jq -r '.status'

# Test SQL gen bot
echo -n "3. SQL Gen Bot: "
curl -s http://localhost:8012/health | jq -r '.status'

# Test formatter bot (if enabled)
if [ "$USE_LLM_FORMATTER" = "true" ]; then
    echo -n "4. LLM Formatter Bot: "
    curl -s http://localhost:8017/health | jq -r '.status'
fi

echo "Done!"
```

### Token Cost Calculator
```python
# calculate_costs.py
def calculate_cost(model, prompt_tokens, completion_tokens):
    """Calculate cost based on model and token counts"""
    
    costs = {
        "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
        "gpt-4o": {"prompt": 0.005, "completion": 0.015},
        "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006}
    }
    
    if model not in costs:
        return 0
    
    prompt_cost = (prompt_tokens / 1000) * costs[model]["prompt"]
    completion_cost = (completion_tokens / 1000) * costs[model]["completion"]
    
    return prompt_cost + completion_cost

# Example usage
print(f"GPT-3.5 (200 prompt, 100 completion): ${calculate_cost('gpt-3.5-turbo', 200, 100):.4f}")
print(f"GPT-4o (300 prompt, 150 completion): ${calculate_cost('gpt-4o', 300, 150):.4f}")
print(f"GPT-4o-mini (150 prompt, 50 completion): ${calculate_cost('gpt-4o-mini', 150, 50):.4f}")
```

## 📝 Test Results Template

```markdown
## Test Results - [DATE]

### Individual Bot Tests
| Bot | Endpoint | Model | Avg Tokens | Avg Cost | Status |
|-----|----------|-------|------------|----------|--------|
| Rewrite Bot | /rewrite | gpt-3.5-turbo | XXX | $X.XXXX | ✅/❌ |
| Intent Bot | /detect_intent | gpt-3.5-turbo | XXX | $X.XXXX | ✅/❌ |
| SQL Gen Bot | /sqlgen | template/gpt-3.5 | XXX | $X.XXXX | ✅/❌ |
| LLM Formatter | /format | gpt-4o-mini | XXX | $X.XXXX | ✅/❌ |

### Pipeline Tests
| Architecture | Avg Cost | Avg Time | Quality Score | Notes |
|--------------|----------|----------|---------------|-------|
| Old (7-bot) | $X.XXXX | XXXms | X/10 | |
| Unified | $X.XXXX | XXXms | X/10 | |

### Load Test Results
- Concurrent Requests: 10
- Total Requests: XXX
- Success Rate: XX%
- Avg Response Time: XXXms
- Total Cost: $X.XX

### Issues Found
1. [Issue description]
2. [Issue description]

### Recommendations
1. [Recommendation]
2. [Recommendation]
```

## 🛠️ Troubleshooting

### Common Issues

1. **Bot Not Responding**
   ```bash
   # Check bot logs
   docker-compose logs -f [bot-name]
   
   # Restart specific bot
   docker-compose restart [bot-name]
   ```

2. **Token Usage Not Tracked**
   - Check if bot has `token_usage` in response
   - Verify `cost_usd` calculation in bot code
   - Check backend aggregation logic

3. **High Costs**
   - Review prompt sizes
   - Check for GPT-4 usage where GPT-3.5 suffices
   - Enable template-based SQL generation

4. **Slow Response Times**
   - Check bot health endpoints
   - Monitor Redis cache hit rates
   - Review concurrent request handling

## 📊 Cost Optimization Tips

1. **Use Templates**: SQL Gen bot should use templates when possible (0 tokens)
2. **Optimize Prompts**: Keep prompts under 150 tokens
3. **Cache Results**: Enable response caching for common queries
4. **Batch Requests**: Process multiple items in single GPT calls
5. **Model Selection**: Use GPT-3.5 for simple tasks, GPT-4o only when needed

## 🎯 Next Steps

After completing all test phases:

1. Generate comprehensive test report
2. Present findings to stakeholders
3. Make go/no-go decision for unified architecture
4. Plan phased rollout if approved
5. Set up production monitoring