# Task: Remove All Mock Data and Test Data Usage

## Objective
Remove all possibilities of using mock data in the system. Ensure that all links are real and working (from the database), and all decisions or analysis are based entirely on real data.

## Todo List

### 1. Remove Test Data Infrastructure
- [ ] Delete test data fixtures files
- [ ] Remove seed_test_data.py script
- [ ] Clean up test_data.py with mock decisions

### 2. Clean Bot Chain Test Infrastructure
- [ ] Remove any references to mock decisions (2989, 2000, 1999, etc.) from bot implementations
- [ ] Ensure no bot is returning hardcoded responses
- [ ] Remove test fixture imports from all production code

### 3. Backend Service Cleanup
- [ ] Remove mock_chain test endpoint from chat routes
- [ ] Remove any test mode flags or conditions
- [ ] Ensure botChainService only uses real database queries

### 4. Database Cleanup
- [ ] Create script to remove any test decisions (1000-9999 range) from production database
- [ ] Verify all remaining decisions have real URLs from gov.il

### 5. Documentation Updates
- [ ] Update README files to remove references to test data
- [ ] Update CLAUDE.md to note that no mock data is allowed

### 6. Verification
- [ ] Test with real queries to ensure real data is returned
- [ ] Verify all URLs point to actual government decision pages
- [ ] Ensure no hardcoded decision numbers appear in responses

## Notes
- The test data includes decisions like 2989, 2000, 1999 which might be contaminating production responses
- All URLs must come from the database decision_url field
- No placeholder or generated URLs are acceptable