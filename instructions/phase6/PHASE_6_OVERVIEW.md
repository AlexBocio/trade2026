# Phase 6: Data Augmentation & Swing Trading Intelligence

**Status**: Ready for Implementation  
**Priority**: HIGH  
**Timeline**: 3-4 weeks  
**Cost**: $0/month (all FREE data sources)

---

## Phase Overview

**Goal**: Augment ML-based trading decisions with comprehensive external data sources for short-term swing trading (<$25k account, PDT-compliant).

**Key Deliverables**:
1. **6-Point Checklist Screener** - Automated swing opportunity detection
2. **Money Flow Calculator** - 4-level analysis (Market → Sector → Industry → Stock)
3. **10-Component Fear & Greed Index** - Market regime detection
4. **Sector Rotation Detector** - Identify hot/cold sectors
5. **50+ ML Features** - Enhanced feature engineering for XGBoost

**Backend Integration**: New `data_ingestion` service (port 8400) feeds existing infrastructure
**Frontend Integration**: New dashboard components + real-time widgets

---

## Sub-Phases

### Phase 6.1: Data Venues Setup (Week 1)
- IBKR data streaming (L1, L2, Time & Sales)
- FRED economic data adapter
- Crypto data APIs
- ETF tracking (30 ETFs)
- Market breadth calculator
- Money flow indicators

**Deliverable**: All 38 NEEDS data sources streaming to QuestDB/ClickHouse

---

### Phase 6.2: Core Calculators (Week 2)
- Fear & Greed Composite (10 components → 0-100 score)
- Sector Rotation Detector (rank 11 sectors)
- Relative Strength Calculator (3-tier)
- Money Flow Composite (4-level analysis)

**Deliverable**: Real-time scoring engines operational

---

### Phase 6.3: ML Integration & Screener (Week 3)
- Feast feature definitions (50+ features)
- 6-Point Checklist Screener
- Money Flow Calculator API
- Testing & validation

**Deliverable**: Swing screener functional, API ready

---

### Phase 6.4: Frontend Dashboard (Week 4)
- Market Regime Dashboard
- Sector Rotation Heatmap
- Swing Opportunities Table
- Money Flow Widgets
- Fear & Greed Gauge

**Deliverable**: Complete UI for data augmentation insights

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                         │
│   IBKR (L2) | FRED (9) | Crypto (3) | ETFs (30) | Calculated   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         DATA INGESTION SERVICE (Port 8400 - NEW)                 │
│   Adapters → Processors → Storage (QuestDB/ClickHouse/Valkey)   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FEATURE ENGINEERING (Feast)                     │
│   50+ features: money_flow, sector_rotation, fear_greed, RS     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BACKEND APIs (Existing Services)                │
│   • SwingScreener API (GET /api/v1/swing-opportunities)         │
│   • MoneyFlow API (GET /api/v1/money-flow/{symbol})             │
│   • FearGreed API (GET /api/v1/fear-greed)                      │
│   • SectorRotation API (GET /api/v1/sectors/rotation)           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 FRONTEND DASHBOARD (NEW PAGES)                   │
│   • Market Regime Page                                          │
│   • Sector Rotation Heatmap                                     │
│   • Swing Opportunities Table                                   │
│   • Stock Detail: Money Flow Widget                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Sources (98 total, $0/month)

### NEEDS (38 sources - Week 1-3)
- IBKR: Level 1, Level 2, Time & Sales, Historical
- FRED: 9 economic indicators
- Crypto: Binance, Alternative.me, CoinGecko
- ETFs: 30 (11 sectors + 4 benchmarks + 15 leveraged)
- Calculated: Breadth, money flow, order imbalance, RS

### WANTS (20 sources - Week 4)
- Industry ETFs: 8 (IGV, SOXX, HACK...)
- Themed ETFs: 6 (BOTZ, ARKG, ICLN...)
- Options: Put/Call ratios, IV skew
- Additional FRED: 6 indicators

### NICE-TO-HAVE (40 sources - Future)
- Social sentiment: Reddit, CNN, Google Trends
- Short interest: FINRA, IBKR
- Institutional: 13F, Form 4

---

## Success Criteria

**Backend**:
- [ ] All 38 data sources streaming to databases
- [ ] Fear & Greed composite updating every 5 min
- [ ] Sector rotation detector ranking 11 sectors
- [ ] Money flow calculator operational
- [ ] 6-point screener running (2:30-3:30 PM daily)
- [ ] 50+ features available in Feast

**Frontend**:
- [ ] Market Regime dashboard shows F&G (0-100)
- [ ] Sector Rotation heatmap shows top 3 / bottom 3
- [ ] Swing Opportunities table shows stocks passing 6-point checklist
- [ ] Stock detail page shows Money Flow score + breakdown
- [ ] Real-time updates (WebSocket or polling)

**Performance**:
- [ ] Data ingestion latency <5 seconds
- [ ] API response time <200ms
- [ ] Screener scan completes in <10 seconds
- [ ] Frontend updates every 30-60 seconds

---

## Next Steps

1. **Review Sub-Phase Instructions** (this folder):
   - `PHASE_6_1_DATA_VENUES.md` - Data ingestion setup
   - `PHASE_6_2_CALCULATORS.md` - Core calculators
   - `PHASE_6_3_ML_INTEGRATION.md` - Screener & ML features
   - `PHASE_6_4_FRONTEND.md` - Dashboard & UI components

2. **Start Implementation**:
   - Begin with Phase 6.1 (Data Venues)
   - Complete in order (6.1 → 6.2 → 6.3 → 6.4)

3. **Validate After Each Sub-Phase**:
   - Run tests
   - Check data quality
   - Measure performance

---

## References

**Strategic Documents** (created in this session):
- `docs/system_overview/ALPHA_DATA_AUGMENTATION_PLAN.md` - Original phased plan
- `docs/system_overview/FREE_FIRST_DATA_PLAN.md` - Free data maximization
- `docs/system_overview/SHORT_TERM_SWING_MONEY_FLOW_PLAN.md` - Swing trading strategy
- `docs/system_overview/DATA_VENUES_NEEDS_WANTS_SUMMARY.md` - Data inventory

**Integration Points**:
- Existing: `backend/apps/live_gateway` (IBKR connection)
- Existing: `backend/apps/feature_engineering` (Feast)
- Existing: `library/pipelines/default_ml` (XGBoost)
- New: `backend/apps/data_ingestion` (port 8400)
- New: `frontend/src/pages/MarketRegime` (dashboard)

---

**Phase Owner**: Trading Strategy Team  
**Last Updated**: 2025-10-21
