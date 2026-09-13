#!/bin/bash

# E2E Test Runner for PunterEdge
# Usage: ./run_e2e_tests.sh [--url URL] [--headless] [--admin-email EMAIL] [--admin-password PASSWORD]

set -e

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
TEST_URL="http://localhost:8000"
HEADLESS_MODE=""
ADMIN_EMAIL="info@fm8.global"
ADMIN_PASSWORD="admin123"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            TEST_URL="$2"
            shift 2
            ;;
        --headless)
            HEADLESS_MODE="--headless"
            shift
            ;;
        --admin-email)
            ADMIN_EMAIL="$2"
            shift 2
            ;;
        --admin-password)
            ADMIN_PASSWORD="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${YELLOW}==============================================================${NC}"
echo -e "${YELLOW}PunterEdge E2E Test Suite${NC}"
echo -e "${YELLOW}==============================================================${NC}\n"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"

# Check if test script exists
if [ ! -f "e2e_test_automated.py" ]; then
    echo -e "${RED}✗ e2e_test_automated.py not found in current directory${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Test script found${NC}\n"

# Install test dependencies
echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install -q -r requirements-test.txt || {
    echo -e "${RED}✗ Failed to install test dependencies${NC}"
    exit 1
}

echo -e "${GREEN}✓ Dependencies installed${NC}\n"

# Run tests
echo -e "${YELLOW}Running tests against: $TEST_URL${NC}\n"

python3 e2e_test_automated.py \
    --url "$TEST_URL" \
    --admin-email "$ADMIN_EMAIL" \
    --admin-password "$ADMIN_PASSWORD" \
    $HEADLESS_MODE

TEST_RESULT=$?

echo -e "\n${YELLOW}==============================================================${NC}"
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}E2E Tests Passed${NC}"
else
    echo -e "${RED}E2E Tests Failed${NC}"
fi
echo -e "${YELLOW}==============================================================${NC}\n"

exit $TEST_RESULT
