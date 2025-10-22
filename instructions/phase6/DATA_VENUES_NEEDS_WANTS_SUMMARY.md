# Trade2026 Data Venues: NEEDS, WANTS, NICE-TO-HAVE Summary

## 🔴 NEEDS (Must Have - Week 1-3, $0/month)

### Critical Data Sources (38 total)

**IBKR Data** (You Already Pay!)
- Level 1: Price/Volume (real-time)
- Level 2: Order Book 10 levels (real-time) 
- Time & Sales: Tick data (real-time)
- Historical Bars: 1-min, 5-min, daily

**Sector & Market ETFs** (via IBKR)
- 11 Sector ETFs: XLK, XLV, XLF, XLY, XLI, XLP, XLE, XLB, XLRE, XLU, XLC
- 4 Benchmarks: SPY, QQQ, IWM, DIA
- 7 Leveraged (Equity): TQQQ, SQQQ, SPXL, SPXS, UPRO, TNA, TZA
- 8 Leveraged (Sector): SOXL, SOXS, TECL, TECS, FAS, FAZ, ERX, ERY

**FRED Economic Data** (Free API)
- VIXCLS: VIX volatility
- GS10, GS2: Treasury yields
- T10Y2Y: Yield curve
- BAMLH0A0HYM2: High yield spread
- TEDRATE: TED spread
- DFF: Fed funds rate

**Crypto Data** (Free APIs)
- Binance: BTC/ETH prices, funding rates
- Alternative.me: Crypto Fear & Greed
- CoinGecko: BTC dominance

**Calculated Data** (From IBKR)
- Market Breadth: A-D ratio, new H-L, % above 50-DMA
- Money Flow: OBV, MFI, CMF
- Order Book Imbalance
- Relative Strength (3-tier)

---

## 🟡 WANTS (Important - Week 4, $0/month)

**Industry ETFs** (8 total, via IBKR)
- IGV (Software), SOXX/SMH (Semis), FDN (Internet)
- HACK (Cyber), SKYY (Cloud), XBI (Biotech), KRE (Banks)

**Themed ETFs** (6 total, via IBKR)
- BOTZ/ROBO (AI), ARKG (Genomics), ICLN/TAN (Clean Energy), FINX (Fintech)

**Options Data** (via IBKR)
- Put/Call ratios
- Options chains
- IV skew

**Additional FRED** (6 indicators)
- MOVE: Bond volatility
- MMMFAQ: Money market funds
- M2SL: Money supply
- NFCI: Financial stress

---

## 🟢 NICE-TO-HAVE (Later, $0/month)

**Social Sentiment**
- Reddit API: WallStreetBets
- CNN: Fear & Greed scrape
- Google Trends

**Short Interest**
- FINRA: Semi-monthly
- IBKR: Daily via API

**Institutional**
- SEC 13F: Quarterly filings
- SEC Form 4: Insider trading

---

## Implementation Plan

### Week 1: Data Ingestion
- Day 1-2: IBKR streaming (L1, L2, Time & Sales)
- Day 3: FRED adapter (9 indicators)
- Day 4: Crypto adapter (3 sources)
- Day 5: ETF tracking (30 ETFs)
- Day 6: Breadth calculator
- Day 7: Money flow indicators

### Week 2: Calculators
- Day 8-9: Fear & Greed Composite (10 components)
- Day 10-11: Sector Rotation Detector (rank 11 sectors)
- Day 12: Relative Strength (3-tier)
- Day 13-14: Money Flow Composite (4-level)

### Week 3: Integration
- Day 15-16: Feast features (50+ features)
- Day 17-18: 6-Point Screener
- Day 19: Money Flow Calculator API
- Day 20-21: Testing & validation

---

## Cost Summary

**Total Data Sources**: 98
**Total Cost**: $0/month (all FREE!)
**Implementation Time**: 
- NEEDS: 21 days (3 weeks)
- WANTS: 5 days
- NICE-TO-HAVE: 8 days

**You Already Pay**: ~$10/month IBKR subscription (includes L2 data)
