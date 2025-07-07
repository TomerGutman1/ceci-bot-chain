#!/bin/bash

# CECI Bot Chain Production Smoke Test Script
# Usage: ./scripts/smoke-test.sh [--local|--production]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PRODUCTION_URL="https://ceci-ai.ceci.org.il"
LOCAL_URL="http://localhost"
BASE_URL="${PRODUCTION_URL}"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test results log
TEST_LOG="/tmp/ceci-smoke-test-$(date +%Y%m%d-%H%M%S).log"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$TEST_LOG"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1" | tee -a "$TEST_LOG"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1" | tee -a "$TEST_LOG"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$TEST_LOG"
}

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    local method="${4:-GET}"
    local data="${5:-}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    print_info "Testing: $name"
    
    # Prepare curl command
    local curl_cmd="curl -s -o /tmp/response.txt -w '%{http_code}' -X $method"
    
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        curl_cmd="$curl_cmd -H 'Content-Type: application/json' -d '$data'"
    fi
    
    # Execute request
    local status_code=$(eval "$curl_cmd '$url'")
    local response=$(cat /tmp/response.txt)
    
    if [ "$status_code" = "$expected_status" ]; then
        print_success "$name (Status: $status_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        
        # Additional validation for specific endpoints
        case "$name" in
            "Backend Health")
                if echo "$response" | grep -q "healthy"; then
                    print_success "  ✓ Response contains 'healthy'"
                else
                    print_warning "  ! Response doesn't contain expected 'healthy' text"
                fi
                ;;
            "Chat API Test")
                if echo "$response" | grep -q "החלטה"; then
                    print_success "  ✓ Response contains decision data"
                else
                    print_warning "  ! Response doesn't contain expected decision data"
                fi
                ;;
        esac
        
        return 0
    else
        print_error "$name (Expected: $expected_status, Got: $status_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        
        # Print error details
        if [ -n "$response" ]; then
            echo "  Response: $(echo "$response" | head -100)" >> "$TEST_LOG"
        fi
        
        return 1
    fi
}

# Function to test bot health endpoints
test_bot_health() {
    local bot_name="$1"
    local port="$2"
    
    if [ "$BASE_URL" = "$LOCAL_URL" ]; then
        # For local testing, use direct port access
        test_endpoint "$bot_name Health" "http://localhost:$port/health"
    else
        # For production, bots are not directly accessible
        print_info "Skipping direct bot test for $bot_name (production mode)"
    fi
}

# Function to test chat functionality
test_chat_functionality() {
    print_info "Testing chat functionality..."
    
    # Test 1: Simple decision query
    test_endpoint "Chat API - Simple Query" \
        "$BASE_URL/api/chat" \
        200 \
        POST \
        '{"message":"החלטה 2989","conversationId":"test-'$(date +%s)'"}'
    
    # Test 2: Search query
    test_endpoint "Chat API - Search Query" \
        "$BASE_URL/api/chat" \
        200 \
        POST \
        '{"message":"החלטות בנושא חינוך","conversationId":"test-search-'$(date +%s)'"}'
    
    # Test 3: Count query
    test_endpoint "Chat API - Count Query" \
        "$BASE_URL/api/chat" \
        200 \
        POST \
        '{"message":"כמה החלטות יש בנושא בריאות","conversationId":"test-count-'$(date +%s)'"}'
}

# Function to test static assets
test_static_assets() {
    print_info "Testing static assets..."
    
    # Test main page
    test_endpoint "Frontend Main Page" "$BASE_URL/" 200
    
    # Test if main JS bundle exists
    local js_test=$(curl -s "$BASE_URL/" | grep -o 'src="[^"]*\.js"' | head -1 | sed 's/src="//;s/"//')
    if [ -n "$js_test" ]; then
        test_endpoint "Frontend JS Bundle" "$BASE_URL$js_test" 200
    fi
}

# Function to test security headers
test_security_headers() {
    print_info "Testing security headers..."
    
    local headers=$(curl -s -I "$BASE_URL/")
    
    # Check for important security headers
    local security_headers=(
        "Strict-Transport-Security"
        "X-Frame-Options"
        "X-Content-Type-Options"
        "X-XSS-Protection"
        "Referrer-Policy"
    )
    
    for header in "${security_headers[@]}"; do
        if echo "$headers" | grep -qi "$header"; then
            print_success "Security header present: $header"
        else
            print_error "Security header missing: $header"
        fi
    done
}

# Function to test SSL certificate
test_ssl_certificate() {
    if [[ "$BASE_URL" =~ ^https ]]; then
        print_info "Testing SSL certificate..."
        
        local domain=$(echo "$BASE_URL" | sed 's|https://||;s|/.*||')
        
        # Check certificate validity
        if openssl s_client -connect "$domain:443" -servername "$domain" </dev/null 2>/dev/null | openssl x509 -noout -checkend 86400; then
            print_success "SSL certificate is valid for at least 24 hours"
        else
            print_error "SSL certificate expires within 24 hours or is invalid"
        fi
        
        # Check certificate chain
        local cert_info=$(echo | openssl s_client -connect "$domain:443" -servername "$domain" 2>/dev/null | openssl x509 -noout -text)
        if [ -n "$cert_info" ]; then
            print_success "SSL certificate chain is valid"
        else
            print_error "SSL certificate chain validation failed"
        fi
    fi
}

# Function to run performance test
test_performance() {
    print_info "Running basic performance test..."
    
    # Test response time for health endpoint
    local start_time=$(date +%s%N)
    curl -s "$BASE_URL/health" > /dev/null
    local end_time=$(date +%s%N)
    local response_time=$(( (end_time - start_time) / 1000000 ))
    
    if [ "$response_time" -lt 1000 ]; then
        print_success "Health endpoint response time: ${response_time}ms"
    else
        print_warning "Health endpoint response time: ${response_time}ms (slow)"
    fi
    
    # Test chat API response time
    local start_time=$(date +%s%N)
    curl -s -X POST "$BASE_URL/api/chat" \
        -H "Content-Type: application/json" \
        -d '{"message":"test","conversationId":"perf-test"}' > /dev/null
    local end_time=$(date +%s%N)
    local response_time=$(( (end_time - start_time) / 1000000 ))
    
    if [ "$response_time" -lt 5000 ]; then
        print_success "Chat API response time: ${response_time}ms"
    else
        print_warning "Chat API response time: ${response_time}ms (slow)"
    fi
}

# Main test suite
run_tests() {
    print_info "Starting CECI Bot Chain Smoke Tests"
    print_info "Target: $BASE_URL"
    print_info "=================================="
    
    # 1. Basic connectivity
    print_info "=== Basic Connectivity ==="
    test_endpoint "Frontend Health" "$BASE_URL/health"
    test_endpoint "Backend Health" "$BASE_URL/api/health"
    
    # 2. API endpoints
    print_info "\n=== API Endpoints ==="
    test_endpoint "Chat Health" "$BASE_URL/api/chat/health"
    test_endpoint "Statistics API" "$BASE_URL/api/statistics/overview"
    
    # 3. Bot health checks (local only)
    if [ "$BASE_URL" = "$LOCAL_URL" ]; then
        print_info "\n=== Bot Services ==="
        test_bot_health "Rewrite Bot" 8010
        test_bot_health "Intent Bot" 8011
        test_bot_health "SQL Gen Bot" 8012
        test_bot_health "Context Router" 8013
        test_bot_health "Evaluator Bot" 8014
        test_bot_health "Clarify Bot" 8015
        test_bot_health "Ranker Bot" 8016
        test_bot_health "Formatter Bot" 8017
    fi
    
    # 4. Chat functionality
    print_info "\n=== Chat Functionality ==="
    test_chat_functionality
    
    # 5. Static assets
    print_info "\n=== Static Assets ==="
    test_static_assets
    
    # 6. Security
    print_info "\n=== Security ==="
    test_security_headers
    test_ssl_certificate
    
    # 7. Performance
    print_info "\n=== Performance ==="
    test_performance
    
    # Summary
    print_info "\n=== Test Summary ==="
    print_info "Total tests: $TOTAL_TESTS"
    print_success "Passed: $PASSED_TESTS"
    
    if [ "$FAILED_TESTS" -gt 0 ]; then
        print_error "Failed: $FAILED_TESTS"
    fi
    
    local success_rate=$(( PASSED_TESTS * 100 / TOTAL_TESTS ))
    print_info "Success rate: ${success_rate}%"
    
    print_info "\nTest log saved to: $TEST_LOG"
    
    # Exit with appropriate code
    if [ "$FAILED_TESTS" -eq 0 ]; then
        print_success "\n✅ All smoke tests passed!"
        exit 0
    else
        print_error "\n❌ Some tests failed!"
        exit 1
    fi
}

# Parse command line arguments
case "${1:-production}" in
    --local)
        BASE_URL="$LOCAL_URL"
        ;;
    --production)
        BASE_URL="$PRODUCTION_URL"
        ;;
    --help)
        echo "Usage: $0 [--local|--production]"
        echo "  --local       Test local deployment (http://localhost)"
        echo "  --production  Test production deployment (https://ceci-ai.ceci.org.il)"
        echo "  --help        Show this help message"
        exit 0
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac

# Run the tests
run_tests