#!/bin/bash
# Ávila DevOps SaaS - Load Test Runner (Bash)
# Automates load testing with k6 and generates reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_URL="${BASE_URL:-https://aviladevops.com.br}"
RESULTS_DIR="${RESULTS_DIR:-$SCRIPT_DIR/../../test-results}"
K6_SCRIPT="${K6_SCRIPT:-$SCRIPT_DIR/load-test-k6.js}"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Banner
echo -e "${BLUE}"
echo "=========================================="
echo "  Ávila DevOps SaaS - Load Test Runner"
echo "=========================================="
echo -e "${NC}"

# Check if k6 is installed
if ! command -v k6 &> /dev/null; then
    echo -e "${RED}❌ k6 is not installed${NC}"
    echo ""
    echo "To install k6:"
    echo "  - macOS: brew install k6"
    echo "  - Linux: sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69"
    echo "           echo 'deb https://dl.k6.io/deb stable main' | sudo tee /etc/apt/sources.list.d/k6.list"
    echo "           sudo apt-get update"
    echo "           sudo apt-get install k6"
    echo "  - Docker: docker run --rm -i grafana/k6 run - <$K6_SCRIPT"
    echo ""
    exit 1
fi

# Verify base URL is accessible
echo -e "${YELLOW}🔍 Checking system availability...${NC}"
if curl -s --head --request GET "$BASE_URL/health" | grep "200" > /dev/null; then
    echo -e "${GREEN}✅ System is accessible at $BASE_URL${NC}"
else
    echo -e "${RED}❌ System is not accessible at $BASE_URL${NC}"
    echo "Please check:"
    echo "  - Is the system running?"
    echo "  - Is the BASE_URL correct?"
    echo "  - Are there any network issues?"
    exit 1
fi

# Get system info before test
echo ""
echo -e "${YELLOW}📊 Pre-test system check...${NC}"
echo "Base URL: $BASE_URL"
echo "K6 Version: $(k6 version)"
echo "Test Script: $K6_SCRIPT"
echo "Results Directory: $RESULTS_DIR"

# Timestamp for this test run
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_FILE="$RESULTS_DIR/load-test-$TIMESTAMP.json"
HTML_REPORT="$RESULTS_DIR/load-test-$TIMESTAMP.html"

# Run the load test
echo ""
echo -e "${BLUE}🚀 Starting load test...${NC}"
echo "Target: 1000+ concurrent requests per second"
echo "Duration: ~45 minutes (full test cycle)"
echo ""

# Export environment variables
export BASE_URL

# Run k6 with detailed output
k6 run \
    --out json="$RESULTS_FILE" \
    --summary-export="$RESULTS_DIR/summary-$TIMESTAMP.json" \
    --verbose \
    "$K6_SCRIPT"

# Check test results
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Load test completed successfully!${NC}"
else
    echo -e "${RED}❌ Load test failed or had warnings${NC}"
fi

# Generate HTML report if k6-reporter is available
if command -v k6-to-junit &> /dev/null; then
    echo ""
    echo -e "${YELLOW}📝 Generating HTML report...${NC}"
    k6-to-junit "$RESULTS_FILE" > "$RESULTS_DIR/junit-$TIMESTAMP.xml"
    echo -e "${GREEN}✅ JUnit report generated${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}=========================================="
echo "  Test Results Summary"
echo "==========================================${NC}"
echo ""
echo "Results saved to:"
echo "  - JSON: $RESULTS_FILE"
echo "  - Summary: $RESULTS_DIR/summary-$TIMESTAMP.json"
echo ""

# Parse key metrics from summary if available
SUMMARY_FILE="$RESULTS_DIR/summary-$TIMESTAMP.json"
if [ -f "$SUMMARY_FILE" ]; then
    echo -e "${YELLOW}📈 Key Metrics:${NC}"
    
    # Extract metrics using jq if available
    if command -v jq &> /dev/null; then
        TOTAL_REQUESTS=$(jq -r '.metrics.http_reqs.values.count' "$SUMMARY_FILE")
        REQ_RATE=$(jq -r '.metrics.http_reqs.values.rate' "$SUMMARY_FILE")
        AVG_DURATION=$(jq -r '.metrics.http_req_duration.values.avg' "$SUMMARY_FILE")
        P95_DURATION=$(jq -r '.metrics.http_req_duration.values["p(95)"]' "$SUMMARY_FILE")
        ERROR_RATE=$(jq -r '.metrics.http_req_failed.values.rate' "$SUMMARY_FILE")
        
        echo "  Total Requests: $TOTAL_REQUESTS"
        echo "  Request Rate: $(printf '%.2f' $REQ_RATE) req/s"
        echo "  Avg Response Time: $(printf '%.2f' $AVG_DURATION) ms"
        echo "  p95 Response Time: $(printf '%.2f' $P95_DURATION) ms"
        echo "  Error Rate: $(printf '%.2f%%' $(echo "$ERROR_RATE * 100" | bc))"
        
        # Check success criteria
        echo ""
        echo -e "${YELLOW}✅ Success Criteria:${NC}"
        
        # p95 < 300ms
        if (( $(echo "$P95_DURATION < 300" | bc -l) )); then
            echo -e "  ${GREEN}✅ p95 < 300ms: PASS${NC}"
        else
            echo -e "  ${RED}❌ p95 < 300ms: FAIL (${P95_DURATION}ms)${NC}"
        fi
        
        # Error rate < 1%
        if (( $(echo "$ERROR_RATE < 0.01" | bc -l) )); then
            echo -e "  ${GREEN}✅ Error rate < 1%: PASS${NC}"
        else
            ERROR_PCT=$(echo "$ERROR_RATE * 100" | bc)
            echo -e "  ${RED}❌ Error rate < 1%: FAIL (${ERROR_PCT}%)${NC}"
        fi
        
        # Rate > 1000 req/s
        if (( $(echo "$REQ_RATE > 1000" | bc -l) )); then
            echo -e "  ${GREEN}✅ Rate > 1000 req/s: PASS${NC}"
        else
            echo -e "  ${RED}❌ Rate > 1000 req/s: FAIL (${REQ_RATE} req/s)${NC}"
        fi
    else
        echo "  (Install 'jq' for detailed metrics parsing)"
    fi
fi

echo ""
echo -e "${BLUE}==========================================${NC}"

# Clean up old test results (keep last 10)
echo ""
echo -e "${YELLOW}🧹 Cleaning up old test results...${NC}"
cd "$RESULTS_DIR"
ls -t load-test-*.json 2>/dev/null | tail -n +11 | xargs -r rm
echo -e "${GREEN}✅ Cleanup complete${NC}"

# Exit with k6's exit code
exit $EXIT_CODE
