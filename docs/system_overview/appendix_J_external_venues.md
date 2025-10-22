# Appendix J: External Venues & Trading Integration

**Purpose**: Guide for integrating external data venues and progressing from SHADOW to LIVE trading.

**Last Updated**: 2025-10-21
**Current Status**: SHADOW mode (all orders logged, none sent to broker)

---

## Overview

Trade2026 currently supports:
- **IBKR** (Interactive Brokers) - Primary broker, SHADOW mode
- **Binance** - Crypto exchange, MOCK mode
- **CCXT** - Multi-exchange library (100+ exchanges available)

**User Configuration**: Uses IBKR (not Alpaca)

---

## 1. Interactive Brokers (IBKR) Setup

### Prerequisites

**Software Required**:
- TWS (Trader Workstation) or IB Gateway
- Paper trading account (for testing)
- Real trading account (for production)

**Download**:
- TWS: https://www.interactivebrokers.com/en/trading/tws.php
- IB Gateway: https://www.interactivebrokers.com/en/trading/ibgateway-stable.php

### Current Configuration

**File**: `backend/apps/live_gateway/config.yaml`

```yaml
modes:
  global: "SHADOW"  # SHADOW | CANARY | LIVE
  venues:
    IBKR:
      mode: "SHADOW"
      canary_pct: 0.0  # % of orders sent live (0-100)

venues:
  ibkr:
    host: "127.0.0.1"
    port: 7497  # 7497 = paper, 7496 = live
    client_id: 7
    paper_only: true
    timeout: 30
```

**Environment Variables** (`.env`):
```bash
# Interactive Brokers
IB_HOST=127.0.0.1
IB_PORT=7497
IB_CLIENT_ID=1
```

### TWS/Gateway Setup

**Step 1**: Install TWS or IB Gateway

**Step 2**: Configure API Settings
1. Open TWS/Gateway
2. Go to: Configure → Settings → API → Settings
3. Enable API:
   - ✅ Enable ActiveX and Socket Clients
   - ✅ Read-Only API
   - Port: 7497 (paper) or 7496 (live)
   - Trusted IPs: 127.0.0.1
   - Master API client ID: Leave blank

**Step 3**: Start TWS/Gateway
- Login with paper trading account
- Verify connection on port 7497

**Step 4**: Test Connection
```bash
# Check if TWS/Gateway is running
netstat -an | findstr 7497

# Test with Python
python -c "from ib_insync import IB; ib = IB(); ib.connect('127.0.0.1', 7497, clientId=1); print('Connected:', ib.isConnected()); ib.disconnect()"
```

---

## 2. Trading Mode Progression

### SHADOW Mode (Current)

**Purpose**: Validate order flow without sending to broker

**Behavior**:
- All orders validated and logged
- Order flow tested end-to-end
- NO orders sent to IBKR
- Simulated fills generated
- Full observability of order lifecycle

**Use Cases**:
- Development and testing
- Order flow validation
- System integration testing
- Performance testing

**Duration**: Until confident in system stability (current: ~7 days)

---

### CANARY Mode (Next Step)

**Purpose**: Gradual production rollout with limited risk

**Behavior**:
- Small % of orders sent to IBKR (1-5%)
- Remaining orders in SHADOW mode
- Real market feedback
- Validation of broker integration
- Early detection of issues

**Configuration**:
```yaml
modes:
  global: "CANARY"
  venues:
    IBKR:
      mode: "CANARY"
      canary_pct: 1.0  # Start with 1%
```

**Progression Plan**:
1. Day 1-3: 1% live orders
2. Day 4-7: 5% live orders
3. Day 8-14: 10% live orders
4. Day 15-21: 25% live orders
5. Day 22-30: 50% live orders
6. After 30 days: Evaluate for LIVE mode

**Monitoring**:
- Fill rate (real vs simulated)
- Execution quality (slippage, latency)
- Error rates
- Broker rejections

---

### LIVE Mode (Production)

**Purpose**: Full production trading

**Behavior**:
- 100% orders sent to IBKR
- No simulation
- Real capital at risk
- Full production mode

**Configuration**:
```yaml
modes:
  global: "LIVE"
  venues:
    IBKR:
      mode: "LIVE"
      canary_pct: 100.0

venues:
  ibkr:
    port: 7496  # LIVE port (not paper!)
    paper_only: false
```

**Prerequisites**:
- ✅ 30+ days successful CANARY mode
- ✅ Error rate < 0.1%
- ✅ Fill rate > 95%
- ✅ Slippage within acceptable bounds
- ✅ Risk management validated
- ✅ Compliance checks operational
- ✅ Real account funded
- ✅ All monitoring/alerting in place

---

## 3. Market Data Configuration

### IBKR Market Data

**Data Types**:
- Level 1 (BBO - Best Bid/Offer)
- Level 2 (Market depth)
- Last trades
- Historical data

**Subscription** (required):
- US Securities Snapshot and Futures Value Bundle (~$10/month)
- Or real-time subscriptions ($1-10/month per exchange)

**Configuration**:
```python
# backend/apps/live_gateway/ibkr_client.py
from ib_insync import IB, Stock

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# Subscribe to market data
contract = Stock('AAPL', 'SMART', 'USD')
ib.reqMktData(contract, '', False, False)

# Historical data
bars = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='1 D',
    barSizeSetting='1 min',
    whatToShow='TRADES',
    useRTH=True
)
```

### Binance Market Data

**Current Status**: MOCK mode (to avoid rate limits)

**Configuration**: `backend/apps/gateway/config.yaml`
```yaml
exchange: mock  # Change to 'binance' for real data
symbols:
  - BTC/USDT
  - ETH/USDT
refresh_interval: 5
```

**API Keys** (`.env`):
```bash
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET=your_secret_here
BINANCE_TESTNET=true  # Use testnet first
```

**Enable Real Data**:
1. Get API keys from Binance
2. Add to `.env` file
3. Change `exchange: mock` to `exchange: binance`
4. Restart gateway service

**Rate Limits**:
- Spot: 1200 requests/minute
- Futures: 2400 requests/minute
- WebSocket: Unlimited (use for real-time)

---

## 4. Symbol/Contract Configuration

### IBKR Contracts

**Stocks**:
```python
Stock('AAPL', 'SMART', 'USD')  # US stock
Stock('TSLA', 'NASDAQ', 'USD')  # Specific exchange
```

**Futures**:
```python
Future('ES', '202503', 'CME')  # S&P 500 E-mini, Mar 2025
Future('NQ', '202503', 'CME')  # NASDAQ E-mini
```

**Options**:
```python
Option('AAPL', '20250321', 150, 'C', 'SMART')  # Call option
```

**Forex**:
```python
Forex('EURUSD')
```

**Configuration File**: `backend/apps/instruments/symbols.yaml`
```yaml
symbols:
  equities:
    - symbol: AAPL
      exchange: SMART
      currency: USD
      enabled: true
    - symbol: TSLA
      exchange: NASDAQ
      currency: USD
      enabled: true

  futures:
    - symbol: ES
      exchange: CME
      expiry: "202503"
      enabled: false  # Enable when ready
```

### Binance Symbols

**Configuration**: `backend/apps/gateway/config.yaml`
```yaml
symbols:
  - BTC/USDT
  - ETH/USDT
  - BNB/USDT
  - SOL/USDT
```

---

## 5. Risk Management Integration

### Pre-Trade Risk Checks

**File**: `backend/apps/risk/risk_checks.py`

**Checks**:
1. **Position Limit**: Max shares per symbol
2. **Order Size**: Max $ per order
3. **Concentration**: Max % portfolio in one symbol
4. **Daily Loss Limit**: Max loss per day
5. **Leverage**: Max leverage allowed

**Configuration**: `backend/apps/risk/config.yaml`
```yaml
limits:
  max_position_size: 10000  # shares
  max_order_value: 50000    # USD
  max_concentration: 0.2    # 20% max
  daily_loss_limit: 5000    # USD
  max_leverage: 1.0         # No leverage initially
```

### OPA Policy Integration

**File**: `infrastructure/configs/opa/policies/trading.rego`

```rego
package trading

default allow = false

# Allow order if all conditions met
allow {
    input.order.size <= 1000
    input.order.symbol in data.approved_symbols
    input.user.role == "trader"
    not is_market_closed
}

is_market_closed {
    # Check if current time is outside trading hours
    # 9:30 AM - 4:00 PM ET
}
```

---

## 6. Monitoring & Alerting

### Key Metrics to Monitor

**Order Flow**:
- Order submission rate
- Fill rate (%)
- Rejection rate (%)
- Average fill time

**Execution Quality**:
- Slippage (bp)
- Fill price vs VWAP
- Partial fill rate
- Cancel/replace rate

**System Health**:
- IBKR connection status
- Market data latency
- Order latency (submit to fill)
- Error rates

### Alerting Rules

**Critical Alerts** (immediate notification):
- IBKR connection lost
- Fill rate < 80%
- Rejection rate > 5%
- Daily loss limit exceeded

**Warning Alerts**:
- Fill rate < 95%
- Latency > 100ms
- Unusual order volumes

**Implementation**:
```python
# backend/apps/live_gateway/monitoring.py
from prometheus_client import Counter, Histogram

order_counter = Counter('orders_total', 'Total orders', ['status', 'venue'])
fill_latency = Histogram('fill_latency_seconds', 'Fill latency')

# Increment on order
order_counter.labels(status='filled', venue='IBKR').inc()

# Record latency
fill_latency.observe(latency_seconds)
```

---

## 7. Troubleshooting

### IBKR Connection Issues

**Problem**: Cannot connect to TWS/Gateway
**Solutions**:
1. Verify TWS/Gateway is running
2. Check API settings enabled
3. Verify port (7497 paper, 7496 live)
4. Check firewall rules
5. Verify client ID not in use

**Problem**: Connection timeout
**Solutions**:
1. Increase timeout in config
2. Check network latency
3. Restart TWS/Gateway

### Market Data Issues

**Problem**: No market data received
**Solutions**:
1. Verify market data subscription
2. Check symbol format
3. Verify market hours
4. Check data permissions

**Problem**: Delayed data
**Solutions**:
1. Upgrade to real-time subscription
2. Check network latency
3. Verify snapshot vs streaming

### Order Execution Issues

**Problem**: Orders rejected
**Solutions**:
1. Check symbol permissions
2. Verify account margin
3. Check order size limits
4. Review OPA policies

**Problem**: Partial fills
**Solutions**:
1. Review order type (limit vs market)
2. Check liquidity
3. Adjust limit price
4. Consider iceberg orders

---

## 8. Next Steps

### Immediate (Week 1-2)
- [ ] Install TWS/Gateway
- [ ] Configure API settings
- [ ] Test connection from Trade2026
- [ ] Validate SHADOW mode end-to-end

### Short-term (Week 3-4)
- [ ] Switch to CANARY mode (1% live)
- [ ] Monitor fill rates and execution quality
- [ ] Gradually increase canary %
- [ ] Document any issues

### Medium-term (Month 2)
- [ ] Reach 50% CANARY
- [ ] Evaluate for LIVE mode
- [ ] Fund real account
- [ ] Prepare for production

### Long-term (Month 3+)
- [ ] Full LIVE mode
- [ ] Production trading
- [ ] Continuous optimization
- [ ] Add more venues (if needed)

---

## Summary

Trade2026 is currently in **SHADOW mode** with IBKR configured but not connected. The progression path is:

1. **SHADOW** (Current) → 2. **CANARY** (1-50% live) → 3. **LIVE** (100% production)

**Critical**: Do NOT skip CANARY mode. Gradual rollout is essential for risk management.

**User-Specific**: No Alpaca integration needed (user uses IBKR only).

---
