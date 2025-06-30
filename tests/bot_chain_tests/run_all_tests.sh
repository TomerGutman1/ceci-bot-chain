#!/bin/bash
# Master test script - runs all test suites

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Make all scripts executable
chmod +x *.sh

echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo -e "${YELLOW}       Bot Chain Complete Test Suite       ${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo ""

# Run individual test suites
echo -e "${BLUE}Running Basic Tests...${NC}"
./test_runner.sh

echo -e "\n${BLUE}Running Bot-Specific Tests...${NC}"
./test_specific_bots.sh

echo -e "\n${BLUE}Running Edge Case Tests...${NC}"
./test_edge_cases.sh

echo -e "\n${YELLOW}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}All test suites completed!${NC}"
