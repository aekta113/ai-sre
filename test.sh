#!/bin/bash
# AI SRE Test Suite
# Comprehensive testing for the AI SRE container and MCP Server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
CONTAINER_NAME="ai-sre-test"
MCP_SERVER_URL="http://localhost:8080"
TIMEOUT=30

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test function wrapper
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    ((TOTAL_TESTS++))
    log_info "Running test: $test_name"
    
    if eval "$test_command"; then
        log_success "$test_name"
        return 0
    else
        log_error "$test_name"
        return 1
    fi
}

# Wait for service to be ready
wait_for_service() {
    local url="$1"
    local max_attempts=30
    local attempt=1
    
    log_info "Waiting for service at $url to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            log_success "Service is ready after $attempt attempts"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts - waiting..."
        sleep 2
        ((attempt++))
    done
    
    log_error "Service failed to become ready after $max_attempts attempts"
    return 1
}

# Test container startup
test_container_startup() {
    log_info "Testing container startup..."
    
    # Start container
    docker run -d --name "$CONTAINER_NAME" \
        -p 8080:8080 \
        -e AGENT_LOG_LEVEL=DEBUG \
        ai-sre:latest
    
    # Wait for container to be ready
    sleep 5
    
    # Check if container is running
    if docker ps --filter name="$CONTAINER_NAME" --filter status=running | grep -q "$CONTAINER_NAME"; then
        return 0
    else
        log_error "Container failed to start"
        docker logs "$CONTAINER_NAME"
        return 1
    fi
}

# Test MCP Server health endpoints
test_health_endpoints() {
    run_test "Health endpoint" "curl -s $MCP_SERVER_URL/health | jq -e '.status == \"healthy\"'"
    run_test "Ready endpoint" "curl -s $MCP_SERVER_URL/ready | jq -e '.status == \"ready\"'"
    run_test "Version endpoint" "curl -s $MCP_SERVER_URL/version | jq -e '.service == \"ai-sre-mcp-server\"'"
}

# Test kubectl functionality
test_kubectl_endpoints() {
    run_test "Kubectl version" "curl -s -X POST $MCP_SERVER_URL/kubectl/version -H 'Content-Type: application/json' -d '{}' | jq -e '.result.success == true'"
    run_test "Kubectl get nodes" "curl -s -X POST $MCP_SERVER_URL/kubectl/get -H 'Content-Type: application/json' -d '{\"resource\": \"nodes\", \"output\": \"json\"}' | jq -e '.result.success == true'"
}

# Test git functionality
test_git_endpoints() {
    run_test "Git version" "curl -s -X POST $MCP_SERVER_URL/git/status -H 'Content-Type: application/json' -d '{}' | jq -e '.result.success == true'"
}

# Test flux functionality
test_flux_endpoints() {
    run_test "Flux version" "curl -s -X POST $MCP_SERVER_URL/flux/version -H 'Content-Type: application/json' -d '{}' | jq -e '.result.success == true'"
}

# Test container tools
test_container_tools() {
    run_test "kubectl available" "docker exec $CONTAINER_NAME kubectl version --client"
    run_test "helm available" "docker exec $CONTAINER_NAME helm version --client"
    run_test "flux available" "docker exec $CONTAINER_NAME flux version --client"
    run_test "git available" "docker exec $CONTAINER_NAME git --version"
    run_test "github-cli available" "docker exec $CONTAINER_NAME gh --version"
    run_test "jq available" "docker exec $CONTAINER_NAME jq --version"
    run_test "yq available" "docker exec $CONTAINER_NAME yq --version"
}

# Test container security
test_container_security() {
    run_test "Non-root user" "docker exec $CONTAINER_NAME whoami | grep -q aisre"
    run_test "Read-only filesystem check" "docker exec $CONTAINER_NAME test -w /app"
}

# Test container performance
test_container_performance() {
    run_test "Container size check" "[ \$(docker images ai-sre:latest --format '{{.Size}}' | sed 's/[^0-9.]//g' | awk -F. '{print \$1}') -lt 1000 ]"
    
    # Test memory usage (should be less than 256MB)
    local memory_usage=$(docker stats --no-stream --format "{{.MemUsage}}" "$CONTAINER_NAME" | awk -F'/' '{print $1}' | sed 's/[^0-9.]//g')
    if [ -n "$memory_usage" ] && [ "$(echo "$memory_usage < 256" | bc -l)" -eq 1 ]; then
        log_success "Memory usage check (< 256MB)"
    else
        log_error "Memory usage check (< 256MB) - Current: ${memory_usage}MB"
    fi
}

# Test error handling
test_error_handling() {
    run_test "Invalid kubectl command" "curl -s -X POST $MCP_SERVER_URL/kubectl/invalid -H 'Content-Type: application/json' -d '{}' | jq -e '.result.success == false'"
    run_test "Invalid git command" "curl -s -X POST $MCP_SERVER_URL/git/invalid -H 'Content-Type: application/json' -d '{}' | jq -e '.result.success == false'"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up test environment..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
}

# Main test execution
main() {
    echo "=========================================="
    echo "AI SRE Test Suite"
    echo "=========================================="
    
    # Set up cleanup trap
    trap cleanup EXIT
    
    # Run tests
    log_info "Starting comprehensive test suite..."
    
    # Container tests
    test_container_startup
    wait_for_service "$MCP_SERVER_URL/health"
    
    # Tool availability tests
    test_container_tools
    
    # Security tests
    test_container_security
    
    # Performance tests
    test_container_performance
    
    # API endpoint tests
    test_health_endpoints
    test_kubectl_endpoints
    test_git_endpoints
    test_flux_endpoints
    
    # Error handling tests
    test_error_handling
    
    # Print test results
    echo ""
    echo "=========================================="
    echo "Test Results Summary"
    echo "=========================================="
    echo "Total Tests: $TOTAL_TESTS"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed! 🎉${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed! ❌${NC}"
        exit 1
    fi
}

# Check dependencies
check_dependencies() {
    local deps=("docker" "curl" "jq" "bc")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "Required dependency '$dep' is not installed"
            exit 1
        fi
    done
}

# Run main function
check_dependencies
main
