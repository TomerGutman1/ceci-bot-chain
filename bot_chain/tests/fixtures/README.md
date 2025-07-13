# Test Fixtures Documentation

This directory contains standardized test data and configuration for consistent testing across all test suites.

## Structure

```
fixtures/
├── __init__.py          # Package initialization
├── test_data.py         # Core test data fixtures
├── test_config.py       # Test environment configuration
├── seed_test_data.py    # Database seeding script
└── README.md           # This file
```

## Usage

### Importing Test Data

```python
from tests.fixtures import (
    TEST_DECISIONS,
    get_test_decision,
    get_test_queries_by_type,
    validate_response
)

# Get test queries for a specific type
unclear_queries = get_test_queries_by_type("unclear")

# Get mock decision data
decision = get_test_decision(2989)

# Validate response format
is_valid = validate_response(response_text, "clarification")
```

### Using Test Configuration

```python
from tests.fixtures.test_config import (
    API_ENDPOINTS,
    get_timeout_for_query,
    is_feature_enabled
)

# Get API endpoint
chat_url = API_ENDPOINTS["chat"]

# Get appropriate timeout
timeout = get_timeout_for_query("analysis")  # Returns 30 seconds

# Check feature flags
if is_feature_enabled("USE_UNIFIED_INTENT"):
    # Use unified intent bot
```

## Test Data Categories

### Decision Numbers
- **Basic**: 1000, 1234, 2000, 2989, 3000
- **Government 36**: 1000-1004
- **Government 37**: 2000-2004, 2989
- **Government 38**: 3000-3004

### Topics
- **Education**: 1001, 2001, 2989, 3001
- **Health**: 1002, 2002, 3002
- **Transport**: 1003, 2003, 3003
- **Security**: 1004, 2004, 3004

### Query Types
- **specific_decision**: Direct decision lookups
- **government_search**: Government-based searches
- **topic_search**: Topic-based queries
- **statistical**: Count queries
- **unclear**: Ambiguous queries requiring clarification
- **reference**: Context-dependent queries
- **analysis**: Evaluation requests
- **comparison**: Comparison queries

## Seeding Test Database

To populate the database with test data:

```bash
cd bot_chain/tests/fixtures
python seed_test_data.py
```

This will:
1. Clear existing test data (decisions 1000-9999)
2. Insert standardized test decisions
3. Verify the seeded data

## Environment Variables

Configure test environment:

```bash
# Service URLs
export TEST_BACKEND_URL=http://localhost:5001
export TEST_CONTEXT_ROUTER_URL=http://localhost:8013

# Database
export TEST_DB_HOST=localhost
export TEST_DB_PORT=5433
export TEST_DB_NAME=ceci_bot_chain

# Test settings
export TEST_TIMEOUT=30
export TEST_LOG_LEVEL=INFO
```

## Performance Benchmarks

The fixtures include performance benchmarks:

- **Response times**: Expected times for different query types
- **Cache hit rates**: Expected cache performance
- **Concurrent sessions**: Load testing parameters

## Conversation Flows

Predefined conversation flows for integration testing:

- **research_flow**: Search → Count → Analyze → Compare
- **decision_exploration**: Find → Content → Details → Analysis
- **entity_accumulation**: Gradual filter building

## Best Practices

1. **Always use fixtures** for test data instead of hardcoding
2. **Seed database** before running integration tests
3. **Check feature flags** to test both old and new architectures
4. **Use appropriate timeouts** based on query type
5. **Validate responses** using provided patterns

## Adding New Test Data

To add new test data:

1. Update `test_data.py` with new fixtures
2. Add corresponding mock decisions in `MOCK_DECISIONS`
3. Update expected responses in `EXPECTED_RESPONSES`
4. Re-run seed script to update database

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker compose ps postgres

# Verify connection
psql -h localhost -p 5433 -U postgres -d ceci_bot_chain
```

### Missing Test Data
```bash
# Re-seed the database
python seed_test_data.py
```

### Feature Flag Issues
```bash
# Check current flags
python -c "from tests.fixtures.test_config import FEATURE_FLAGS; print(FEATURE_FLAGS)"
```