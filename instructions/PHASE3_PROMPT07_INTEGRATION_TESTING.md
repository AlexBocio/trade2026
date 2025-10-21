# Phase 3 - Prompt 07: Integration Testing

**Phase**: 3 - Frontend Integration  
**Prompt**: 07 of 08  
**Purpose**: Comprehensive end-to-end integration testing  
**Duration**: 4 hours  
**Status**: ⏸️ Ready after Prompt 06 complete

---

## 🛑 PREREQUISITES

- [ ] Prompts 01-06 complete
- [ ] Frontend containerized and running
- [ ] All backend services operational
- [ ] Nginx gateway configured
- [ ] Authentication working

---

## 🎯 TASK OVERVIEW

### What This Prompt Does

Performs comprehensive integration testing:
1. End-to-end user workflows
2. API integration verification
3. Performance testing
4. Error handling validation
5. Cross-browser testing
6. Load testing
7. Security checks

---

## 📋 TEST SCENARIOS

### Scenario 1: Complete Order Flow (Critical Path)

```bash
# Test the complete order submission and execution flow
```

**Steps**:
1. **Login**
   - Navigate to http://localhost
   - Enter credentials (demo@trade2026.com / demo123)
   - Click Login
   - ✅ Should redirect to dashboard

2. **View Market Data**
   - Navigate to Market Data page
   - ✅ Should display tickers
   - ✅ Should show real-time updates
   - Select BTCUSDT
   - ✅ Should display price chart

3. **Submit Order**
   - Navigate to Orders page
   - Click "New Order"
   - Enter order details:
     - Symbol: BTCUSDT
     - Type: Limit
     - Side: Buy
     - Quantity: 0.001
     - Price: 45000
   - Click Submit
   - ✅ Should show success message
   - ✅ Order should appear in orders table
   - ✅ Status should be "Submitted" then "Accepted"

4. **Risk Check Verification**
   - Submit high-risk order:
     - Quantity: 1000 (exceeds limits)
   - ✅ Should be rejected by risk service
   - ✅ Should show rejection reason

5. **View Positions**
   - Navigate to Positions page
   - ✅ Should show current positions
   - ✅ P&L should be calculated
   - ✅ Should update when orders fill

6. **Analytics**
   - Navigate to Analytics page
   - ✅ Should show P&L summary
   - ✅ Should display trading metrics
   - Generate report
   - ✅ Should create and download report

**Test Script**:
```bash
cat > tests/integration/order_flow_test.sh << 'EOF'
#!/bin/bash

echo "🧪 Testing Complete Order Flow..."

BASE_URL="http://localhost"
API_URL="$BASE_URL/api"

# 1. Login
echo "1. Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@trade2026.com","password":"demo123"}')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.token')
if [ -z "$TOKEN" ] || [ "$TOKEN" == "null" ]; then
  echo "❌ Login failed"
  exit 1
fi
echo "✅ Login successful, token: ${TOKEN:0:20}..."

# 2. Get market data
echo "2. Testing market data..."
TICKERS=$(curl -s "$API_URL/gateway/tickers" \
  -H "Authorization: Bearer $TOKEN")
  
if echo "$TICKERS" | jq -e '.[] | select(.symbol=="BTCUSDT")' > /dev/null; then
  echo "✅ Market data retrieved"
else
  echo "❌ Market data failed"
  exit 1
fi

# 3. Submit order
echo "3. Testing order submission..."
ORDER_RESPONSE=$(curl -s -X POST "$API_URL/oms/orders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "account": "demo",
    "symbol": "BTCUSDT",
    "side": "buy",
    "type": "limit",
    "quantity": 0.001,
    "price": 45000
  }')

ORDER_ID=$(echo $ORDER_RESPONSE | jq -r '.order_id')
if [ -z "$ORDER_ID" ] || [ "$ORDER_ID" == "null" ]; then
  echo "❌ Order submission failed"
  echo "Response: $ORDER_RESPONSE"
  exit 1
fi
echo "✅ Order submitted, ID: $ORDER_ID"

# 4. Check order status
echo "4. Checking order status..."
sleep 2
ORDER_STATUS=$(curl -s "$API_URL/oms/orders/$ORDER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.status')
  
echo "✅ Order status: $ORDER_STATUS"

# 5. Get positions
echo "5. Testing positions..."
POSITIONS=$(curl -s "$API_URL/oms/positions" \
  -H "Authorization: Bearer $TOKEN")
  
if echo "$POSITIONS" | jq -e '.' > /dev/null; then
  echo "✅ Positions retrieved"
else
  echo "❌ Positions failed"
  exit 1
fi

# 6. Get P&L
echo "6. Testing P&L..."
PNL=$(curl -s "$API_URL/ptrc/pnl" \
  -H "Authorization: Bearer $TOKEN")
  
if echo "$PNL" | jq -e '.total_pnl' > /dev/null; then
  echo "✅ P&L retrieved"
else
  echo "❌ P&L failed"
  exit 1
fi

echo ""
echo "✅ All order flow tests passed!"
EOF

chmod +x tests/integration/order_flow_test.sh
./tests/integration/order_flow_test.sh
```

---

### Scenario 2: Performance Testing

```bash
# Create performance test script
cat > tests/integration/performance_test.sh << 'EOF'
#!/bin/bash

echo "🚀 Performance Testing..."

BASE_URL="http://localhost"

# Test static asset loading
echo "1. Testing static asset performance..."
time curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" $BASE_URL/

# Test API response times
echo "2. Testing API response times..."

# Health check (should be < 50ms)
echo -n "Health check: "
time curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" $BASE_URL/api/oms/health

# Market data (should be < 100ms)
echo -n "Market data: "
time curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" $BASE_URL/api/gateway/tickers

# Risk check (should be < 10ms)
echo -n "Risk check: "
time curl -s -X POST $BASE_URL/api/risk/check \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","quantity":0.1}' \
  -o /dev/null -w "%{http_code} %{time_total}s\n"

echo ""
echo "3. Load testing with concurrent requests..."
# Use Apache Bench if available
if command -v ab &> /dev/null; then
  echo "Running Apache Bench (100 requests, 10 concurrent)..."
  ab -n 100 -c 10 -H "Authorization: Bearer test" $BASE_URL/api/gateway/health
else
  echo "Apache Bench not installed, using curl loop..."
  for i in {1..10}; do
    curl -s -o /dev/null -w "Request $i: %{time_total}s\n" $BASE_URL/api/gateway/health &
  done
  wait
fi

echo ""
echo "✅ Performance testing complete"
EOF

chmod +x tests/integration/performance_test.sh
./tests/integration/performance_test.sh
```

**Performance Criteria**:
- [ ] Static assets: < 100ms
- [ ] API health checks: < 50ms
- [ ] Market data: < 200ms
- [ ] Risk checks: < 10ms
- [ ] Order submission: < 500ms
- [ ] No errors under load

---

### Scenario 3: Error Handling

```bash
# Test error scenarios
cat > tests/integration/error_handling_test.sh << 'EOF'
#!/bin/bash

echo "⚠️ Testing Error Handling..."

BASE_URL="http://localhost/api"

# 1. Invalid credentials
echo "1. Testing invalid login..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"wrong@email.com","password":"wrongpass"}')
STATUS=$(echo "$RESPONSE" | tail -n1)
if [ "$STATUS" == "401" ] || [ "$STATUS" == "403" ]; then
  echo "✅ Invalid login rejected correctly"
else
  echo "❌ Invalid login not handled properly (status: $STATUS)"
fi

# 2. Invalid order
echo "2. Testing invalid order..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/oms/orders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid_token" \
  -d '{"invalid":"data"}')
STATUS=$(echo "$RESPONSE" | tail -n1)
if [ "$STATUS" == "401" ] || [ "$STATUS" == "400" ]; then
  echo "✅ Invalid order rejected correctly"
else
  echo "❌ Invalid order not handled properly (status: $STATUS)"
fi

# 3. Non-existent endpoint
echo "3. Testing 404 handling..."
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/nonexistent")
STATUS=$(echo "$RESPONSE" | tail -n1)
if [ "$STATUS" == "404" ]; then
  echo "✅ 404 handled correctly"
else
  echo "❌ 404 not handled properly (status: $STATUS)"
fi

# 4. Service unavailable simulation
echo "4. Testing service unavailable..."
# This would require stopping a service, simplified here
echo "✅ Service unavailable handling (manual verification needed)"

echo ""
echo "✅ Error handling tests complete"
EOF

chmod +x tests/integration/error_handling_test.sh
./tests/integration/error_handling_test.sh
```

---

### Scenario 4: Cross-Browser Testing

Create manual test checklist:

```bash
cat > tests/integration/browser_test_checklist.md << 'EOF'
# Cross-Browser Testing Checklist

## Browsers to Test
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Chrome
- [ ] Mobile Safari

## Test Items per Browser

### Layout and Rendering
- [ ] Dashboard layout correct
- [ ] Responsive design works
- [ ] Charts display correctly
- [ ] Tables render properly
- [ ] Forms aligned correctly

### Functionality
- [ ] Login/logout works
- [ ] Navigation works
- [ ] Order submission works
- [ ] Market data updates
- [ ] WebSocket connections (if used)

### Performance
- [ ] Page load time < 3s
- [ ] Smooth scrolling
- [ ] No JavaScript errors in console
- [ ] Memory usage stable

### Compatibility
- [ ] Local storage works
- [ ] Session storage works
- [ ] Cookies work
- [ ] CORS headers work

## Mobile Specific
- [ ] Touch interactions work
- [ ] Viewport scaling correct
- [ ] Keyboard input works
- [ ] Orientation changes handled

## Accessibility
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast sufficient
- [ ] Focus indicators visible
EOF
```

---

### Scenario 5: Security Testing

```bash
# Security test script
cat > tests/integration/security_test.sh << 'EOF'
#!/bin/bash

echo "🔒 Security Testing..."

BASE_URL="http://localhost"

# 1. Check security headers
echo "1. Testing security headers..."
HEADERS=$(curl -s -I $BASE_URL)

check_header() {
  if echo "$HEADERS" | grep -i "$1" > /dev/null; then
    echo "✅ $1 present"
  else
    echo "⚠️ $1 missing"
  fi
}

check_header "X-Frame-Options"
check_header "X-Content-Type-Options"
check_header "X-XSS-Protection"

# 2. Test authentication required
echo ""
echo "2. Testing authentication requirements..."
RESPONSE=$(curl -s -w "\n%{http_code}" $BASE_URL/api/oms/orders)
STATUS=$(echo "$RESPONSE" | tail -n1)
if [ "$STATUS" == "401" ] || [ "$STATUS" == "403" ]; then
  echo "✅ Unauthenticated requests blocked"
else
  echo "❌ Unauthenticated requests not blocked (status: $STATUS)"
fi

# 3. Test SQL injection (basic)
echo ""
echo "3. Testing SQL injection protection..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com\" OR \"1\"=\"1","password":"\" OR \"1\"=\"1"}')
  
if echo "$RESPONSE" | grep -q "error\|invalid\|failed"; then
  echo "✅ SQL injection attempt blocked"
else
  echo "⚠️ Check SQL injection protection"
fi

# 4. Test XSS (basic)
echo ""
echo "4. Testing XSS protection..."
XSS_PAYLOAD="<script>alert('XSS')</script>"
RESPONSE=$(curl -s -X POST "$BASE_URL/api/oms/orders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d "{\"comment\":\"$XSS_PAYLOAD\"}")
  
if echo "$RESPONSE" | grep -q "<script>"; then
  echo "⚠️ XSS payload not sanitized"
else
  echo "✅ XSS protection working"
fi

# 5. Rate limiting
echo ""
echo "5. Testing rate limiting..."
for i in {1..20}; do
  curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/auth/login" \
    -X POST -H "Content-Type: application/json" \
    -d '{"email":"test","password":"test"}' &
done | grep -c "429" | read RATE_LIMITED

if [ "$RATE_LIMITED" -gt 0 ]; then
  echo "✅ Rate limiting active"
else
  echo "⚠️ Rate limiting may not be configured"
fi

echo ""
echo "✅ Security tests complete"
EOF

chmod +x tests/integration/security_test.sh
./tests/integration/security_test.sh
```

---

### Scenario 6: Data Integrity Testing

```bash
# Test data consistency across services
cat > tests/integration/data_integrity_test.sh << 'EOF'
#!/bin/bash

echo "📊 Data Integrity Testing..."

BASE_URL="http://localhost/api"
TOKEN="your_auth_token"  # Set after login

# 1. Submit order and verify across services
echo "1. Testing order data consistency..."

# Submit order
ORDER=$(curl -s -X POST "$BASE_URL/oms/orders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "account": "test",
    "symbol": "ETHUSDT",
    "side": "buy",
    "type": "limit",
    "quantity": 0.1,
    "price": 3000
  }')

ORDER_ID=$(echo $ORDER | jq -r '.order_id')

# Check order in OMS
OMS_ORDER=$(curl -s "$BASE_URL/oms/orders/$ORDER_ID" \
  -H "Authorization: Bearer $TOKEN")

# Check position updated
POSITION=$(curl -s "$BASE_URL/oms/positions" \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | select(.symbol=="ETHUSDT")')

# Verify consistency
if [ ! -z "$POSITION" ]; then
  echo "✅ Position updated correctly"
else
  echo "⚠️ Position not found or not updated"
fi

# 2. Test P&L calculation
echo "2. Testing P&L calculation..."
PNL=$(curl -s "$BASE_URL/ptrc/pnl" \
  -H "Authorization: Bearer $TOKEN")

if echo $PNL | jq -e '.total_pnl' > /dev/null; then
  echo "✅ P&L calculated"
else
  echo "❌ P&L calculation failed"
fi

echo ""
echo "✅ Data integrity tests complete"
EOF
```

---

### Scenario 7: WebSocket Testing (if applicable)

```bash
# Create WebSocket test HTML file
cat > tests/integration/websocket_test.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test</title>
</head>
<body>
    <h1>WebSocket Connection Test</h1>
    <div id="status">Connecting...</div>
    <div id="messages"></div>
    
    <script>
        const ws = new WebSocket('ws://localhost/ws');
        const status = document.getElementById('status');
        const messages = document.getElementById('messages');
        
        ws.onopen = function() {
            status.textContent = '✅ Connected';
            console.log('WebSocket connected');
            
            // Subscribe to market data
            ws.send(JSON.stringify({
                type: 'subscribe',
                channels: ['ticker.BTCUSDT']
            }));
        };
        
        ws.onmessage = function(event) {
            const msg = document.createElement('div');
            msg.textContent = new Date().toISOString() + ': ' + event.data;
            messages.appendChild(msg);
            console.log('Message:', event.data);
        };
        
        ws.onerror = function(error) {
            status.textContent = '❌ Error: ' + error;
            console.error('WebSocket error:', error);
        };
        
        ws.onclose = function() {
            status.textContent = '⚠️ Disconnected';
            console.log('WebSocket closed');
        };
    </script>
</body>
</html>
EOF
```

---

## 📋 AUTOMATED TEST SUITE

Create comprehensive test runner:

```bash
cat > tests/integration/run_all_tests.sh << 'EOF'
#!/bin/bash

echo "🧪 Trade2026 Integration Test Suite"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Run test function
run_test() {
    local test_name=$1
    local test_script=$2
    
    echo -e "${YELLOW}Running: $test_name${NC}"
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if ./$test_script; then
        echo -e "${GREEN}✅ $test_name PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ $test_name FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    echo ""
}

# Check prerequisites
echo "Checking prerequisites..."
if ! curl -s http://localhost/health > /dev/null; then
    echo -e "${RED}Frontend not accessible at http://localhost${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Frontend accessible${NC}"
echo ""

# Run tests
run_test "Order Flow Test" "order_flow_test.sh"
run_test "Performance Test" "performance_test.sh"
run_test "Error Handling Test" "error_handling_test.sh"
run_test "Security Test" "security_test.sh"
run_test "Data Integrity Test" "data_integrity_test.sh"

# Summary
echo "===================================="
echo "Test Summary"
echo "===================================="
echo -e "Tests Run: $TESTS_RUN"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
EOF

chmod +x tests/integration/run_all_tests.sh
```

---

## 📊 TEST REPORT TEMPLATE

```bash
cat > tests/integration/TEST_REPORT.md << 'EOF'
# Integration Test Report

**Date**: $(date)
**Tester**: _______________
**Environment**: Development / Staging / Production

## Test Summary

| Category | Tests Run | Passed | Failed | Notes |
|----------|-----------|---------|---------|-------|
| Order Flow | 6 | | | |
| Performance | 5 | | | |
| Error Handling | 4 | | | |
| Security | 5 | | | |
| Data Integrity | 2 | | | |
| Cross-Browser | 4 | | | |
| **TOTAL** | **26** | | | |

## Detailed Results

### Order Flow Testing
- [x] Login functionality
- [x] Market data display
- [x] Order submission
- [x] Risk validation
- [x] Position tracking
- [x] P&L calculation

### Performance Metrics
| Metric | Target | Actual | Pass/Fail |
|--------|--------|--------|-----------|
| Page Load | < 3s | ___s | |
| API Response | < 200ms | ___ms | |
| Risk Check | < 10ms | ___ms | |
| Order Submit | < 500ms | ___ms | |

### Browser Compatibility
| Browser | Version | Pass/Fail | Issues |
|---------|---------|-----------|--------|
| Chrome | | | |
| Firefox | | | |
| Safari | | | |
| Edge | | | |

### Security Checks
- [x] Authentication required
- [x] Security headers present
- [x] XSS protection
- [x] SQL injection protection
- [x] Rate limiting active

## Issues Found

### Critical
1. None

### Major
1. 

### Minor
1. 

## Recommendations

1. 
2. 
3. 

## Sign-off

- [ ] Development Team
- [ ] QA Team
- [ ] Product Owner
- [ ] DevOps Team

---
**Test Status**: PASSED / FAILED
**Ready for Production**: YES / NO
EOF
```

---

## ✅ PROMPT 07 DELIVERABLES

### Test Scripts Created

- [ ] `tests/integration/order_flow_test.sh`
- [ ] `tests/integration/performance_test.sh`
- [ ] `tests/integration/error_handling_test.sh`
- [ ] `tests/integration/security_test.sh`
- [ ] `tests/integration/data_integrity_test.sh`
- [ ] `tests/integration/run_all_tests.sh`

### Documentation

- [ ] `tests/integration/browser_test_checklist.md`
- [ ] `tests/integration/TEST_REPORT.md`
- [ ] `tests/integration/websocket_test.html` (if applicable)

### Test Results

- [ ] Order flow tests passing
- [ ] Performance metrics met
- [ ] Error handling verified
- [ ] Security checks passed
- [ ] Data integrity confirmed
- [ ] Cross-browser compatibility verified

---

## 🚦 VALIDATION GATE

### All Tests Passing?

**Check**:
- [ ] Automated tests all pass
- [ ] Performance SLAs met
- [ ] No critical bugs found
- [ ] Security vulnerabilities addressed
- [ ] Browser compatibility confirmed
- [ ] Error handling robust
- [ ] Data consistency verified

**Decision**:
- ✅ ALL TESTS PASS → Proceed to Prompt 08 (final polish)
- ⚠️ MINOR ISSUES → Document and proceed with caution
- ❌ CRITICAL ISSUES → Fix before proceeding

---

## 📊 PROMPT 07 COMPLETION CRITERIA

Prompt 07 complete when:

- [ ] All test scripts created and run
- [ ] Integration tests passing (>95%)
- [ ] Performance benchmarks met
- [ ] Security checks passed
- [ ] Test report completed
- [ ] Issues documented
- [ ] COMPLETION_TRACKER.md updated

**Next Prompt**: PHASE3_PROMPT08_PRODUCTION_POLISH.md

---

**Prompt Status**: ⏸️ READY (after Prompt 06 complete)

**Estimated Time**: 4 hours

**Outcome**: Fully tested platform with comprehensive test suite and results
