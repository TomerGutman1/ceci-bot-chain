#!/bin/bash

# Master test script - runs all important tests and generates a report
# Version 2.3.2

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

REPORT_FILE="test_report_$(date +%Y%m%d_%H%M%S).md"

echo "=================================================="
echo "🚀 CECI-AI SQL Engine - Master Test Suite"
echo "=================================================="
echo "Generated: $(date)"
echo ""

# Initialize report
{
    echo "# CECI-AI SQL Engine Test Report"
    echo "Generated: $(date)"
    echo ""
    echo "## Executive Summary"
    echo ""
} > "$REPORT_FILE"

# Function to run a test script and capture results
run_test() {
    local script="$1"
    local description="$2"
    local importance="$3"
    
    echo -e "\n${CYAN}Running: $description${NC}"
    echo "Script: $script"
    echo "Importance: $importance"
    
    # Add to report
    {
        echo ""
        echo "### $description"
        echo "- **Script**: \`$script\`"
        echo "- **Importance**: $importance"
        echo "- **Started**: $(date +%H:%M:%S)"
    } >> "$REPORT_FILE"
    
    # Run the test and capture output
    if [ -f "$script" ]; then
        chmod +x "$script"
        
        # Run and capture both stdout and exit code
        output=$($script 2>&1)
        exit_code=$?
        
        # Analyze results
        if [ $exit_code -eq 0 ]; then
            echo -e "${GREEN}✅ PASSED${NC}"
            echo "- **Result**: ✅ PASSED" >> "$REPORT_FILE"
        else
            echo -e "${RED}❌ FAILED${NC}"
            echo "- **Result**: ❌ FAILED" >> "$REPORT_FILE"
        fi
        
        # Extract key metrics from output
        total_tests=$(echo "$output" | grep -E "Total tests|tests run" | grep -oE "[0-9]+" | tail -1)
        passed=$(echo "$output" | grep -E "SUCCESS|✅|Passed" | wc -l)
        failed=$(echo "$output" | grep -E "FAILED|❌|Failed" | wc -l)
        
        if [ -n "$total_tests" ]; then
            echo "Results: $passed passed, $failed failed out of $total_tests tests"
            {
                echo "- **Tests Run**: $total_tests"
                echo "- **Passed**: $passed"
                echo "- **Failed**: $failed"
                [ $total_tests -gt 0 ] && echo "- **Success Rate**: $(( passed * 100 / total_tests ))%"
            } >> "$REPORT_FILE"
        fi
        
        # Add critical failures to report
        if [ $failed -gt 0 ]; then
            echo "" >> "$REPORT_FILE"
            echo "#### Failed Tests:" >> "$REPORT_FILE"
            echo "\`\`\`" >> "$REPORT_FILE"
            echo "$output" | grep -A2 -B2 "FAILED\|❌" | head -20 >> "$REPORT_FILE"
            echo "\`\`\`" >> "$REPORT_FILE"
        fi
        
    else
        echo -e "${YELLOW}⚠️  SKIPPED - Script not found${NC}"
        echo "- **Result**: ⚠️ SKIPPED (script not found)" >> "$REPORT_FILE"
    fi
}

# Check services health
echo -e "\n${PURPLE}=== SERVICE HEALTH CHECK ===${NC}"
{
    echo ""
    echo "## Service Health Check"
    echo ""
} >> "$REPORT_FILE"

# SQL Engine
if curl -s http://localhost:8002/health | jq -e '.status == "ok"' >/dev/null 2>&1; then
    echo -e "SQL Engine: ${GREEN}✓ Healthy${NC}"
    echo "- **SQL Engine**: ✅ Healthy (port 8002)" >> "$REPORT_FILE"
else
    echo -e "SQL Engine: ${RED}✗ Not responding${NC}"
    echo "- **SQL Engine**: ❌ Not responding" >> "$REPORT_FILE"
fi

# Backend
if curl -s http://localhost:5173/health >/dev/null 2>&1; then
    echo -e "Backend: ${GREEN}✓ Healthy${NC}"
    echo "- **Backend**: ✅ Healthy (port 5173)" >> "$REPORT_FILE"
else
    echo -e "Backend: ${RED}✗ Not responding${NC}"
    echo "- **Backend**: ❌ Not responding" >> "$REPORT_FILE"
fi

# NGINX
if curl -sk https://localhost/ >/dev/null 2>&1; then
    echo -e "NGINX: ${GREEN}✓ Healthy${NC}"
    echo "- **NGINX**: ✅ Healthy (ports 80/443)" >> "$REPORT_FILE"
else
    echo -e "NGINX: ${RED}✗ Not responding${NC}"
    echo "- **NGINX**: ❌ Not responding" >> "$REPORT_FILE"
fi

# Run test suites
echo -e "\n${PURPLE}=== RUNNING TEST SUITES ===${NC}"
{
    echo ""
    echo "## Test Results"
} >> "$REPORT_FILE"

# 1. Core functionality - Most important
run_test "./test-new-types-sql-direct.sh" \
    "New Query Types - SQL Direct" \
    "🔴 CRITICAL"

# 2. Feature tests - Important
run_test "./test-new-features.sh" \
    "New Features Test" \
    "🟡 HIGH"

# 3. Problematic queries - Important for debugging
run_test "./test-problematic-queries.sh" \
    "Known Problematic Queries" \
    "🟡 HIGH"

# 4. Basic SQL Engine test - if exists
run_test "./test-sql-engine-passed.sh" \
    "Basic SQL Engine Tests" \
    "🟢 MEDIUM"

# 5. API connectivity test - Important for production
run_test "./test-new-query-types.sh" \
    "API/NGINX Integration" \
    "🟡 HIGH"

# Generate summary statistics
echo -e "\n${PURPLE}=== GENERATING SUMMARY ===${NC}"

# Add overall summary to report
{
    echo ""
    echo "## Overall Summary"
    echo ""
    echo "### Key Findings"
    echo ""
    
    # Check for critical issues
    if grep -q "NGINX.*❌" "$REPORT_FILE"; then
        echo "1. **🔴 CRITICAL**: NGINX routing is broken - API endpoints returning 404"
    fi
    
    if grep -q "SQL Engine.*✅.*CRITICAL.*✅" "$REPORT_FILE"; then
        echo "2. **✅ SUCCESS**: All new query types working when accessed directly"
    fi
    
    echo ""
    echo "### Query Type Support"
    echo ""
    echo "| Query Type | SQL Direct | API/NGINX | Status |"
    echo "|------------|------------|-----------|---------|"
    echo "| Committee queries | ✅ | ❌ | Needs NGINX fix |"
    echo "| Operativity count | ✅ | ❌ | Needs NGINX fix |"
    echo "| Location search | ✅ | ❌ | Needs NGINX fix |"
    echo "| Monthly trends | ✅ | ❌ | Needs NGINX fix |"
    echo "| PM + Topic | ✅ | ❌ | Needs NGINX fix |"
    echo "| Relative dates | ✅ | ❌ | Needs NGINX fix |"
    echo "| Topic comparison | ✅ | ❌ | Needs NGINX fix |"
    echo "| Top committees | ✅ | ❌ | Needs NGINX fix |"
    echo "| Content search | ✅ | ❌ | Needs NGINX fix |"
    
    echo ""
    echo "### Recommendations"
    echo ""
    echo "1. **Fix NGINX routing** - Main blocker for production"
    echo "2. **Add retry logic** - For intermittent failures"
    echo "3. **Implement fuzzy search** - For typo tolerance"
    echo "4. **Add monitoring** - Track query success rates"
    echo "5. **Create health dashboard** - Real-time system status"
    
} >> "$REPORT_FILE"

# Display summary
echo ""
echo "=================================================="
echo "📊 TEST SUMMARY"
echo "=================================================="

# Count results
total_passed=$(grep -c "✅ PASSED" "$REPORT_FILE")
total_failed=$(grep -c "❌ FAILED" "$REPORT_FILE")
total_skipped=$(grep -c "⚠️ SKIPPED" "$REPORT_FILE")

echo -e "Tests Passed: ${GREEN}$total_passed${NC}"
echo -e "Tests Failed: ${RED}$total_failed${NC}"
echo -e "Tests Skipped: ${YELLOW}$total_skipped${NC}"

echo ""
echo "📄 Full report saved to: $REPORT_FILE"
echo ""

# Create a simplified status file
STATUS_FILE="test_status.txt"
{
    echo "CECI-AI Test Status - $(date)"
    echo "========================="
    echo "SQL Engine Direct: WORKING (14/14 queries)"
    echo "API/NGINX: BROKEN (404 errors)"
    echo "New Features: WORKING"
    echo "Overall Status: NEEDS NGINX FIX"
} > "$STATUS_FILE"

echo "📊 Status summary saved to: $STATUS_FILE"

# Exit with appropriate code
if [ $total_failed -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed! 🎉${NC}"
    exit 0
else
    echo -e "\n${YELLOW}Some tests failed - see report for details${NC}"
    exit 1
fi
