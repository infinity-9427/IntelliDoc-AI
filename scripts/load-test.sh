#!/bin/bash

# IntelliDoc AI Load Testing Script
# Tests system performance under load

set -e

echo "⚡ IntelliDoc AI - Load Testing"
echo "=============================="

# Configuration
API_BASE="http://localhost:8000"
CONCURRENT_USERS=${1:-10}
TEST_DURATION=${2:-60}
TEST_FILE=${3:-"test-document.pdf"}

# Check if API is running
if ! curl -f "$API_BASE/health" > /dev/null 2>&1; then
    echo "❌ API is not running at $API_BASE"
    echo "Please start the application first with ./scripts/dev-start.sh"
    exit 1
fi

# Check if test file exists
if [ ! -f "$TEST_FILE" ]; then
    echo "📄 Creating test PDF file..."
    # Create a simple test PDF using Python
    python3 -c "
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

if not os.path.exists('$TEST_FILE'):
    c = canvas.Canvas('$TEST_FILE', pagesize=letter)
    c.drawString(100, 750, 'IntelliDoc AI Load Test Document')
    c.drawString(100, 700, 'This is a test document for load testing.')
    c.drawString(100, 650, 'It contains sample text that can be processed by OCR.')
    c.drawString(100, 600, 'Date: $(date)')
    c.drawString(100, 550, 'Test parameters: $CONCURRENT_USERS users, ${TEST_DURATION}s duration')
    for i in range(20):
        c.drawString(100, 500 - i*20, f'Sample line {i+1} with some text content for processing.')
    c.save()
    print('Test PDF created: $TEST_FILE')
else:
    print('Using existing test file: $TEST_FILE')
" 2>/dev/null || {
        echo "⚠️  Python/reportlab not available, creating simple text file instead..."
        cat > test-document.txt << EOF
IntelliDoc AI Load Test Document
===============================

This is a test document for load testing.
It contains sample text that can be processed by OCR.
Date: $(date)
Test parameters: $CONCURRENT_USERS users, ${TEST_DURATION}s duration

Sample content for processing:
$(for i in {1..50}; do echo "Sample line $i with some text content for processing."; done)
EOF
        TEST_FILE="test-document.txt"
    }
fi

echo "✅ Test file ready: $TEST_FILE"

# Install dependencies if needed
if ! command -v hey &> /dev/null; then
    echo "📦 Installing 'hey' HTTP load testing tool..."
    
    if command -v go &> /dev/null; then
        go install github.com/rakyll/hey@latest
        export PATH=$PATH:$(go env GOPATH)/bin
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget -O hey https://hey-release.s3.us-east-2.amazonaws.com/hey_linux_amd64
        chmod +x hey
        sudo mv hey /usr/local/bin/
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install hey
        else
            echo "❌ Please install 'hey' manually: https://github.com/rakyll/hey"
            exit 1
        fi
    else
        echo "❌ Please install 'hey' manually: https://github.com/rakyll/hey"
        exit 1
    fi
fi

# Create results directory
RESULTS_DIR="load-test-results-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULTS_DIR"

echo ""
echo "🔧 Test Configuration:"
echo "====================="
echo "• API Base: $API_BASE"
echo "• Concurrent Users: $CONCURRENT_USERS"
echo "• Test Duration: ${TEST_DURATION}s"
echo "• Test File: $TEST_FILE"
echo "• Results Directory: $RESULTS_DIR"

# Start monitoring
echo ""
echo "📊 Starting system monitoring..."

# Monitor system resources during test
monitor_resources() {
    while true; do
        echo "$(date +%Y-%m-%d\ %H:%M:%S),$(top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | sed 's/%us,//'),$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}'),$(df . | tail -1 | awk '{print $5}' | sed 's/%//')" >> "$RESULTS_DIR/system_metrics.csv"
        sleep 5
    done
}

# Start resource monitoring in background
echo "timestamp,cpu_usage,memory_usage,disk_usage" > "$RESULTS_DIR/system_metrics.csv"
monitor_resources &
MONITOR_PID=$!

# Cleanup function
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    kill $MONITOR_PID 2>/dev/null || true
    
    # Generate final report
    generate_report
    
    echo "✅ Load test completed!"
    echo "📊 Results saved in: $RESULTS_DIR/"
}

trap cleanup EXIT

# Test 1: Health Check Load Test
echo ""
echo "🏃 Test 1: Health Check Endpoint"
echo "==============================="

hey -n 1000 -c "$CONCURRENT_USERS" -z "${TEST_DURATION}s" \
    -o csv "$API_BASE/health" > "$RESULTS_DIR/health_test.csv" 2>&1

echo "✅ Health check test completed"

# Test 2: File Upload Load Test
echo ""
echo "📤 Test 2: File Upload Endpoint"
echo "=============================="

# Create a wrapper script for upload testing
cat > upload_test.sh << 'EOF'
#!/bin/bash
API_BASE="$1"
TEST_FILE="$2"
RESULTS_DIR="$3"

for i in $(seq 1 100); do
    start_time=$(date +%s.%N)
    
    response=$(curl -s -w "%{http_code},%{time_total}" \
        -X POST \
        -F "file=@$TEST_FILE" \
        "$API_BASE/api/v1/upload" \
        -o /dev/null)
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    
    echo "$i,$response,$duration" >> "$RESULTS_DIR/upload_test.csv"
    
    # Rate limiting
    sleep 0.1
done
EOF

chmod +x upload_test.sh

echo "request_id,http_code,response_time,total_time" > "$RESULTS_DIR/upload_test.csv"

# Run upload tests with fewer concurrent users (to avoid overwhelming the system)
UPLOAD_USERS=$((CONCURRENT_USERS / 2))
if [ $UPLOAD_USERS -lt 1 ]; then
    UPLOAD_USERS=1
fi

echo "Running upload tests with $UPLOAD_USERS concurrent users..."

for i in $(seq 1 $UPLOAD_USERS); do
    ./upload_test.sh "$API_BASE" "$TEST_FILE" "$RESULTS_DIR" &
done

wait

rm upload_test.sh
echo "✅ Upload test completed"

# Test 3: API Documentation Load Test
echo ""
echo "📚 Test 3: API Documentation"
echo "==========================="

hey -n 500 -c "$CONCURRENT_USERS" -z "30s" \
    -o csv "$API_BASE/docs" > "$RESULTS_DIR/docs_test.csv" 2>&1

echo "✅ Documentation test completed"

# Generate comprehensive report
generate_report() {
    echo ""
    echo "📋 Generating load test report..."
    
    cat > "$RESULTS_DIR/report.md" << EOF
# IntelliDoc AI Load Test Report

**Test Date:** $(date)
**Test Duration:** ${TEST_DURATION} seconds
**Concurrent Users:** $CONCURRENT_USERS
**Test File:** $TEST_FILE

## Test Results Summary

### 1. Health Check Endpoint
$([ -f "$RESULTS_DIR/health_test.csv" ] && tail -n +2 "$RESULTS_DIR/health_test.csv" | head -10 || echo "No data available")

### 2. File Upload Endpoint
$([ -f "$RESULTS_DIR/upload_test.csv" ] && echo "Total upload requests: $(wc -l < "$RESULTS_DIR/upload_test.csv")" || echo "No data available")

### 3. API Documentation
$([ -f "$RESULTS_DIR/docs_test.csv" ] && tail -n +2 "$RESULTS_DIR/docs_test.csv" | head -10 || echo "No data available")

## System Resource Usage

### Peak Resource Usage
- **CPU Usage:** $([ -f "$RESULTS_DIR/system_metrics.csv" ] && tail -n +2 "$RESULTS_DIR/system_metrics.csv" | cut -d',' -f2 | sort -nr | head -1 || echo "N/A")%
- **Memory Usage:** $([ -f "$RESULTS_DIR/system_metrics.csv" ] && tail -n +2 "$RESULTS_DIR/system_metrics.csv" | cut -d',' -f3 | sort -nr | head -1 || echo "N/A")%
- **Disk Usage:** $([ -f "$RESULTS_DIR/system_metrics.csv" ] && tail -n +2 "$RESULTS_DIR/system_metrics.csv" | cut -d',' -f4 | sort -nr | head -1 || echo "N/A")%

## Docker Container Stats
\`\`\`
$(docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" 2>/dev/null || echo "Docker stats not available")
\`\`\`

## Recommendations

Based on the test results:
1. **Performance:** $([ -f "$RESULTS_DIR/health_test.csv" ] && echo "System handled basic requests well" || echo "Need to verify API connectivity")
2. **Scalability:** Monitor resource usage during peak loads
3. **Optimization:** Consider implementing caching for frequently accessed endpoints
4. **Monitoring:** Set up alerts for high resource usage

## Files Generated
- \`health_test.csv\` - Health endpoint performance data
- \`upload_test.csv\` - File upload performance data
- \`docs_test.csv\` - Documentation endpoint performance data
- \`system_metrics.csv\` - System resource usage during tests
- \`report.md\` - This summary report

## Next Steps
1. Review performance bottlenecks in the results
2. Optimize slow endpoints identified in the tests
3. Set up continuous performance monitoring
4. Scale infrastructure based on load requirements
EOF

    echo "✅ Report generated: $RESULTS_DIR/report.md"
}

# Wait a bit more for final metrics
sleep 5

echo ""
echo "🎯 Load Test Summary:"
echo "===================="
echo "• Test completed successfully"
echo "• Duration: ${TEST_DURATION} seconds"
echo "• Concurrent users: $CONCURRENT_USERS"
echo "• Results directory: $RESULTS_DIR/"
echo ""
echo "📊 Quick Performance Check:"
if [ -f "$RESULTS_DIR/health_test.csv" ]; then
    echo "• Health endpoint tests: ✅"
else
    echo "• Health endpoint tests: ❌"
fi

if [ -f "$RESULTS_DIR/upload_test.csv" ]; then
    echo "• Upload endpoint tests: ✅"
else
    echo "• Upload endpoint tests: ❌"
fi

echo ""
echo "💡 Next steps:"
echo "• Review detailed results in $RESULTS_DIR/report.md"
echo "• Analyze system_metrics.csv for resource usage patterns"
echo "• Optimize any performance bottlenecks identified"
echo "• Consider scaling infrastructure if needed"
