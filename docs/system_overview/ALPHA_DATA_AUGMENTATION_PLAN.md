# Trade2026 - External Data Augmentation Plan for Alpha Generation

**Purpose**: Strategic plan for integrating external data sources to enhance ML-based trading decisions and alpha generation.

**Created**: 2025-10-21
**Status**: Planning Phase
**Priority**: High (Critical for production-ready alpha signals)

---

## Executive Summary

**Current State**: Trade2026 has a solid infrastructure foundation with:
- IBKR configured (SHADOW mode, not connected)
- Binance in MOCK mode
- QuestDB + ClickHouse for data storage
- Default ML Pipeline with XGBoost + Feast
- PRISM Physics Engine for backtesting

**Gap**: Limited external data sources beyond basic market data (price/volume). No fundamental, sentiment, alternative, or on-chain data feeding into ML models.

**Goal**: Integrate high-value external data sources to improve:
1. **Alpha Generation**: Better feature engineering for ML models
2. **Risk Management**: Enhanced risk signals and early warning indicators
3. **Market Microstructure**: Deeper understanding of order flow and liquidity
4. **Signal Quality**: Higher Sharpe ratios, better win rates, reduced drawdowns

**Investment**: Phased approach with estimated costs:
- Phase 1 (Essential): $50-100/month
- Phase 2 (Enhanced): $200-500/month
- Phase 3 (Advanced): $500-2000/month

**Expected Impact**:
- **10-30% improvement** in ML model performance (Sharpe ratio)
- **15-25% reduction** in false signals
- **Enhanced risk-adjusted returns** through better feature engineering

---

## Table of Contents

1. [Data Source Categories](#1-data-source-categories)
2. [Priority Matrix](#2-priority-matrix)
3. [Architecture Design](#3-architecture-design)
4. [Implementation Phases](#4-implementation-phases)
5. [Integration Details](#5-integration-details)
6. [Cost-Benefit Analysis](#6-cost-benefit-analysis)
7. [Technical Implementation](#7-technical-implementation)
8. [Monitoring & Validation](#8-monitoring--validation)
9. [Next Steps](#9-next-steps)

---

## 1. Data Source Categories

### 1.1 Market Data (Foundation)

**Current State**: 
- Binance (MOCK mode)
- IBKR (SHADOW, not connected)

**Enhancement Needed**:

| Data Type | Source | Purpose | Priority |
|-----------|--------|---------|----------|
| **Level 2 Order Book** | IBKR Market Data | Market microstructure, liquidity analysis | 🔴 HIGH |
| **Trade-by-Trade Data** | IBKR + Binance | Aggressive vs passive flow, VWAP | 🔴 HIGH |
| **Historical Tick Data** | Polygon.io / Databento | Backtesting, feature engineering | 🟡 MEDIUM |
| **Options Flow** | IBKR / CBOE DataShop | Implied volatility, sentiment | 🟢 LOW |
| **Futures Spreads** | IBKR / CME | Term structure, contango/backwardation | 🟡 MEDIUM |

**ML Features Generated**:
- Order book imbalance (bid/ask ratio)
- Trade flow toxicity (PIN, VPIN)
- Liquidity metrics (spread, depth)
- Volume-weighted prices (VWAP, TWAP)
- Microstructure noise (Kyle's lambda)

**Alpha Impact**: ⭐⭐⭐⭐⭐ (Critical for short-term alpha)

---

### 1.2 Fundamental Data

**Purpose**: Long-term value signals, earnings surprises, financial health

| Data Type | Source | Purpose | Priority | Cost |
|-----------|--------|---------|----------|------|
| **Financials** | Financial Modeling Prep (FMP) | Balance sheet, income statement, cash flow | 🔴 HIGH | $50/mo |
| **Earnings** | Alpha Vantage | Earnings surprises, guidance | 🔴 HIGH | Free/paid |
| **Economic Indicators** | FRED (Federal Reserve) | GDP, unemployment, inflation, rates | 🔴 HIGH | Free |
| **SEC Filings** | SEC EDGAR API | 10-K, 10-Q, 8-K parsing | 🟡 MEDIUM | Free |
| **Analyst Estimates** | Yahoo Finance / FMP | Consensus estimates, revisions | 🟡 MEDIUM | Free/paid |
| **Insider Trading** | SEC Form 4 (via QuiverQuant) | Corporate insider buy/sell signals | 🟢 LOW | $50/mo |

**ML Features Generated**:
- P/E ratio, P/B ratio, EV/EBITDA
- Earnings surprise (actual vs estimate)
- Revenue growth (YoY, QoQ)
- Debt-to-equity ratio
- Free cash flow yield
- Economic regime indicators (expansion, recession)

**Alpha Impact**: ⭐⭐⭐⭐ (Strong for medium/long-term strategies)

---

### 1.3 Sentiment & Alternative Data

**Purpose**: Market psychology, crowd behavior, news-driven moves

| Data Type | Source | Purpose | Priority | Cost |
|-----------|--------|---------|----------|------|
| **News Sentiment** | News API / Benzinga | Real-time news sentiment scoring | 🔴 HIGH | $100-300/mo |
| **Social Media** | Twitter API (X) / Reddit | Retail sentiment (WallStreetBets, Crypto Twitter) | 🟡 MEDIUM | $100/mo |
| **Fear & Greed Index** | CNN Business / Alternative.me | Market sentiment indicator | 🔴 HIGH | Free |
| **Google Trends** | Google Trends API | Search interest as demand proxy | 🟡 MEDIUM | Free |
| **Put/Call Ratio** | CBOE / IBKR | Options-based sentiment | 🟡 MEDIUM | Free via IBKR |
| **Institutional Flow** | WhaleWisdom / Form 13F | 13F filings, institutional positions | 🟢 LOW | $50/mo |

**ML Features Generated**:
- News sentiment score (positive/negative/neutral)
- Social media buzz volume
- Fear & greed index (0-100)
- Search interest trends
- Put/call ratio (contrarian indicator)
- Institutional ownership changes

**Alpha Impact**: ⭐⭐⭐⭐ (High for short-term momentum strategies)

---

### 1.4 Crypto-Specific Data (For Binance Trading)

**Purpose**: On-chain metrics, exchange flows, funding rates

| Data Type | Source | Purpose | Priority | Cost |
|-----------|--------|---------|----------|------|
| **On-Chain Metrics** | Glassnode / CryptoQuant | Active addresses, MVRV, NVT ratio | 🔴 HIGH | $300-800/mo |
| **Exchange Flows** | CryptoQuant | Whale deposits/withdrawals (sell/buy pressure) | 🔴 HIGH | Included above |
| **Funding Rates** | Binance API / Coinglass | Perpetual futures funding (long/short bias) | 🔴 HIGH | Free |
| **Liquidations** | Coinglass / Binance API | Liquidation heatmaps, cascade risk | 🟡 MEDIUM | Free |
| **Stablecoin Supply** | Glassnode / DeFi Llama | USDT/USDC supply (buying power proxy) | 🟡 MEDIUM | Included above |
| **Mining Metrics** | Blockchain.com / Glassnode | Hash rate, miner revenue, capitulation | 🟢 LOW | Free/paid |

**ML Features Generated**:
- MVRV (Market Value to Realized Value) - overvaluation signal
- Exchange netflow (inflow = bearish, outflow = bullish)
- Funding rate (positive = long-heavy, negative = short-heavy)
- Liquidation levels (potential cascade zones)
- Stablecoin supply delta (buying power indicator)

**Alpha Impact**: ⭐⭐⭐⭐⭐ (Critical for crypto trading)

---

### 1.5 Macro & Cross-Asset Data

**Purpose**: Regime detection, correlation analysis, macro themes

| Data Type | Source | Purpose | Priority | Cost |
|-----------|--------|---------|----------|------|
| **Interest Rates** | FRED (Federal Reserve) | Fed funds rate, 10Y yield, curve shape | 🔴 HIGH | Free |
| **Currencies (FX)** | IBKR / OANDA | EUR/USD, DXY (dollar index) | 🔴 HIGH | Free via IBKR |
| **Commodities** | IBKR / Alpha Vantage | Gold, oil, copper (risk-on/risk-off) | 🟡 MEDIUM | Free via IBKR |
| **Volatility Indices** | CBOE (VIX, VXN) | S&P 500 vol, NASDAQ vol | 🔴 HIGH | Free |
| **Correlation Matrices** | Self-computed from IBKR data | Asset correlation for diversification | 🟡 MEDIUM | N/A |

**ML Features Generated**:
- Yield curve slope (10Y - 2Y) - recession predictor
- DXY (dollar strength) - inverse correlation with crypto
- Gold/bonds ratio (risk-on vs risk-off regime)
- VIX level (market fear gauge)
- Cross-asset correlations (regime shifts)

**Alpha Impact**: ⭐⭐⭐ (Moderate, improves regime detection)

---

## 2. Priority Matrix

### Phase 1: Essential (Immediate, $50-100/month)

**Goal**: Get minimal viable data feeding into ML models within 2 weeks.

| Data Source | Cost | Reason | ML Impact |
|-------------|------|--------|-----------|
| **IBKR Live Market Data** | $10/mo | User already has IBKR, just need to connect | Critical |
| **FRED Economic Data** | Free | Essential macro context | High |
| **Financial Modeling Prep (Basic)** | $50/mo | Fundamentals for equity trading | High |
| **Fear & Greed Index** | Free | Simple sentiment indicator | Medium |
| **Binance Real Data (not mock)** | Free | Already configured, just enable | High |

**Total Cost**: ~$60/month  
**Implementation Time**: 1-2 weeks  
**Expected Alpha Improvement**: 10-15%

---

### Phase 2: Enhanced ($200-500/month)

**Goal**: Add high-value alternative data and sentiment within 1 month.

| Data Source | Cost | Reason | ML Impact |
|-------------|------|--------|-----------|
| **News Sentiment (News API)** | $100/mo | Real-time news-driven signals | High |
| **Glassnode (Crypto On-Chain)** | $300/mo | Unique crypto alpha | Very High |
| **Social Media Sentiment** | $100/mo | Retail sentiment gauge | Medium |
| **Historical Tick Data (Polygon.io)** | $200/mo | Backtesting quality improvement | High |

**Total Cost**: ~$400/month (Phase 1 + 2 = $460/month)  
**Implementation Time**: 2-4 weeks  
**Expected Alpha Improvement**: 20-25% (cumulative)

---

### Phase 3: Advanced ($500-2000/month)

**Goal**: Institutional-grade data for production trading (3-6 months out).

| Data Source | Cost | Reason | ML Impact |
|-------------|------|--------|-----------|
| **CryptoQuant (Advanced)** | $500/mo | Deep on-chain analytics | Very High |
| **Benzinga Pro (Premium News)** | $300/mo | Faster, cleaner news | High |
| **S3 Partners (Short Interest)** | $500/mo | Short squeeze detection | Medium |
| **WhaleWisdom (Institutional)** | $50/mo | 13F filings, smart money | Medium |

**Total Cost**: ~$1,350/month additional (Total = $1,810/month)  
**Implementation Time**: 3-6 months  
**Expected Alpha Improvement**: 30%+ (cumulative)

---

## 3. Architecture Design

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                         │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  IBKR    │  │ Binance  │  │   FRED   │  │   FMP    │       │
│  │  Market  │  │   API    │  │   API    │  │   API    │       │
│  │   Data   │  │          │  │          │  │          │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │              │             │              │
└───────┼─────────────┼──────────────┼─────────────┼──────────────┘
        │             │              │             │
        ▼             ▼              ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATA INGESTION LAYER (NEW SERVICE)                  │
│                  Port 8400 - backend network                     │
│                                                                  │
│  - API adapters (IBKR, FMP, FRED, Glassnode, etc.)             │
│  - Rate limiting (per-source)                                   │
│  - Error handling & retries                                     │
│  - Data validation & cleaning                                   │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DATA STORAGE LAYER                              │
│                                                                  │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐        │
│  │   QuestDB    │  │  ClickHouse   │  │   Valkey     │        │
│  │              │  │               │  │              │        │
│  │ • Tick data  │  │ • Fundamental │  │ • Latest     │        │
│  │ • Order book │  │   data (daily)│  │   prices     │        │
│  │ • On-chain   │  │ • News        │  │ • Sentiment  │        │
│  │   metrics    │  │   sentiment   │  │   scores     │        │
│  │   (hourly)   │  │ • Economics   │  │              │        │
│  └──────┬───────┘  └───────┬───────┘  └──────┬───────┘        │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────┬───────┴──────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FEATURE ENGINEERING LAYER                       │
│                   (Feast - Already Exists!)                      │
│                                                                  │
│  - Materialize features from raw data                           │
│  - Time-series features (rolling, lagged)                       │
│  - Cross-sectional features (zscore, ranking)                   │
│  - Feature versioning                                           │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ML MODEL LAYER                                │
│               (Default ML Pipeline - XGBoost)                    │
│                                                                  │
│  - Fetch features from Feast                                    │
│  - Train/predict with external data features                    │
│  - Generate alpha signals                                       │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                  TRADING DECISION LAYER                          │
│     Order → Portfolio → Risk → Execution Services                │
└─────────────────────────────────────────────────────────────────┘
```

**Key Design Decisions**:

1. **New Service**: `Data Ingestion Service` (Port 8400)
   - Consolidates all external API calls
   - Prevents rate limit violations
   - Centralizes error handling

2. **Storage Strategy**:
   - **QuestDB**: High-frequency data (ticks, order book, hourly on-chain)
   - **ClickHouse**: Low-frequency data (daily fundamentals, news, economics)
   - **Valkey**: Cache latest values for ultra-low latency access

3. **Feast Integration** (Already Exists!):
   - Define new features using external data
   - Materialize features to offline/online stores
   - ML models fetch from Feast (clean abstraction)

4. **Minimal Changes to Existing Services**:
   - ML Pipeline already uses Feast
   - Just add new features to Feast definitions
   - Order/Portfolio/Risk services unchanged

---

## 4. Implementation Phases

### Phase 1: Essential Foundation (Weeks 1-2)

**Tasks**:

1. **Connect IBKR (Week 1, Days 1-2)**
   - Install TWS/Gateway (port 7497 for paper trading)
   - Enable API in TWS settings
   - Test connection from Trade2026
   - Update live_gateway config (keep SHADOW mode)
   - **Deliverable**: IBKR connection validated, market data streaming

2. **Enable Binance Real Data (Week 1, Day 3)**
   - Get Binance API keys (testnet first)
   - Update gateway config: `exchange: binance` (not `mock`)
   - Test WebSocket data stream
   - **Deliverable**: Real Binance market data flowing to QuestDB

3. **Create Data Ingestion Service (Week 1, Days 4-7)**
   - Create `backend/apps/data_ingestion/` directory
   - Implement FastAPI app with APScheduler
   - Add to Docker Compose (port 8400)
   - Create initial adapters: IBKR, FRED, FMP
   - **Deliverable**: New service operational, health check passing

4. **Integrate FRED Economic Data (Week 2, Days 1-2)**
   - Get free FRED API key
   - Fetch daily: GDP, Unemployment, Fed Funds Rate, 10Y Yield, VIX
   - Store in ClickHouse: `economic_indicators` table
   - **Deliverable**: Daily economic data populating ClickHouse

5. **Integrate Financial Modeling Prep (Week 2, Days 3-4)**
   - Sign up for FMP API ($50/month)
   - Fetch daily fundamentals: P/E, P/B, revenue growth, earnings surprise
   - Store in ClickHouse: `fundamentals` table
   - **Deliverable**: Fundamental data for top 100 stocks

6. **Create Feast Features (Week 2, Day 5)**
   - Define new feature views in Feast
   - Add fundamentals, sentiment, macro features
   - Materialize to online store (Valkey)
   - **Deliverable**: New features available in Feast

7. **Update ML Model (Week 2, Days 6-7)**
   - Modify ML model to fetch new features
   - Retrain XGBoost with augmented feature set
   - Backtest on historical data
   - **Deliverable**: ML model performance comparison

**Expected Outcome**: 10-15% improvement in ML model metrics  
**Cost**: ~$60/month

---

### Phase 2: Enhanced Alternative Data (Weeks 3-6)

**Tasks**:

1. **News Sentiment Integration (Week 3)**
   - Sign up for News API ($100/month)
   - Implement sentiment analysis (FinBERT)
   - Store in ClickHouse: `news_sentiment` table
   - **Deliverable**: Real-time news sentiment scores

2. **Glassnode On-Chain Data (Week 4)**
   - Sign up for Glassnode ($300/month)
   - Fetch hourly: MVRV, exchange netflow, active addresses
   - Store in QuestDB: `onchain_metrics` table
   - **Deliverable**: On-chain metrics for BTC/ETH

3. **Social Media Sentiment (Week 5)**
   - Twitter API v2 ($100/month)
   - Reddit API (free with rate limits)
   - Sentiment analysis
   - **Deliverable**: Social sentiment indicators

4. **Historical Tick Data (Week 6)**
   - Sign up for Polygon.io ($200/month)
   - Download historical tick data
   - **Deliverable**: Improved backtest accuracy

5. **Retrain & Validate (Week 6)**
   - Retrain ML model with all new features
   - Run extensive backtests
   - **Deliverable**: Performance report

**Expected Outcome**: 20-25% cumulative improvement  
**Cost**: ~$460/month total

---

## 5. Integration Details

### QuestDB Schema (High-Frequency Data)

```sql
-- Order book snapshots (new)
CREATE TABLE order_book (
    timestamp TIMESTAMP,
    symbol SYMBOL,
    bid_price_1 DOUBLE,
    bid_size_1 DOUBLE,
    ask_price_1 DOUBLE,
    ask_size_1 DOUBLE,
    exchange SYMBOL
) timestamp(timestamp) PARTITION BY HOUR;

-- On-chain metrics (new, hourly)
CREATE TABLE onchain_metrics (
    timestamp TIMESTAMP,
    symbol SYMBOL,
    mvrv_ratio DOUBLE,
    exchange_netflow DOUBLE,
    active_addresses LONG,
    funding_rate DOUBLE
) timestamp(timestamp) PARTITION BY DAY;
```

### ClickHouse Schema (Low-Frequency Data)

```sql
-- Fundamentals (daily)
CREATE TABLE fundamentals (
    date Date,
    symbol String,
    pe_ratio Float64,
    pb_ratio Float64,
    revenue_growth_yoy Float64,
    earnings_surprise Float64,
    debt_to_equity Float64
) ENGINE = ReplacingMergeTree()
ORDER BY (symbol, date)
PARTITION BY toYYYYMM(date);

-- News sentiment (5-minute aggregates)
CREATE TABLE news_sentiment (
    timestamp DateTime,
    symbol String,
    avg_sentiment_score Float64,
    positive_count UInt32,
    negative_count UInt32
) ENGINE = SummingMergeTree()
ORDER BY (symbol, timestamp)
PARTITION BY toYYYYMMDD(timestamp);
```

### Valkey Cache Keys

```
# Latest prices
price:{symbol}

# Latest sentiment
sentiment:{symbol}:news
sentiment:{symbol}:social

# Latest on-chain
onchain:{symbol}:mvrv
onchain:{symbol}:netflow

# Latest macro
macro:vix
macro:10y_yield
```

---

## 6. Cost-Benefit Analysis

### Phase 1: Essential ($60/month)

**Expected Alpha Improvement**: 10-15%  
**Breakeven**: If trading $10,000, need 0.6% monthly return improvement  
**Verdict**: ✅ **Essential, very high ROI**

### Phase 2: Enhanced ($460/month total)

**Expected Alpha Improvement**: 20-25% cumulative  
**Breakeven**: If trading $50,000, need 0.9% monthly return improvement  
**Verdict**: ✅ **High ROI if doing crypto trading**

### Phase 3: Institutional ($1,810/month total)

**Expected Alpha Improvement**: 30%+ cumulative  
**Breakeven**: If trading $200,000, need 0.9% monthly return improvement  
**Verdict**: ⚠️ **Only if live trading capital justifies cost**

---

## 7. Technical Implementation

### Data Ingestion Service Structure

```
backend/apps/data_ingestion/
├── main.py                    # FastAPI app, scheduler
├── config.yaml                # Configuration
├── requirements.txt
├── adapters/
│   ├── ibkr_adapter.py       # IBKR market data
│   ├── fred_adapter.py       # FRED economic data
│   ├── fmp_adapter.py        # Financial Modeling Prep
│   ├── glassnode_adapter.py  # Glassnode on-chain
│   └── newsapi_adapter.py    # News API sentiment
├── storage/
│   ├── questdb_client.py     # QuestDB insertion
│   ├── clickhouse_client.py  # ClickHouse insertion
│   └── valkey_client.py      # Valkey caching
└── utils/
    ├── rate_limiter.py       # Rate limiting
    └── validation.py         # Data validation
```

### Feast Feature Definitions

```python
# library/pipelines/default_ml/feast/features.py

# Fundamental features (daily)
fundamentals_fv = FeatureView(
    name="fundamentals",
    entities=["symbol"],
    ttl=timedelta(days=1),
    features=[
        Feature(name="pe_ratio", dtype=ValueType.DOUBLE),
        Feature(name="earnings_surprise", dtype=ValueType.DOUBLE),
        Feature(name="revenue_growth_yoy", dtype=ValueType.DOUBLE),
    ],
    online=True,
    batch_source=...,  # ClickHouse
    online_store="valkey",
)

# Sentiment features (5-minute)
sentiment_fv = FeatureView(
    name="sentiment",
    entities=["symbol"],
    ttl=timedelta(minutes=5),
    features=[
        Feature(name="news_sentiment_score", dtype=ValueType.DOUBLE),
        Feature(name="fear_greed_index", dtype=ValueType.INT64),
    ],
    online=True,
    batch_source=...,  # ClickHouse
    online_store="valkey",
)

# On-chain features (hourly) - Crypto only
onchain_fv = FeatureView(
    name="onchain",
    entities=["symbol"],
    ttl=timedelta(hours=1),
    features=[
        Feature(name="mvrv_ratio", dtype=ValueType.DOUBLE),
        Feature(name="exchange_netflow_btc", dtype=ValueType.DOUBLE),
        Feature(name="funding_rate", dtype=ValueType.DOUBLE),
    ],
    online=True,
    batch_source=...,  # QuestDB
    online_store="valkey",
)
```

---

## 8. Monitoring & Validation

### Data Quality Checks

**Automated Checks** (Run daily):

1. **Data Freshness**: Check latest timestamp in each table
2. **Data Completeness**: Check for missing values (NULLs)
3. **Data Sanity**: Check for outliers
4. **Rate Limit Monitoring**: Track API calls per minute

### ML Model Performance Tracking

| Metric | Before | Phase 1 | Phase 2 | Phase 3 |
|--------|--------|---------|---------|---------|
| **Sharpe Ratio** | Baseline | ? | ? | ? |
| **Win Rate** | Baseline | ? | ? | ? |
| **Max Drawdown** | Baseline | ? | ? | ? |

---

## 9. Next Steps

### Immediate Actions (This Week):

1. **Review & Approve Plan** (1 hour)
   - Read this document
   - Decide on Phase 1 scope
   - Approve budget ($60/month)

2. **Set Up IBKR Connection** (2 hours)
   - Install TWS/Gateway
   - Configure API settings
   - Test connection

3. **Create Data Ingestion Service Skeleton** (4 hours)
   - Create directory structure
   - Write FastAPI skeleton
   - Add to Docker Compose

4. **Sign Up for APIs** (1 hour)
   - Get FRED API key (free)
   - Sign up for FMP ($50/month)

5. **Implement First Adapter** (4 hours)
   - Start with FREDAdapter
   - Test data fetching
   - Insert into ClickHouse

**Total Time**: ~12 hours (1.5 days)

---

## Summary

This plan provides a **phased, cost-effective approach** to augmenting Trade2026's ML-based decision-making with external data sources.

**Key Takeaways**:

1. **Phase 1** ($60/month): Essential foundation - **Start here**
2. **Phase 2** ($460/month): Enhanced alternative data - **Pursue after Phase 1 validation**
3. **Phase 3** ($1,810/month): Institutional-grade - **Only if live trading justifies cost**
4. **Architecture**: New Data Ingestion Service feeding existing infrastructure
5. **Risk Mitigation**: Graceful degradation, redundant sources, monitoring

**Bottom Line**: Start with Phase 1, validate impact, then scale to Phase 2/3 if results justify investment.

---
