# 🔧 Intent Detector Integration Specification

## 📋 Overview

This specification defines the integration of the **deterministic Intent Detector Engine** (JavaScript) to replace the current **GPT-based MAIN_INTENT_BOT_1** (Python) while maintaining API compatibility and improving performance.

## 🎯 Integration Goals

- **Zero AI Token Usage**: Replace GPT-4 calls with deterministic rule-based detection
- **100% Accuracy**: Maintain the achieved 100% accuracy on test suites
- **Sub-millisecond Performance**: Drastically improve response times
- **API Compatibility**: Maintain existing FastAPI interface for seamless integration
- **Cost Elimination**: Remove OpenAI API dependency for intent detection

---

## 📊 Algorithm Output Specification

### Input Format
```javascript
// Text input (Hebrew)
const query = "החלטות ממשלה 37 בנושא חינוך";
```

### Output Format
```javascript
{
  "intent_type": "QUERY",           // QUERY | EVAL | REFERENCE | CLARIFICATION
  "entities": {
    "government_number": 37,         // int | null
    "decision_number": null,         // int | null
    "topic": "חינוך",                // string | null
    "date_range": {                  // object | null
      "start": "2020-01-01",
      "end": "2025-12-31"
    },
    "ministries": ["משרד החינוך"],    // array | null
    "limit": 5,                      // int | null
    "comparison_target": null,       // string | null
    "operation": "search",           // "search" | "count" | "compare"
    "reference_type": null,          // "last" | "previous" | "specific" | "context" | null
    "reference_position": null       // int | null
  },
  "confidence": 0.95,                // float 0.0-1.0
  "route_flags": {
    "needs_context": false,          // bool
    "is_statistical": false,         // bool  
    "is_comparison": false           // bool
  },
  "explanation": "search operation"  // string
}
```

---

## 🔄 Intent Type Mapping

### Current System → New System
| **Current** | **New** | **Description** | **Route Flags** |
|-------------|---------|-----------------|-----------------|
| `QUERY` | `QUERY` | Basic search queries | `is_statistical: false`, `is_comparison: false` |
| `STATISTICAL` | `QUERY` | Count operations | `is_statistical: true`, `is_comparison: false` |
| `COMPARISON` | `QUERY` | Comparison operations | `is_statistical: false`, `is_comparison: true` |
| `EVAL` | `EVAL` | Deep analysis requests | All flags: `false` |
| `CLARIFICATION` | `CLARIFICATION` | Vague/unclear queries | All flags: `false` |
| *(New)* | `REFERENCE` | Context references | `needs_context: true` |

---

## 🏗️ Integration Architecture

### Option A: JavaScript Service (Recommended)
```
┌─────────────────┐    HTTP     ┌─────────────────┐
│   Bot Chain     │────────────▶│  Intent Detector│
│   (Python)      │             │   (Node.js)     │
│   Port: Various │◀────────────│   Port: 8011    │
└─────────────────┘    JSON     └─────────────────┘
```

### Option B: Python Wrapper
```
┌─────────────────┐   subprocess  ┌─────────────────┐
│   Bot Chain     │──────────────▶│  Intent Detector│
│   (Python)      │               │   (Node.js)     │
│   Port: 8011    │◀──────────────│   Embedded      │
└─────────────────┘     JSON      └─────────────────┘
```

---

## 🔌 API Interface Specification

### Endpoint: `POST /intent`

#### Request Model (Unchanged)
```python
class IntentRequest(BaseModel):
    text: str = Field(..., description="Cleaned text from rewrite bot")
    conv_id: str = Field(..., description="Conversation ID for tracking")
    trace_id: Optional[str] = Field(None, description="Request trace ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Previous conversation context")
```

#### Response Model (Updated)
```python
class IntentResponse(BaseModel):
    conv_id: str
    intent_type: str = Field(..., pattern="^(QUERY|EVAL|REFERENCE|CLARIFICATION)$")
    entities: IntentEntities
    confidence: float = Field(..., ge=0, le=1)
    route_flags: RouteFlags  # Updated structure
    timestamp: datetime
    layer: str = "1_MAIN_INTENT_BOT"
    token_usage: Optional[TokenUsage] = None  # Always null for deterministic
    explanation: Optional[str] = None
```

#### Updated Route Flags
```python
class RouteFlags(BaseModel):
    needs_clarification: bool      # Legacy compatibility
    has_context: bool             # Legacy compatibility  
    is_follow_up: bool            # Legacy compatibility
    # New flags from deterministic engine
    needs_context: bool           # From REFERENCE detection
    is_statistical: bool          # From operation="count"
    is_comparison: bool           # From operation="compare"
```

#### Updated Entities Model
```python
class IntentEntities(BaseModel):
    government_number: Optional[int] = None
    decision_number: Optional[int] = None
    topic: Optional[str] = None
    date_range: Optional[Dict[str, str]] = None
    ministries: Optional[List[str]] = None
    count_target: Optional[str] = None      # Deprecated, use operation
    comparison_target: Optional[str] = None
    limit: Optional[int] = None
    # New fields from deterministic engine
    operation: Optional[str] = None         # "search" | "count" | "compare"
    reference_type: Optional[str] = None    # "last" | "previous" | "specific" | "context"
    reference_position: Optional[int] = None
```

---

## 🚀 Implementation Plan

### Phase 1: Node.js Service Setup
1. **Create FastAPI-compatible Node.js service**
   ```bash
   cd /app/INTENT_RCGNZR_0
   npm init -y
   npm install express cors helmet
   ```

2. **Implement HTTP wrapper around intent_detector.js**
   ```javascript
   // server.js
   import express from 'express';
   import IntentDetector from './intent_detector.js';
   
   const app = express();
   const detector = new IntentDetector();
   
   app.post('/intent', (req, res) => {
     const { text, conv_id, trace_id, context } = req.body;
     const result = detector.detect(text);
     // Transform to expected format
     res.json(transformToApiFormat(result, conv_id));
   });
   ```

3. **Update Dockerfile**
   ```dockerfile
   FROM node:18-slim
   WORKDIR /app
   COPY INTENT_RCGNZR_0/ /app/
   RUN npm install
   EXPOSE 8011
   CMD ["node", "server.js"]
   ```

### Phase 2: Response Transformation
```javascript
function transformToApiFormat(detectorResult, conv_id) {
  // Map new intent types to legacy format for compatibility
  const intentMapping = {
    'QUERY': getQuerySubtype(detectorResult.route_flags),
    'EVAL': 'EVAL',
    'REFERENCE': 'QUERY', // Map to QUERY with needs_context=true
    'CLARIFICATION': 'CLARIFICATION'
  };
  
  return {
    conv_id,
    intent_type: intentMapping[detectorResult.intent_type],
    entities: {
      ...detectorResult.entities,
      count_target: detectorResult.route_flags.is_statistical ? "decisions" : null
    },
    confidence: detectorResult.confidence,
    route_flags: {
      // Legacy flags for backward compatibility
      needs_clarification: detectorResult.intent_type === 'CLARIFICATION',
      has_context: detectorResult.route_flags.needs_context,
      is_follow_up: detectorResult.route_flags.needs_context,
      // New flags
      needs_context: detectorResult.route_flags.needs_context,
      is_statistical: detectorResult.route_flags.is_statistical,
      is_comparison: detectorResult.route_flags.is_comparison
    },
    timestamp: new Date().toISOString(),
    layer: "1_MAIN_INTENT_BOT",
    token_usage: null, // No tokens used in deterministic approach
    explanation: detectorResult.explanation
  };
}

function getQuerySubtype(route_flags) {
  if (route_flags.is_statistical) return 'STATISTICAL';
  if (route_flags.is_comparison) return 'COMPARISON';
  return 'QUERY';
}
```

### Phase 3: Legacy Compatibility Layer
```javascript
// Handle entity normalization for existing downstream systems
function normalizeEntitiesForLegacy(entities) {
  // Ensure ministries are in full form
  if (entities.ministries) {
    entities.ministries = entities.ministries.map(ministry => {
      if (!ministry.startsWith('משרד ')) {
        return `משרד ${ministry}`;
      }
      return ministry;
    });
  }
  
  // Ensure topics are cleaned
  if (entities.topic) {
    entities.topic = entities.topic.replace(/^(בנושא|על|לגבי)\s+/, '');
  }
  
  return entities;
}
```

---

## 🔧 Configuration Changes

### Environment Variables
```bash
# Remove OpenAI dependency
# OPENAI_API_KEY=""  # No longer needed

# Intent service configuration
INTENT_SERVICE_URL=http://localhost:8011
INTENT_TIMEOUT_MS=1000
INTENT_FALLBACK_CONFIDENCE=0.3
```

### Docker Compose Update
```yaml
services:
  intent-detector:
    build: 
      context: ./bot_chain/INTENT_RCGNZR_0
    ports:
      - "8011:8011"
    environment:
      - NODE_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8011/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 📊 Performance Expectations

### Before (GPT-based)
- **Latency**: 500-2000ms
- **Cost**: $0.002-0.01 per request
- **Accuracy**: 85-95%
- **Reliability**: Dependent on OpenAI API

### After (Deterministic)
- **Latency**: <1ms
- **Cost**: $0 per request
- **Accuracy**: 100% (validated)
- **Reliability**: 99.9%+ (no external dependencies)

---

## 🧪 Testing Strategy

### Unit Tests
```javascript
// Test deterministic engine directly
import { test } from 'node:test';
import IntentDetector from './intent_detector.js';

test('Basic intent detection', () => {
  const detector = new IntentDetector();
  const result = detector.detect('החלטות ממשלה 37');
  assert.equal(result.intent_type, 'QUERY');
  assert.equal(result.entities.government_number, 37);
});
```

### Integration Tests
```python
# Test API compatibility
def test_intent_api_compatibility():
    response = requests.post('/intent', json={
        'text': 'החלטות ממשלה 37',
        'conv_id': 'test-123'
    })
    assert response.status_code == 200
    data = response.json()
    assert 'intent_type' in data
    assert 'entities' in data
    assert 'route_flags' in data
```

### Performance Tests
```bash
# Load testing
ab -n 1000 -c 10 -H "Content-Type: application/json" \
   -p test_payload.json http://localhost:8011/intent
```

---

## 🔄 Migration Steps

### Step 1: Preparation
1. Backup current MAIN_INTENT_BOT_1
2. Set up new intent detector service
3. Create parallel testing environment

### Step 2: Parallel Testing
1. Route 10% of traffic to new service
2. Compare results with current system
3. Monitor performance metrics
4. Validate downstream compatibility

### Step 3: Full Migration
1. Update docker-compose to use new service
2. Remove OpenAI dependencies
3. Update monitoring dashboards
4. Deploy to production

### Step 4: Cleanup
1. Remove old MAIN_INTENT_BOT_1 code
2. Update documentation
3. Archive old prompts and GPT logic

---

## 🚨 Risk Mitigation

### Fallback Strategy
```javascript
// If deterministic engine fails, use minimal fallback
function fallbackIntentDetection(text) {
  return {
    intent_type: 'CLARIFICATION',
    entities: {},
    confidence: 0.1,
    route_flags: { needs_clarification: true },
    explanation: 'Fallback: System temporarily unavailable'
  };
}
```

### Monitoring
- **Health checks**: Every 30s
- **Response time**: Alert if >10ms
- **Error rate**: Alert if >0.1%
- **Accuracy**: Daily validation against test suite

### Rollback Plan
1. Keep old service running in parallel for 48h
2. Traffic switch capability via feature flag
3. Database compatibility maintained
4. Automated rollback on error threshold

---

## 📈 Success Metrics

### Technical KPIs
- **Latency**: Target <1ms (vs current 500-2000ms)
- **Cost**: $0/month (vs current ~$300/month)
- **Accuracy**: Maintain 100% on test suite
- **Uptime**: >99.9%

### Business KPIs  
- **User satisfaction**: Faster response times
- **Operational cost**: 100% reduction in AI costs
- **System reliability**: No OpenAI dependency
- **Scalability**: Linear scaling with hardware

---

## 🔗 Integration Dependencies

### Upstream Services
- **MAIN_REWRITE_BOT_0**: Provides cleaned text input
- **Common logging**: Maintains audit trail

### Downstream Services
- **QUERY_SQL_GEN_BOT_2Q**: Receives intent classification
- **CLARIFY_CLARIFY_BOT_2C**: Handles clarification requests
- **MAIN_CTX_ROUTER_BOT_2X**: Processes context references

### Configuration Files
- `docker-compose.yml`: Service definition
- `nginx-bot-chain.conf`: Routing rules
- `schemas/intent_taxonomy.yml`: Entity definitions (for reference)

---

## ✅ Implementation Checklist

- [ ] Create Node.js wrapper service
- [ ] Implement API transformation layer
- [ ] Update Dockerfile and docker-compose
- [ ] Create comprehensive test suite
- [ ] Set up monitoring and health checks
- [ ] Implement fallback mechanisms
- [ ] Update documentation
- [ ] Plan rollback strategy
- [ ] Conduct performance testing
- [ ] Execute phased migration
- [ ] Monitor production deployment
- [ ] Clean up old code and dependencies

---

**Integration Timeline**: 2-3 days
**Go-live Target**: Next deployment window
**Expected ROI**: Immediate cost savings + performance improvement