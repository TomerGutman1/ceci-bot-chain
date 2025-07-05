# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CECI Bot Chain** is a sophisticated 7-bot pipeline system for processing Hebrew queries about Israeli government decisions. The system replaces a traditional SQL engine with specialized GPT-powered bots that handle different aspects of query processing, from intent detection to response formatting.

## Key Architecture & Flow

The system follows a sequential bot pipeline:
```
User Query → 0_REWRITE → 1_INTENT → 2X_ROUTER → [2C_CLARIFY | 2Q_SQL_GEN] → 2E_EVALUATOR → 3Q_RANKER → 4_FORMATTER → Response
```

Each bot runs as a separate microservice with specific responsibilities:
- **Port 8010**: Rewrite Bot - Text normalization & Hebrew correction
- **Port 8011**: Intent Bot - Intent detection & entity extraction  
- **Port 8012**: SQL Gen Bot - SQL query generation with templates
- **Port 8013**: Context Router Bot - Context management & routing
- **Port 8014**: Evaluator Bot - Result evaluation & scoring
- **Port 8015**: Clarify Bot - Clarification question generation
- **Port 8016**: Ranker Bot - Result ranking & prioritization
- **Port 8017**: Formatter Bot - Response formatting

## Common Development Commands

**Start all services:**
```bash
docker compose up -d
```

**Check service health:**
```bash
docker compose ps
docker compose logs -f [service-name]
```

**Run tests:**
```bash
# Run all bot tests
./tests/run_bot_chain_tests.sh

# Run specific bot tests
python -m pytest tests/test_0_main_rewrite_bot.py -v
python -m pytest tests/test_1_main_intent_bot.py -v
python -m pytest tests/test_2q_sql_gen_bot.py -v
```

**Test individual bot endpoints:**
```bash
curl http://localhost:8010/health  # Rewrite Bot
curl http://localhost:8011/health  # Intent Bot
curl http://localhost:8012/health  # SQL Gen Bot
```

## Critical Development Constraints

**Budget & Cost Control:**
- Budget cap: $10/day, $0.10/query enforced by CostController
- Prefer GPT-3.5-turbo; escalate to GPT-4-turbo only via fallback
- **DO NOT run CI tests** - they are suspended due to budget constraints

**Schema Integrity Rule:**
- **NEVER change fundamental data types** - the `id` field MUST stay UUID4 as string
- All DB schema changes require explicit approval

**Current Status:**
- **Evaluator Bot (2E)**: Disabled on QUERY path to save GPT-4 tokens
- **Ranker Bot (3Q)**: Currently skipped (SKIP_RANKER=true)
- **Intent Bot**: Replaced with deterministic JavaScript Intent Recognizer (port 8011)

## Memory Service Integration

**Critical Integration Points:**
1. **BotChainService → Context Router** (server/src/services/botChainService.ts)
2. **Context Router → SQL Gen Bot** (conversation history passing)
3. **Context Router → Clarify Bot** (context-aware clarification)
4. **SQL Gen Bot → Formatter** (memory-enhanced responses)

See `MAIN_CTX_ROUTER_BOT_2X/CTX_integration_guide.md` for detailed implementation steps.

## File Structure & Navigation

**Core Bot Directories:**
- `MAIN_REWRITE_BOT_0/` - Text normalization
- `MAIN_INTENT_BOT_1/` - Intent detection (legacy, replaced by INTENT_RCGNZR_0)
- `INTENT_RCGNZR_0/` - Deterministic intent recognizer
- `QUERY_SQL_GEN_BOT_2Q/` - SQL generation with templates
- `MAIN_CTX_ROUTER_BOT_2X/` - Context management & memory service
- `CLARIFY_CLARIFY_BOT_2C/` - Clarification questions
- `EVAL_EVALUATOR_BOT_2E/` - Result evaluation
- `QUERY_RANKER_BOT_3Q/` - Result ranking
- `MAIN_FORMATTER_4/` - Response formatting

**Configuration & Common:**
- `common/` - Shared libraries (logging, config)
- `schemas/` - Database schema and API contracts
- `tests/` - Comprehensive test suite
- `docker-compose.yml` - Service orchestration

## Database Integration

**PostgreSQL Schema:**
- Main table: `government_decisions`
- Supporting: `governments`, `topics`, `ministries`
- Hebrew full-text search capabilities
- Array-based topic/ministry storage

**Connection Details:**
- Database: `ceci_bot_chain`
- Port: 5432 (internal), exposed via docker-compose
- Redis: Port 6379 for caching and memory storage

## Performance Optimization

**Token Usage per Query:**
- 0_REWRITE: ~100 tokens (GPT-3.5)
- 1_INTENT: 0 tokens (deterministic)
- 2Q_SQL_GEN: ~190 tokens (GPT-4, templates reduce by 90%)
- Total: ~290 tokens vs original ~2000+ tokens

**Caching Strategy:**
- Response cache: 4 hours TTL
- SQL template cache: 24 hours TTL
- Intent pattern cache: 24 hours TTL
- Memory service: Redis-based conversation storage

## Environment Variables

**Required:**
```bash
OPENAI_API_KEY=sk-your-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
REDIS_URL=redis://redis:6379
LOG_LEVEL=INFO
```

**Optional:**
```bash
SKIP_RANKER=true  # Skip ranking step
SKIP_EVALUATOR=true  # Skip evaluation step
```

## Testing Strategy

**Test Types:**
- Unit tests: `python -m pytest tests/test_*.py`
- Integration tests: `./tests/run_bot_chain_tests.sh`
- End-to-end: `./tests/test_e2e_simple.py`

**Test Data:**
- Hebrew query samples in `tests/manual_test_cases_hebrew.md`
- Edge cases in `tests/test_edge_cases.sh`
- Token tracking in `tests/token_tracking/`

## Monitoring & Observability

**Health Checks:**
- All bots expose `/health` endpoints
- 30-second intervals with 10-second timeout
- Prometheus metrics on `/metrics`

**Debugging:**
- Conversation IDs for request tracing
- Detailed logging in `common/logging.py`
- Token usage tracking per bot

## Common Gotchas

**Python Module Naming:**
- Modules starting with numbers cause import issues
- Use service aliases in docker-compose.yml

**Hebrew Text Processing:**
- Complex normalization edge cases
- Ensure UTF-8 encoding throughout
- Test with actual Hebrew samples

**Memory Management:**
- Trim conversation history to prevent large payloads
- Implement graceful fallbacks for missing context
- Maintain backward compatibility for legacy requests

## Integration with Main System

**Backend Integration:**
- Main backend: `../server/src/services/botChainService.ts`
- Frontend: `../src/components/chat/ChatInterface.tsx`
- Service ports: Backend 5001, Frontend 3001

**API Contracts:**
- OpenAPI specifications in `openapi/bot-chain.yml`
- Request/response models in individual bot `main.py` files
- Conversation context models in `MAIN_CTX_ROUTER_BOT_2X/`