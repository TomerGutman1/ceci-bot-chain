# 🚀 MIGRATION GUIDE – Unified GPT Architecture

> **Purpose**: Step-by-step guide for migrating from the 7-bot pipeline to the unified GPT-4o architecture.

---

## 📋 Pre-Migration Checklist

- [ ] **Backup**: Full backup of production database and configurations
- [ ] **API Keys**: Ensure OpenAI API keys have sufficient quota for GPT-4o
- [ ] **Monitoring**: Set up dashboards for quality and performance metrics
- [ ] **Rollback Plan**: Document and test rollback procedures
- [ ] **Team Training**: Brief team on new architecture and feature flags

---

## 🎯 Migration Strategy

### Phase 1: Development & Testing (Week 1)
1. **Deploy New Bots to Staging**
   ```bash
   # Build new bot images
   docker-compose -f docker-compose.new-bots.yml build
   
   # Deploy to staging
   docker-compose -f docker-compose.new-bots.yml up -d
   ```

2. **Configure Feature Flags**
   ```bash
   # Copy new architecture env file
   cp .env.new-architecture .env.staging
   
   # Start with 0% traffic
   USE_UNIFIED_INTENT=false
   USE_LLM_FORMATTER=false
   ```

3. **Run Test Suites**
   ```bash
   # Test unified intent bot
   python bot_chain/UNIFIED_INTENT_BOT_1/test_unified_intent.py
   
   # Test LLM formatter
   python bot_chain/LLM_FORMATTER_BOT_4/test_llm_formatter.py
   
   # Run integration tests
   ./tests/test_unified_architecture.sh
   ```

### Phase 2: Gradual Rollout (Week 2-3)

#### 10% Traffic (Day 1-3)
```bash
# Enable for 10% of traffic
export USE_UNIFIED_INTENT=true
export USE_LLM_FORMATTER=true
export UNIFIED_INTENT_ROLLOUT_PERCENTAGE=10
export LLM_FORMATTER_ROLLOUT_PERCENTAGE=10
```

**Monitor**:
- Response times (target: <300ms for intent)
- Token usage (expect ~330 tokens for unified intent)
- Quality scores (target: >98% accuracy)
- Error rates (target: <0.1%)

#### 25% Traffic (Day 4-7)
```bash
# Increase to 25%
export UNIFIED_INTENT_ROLLOUT_PERCENTAGE=25
export LLM_FORMATTER_ROLLOUT_PERCENTAGE=25
```

**Validate**:
- Cost projections ($0.016/query average)
- User feedback on response quality
- Hebrew handling improvements
- Formatter output quality

#### 50% Traffic (Week 2)
```bash
# Half traffic on new architecture
export UNIFIED_INTENT_ROLLOUT_PERCENTAGE=50
export LLM_FORMATTER_ROLLOUT_PERCENTAGE=50
```

**Check**:
- System stability
- OpenAI API usage patterns
- Cache hit rates
- Performance consistency

### Phase 3: Full Migration (Week 3-4)

#### 100% Traffic
```bash
# Full rollout
export UNIFIED_INTENT_ROLLOUT_PERCENTAGE=100
export LLM_FORMATTER_ROLLOUT_PERCENTAGE=100
```

#### Archive Old Bots
```bash
# After 1 week of stable operation
docker-compose stop rewrite_bot
docker-compose rm rewrite_bot

# Update main docker-compose.yml
# Remove old bot definitions
```

---

## 🔧 Technical Implementation

### 1. Backend Integration Points

**botChainService.ts** modifications:
```typescript
// Feature flag checks
const useUnifiedIntent = process.env.USE_UNIFIED_INTENT === 'true';
const useLLMFormatter = process.env.USE_LLM_FORMATTER === 'true';

// Percentage-based rollout
const rolloutPercentage = parseInt(process.env.UNIFIED_INTENT_ROLLOUT_PERCENTAGE || '0');
const shouldUseNewFlow = Math.random() * 100 < rolloutPercentage;
```

### 2. Database Schema (No Changes Required)
The unified architecture maintains full compatibility with existing schema.

### 3. API Contracts
- Unified Intent Bot accepts same input as old Rewrite Bot
- Output includes all fields from both Rewrite + Intent
- LLM Formatter maintains same output structure

---

## 📊 Monitoring & Metrics

### Key Metrics to Track

| Metric | Old Target | New Target | Alert Threshold |
|--------|------------|------------|-----------------|
| Intent Latency | 500ms | 300ms | >500ms |
| Format Quality | 4.0/5 | 4.5/5 | <4.3/5 |
| Daily Cost | $10 | $50 | >$60 |
| Error Rate | 1% | 0.5% | >1% |

### Dashboards to Create
1. **Performance Dashboard**
   - Request latency by bot
   - Token usage breakdown
   - Cache hit rates

2. **Quality Dashboard**
   - Intent classification accuracy
   - Formatter output ratings
   - Hebrew handling success

3. **Cost Dashboard**
   - Hourly token consumption
   - Cost by model type
   - Projected daily/monthly costs

---

## 🚨 Rollback Procedures

### Immediate Rollback (< 5 minutes)
```bash
# Disable new architecture
export USE_UNIFIED_INTENT=false
export USE_LLM_FORMATTER=false

# Restart backend
docker-compose restart backend
```

### Full Rollback (if needed)
```bash
# Switch to old branch
git checkout main

# Restore old docker-compose
docker-compose down
docker-compose up -d

# Verify old flow working
curl http://localhost:8010/health  # Rewrite bot
curl http://localhost:8011/health  # Old intent bot
```

---

## ✅ Post-Migration Tasks

1. **Documentation**
   - [ ] Update all API documentation
   - [ ] Create new architecture diagrams
   - [ ] Update runbooks

2. **Cleanup**
   - [ ] Remove old bot code
   - [ ] Clean up unused dependencies
   - [ ] Archive old test suites

3. **Optimization**
   - [ ] Fine-tune prompts based on production data
   - [ ] Optimize token usage
   - [ ] Implement advanced caching

---

## 🎯 Success Criteria

Migration is considered successful when:
- ✅ 100% traffic on new architecture for 7 days
- ✅ Quality metrics meet or exceed targets
- ✅ No critical incidents
- ✅ Cost within projected budget
- ✅ Team trained on new system
- ✅ All documentation updated

---

## 📞 Support & Escalation

**Issues during migration**:
1. Check #ceci-migration Slack channel
2. Review logs: `docker-compose logs -f unified_intent_bot`
3. Escalate to: Tomer (Architecture Lead)

**Emergency contacts**:
- Backend Team: backend-oncall@example.com
- OpenAI Support: (for quota issues)
- DevOps: devops-oncall@example.com

---

*Last updated: 7 July 2025*