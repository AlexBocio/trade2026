# Trade2026 - CONSOLIDATED IMPLEMENTATION PROMPT

**Purpose**: Complete implementation guide for Money Flow & 6-Point Screener following ClaudeKnowledge guidelines

**Prerequisites**: `00_VALIDATION_GATE_SYSTEM_CHECK.md` PASSED (50/50)

**Implementation Philosophy**:
- Component Isolation (Rule #1)
- Fault Isolation
- Error Correction Within Component
- Comprehensive Testing at Every Stage
- Real-Time Documentation

---

## 📊 Implementation Overview

**What We're Building**:
1. Data Ingestion Service (IBKR, FRED, Crypto, ETFs, Breadth)
2. Money Flow Calculator (4-level composite, 0-100 score)
3. Sector Rotation Detector (11 sectors ranked)
4. Fear & Greed Composite (10 components, 0-100 score)
5. 6-Point Screener (Opportunity finder)
6. API Layer (REST endpoints)
7. Frontend Dashboard (React components)

**Total Timeline**: 4 weeks (3 weeks backend + 1 week frontend)

**Total Cost**: $0/month (all FREE data sources)

---

## 🏗️ Component Architecture

```
Frontend (React)
    ↓ HTTP/REST
API Layer (FastAPI, Port 8400)
    ↓
Business Logic Components:
  - Screener Engine
  - Money Flow Calculator
  - Sector Rotation Detector
  - Fear & Greed Composite
    ↓
Data Ingestion Service (FastAPI, Port 8500)
  - IBKR Adapter
  - FRED Adapter
  - Crypto Adapter
  - ETF Adapter
  - Breadth Calculator
    ↓
Storage Layer:
  - QuestDB (tick data)
  - ClickHouse (daily data)
  - Valkey (cache)
    ↓
Feature Store (Feast)
  - 50+ features
  - Online/Offline serving
```

---

## 📋 Implementation Phases

### Week 1: Data Ingestion
- Day 1-2: IBKR Adapter (Level 1, Level 2, Time & Sales)
- Day 3: FRED Adapter (9 economic indicators)
- Day 4: Crypto Adapter (Binance, CoinGecko, Alternative.me)
- Day 5: ETF Adapter (30 ETFs via IBKR)
- Day 6: Breadth Calculator (A-D, H-L, % above MA)
- Day 7: Testing & Validation

### Week 2: Calculation Engines
- Day 8-9: Fear & Greed Composite (10 components)
- Day 10-11: Sector Rotation Detector
- Day 12: Relative Strength Calculator (3-tier)
- Day 13-14: Money Flow Calculator (4-level)

### Week 3: Integration
- Day 15-16: Feast Features (50+ features)
- Day 17-18: 6-Point Screener Engine
- Day 19: API Layer (REST endpoints)
- Day 20-21: Testing & Validation

### Week 4: Frontend
- Day 22-23: React Components
- Day 24-25: Dashboard Integration
- Day 26-28: E2E Testing & Polish

---

## 🔧 Component Specifications

### 1. Data Ingestion Service

**Port**: 8500
**Framework**: FastAPI
**Location**: `backend/apps/data_ingestion/`

**Adapters**:

#### 1.1 IBKR Adapter
- Input: IBKR API (ib_insync)
- Output: QuestDB (tick data), Valkey (cache)
- Error Handling: Retry with exponential backoff
- Component Tests: Mock IBKR connection
- Integration Tests: Real IBKR connection (if available)

#### 1.2 FRED Adapter
- Input: FRED REST API (requests)
- Output: ClickHouse (daily economic data)
- Error Handling: Skip indicator if API fails, use cached
- Component Tests: Mock FRED API responses
- Integration Tests: Real FRED API (free, no auth needed)

#### 1.3 Crypto Adapter
- Input: Binance/CoinGecko/Alternative.me APIs
- Output: ClickHouse
- Error Handling: Optional - system works without crypto data
- Component Tests: Mock crypto APIs
- Integration Tests: Real APIs (free tier)

#### 1.4 ETF Adapter
- Input: IBKR API (same connection as Level 1)
- Output: ClickHouse
- Error Handling: Use IBKR Adapter connection, fallback to cached
- Component Tests: Mock IBKR data
- Integration Tests: Real IBKR connection

#### 1.5 Breadth Calculator
- Input: QuestDB (500+ stock prices)
- Output: ClickHouse (breadth indicators)
- Error Handling: Calculate from available stocks
- Component Tests: Mock price data
- Integration Tests: Real QuestDB query

---

### 2. Calculation Engines

#### 2.1 Money Flow Calculator

**Composite Score (0-100) from 4 Levels**:

```python
# Market-level (20% weight)
market_obv = calculate_obv('SPY')
market_cmf = calculate_chaikin_money_flow('SPY')
market_score = (market_obv + market_cmf) / 2 * 20

# Sector-level (40% weight) - HIGHEST WEIGHT
sector_rank = get_sector_rank(symbol)  # 1-11
sector_rel_strength = get_sector_relative_strength(symbol)
sector_score = ((11 - sector_rank) / 11 * 0.6 + sector_rel_strength * 0.4) * 40

# Industry-level (20% weight)
industry_rel_strength = get_industry_relative_strength(symbol)
industry_score = industry_rel_strength * 20

# Stock-level (20% weight)
stock_rel_volume = get_relative_volume(symbol)
stock_obv = calculate_obv(symbol)
stock_order_imbalance = get_order_imbalance(symbol)  # From IBKR L2
stock_score = (stock_rel_volume * 0.4 + stock_obv * 0.3 + stock_order_imbalance * 0.3) * 20

# Composite
composite_score = market_score + sector_score + industry_score + stock_score
signal = 'BUY' if composite_score > 65 else 'SELL' if composite_score < 35 else 'NEUTRAL'
```

**Component Isolation**:
- No dependencies on other calculation engines
- Uses only ClickHouse/QuestDB data
- Error Handling: Returns partial score if data missing

**Component Tests**:
- Test OBV calculation
- Test CMF calculation
- Test composite scoring logic
- Test signal generation

**Integration Tests**:
- Query real databases
- Verify score ranges (0-100)
- Verify signal logic

---

#### 2.2 Sector Rotation Detector

**Ranks 11 Sectors (1 = Hot, 11 = Cold)**:

```python
for sector in ['XLK', 'XLV', 'XLF', ...]:
    # Relative strength (vs SPY, 20-day return)
    sector_return = (sector_price / sector_price_20d_ago) - 1
    spy_return = (spy_price / spy_price_20d_ago) - 1
    rel_strength = (1 + sector_return) / (1 + spy_return)
    
    # Volume ratio (today / 20-day avg)
    volume_ratio = sector_volume / sector_volume_20d_avg
    
    # Breadth (% of stocks in sector above 20-DMA)
    breadth = count_stocks_above_ma(sector) / total_stocks_in_sector
    
    # Composite score
    score = rel_strength * 0.5 + (volume_ratio / 2) * 0.3 + breadth * 0.2
    
    rotation_scores[sector] = score

# Rank 1-11
ranked_sectors = sorted(rotation_scores, key=lambda x: x[1], reverse=True)
```

**Component Isolation**:
- Uses only ETF data from ClickHouse
- No dependencies on Money Flow or F&G

**Component Tests**:
- Test relative strength calculation
- Test volume ratio calculation
- Test ranking logic

**Integration Tests**:
- Query ClickHouse for ETF data
- Verify ranking output

---

#### 2.3 Fear & Greed Composite

**10 Components → 0-100 Score**:

```python
scores = {
    'volatility': calc_volatility_score(),      # 35% - VIX, VXN, MOVE
    'putcall': calc_putcall_score(),            # 20% - CBOE ratios
    'breadth': calc_breadth_score(),            # 25% - A-D, H-L, % above MA
    'credit': calc_credit_score(),              # 20% - HY spread, TED
    'safe_haven': calc_safe_haven_score(),     # 15% - Gold/SPX, TLT/SPY
    'crypto': calc_crypto_score(),              # 10% - Alternative.me
    'sentiment': calc_sentiment_score(),        # 5% - CNN F&G
    'flow': calc_flow_score(),                  # 5% - Money market funds
    'macro': calc_macro_score(),                # 8% - NFCI, yield curve
    'technical': calc_technical_score(),        # 5% - RSI, distance from MA
}

# Weighted composite
composite = sum(scores[k] * weights[k] for k in scores) / sum(weights.values())

# Regime
if composite < 20: regime = 'EXTREME_FEAR'
elif composite < 40: regime = 'FEAR'
elif composite < 60: regime = 'NEUTRAL'
elif composite < 80: regime = 'GREED'
else: regime = 'EXTREME_GREED'
```

**Component Isolation**:
- Uses data from ClickHouse (FRED, Breadth, Crypto)
- No dependencies on Money Flow or Sector Rotation

**Component Tests**:
- Test each component calculator
- Test normalization (0-100)
- Test regime logic

**Integration Tests**:
- Query ClickHouse for all indicators
- Verify composite calculation
- Verify regime transitions

---

### 3. 6-Point Screener

**Evaluates Every Stock in Watchlist**:

```python
def evaluate_swing_trade(symbol):
    score = 0
    reasons = []
    
    # 1. Market Regime
    fear_greed = get_fear_greed_composite()
    if fear_greed['composite_score'] >= 40:
        score += 1
        reasons.append("✅ Market regime favorable")
    
    # 2. Sector Rotation
    sector = get_sector(symbol)
    sector_rank = get_sector_rank(sector)
    if sector_rank <= 3:
        score += 1
        reasons.append(f"✅ Sector {sector} hot (rank {sector_rank})")
    
    # 3. Money Flow
    money_flow = get_money_flow_score(symbol)
    if money_flow['composite'] >= 65:
        score += 1
        reasons.append(f"✅ Money flow strong ({money_flow['composite']}/100)")
    
    # 4. Relative Strength
    rel_strength = get_relative_strength(symbol)
    if rel_strength['composite'] >= 70:
        score += 1
        reasons.append(f"✅ Relative strength high ({rel_strength['composite']}/100)")
    
    # 5. Leveraged ETF Confirmation
    leveraged_etf = get_leveraged_etf_for_sector(sector)
    confirmation = check_etf_confirmation(leveraged_etf)
    if confirmation:
        score += 1
        reasons.append(f"✅ {leveraged_etf} confirming")
    
    # 6. Technical Setup
    technical = check_technical_setup(symbol)
    if technical['score'] >= 70:
        score += 1
        reasons.append(f"✅ Technical setup strong")
    
    decision = 'ENTER SWING' if score == 6 else 'WAIT'
    return {'symbol': symbol, 'score': score, 'decision': decision, 'reasons': reasons}
```

**Component Isolation**:
- Aggregates data from Feast features
- No direct database access
- Returns empty list if Feast unavailable

**Component Tests**:
- Mock Feast feature responses
- Test scoring logic
- Test decision threshold

**Integration Tests**:
- Query real Feast features
- Verify opportunities list
- Validate scores

---

## 🧪 Testing Strategy

### Component Testing (Phase 2 of 6-Phase Workflow)

**Every component gets**:
- Unit tests (pure functions)
- Component tests (mocked dependencies)
- No external dependencies

**Example**: IBKR Adapter Component Test

```python
# tests/test_ibkr_adapter_component.py

import pytest
from unittest.mock import Mock, patch
from backend.apps.data_ingestion.adapters.ibkr_adapter import IBKRAdapter

@pytest.mark.component
class TestIBKRAdapterComponent:
    """Component tests for IBKR Adapter (isolated, mocked dependencies)"""
    
    @patch('backend.apps.data_ingestion.adapters.ibkr_adapter.IB')
    def test_connect_success(self, mock_ib):
        """Test successful connection"""
        adapter = IBKRAdapter()
        result = await adapter.connect_with_retry()
        
        assert result == True
        assert adapter.connected == True
        mock_ib().connectAsync.assert_called_once()
    
    @patch('backend.apps.data_ingestion.adapters.ibkr_adapter.IB')
    def test_connect_retry_on_failure(self, mock_ib):
        """Test retry logic on connection failure"""
        mock_ib().connectAsync.side_effect = [
            Exception("Connection refused"),
            Exception("Connection refused"),
            None  # Success on 3rd attempt
        ]
        
        adapter = IBKRAdapter(max_retries=3)
        result = await adapter.connect_with_retry()
        
        assert result == True
        assert mock_ib().connectAsync.call_count == 3
    
    @patch('backend.apps.data_ingestion.adapters.ibkr_adapter.IB')
    def test_stream_level1_without_connection(self, mock_ib):
        """Test that streaming fails gracefully without connection"""
        adapter = IBKRAdapter()
        adapter.connected = False
        
        await adapter.stream_level1_data(['AAPL'])
        
        # Should log error, not crash
        # Verify via logs or mock logger
```

**Run Component Tests**:
```bash
pytest tests/ -m component -v
```

---

### Integration Testing (Phase 4 of 6-Phase Workflow)

**After component tests pass**:
- Test component with real dependencies
- Verify database connections
- Verify data flow

**Example**: IBKR Adapter Integration Test

```python
# tests/integration/test_ibkr_adapter_integration.py

import pytest
from backend.apps.data_ingestion.adapters.ibkr_adapter import IBKRAdapter

@pytest.mark.integration
@pytest.mark.skipif(not IBKR_AVAILABLE, reason="IBKR not running")
class TestIBKRAdapterIntegration:
    """Integration tests for IBKR Adapter (real IBKR connection if available)"""
    
    async def test_connect_to_real_ibkr(self):
        """Test connection to real IBKR TWS/Gateway"""
        adapter = IBKRAdapter(host='127.0.0.1', port=7497)
        result = await adapter.connect_with_retry()
        
        assert result == True
        assert adapter.connected == True
        
        await adapter.disconnect()
    
    async def test_stream_real_level1_data(self):
        """Test streaming real Level 1 data"""
        adapter = IBKRAdapter()
        await adapter.connect_with_retry()
        
        # Stream data for 10 seconds
        await adapter.stream_level1_data(['AAPL', 'MSFT'])
        await asyncio.sleep(10)
        
        # Verify data received
        # (check QuestDB or in-memory buffer)
        
        await adapter.disconnect()
```

**Run Integration Tests**:
```bash
pytest tests/integration/ -v
```

---

### End-to-End Testing

**Full system workflow**:

```python
# tests/e2e/test_screener_e2e.py

@pytest.mark.e2e
class TestScreenerE2E:
    """End-to-end tests for complete screener workflow"""
    
    async def test_screener_finds_opportunities(self):
        """
        E2E Test: Data ingestion → Calculations → Screener → API → Frontend
        """
        # 1. Verify data ingestion running
        response = requests.get("http://localhost:8500/health")
        assert response.status_code == 200
        
        # 2. Verify calculations updated
        response = requests.get("http://localhost:8400/api/v1/sector-rotation")
        assert response.status_code == 200
        sectors = response.json()
        assert len(sectors) == 11
        
        # 3. Verify screener returns opportunities
        response = requests.get("http://localhost:8400/api/v1/screener/opportunities")
        assert response.status_code == 200
        opportunities = response.json()
        assert isinstance(opportunities, list)
        
        # 4. Verify opportunity structure
        if len(opportunities) > 0:
            opp = opportunities[0]
            assert 'symbol' in opp
            assert 'score' in opp
            assert 'reasons' in opp
            assert opp['score'] >= 0 and opp['score'] <= 6
```

**Run E2E Tests**:
```bash
pytest tests/e2e/ -v
```

---

## 📦 Deployment Strategy

### Docker Compose Services

**Add to `docker-compose.yml`**:

```yaml
services:
  data_ingestion:
    build:
      context: ./backend/apps/data_ingestion
      dockerfile: Dockerfile
    ports:
      - "8500:8500"
    environment:
      - IBKR_HOST=host.docker.internal
      - IBKR_PORT=7497
      - QUESTDB_HOST=questdb
      - CLICKHOUSE_HOST=clickhouse
      - VALKEY_HOST=valkey
    networks:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8500/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
  
  screener_api:
    build:
      context: ./backend/apps/screener_api
      dockerfile: Dockerfile
    ports:
      - "8400:8400"
    environment:
      - FEAST_REPO_PATH=/app/feast_repo
      - CLICKHOUSE_HOST=clickhouse
      - VALKEY_HOST=valkey
    networks:
      - backend
    depends_on:
      - data_ingestion
      - clickhouse
      - valkey
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8400/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
```

### Deployment Checklist

**Before deploying**:
- [ ] All component tests pass
- [ ] All integration tests pass
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Health checks implemented
- [ ] Logging configured

**Deploy Steps**:
```bash
# 1. Build images
docker-compose build data_ingestion screener_api

# 2. Start services
docker-compose up -d data_ingestion screener_api

# 3. Verify health
curl http://localhost:8500/health
curl http://localhost:8400/health

# 4. Monitor logs
docker-compose logs -f data_ingestion screener_api

# 5. Validate (Phase 6 - 5+ minutes monitoring)
# No errors, services stable
```

---

## 📊 Monitoring & Validation

### Validation Checklist (Phase 6 of 6-Phase Workflow)

**After deployment, monitor for 5+ minutes**:

- [ ] All services healthy
- [ ] No error patterns in logs
- [ ] Data flowing to databases (check row counts)
- [ ] API endpoints responding (<500ms)
- [ ] Screener returning opportunities (if market hours)
- [ ] Memory usage stable (<80%)
- [ ] CPU usage reasonable (<50% avg)

### Monitoring Dashboard (Grafana)

**Key Metrics**:
- Data ingestion rate (rows/sec)
- API latency (p50, p95, p99)
- Error rate (errors/min)
- Screener opportunities count
- Feature store cache hit rate

---

## 📝 Documentation Requirements

### Real-Time Documentation (Rule 4)

**Update DURING implementation**:

1. **Session Summary** (`docs/implementation/session_YYYYMMDD.md`)
   - What was implemented today
   - Commands executed
   - Tests run
   - Issues encountered
   - Next steps

2. **Component Documentation** (docstrings in code)
   - Purpose
   - Inputs/Outputs
   - Error handling
   - Example usage

3. **Architecture Updates** (`docs/architecture/`)
   - Component diagram updates
   - Data flow changes
   - API changes

4. **GitHub Updates**
   - Commit after each working change
   - PR descriptions with context
   - Issue tracking

---

## ✅ Success Criteria

**Week 1 Complete**:
- [ ] All adapters streaming data
- [ ] Data visible in QuestDB/ClickHouse
- [ ] Component tests pass (IBKR, FRED, Crypto, ETF, Breadth)
- [ ] Integration tests pass
- [ ] Documentation updated

**Week 2 Complete**:
- [ ] All calculators producing scores
- [ ] Scores stored in databases
- [ ] Component tests pass (Money Flow, Sector, F&G, RS)
- [ ] Integration tests pass
- [ ] Documentation updated

**Week 3 Complete**:
- [ ] Feast features defined (50+)
- [ ] Screener returning opportunities
- [ ] API endpoints operational
- [ ] Component/integration/E2E tests pass
- [ ] Documentation updated

**Week 4 Complete**:
- [ ] Frontend dashboard displaying data
- [ ] Real-time updates working
- [ ] All E2E tests pass
- [ ] User acceptance testing complete
- [ ] Production-ready

---

## 🚀 Getting Started

**Next Steps**:

1. ✅ **Validate System** (if not done)
   - Run `00_VALIDATION_GATE_SYSTEM_CHECK.md`
   - Ensure 50/50 validations pass

2. ✅ **Start Phase 1 - Day 1**
   - Implement IBKR Adapter
   - Follow 6-Phase Workflow
   - Test component in isolation
   - Document progress

3. ✅ **Commit Frequently**
   - After each working component
   - With clear commit messages
   - Push to remote

**Ready to begin implementation!** 🎯

