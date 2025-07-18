-- ⚠️ WARNING: TEST DATABASE ONLY ⚠️
-- This PostgreSQL database is used ONLY for bot chain unit tests
-- The actual production data is in Supabase (israeli_government_decisions table)
-- DO NOT confuse this with production data!

-- This schema exists only to support test fixtures in bot_chain/tests/
-- It mimics a simplified version of government decisions for testing
-- See: bot_chain/tests/fixtures/seed_test_data.py

-- The real schema is documented in:
-- 1. /israeli_government_decisions_DB_SCHEMA.md (Supabase production schema)
-- 2. /server/src/services/sqlQueryEngine/schema.ts (TypeScript schema definition)

-- TEST TABLES (not used in production):
-- government_decisions, topics, ministries, etc.