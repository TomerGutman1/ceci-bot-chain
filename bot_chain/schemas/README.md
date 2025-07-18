# ⚠️ WARNING: TEST SCHEMAS ONLY ⚠️

This directory contains schemas for the **TEST DATABASE** used by bot chain unit tests.

## DO NOT USE THESE SCHEMAS FOR PRODUCTION!

### Production Database:
- **Provider**: Supabase
- **Table**: `israeli_government_decisions`
- **Schema**: See `/israeli_government_decisions_DB_SCHEMA.md`

### Test Database (This Directory):
- **Provider**: Local PostgreSQL (Docker container)
- **Port**: 5433
- **Purpose**: Unit tests only
- **Table**: `government_decisions` (simplified schema)
- **Status**: Always empty except during tests

## Why Two Databases?

1. **Production (Supabase)**: Real government decision data, accessed via Supabase SDK
2. **Test (Local PostgreSQL)**: Isolated environment for bot chain unit tests

## Common Mistake to Avoid

❌ **WRONG**: Checking local PostgreSQL for production data
```bash
# This will show empty tables - it's only for tests!
docker exec ceci-postgres psql -U postgres ceci_bot_chain
```

✅ **RIGHT**: Use Supabase SDK or SQL Engine Service
```python
# Production queries go through these services
from server.src.services.sqlQueryEngine import getSQLQueryEngineService
```

## If You're Confused About Schema

Always refer to:
1. `/israeli_government_decisions_DB_SCHEMA.md` - Production schema
2. `/server/src/services/sqlQueryEngine/schema.ts` - TypeScript definitions
3. **NOT** this directory!