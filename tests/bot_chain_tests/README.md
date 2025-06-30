# Bot Chain Test Suite

## Overview
Clean, efficient test suite for the CECI-AI bot chain system.

## Structure
- `test_runner.sh` - Basic tests for intent recognition and core functionality
- `test_specific_bots.sh` - Tests for individual bot behaviors  
- `test_edge_cases.sh` - Edge cases and performance tests
- `run_all_tests.sh` - Master script to run all tests

## Usage

### Run all tests:
```bash
./run_all_tests.sh
```

### Run specific test suite:
```bash
./test_runner.sh         # Basic tests only
./test_specific_bots.sh  # Bot-specific tests only
./test_edge_cases.sh     # Edge cases only
```

## Test Categories

### 1. Intent Recognition - Numbers
- Tests correct identification of limit vs government number
- Example: "3 החלטות" → limit=3

### 2. Intent Type Recognition  
- Tests routing to correct path (QUERY/STATISTICAL/EVAL)
- Example: "כמה החלטות?" → STATISTICAL

### 3. Results Validation
- Tests that results match expected counts
- Example: "3 החלטות אחרונות" → returns exactly 3

### 4. Bot-Specific Behaviors
- Rewrite bot: typo correction
- SQL bot: date handling
- Router bot: path selection

### 5. Edge Cases
- Empty queries
- Very long queries  
- Special characters
- Performance checks

## Output Format
Each test shows:
- Test name and query
- What it's checking
- PASSED/FAILED with specific error if failed
- Summary at the end

## Requirements
- curl
- jq
- bc (for performance tests)
- Bot chain running on port 8002
