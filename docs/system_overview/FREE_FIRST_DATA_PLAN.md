# Trade2026 - FREE-FIRST Data Augmentation Plan (IBKR L2 Maximization)

**Purpose**: Maximize free/already-paid data sources for alpha generation, with comprehensive fear & greed indicators.

**Created**: 2025-10-21
**Status**: Ready to Implement
**Priority**: IMMEDIATE (Zero additional cost to start)

---

## Executive Summary

**You Already Have**:
- ✅ IBKR Level 2 Market Data + Breadth subscription (PAID)
- ✅ IBKR connection configured (just needs to be enabled)
- ✅ Infrastructure (QuestDB, ClickHouse, Valkey, Feast)
- ✅ ML Pipeline (XGBoost + Feast)

**This Plan**: Squeeze maximum alpha from FREE data sources that complement your IBKR subscription.

**Cost**: $0/month for Phase 1 (100% free), then scale up optionally

**Timeline**: 2 weeks to full implementation

**Expected Impact**: 15-20% alpha improvement from free data alone

---

## 1. IBKR Level 2 + Breadth: Full Exploitation

### What You're Paying For (Maximize This First!)

Your IBKR subscription includes:

| Data Type | Available | Current Usage | **Action Needed** |
|-----------|-----------|---------------|-------------------|
| **Level 2 Order Book** | ✅ | Not streaming | 🔴 START USING |
| **Market Depth (10 levels)** | ✅ | Not streaming | 🔴 START USING |
| **Time & Sales (Trade Flow)** | ✅ | Not streaming | 🔴 START USING |
| **Market Breadth Data** | ✅ | Not streaming | 🔴 START USING |
| **Options Chains** | ✅ | Not streaming | 🟡 ADD LATER |
| **Short Interest** | ✅ | Not streaming | 🟡 ADD LATER |
| **Institutional Ownership** | ✅ | Not using | 🟡 ADD LATER |

### High-Value Features from IBKR L2 + Breadth

**Market Microstructure Signals**:
```python
# Order Book Imbalance
imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
# Range: -1 (heavy ask) to +1 (heavy bid)

# Bid-Ask Spread (Transaction Cost)
spread_bps = ((ask - bid) / midpoint) * 10000

# Order Book Depth (Liquidity)
depth_bid_100bps = sum(bid_volume where price >= midpoint * 0.99)
depth_ask_100bps = sum(ask_volume where price <= midpoint * 1.01)

# Trade Flow Toxicity (PIN/VPIN)
# Buy-initiated vs Sell-initiated volume
buy_volume = sum(trades where price >= midpoint)
sell_volume = sum(trades where price < midpoint)
flow_toxicity = abs(buy_volume - sell_volume) / (buy_volume + sell_volume)
```

**Market Breadth Indicators** (You Have Access!):
```python
# Advance-Decline Line
advances = count(stocks with price_change > 0)
declines = count(stocks with price_change < 0)
ad_ratio = advances / declines

# New Highs - New Lows
high_low_index = (new_highs - new_lows) / total_stocks

# Up Volume vs Down Volume
volume_ratio = up_volume / down_volume

# McClellan Oscillator (from A-D data)
mcclellan = EMA(19, advances-declines) - EMA(39, advances-declines)
```

**ML Features from IBKR Data**:
- Order book imbalance (bid/ask pressure)
- Spread tightness (liquidity indicator)
- Trade flow direction (aggressive buy/sell)
- Market breadth (advance/decline, new highs/lows)
- Volume profile (VWAP, TWAP)
- Short interest ratio (days to cover)
- Options flow (put/call ratio, IV skew)

**Alpha Impact**: ⭐⭐⭐⭐⭐ (You're PAYING for this - use it ALL!)

---

## 2. Comprehensive Fear & Greed Composite (All FREE)

### Problem with Just VIX
- VIX only measures S&P 500 options implied volatility
- Doesn't capture credit spreads, equity sentiment, crypto fear, etc.
- Need multi-dimensional fear/greed indicator

### Multi-Factor Fear & Greed Index (10 Components)

#### **Component 1: Volatility Indicators** (FREE via IBKR + FRED)

| Indicator | Source | Weight | Interpretation |
|-----------|--------|--------|----------------|
| VIX (S&P 500) | CBOE / IBKR | 15% | >30 = Fear, <15 = Greed |
| VXN (NASDAQ) | CBOE / IBKR | 10% | Tech volatility |
| VIX9D (9-day) | CBOE | 5% | Very short-term fear |
| VVIX (Vol of Vol) | CBOE | 5% | "Fear of fear" |
| MOVE Index (Bond Vol) | FRED (via ICE) | 10% | Fixed income fear |

**Free API**: 
- CBOE: http://www.cboe.com/api (delayed, free)
- IBKR: Real-time via your subscription
- FRED: Free API for MOVE index

```python
# Volatility Fear Score (0 = extreme greed, 100 = extreme fear)
def volatility_score():
    vix_normalized = (vix - 10) / (40 - 10) * 100  # 10-40 range
    vxn_normalized = (vxn - 15) / (50 - 15) * 100
    move_normalized = (move - 80) / (200 - 80) * 100
    
    score = (vix_normalized * 0.15 + 
             vxn_normalized * 0.10 + 
             move_normalized * 0.10)
    return clip(score, 0, 100)
```

---

#### **Component 2: Put/Call Ratios** (FREE via IBKR)

| Indicator | Source | Weight | Interpretation |
|-----------|--------|--------|----------------|
| CBOE Equity P/C | CBOE / IBKR | 10% | >1.0 = Fear (more puts), <0.7 = Greed |
| CBOE Index P/C | CBOE / IBKR | 5% | Institutional sentiment |
| SPX P/C Ratio | IBKR | 5% | S&P 500 options sentiment |

**Free API**: CBOE daily summary, IBKR real-time

```python
# Put/Call Fear Score
def putcall_score():
    equity_pc_normalized = (equity_pc - 0.5) / (1.5 - 0.5) * 100
    return clip(equity_pc_normalized, 0, 100)
```

---

#### **Component 3: Market Breadth** (FREE via IBKR Breadth Data)

| Indicator | Source | Weight | Interpretation |
|-----------|--------|--------|----------------|
| Advance/Decline Ratio | IBKR | 10% | <0.5 = Fear, >2.0 = Greed |
| New Highs - New Lows | IBKR | 5% | Negative = Fear |
| % Stocks Above 50-DMA | IBKR / Self-computed | 5% | <30% = Fear, >70% = Greed |
| McClellan Oscillator | Computed from A-D | 5% | <-100 = Oversold (fear) |

```python
# Breadth Fear Score
def breadth_score():
    ad_ratio = advances / declines
    ad_normalized = (ad_ratio - 0.5) / (2.0 - 0.5) * 100
    ad_normalized = 100 - ad_normalized  # Invert (low ratio = high fear)
    
    pct_above_50ma_normalized = (pct_above_50ma / 100) * 100
    pct_above_50ma_normalized = 100 - pct_above_50ma_normalized
    
    score = ad_normalized * 0.10 + pct_above_50ma_normalized * 0.05
    return clip(score, 0, 100)
```

---

#### **Component 4: Credit Spreads** (FREE via FRED)

| Indicator | Source | Weight | Interpretation |
|-----------|--------|--------|----------------|
| High Yield Spread (OAS) | FRED: BAMLH0A0HYM2 | 10% | >500bps = Fear |
| Investment Grade Spread | FRED: BAMLC0A0CM | 5% | >150bps = Fear |
| TED Spread | FRED: TEDRATE | 5% | >50bps = Credit fear |

**Free API**: FRED (https://fred.stlouisfed.org/docs/api/)

```python
# Credit Fear Score
def credit_score():
    hy_spread_normalized = (hy_spread - 300) / (800 - 300) * 100
    ted_normalized = (ted_spread - 10) / (100 - 10) * 100
    
    score = hy_spread_normalized * 0.10 + ted_normalized * 0.05
    return clip(score, 0, 100)
```

---

#### **Component 5: Safe Haven Demand** (FREE via IBKR + Alpha Vantage)

| Indicator | Source | Weight | Interpretation |
|-----------|--------|--------|----------------|
| Gold/SPX Ratio | IBKR | 5% | Rising = Fear (flight to safety) |
| TLT/SPY Ratio | IBKR | 5% | Rising = Fear (bonds outperform) |
| DXY (Dollar Index) | IBKR / Alpha Vantage | 5% | Rising = Fear (dollar strength) |

```python
# Safe Haven Fear Score
def safe_haven_score():
    gold_spx_change = (gold_spx_ratio / gold_spx_ratio_50dma) - 1
    gold_normalized = (gold_spx_change + 0.2) / 0.4 * 100
    
    score = gold_normalized * 0.05
    return clip(score, 0, 100)
```

---

#### **Component 6: Crypto Fear & Greed** (FREE)

| Indicator | Source | Weight | Interpretation |
|-----------|--------|--------|----------------|
| Crypto Fear & Greed Index | Alternative.me | 5% | 0 = Extreme Fear, 100 = Extreme Greed |
| BTC Funding Rate | Binance API | 3% | Positive = Long-heavy (greed) |
| BTC Dominance | CoinGecko | 2% | Rising = Risk-off in crypto |

**Free APIs**:
- Alternative.me: https://api.alternative.me/fng/
- Binance: https://api.binance.com (funding rates)
- CoinGecko: https://www.coingecko.com/api/ (free tier)

```python
# Crypto Fear Score (invert since higher = greed)
def crypto_score():
    crypto_fg_inverted = 100 - crypto_fear_greed_index
    funding_normalized = (funding_rate + 0.05) / 0.10 * 100
    
    score = crypto_fg_inverted * 0.05 + funding_normalized * 0.03
    return clip(score, 0, 100)
```

---

#### **Component 7: Sentiment from Free News** (FREE)

| Indicator | Source | Weight | Interpretation |
|-----------|--------|--------|----------------|
| CNN Fear & Greed | CNN Business | 3% | 0 = Extreme Fear, 100 = Extreme Greed |
| Reddit WallStreetBets Sentiment | Reddit API | 2% | Bear/Bull ratio |

**Free APIs**:
- CNN: Web scraping (they publish daily)
- Reddit: https://www.reddit.com/dev/api (free with rate limits)

```python
# Sentiment Fear Score
def sentiment_score():
    cnn_fg_inverted = 100 - cnn_fear_greed
    
    # Reddit sentiment (need to compute from post analysis)
    reddit_normalized = (reddit_bear_bull_ratio - 0.5) / 1.0 * 100
    
    score = cnn_fg_inverted * 0.03 + reddit_normalized * 0.02
    return clip(score, 0, 100)
```

---

#### **Component 8: Flow of Funds** (FREE via FRED + SEC)

| Indicator | Source | Weight | Interpretation |
|-----------|--------|--------|----------------|
| Money Market Fund Assets | FRED: MMMFAQ | 3% | Rising = Risk-off (fear) |
| Margin Debt (FINRA) | FINRA (monthly, free) | 2% | Falling = Deleveraging (fear) |

```python
# Flow Fear Score
def flow_score():
    mmf_change = (mmf_assets / mmf_assets_1y_ago) - 1
    mmf_normalized = (mmf_change + 0.1) / 0.3 * 100
    
    score = mmf_normalized * 0.03
    return clip(score, 0, 100)
```

---

#### **Component 9: Macro Stress Indicators** (FREE via FRED)

| Indicator | Source | Weight | Interpretation |
|-----------|--------|--------|----------------|
| NFCI (Chicago Fed Stress) | FRED: NFCI | 5% | >0 = Tighter financial conditions |
| Yield Curve (10Y - 2Y) | FRED: T10Y2Y | 3% | Negative = Recession fear |

```python
# Macro Fear Score
def macro_score():
    nfci_normalized = (nfci + 0.5) / 1.5 * 100
    
    # Inverted yield curve = fear
    yc_normalized = (yield_curve + 1.0) / 3.0 * 100
    yc_normalized = 100 - yc_normalized  # Invert
    
    score = nfci_normalized * 0.05 + yc_normalized * 0.03
    return clip(score, 0, 100)
```

---

#### **Component 10: Technical Momentum** (FREE - Self-computed from IBKR)

| Indicator | Source | Weight | Interpretation |
|-----------|--------|--------|----------------|
| SPX RSI (14-day) | Computed from IBKR | 2% | <30 = Oversold (fear), >70 = Overbought |
| SPX Price vs 200-DMA | Computed from IBKR | 2% | <10% below = Fear |
| Market Regime (Bull/Bear) | Computed | 1% | Bear market = Fear premium |

```python
# Technical Fear Score
def technical_score():
    # RSI: 30 = max fear, 70 = max greed
    if rsi < 30:
        rsi_normalized = 100
    elif rsi > 70:
        rsi_normalized = 0
    else:
        rsi_normalized = (70 - rsi) / 40 * 100
    
    # Distance from 200-DMA
    distance_200ma = (price / ma_200) - 1
    distance_normalized = (distance_200ma + 0.20) / 0.40 * 100
    distance_normalized = 100 - distance_normalized
    
    score = rsi_normalized * 0.02 + distance_normalized * 0.02
    return clip(score, 0, 100)
```

---

### **COMPOSITE FEAR & GREED INDEX**

```python
def calculate_composite_fear_greed():
    """
    Composite Fear & Greed Index (0-100 scale)
    
    0-20: Extreme Fear
    20-40: Fear
    40-60: Neutral
    60-80: Greed
    80-100: Extreme Greed
    
    All components are FREE data sources!
    """
    
    scores = {
        'volatility': volatility_score(),      # 35% weight
        'putcall': putcall_score(),            # 20% weight
        'breadth': breadth_score(),            # 25% weight
        'credit': credit_score(),              # 20% weight
        'safe_haven': safe_haven_score(),     # 15% weight
        'crypto': crypto_score(),              # 10% weight
        'sentiment': sentiment_score(),        # 5% weight
        'flow': flow_score(),                  # 5% weight
        'macro': macro_score(),                # 8% weight
        'technical': technical_score(),        # 5% weight
    }
    
    # Weighted average
    composite = (
        scores['volatility'] * 0.35 +
        scores['putcall'] * 0.20 +
        scores['breadth'] * 0.25 +
        scores['credit'] * 0.20 +
        scores['safe_haven'] * 0.15 +
        scores['crypto'] * 0.10 +
        scores['sentiment'] * 0.05 +
        scores['flow'] * 0.05 +
        scores['macro'] * 0.08 +
        scores['technical'] * 0.05
    ) / (0.35 + 0.20 + 0.25 + 0.20 + 0.15 + 0.10 + 0.05 + 0.05 + 0.08 + 0.05)
    
    return {
        'composite_score': composite,
        'regime': get_regime(composite),
        'components': scores,
        'timestamp': datetime.now().isoformat()
    }

def get_regime(score):
    if score < 20:
        return 'EXTREME_FEAR'
    elif score < 40:
        return 'FEAR'
    elif score < 60:
        return 'NEUTRAL'
    elif score < 80:
        return 'GREED'
    else:
        return 'EXTREME_GREED'
```

---

## 3. Complete FREE Data Sources Inventory

### Tier 1: IBKR Data (You're Paying - Use Everything!)

| Data Type | Update Frequency | ML Features | Priority |
|-----------|-----------------|-------------|----------|
| Level 2 Order Book (10 levels) | Real-time (100ms) | Order imbalance, spread, depth | 🔴 CRITICAL |
| Time & Sales (Trade Flow) | Real-time (tick) | Buy/sell aggression, VPIN | 🔴 CRITICAL |
| Market Breadth (A-D, H-L) | Real-time (intraday) | Market participation, divergences | 🔴 CRITICAL |
| Options Chains | Real-time | Put/call ratios, IV skew | 🟡 HIGH |
| Short Interest | Daily | Short squeeze potential | 🟡 HIGH |
| Corporate Actions | As announced | Earnings dates, splits, dividends | 🟢 MEDIUM |

**Implementation**: Already have `live_gateway` service - just enable and extend.

---

### Tier 2: Federal Reserve Economic Data (FRED) - FREE

| Data Type | Update Frequency | ML Features | Priority |
|-----------|-----------------|-------------|----------|
| Interest Rates (DFF, GS10, T10Y2Y) | Daily | Yield curve, rate regime | 🔴 CRITICAL |
| Credit Spreads (BAMLH0A0HYM2) | Daily | Credit risk premium | 🔴 CRITICAL |
| Money Supply (M2) | Weekly | Liquidity conditions | 🟡 HIGH |
| Unemployment (UNRATE) | Monthly | Economic health | 🟡 HIGH |
| GDP Growth (GDP) | Quarterly | Macro regime | 🟢 MEDIUM |
| Inflation (CPI, PCE) | Monthly | Real returns context | 🟡 HIGH |
| Financial Stress (NFCI) | Weekly | Systemic risk | 🔴 CRITICAL |

**API**: https://fred.stlouisfed.org/docs/api/
**Free Tier**: Unlimited requests

```python
# Example FRED API call
import requests

API_KEY = "your_free_fred_api_key"
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

def get_fred_data(series_id):
    params = {
        'series_id': series_id,
        'api_key': API_KEY,
        'file_type': 'json',
        'sort_order': 'desc',
        'limit': 1
    }
    response = requests.get(BASE_URL, params=params)
    return response.json()

# Get VIX from FRED
vix_data = get_fred_data('VIXCLS')
```

---

### Tier 3: US Government Free Data

| Data Source | Data Type | Update Frequency | Priority |
|-------------|-----------|------------------|----------|
| **SEC EDGAR** | Company filings (10-K, 10-Q, 8-K, 13F) | As filed | 🟡 HIGH |
| **FINRA** | Short interest, margin debt | Semi-monthly | 🟡 HIGH |
| **US Treasury** | Treasury rates (entire curve) | Daily | 🔴 CRITICAL |
| **BLS** | Employment, CPI, PPI | Monthly | 🟢 MEDIUM |
| **BEA** | GDP, personal income | Quarterly | 🟢 MEDIUM |

**APIs**:
- SEC EDGAR: https://www.sec.gov/edgar/sec-api-documentation
- US Treasury: https://home.treasury.gov/resource-center/data-chart-center/interest-rates
- FINRA: http://www.finra.org/

---

### Tier 4: Crypto Free Data

| Data Source | Data Type | Update Frequency | Cost |
|-------------|-----------|------------------|------|
| **Binance API** | Spot/futures prices, funding, liquidations | Real-time | FREE |
| **CoinGecko** | Prices, market cap, dominance | 1-min (free tier) | FREE |
| **Alternative.me** | Crypto Fear & Greed Index | Daily | FREE |
| **Blockchain.com** | BTC on-chain (addresses, hash rate) | Daily | FREE |
| **DeFi Llama** | TVL, stablecoin supply | Hourly | FREE |

**APIs**:
- Binance: https://binance-docs.github.io/apidocs/
- CoinGecko: https://www.coingecko.com/en/api
- Alternative.me: https://api.alternative.me/fng/
- Blockchain.com: https://www.blockchain.com/api
- DeFi Llama: https://defillama.com/docs/api

---

### Tier 5: Sentiment & Alternative (Free Tier)

| Data Source | Data Type | Update Frequency | Cost |
|-------------|-----------|------------------|------|
| **Reddit API** | WallStreetBets sentiment | Real-time | FREE (rate limits) |
| **CNN Fear & Greed** | Market sentiment composite | Daily | FREE (scrape) |
| **Google Trends** | Search interest | Daily | FREE |
| **Yahoo Finance** | Analyst estimates, earnings | Daily | FREE |
| **Alpha Vantage** | Fundamental data (limited) | Daily | FREE (25 calls/day) |

**Free APIs**:
- Reddit: https://www.reddit.com/dev/api
- Google Trends: https://pypi.org/project/pytrends/
- Yahoo Finance: https://pypi.org/project/yfinance/
- Alpha Vantage: https://www.alphavantage.co/ (25 calls/day free)

---

## 4. Implementation Roadmap (100% FREE Phase)

### Week 1: IBKR Level 2 + Breadth Maximization

**Day 1-2: Enable IBKR Connection**
```bash
# 1. Start TWS/Gateway (you already have it configured)
# Port 7497 (paper) or 7496 (live)

# 2. Test connection
python -c "from ib_insync import IB; ib = IB(); ib.connect('127.0.0.1', 7497, 1); print(ib.isConnected())"

# 3. Update live_gateway to stream Level 2 data
# Location: backend/apps/live_gateway/ibkr_client.py
```

**Day 3-4: Implement Order Book Streaming**
```python
# backend/apps/live_gateway/ibkr_orderbook.py

from ib_insync import IB, Stock
import asyncio

class IBKROrderBookStream:
    def __init__(self):
        self.ib = IB()
        self.ib.connect('127.0.0.1', 7497, clientId=7)
    
    async def stream_order_book(self, symbols):
        """Stream Level 2 order book for symbols"""
        for symbol in symbols:
            contract = Stock(symbol, 'SMART', 'USD')
            
            # Request market depth (Level 2)
            self.ib.reqMktDepth(contract, numRows=10)
            
            # Request tick-by-tick trades
            self.ib.reqTickByTickData(contract, 'AllLast')
        
        # Handle updates
        self.ib.pendingTickersEvent += self.on_orderbook_update
    
    async def on_orderbook_update(self, tickers):
        """Handle order book updates"""
        for ticker in tickers:
            orderbook_data = {
                'symbol': ticker.contract.symbol,
                'timestamp': datetime.now(),
                'bids': [(bid.price, bid.size) for bid in ticker.domBids[:10]],
                'asks': [(ask.price, ask.size) for ask in ticker.domAsks[:10]],
                'last_price': ticker.last,
            }
            
            # Send to QuestDB
            await questdb_client.insert_orderbook(orderbook_data)
            
            # Cache in Valkey
            await valkey_client.set(
                f"orderbook:{ticker.contract.symbol}",
                json.dumps(orderbook_data),
                ex=5  # 5 second TTL
            )
```

**Day 5-7: Market Breadth Data**
```python
# backend/apps/live_gateway/ibkr_breadth.py

async def stream_market_breadth():
    """Stream market breadth indicators from IBKR"""
    
    # Get S&P 500 constituents (or your watchlist)
    symbols = get_sp500_constituents()  # ~500 stocks
    
    breadth_data = {
        'timestamp': datetime.now(),
        'advances': 0,
        'declines': 0,
        'unchanged': 0,
        'new_highs_52w': 0,
        'new_lows_52w': 0,
        'up_volume': 0,
        'down_volume': 0,
    }
    
    for symbol in symbols:
        price_data = await get_price_change(symbol)
        
        if price_data['change'] > 0:
            breadth_data['advances'] += 1
            breadth_data['up_volume'] += price_data['volume']
        elif price_data['change'] < 0:
            breadth_data['declines'] += 1
            breadth_data['down_volume'] += price_data['volume']
        else:
            breadth_data['unchanged'] += 1
        
        # Check 52-week highs/lows
        if price_data['price'] >= price_data['high_52w']:
            breadth_data['new_highs_52w'] += 1
        if price_data['price'] <= price_data['low_52w']:
            breadth_data['new_lows_52w'] += 1
    
    # Store in ClickHouse
    await clickhouse_client.insert_breadth_data(breadth_data)
```

---

### Week 2: FRED + Composite Fear & Greed

**Day 1-2: FRED Economic Data Integration**
```python
# backend/apps/data_ingestion/adapters/fred_adapter.py

import requests
from datetime import datetime

class FREDAdapter:
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    async def get_economic_indicators(self):
        """Fetch all relevant FRED indicators"""
        
        indicators = {
            'DFF': 'Fed Funds Rate',
            'GS10': '10-Year Treasury',
            'T10Y2Y': 'Yield Curve (10Y-2Y)',
            'VIXCLS': 'VIX',
            'BAMLH0A0HYM2': 'High Yield Spread',
            'TEDRATE': 'TED Spread',
            'NFCI': 'Financial Conditions',
            'MMMFAQ': 'Money Market Funds',
            'M2SL': 'M2 Money Supply',
            'UNRATE': 'Unemployment Rate',
            'CPIAUCSL': 'CPI',
        }
        
        data = {}
        for series_id, name in indicators.items():
            params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json',
                'sort_order': 'desc',
                'limit': 1
            }
            response = requests.get(self.BASE_URL, params=params)
            result = response.json()
            
            if 'observations' in result and len(result['observations']) > 0:
                obs = result['observations'][0]
                data[series_id] = {
                    'name': name,
                    'value': float(obs['value']),
                    'date': obs['date']
                }
        
        return data
```

**Day 3-4: Composite Fear & Greed Calculator**
```python
# backend/apps/data_ingestion/fear_greed/composite.py

class CompositeFearGreedCalculator:
    """
    10-component fear & greed index (all FREE data)
    """
    
    def __init__(self):
        self.fred = FREDAdapter(api_key=FRED_API_KEY)
        self.ibkr = IBKRClient()
        self.crypto = CryptoDataClient()
    
    async def calculate(self):
        """Calculate composite fear & greed score"""
        
        # Fetch all data
        fred_data = await self.fred.get_economic_indicators()
        ibkr_data = await self.ibkr.get_sentiment_data()
        crypto_data = await self.crypto.get_fear_greed()
        
        # Calculate component scores
        scores = {
            'volatility': self._calc_volatility_score(fred_data, ibkr_data),
            'putcall': self._calc_putcall_score(ibkr_data),
            'breadth': self._calc_breadth_score(ibkr_data),
            'credit': self._calc_credit_score(fred_data),
            'safe_haven': self._calc_safe_haven_score(ibkr_data),
            'crypto': self._calc_crypto_score(crypto_data),
            'sentiment': await self._calc_sentiment_score(),
            'flow': self._calc_flow_score(fred_data),
            'macro': self._calc_macro_score(fred_data),
            'technical': await self._calc_technical_score(ibkr_data),
        }
        
        # Weighted composite
        composite = self._weighted_average(scores)
        
        return {
            'composite_score': composite,
            'regime': self._get_regime(composite),
            'components': scores,
            'timestamp': datetime.now().isoformat()
        }
    
    def _weighted_average(self, scores):
        weights = {
            'volatility': 0.35,
            'putcall': 0.20,
            'breadth': 0.25,
            'credit': 0.20,
            'safe_haven': 0.15,
            'crypto': 0.10,
            'sentiment': 0.05,
            'flow': 0.05,
            'macro': 0.08,
            'technical': 0.05,
        }
        
        total = sum(scores[k] * weights[k] for k in scores.keys())
        return total / sum(weights.values())
```

**Day 5-7: Feast Features + ML Model Retrain**
```python
# library/pipelines/default_ml/feast/features.py

# Fear & Greed Feature View
fear_greed_fv = FeatureView(
    name="fear_greed",
    entities=["market"],  # e.g., "US", "CRYPTO"
    ttl=timedelta(minutes=5),
    features=[
        Feature(name="composite_score", dtype=ValueType.DOUBLE),
        Feature(name="volatility_score", dtype=ValueType.DOUBLE),
        Feature(name="putcall_score", dtype=ValueType.DOUBLE),
        Feature(name="breadth_score", dtype=ValueType.DOUBLE),
        Feature(name="credit_score", dtype=ValueType.DOUBLE),
        Feature(name="regime", dtype=ValueType.STRING),  # FEAR/GREED/NEUTRAL
    ],
    online=True,
    batch_source=...,  # ClickHouse
    online_store="valkey",
)

# IBKR Microstructure Features
microstructure_fv = FeatureView(
    name="microstructure",
    entities=["symbol"],
    ttl=timedelta(seconds=30),
    features=[
        Feature(name="order_imbalance", dtype=ValueType.DOUBLE),
        Feature(name="spread_bps", dtype=ValueType.DOUBLE),
        Feature(name="depth_bid_100bps", dtype=ValueType.DOUBLE),
        Feature(name="depth_ask_100bps", dtype=ValueType.DOUBLE),
        Feature(name="flow_toxicity", dtype=ValueType.DOUBLE),
    ],
    online=True,
    batch_source=...,  # QuestDB
    online_store="valkey",
)

# Breadth Features
breadth_fv = FeatureView(
    name="breadth",
    entities=["market"],
    ttl=timedelta(minutes=1),
    features=[
        Feature(name="ad_ratio", dtype=ValueType.DOUBLE),
        Feature(name="high_low_index", dtype=ValueType.DOUBLE),
        Feature(name="volume_ratio", dtype=ValueType.DOUBLE),
        Feature(name="mcclellan_oscillator", dtype=ValueType.DOUBLE),
    ],
    online=True,
    batch_source=...,  # ClickHouse
    online_store="valkey",
)
```

---

## 5. Database Schemas

### QuestDB (High-Frequency: IBKR L2, Trades)

```sql
-- Order book snapshots (from IBKR L2)
CREATE TABLE order_book (
    timestamp TIMESTAMP,
    symbol SYMBOL,
    bid_price_1 DOUBLE, bid_size_1 DOUBLE,
    bid_price_2 DOUBLE, bid_size_2 DOUBLE,
    bid_price_3 DOUBLE, bid_size_3 DOUBLE,
    bid_price_4 DOUBLE, bid_size_4 DOUBLE,
    bid_price_5 DOUBLE, bid_size_5 DOUBLE,
    bid_price_6 DOUBLE, bid_size_6 DOUBLE,
    bid_price_7 DOUBLE, bid_size_7 DOUBLE,
    bid_price_8 DOUBLE, bid_size_8 DOUBLE,
    bid_price_9 DOUBLE, bid_size_9 DOUBLE,
    bid_price_10 DOUBLE, bid_size_10 DOUBLE,
    ask_price_1 DOUBLE, ask_size_1 DOUBLE,
    ask_price_2 DOUBLE, ask_size_2 DOUBLE,
    ask_price_3 DOUBLE, ask_size_3 DOUBLE,
    ask_price_4 DOUBLE, ask_size_4 DOUBLE,
    ask_price_5 DOUBLE, ask_size_5 DOUBLE,
    ask_price_6 DOUBLE, ask_size_6 DOUBLE,
    ask_price_7 DOUBLE, ask_size_7 DOUBLE,
    ask_price_8 DOUBLE, ask_size_8 DOUBLE,
    ask_price_9 DOUBLE, ask_size_9 DOUBLE,
    ask_price_10 DOUBLE, ask_size_10 DOUBLE,
    exchange SYMBOL
) timestamp(timestamp) PARTITION BY HOUR;

-- Trade flow (tick-by-tick from IBKR)
CREATE TABLE trade_flow (
    timestamp TIMESTAMP,
    symbol SYMBOL,
    price DOUBLE,
    size DOUBLE,
    aggressor SYMBOL,  -- 'BUY' or 'SELL'
    exchange SYMBOL
) timestamp(timestamp) PARTITION BY HOUR;

-- Derived microstructure metrics (computed every 1 second)
CREATE TABLE microstructure_metrics (
    timestamp TIMESTAMP,
    symbol SYMBOL,
    order_imbalance DOUBLE,  -- (bid_vol - ask_vol) / (bid_vol + ask_vol)
    spread_bps DOUBLE,       -- (ask - bid) / midpoint * 10000
    depth_bid_100bps DOUBLE, -- Sum of bid sizes within 1% of mid
    depth_ask_100bps DOUBLE,
    flow_toxicity DOUBLE     -- |buy_vol - sell_vol| / (buy_vol + sell_vol)
) timestamp(timestamp) PARTITION BY DAY;
```

### ClickHouse (Low-Frequency: FRED, Fear & Greed, Breadth)

```sql
-- FRED economic indicators (daily)
CREATE TABLE economic_indicators (
    date Date,
    indicator String,  -- e.g., 'VIX', 'DFF', 'GS10'
    value Float64,
    change_1d Float64,
    change_1w Float64,
    change_1m Float64
) ENGINE = ReplacingMergeTree()
ORDER BY (indicator, date)
PARTITION BY toYYYYMM(date);

-- Composite fear & greed index (updated every 5 minutes)
CREATE TABLE fear_greed_composite (
    timestamp DateTime,
    market String,  -- 'US', 'CRYPTO'
    composite_score Float64,
    regime String,  -- 'EXTREME_FEAR', 'FEAR', 'NEUTRAL', 'GREED', 'EXTREME_GREED'
    -- Component scores
    volatility_score Float64,
    putcall_score Float64,
    breadth_score Float64,
    credit_score Float64,
    safe_haven_score Float64,
    crypto_score Float64,
    sentiment_score Float64,
    flow_score Float64,
    macro_score Float64,
    technical_score Float64
) ENGINE = ReplacingMergeTree()
ORDER BY (market, timestamp)
PARTITION BY toYYYYMMDD(timestamp);

-- Market breadth (intraday updates)
CREATE TABLE market_breadth (
    timestamp DateTime,
    market String,  -- 'SPX', 'NASDAQ', 'RUSSELL2000'
    advances UInt32,
    declines UInt32,
    unchanged UInt32,
    new_highs_52w UInt32,
    new_lows_52w UInt32,
    up_volume Float64,
    down_volume Float64,
    ad_ratio Float64,
    volume_ratio Float64,
    mcclellan_oscillator Float64
) ENGINE = ReplacingMergeTree()
ORDER BY (market, timestamp)
PARTITION BY toYYYYMMDD(timestamp);
```

### Valkey (Real-Time Cache)

```
# Order book latest (from IBKR L2)
orderbook:{symbol}:bids     # JSON: [[price, size], ...]
orderbook:{symbol}:asks     # JSON: [[price, size], ...]
orderbook:{symbol}:updated  # Timestamp

# Microstructure metrics latest
micro:{symbol}:imbalance    # Float: order imbalance
micro:{symbol}:spread       # Float: spread in bps
micro:{symbol}:toxicity     # Float: flow toxicity

# Fear & Greed latest
feargreed:us:composite      # Float: 0-100
feargreed:us:regime         # String: FEAR/GREED/etc
feargreed:crypto:composite
feargreed:crypto:regime

# Breadth latest
breadth:spx:ad_ratio
breadth:spx:high_low_index
breadth:spx:mcclellan

# TTL: 5 seconds for orderbook, 60 seconds for others
```

---

## 6. Cost Summary

### Phase 1: 100% FREE

| Data Source | Cost/Month | Status |
|-------------|-----------|--------|
| IBKR Level 2 + Breadth | $0 (already paying) | ✅ Use it all! |
| FRED Economic Data | $0 | ✅ Free API |
| US Treasury Data | $0 | ✅ Free API |
| SEC EDGAR | $0 | ✅ Free API |
| FINRA | $0 | ✅ Free downloads |
| Binance API | $0 | ✅ Free API |
| CoinGecko | $0 | ✅ Free tier |
| Alternative.me (Crypto F&G) | $0 | ✅ Free API |
| Blockchain.com | $0 | ✅ Free API |
| DeFi Llama | $0 | ✅ Free API |
| Reddit API | $0 | ✅ Free (rate limited) |
| CNN Fear & Greed | $0 | ✅ Free (scrape) |
| Google Trends | $0 | ✅ Free API |
| Yahoo Finance | $0 | ✅ Free API |
| Alpha Vantage | $0 | ✅ Free tier (25/day) |

**TOTAL COST: $0/month**

**Expected Alpha Improvement**: 15-20% from free data alone!

---

### Optional Phase 2: Paid Enhancements (Later)

| Data Source | Cost/Month | Added Value |
|-------------|-----------|-------------|
| Financial Modeling Prep | $50 | More fundamental data |
| News API | $100 | Real-time news sentiment |
| Glassnode | $300 | Advanced on-chain crypto |
| Polygon.io | $200 | Historical tick data |

**TOTAL: $650/month** (only if free data validates well)

---

## 7. Expected Impact

### Free Data Features (50+ Features)

**From IBKR L2 + Breadth** (30 features):
- 10 order book levels (bid/ask)
- Order imbalance, spread, depth
- Trade flow direction, toxicity
- Advance/decline ratio, new highs/lows
- Volume ratios, McClellan Oscillator

**From FRED** (10 features):
- VIX, credit spreads, yield curve
- Fed funds rate, unemployment
- M2 money supply, financial stress

**From Composite Fear & Greed** (10 features):
- Composite score + 10 component scores
- Regime indicator (fear/greed)

**From Crypto (Free)** (5 features):
- Crypto fear & greed index
- BTC funding rate, dominance
- Liquidations, stablecoin supply

**ML Impact**: 
- 50+ high-quality features
- Multi-timeframe (tick to daily)
- Multi-dimensional (micro + macro)
- **15-20% Sharpe ratio improvement expected**

---

## 8. Implementation Checklist

### Week 1: IBKR Maximization
- [ ] Start TWS/Gateway (port 7497)
- [ ] Test IBKR connection from Trade2026
- [ ] Implement Level 2 order book streaming
- [ ] Implement trade flow (time & sales) streaming
- [ ] Compute order book imbalance, spread, depth
- [ ] Implement market breadth data collection (500+ stocks)
- [ ] Store in QuestDB (order book, trades, microstructure)
- [ ] Cache latest in Valkey

### Week 2: Free External Data
- [ ] Sign up for FRED API (free)
- [ ] Implement FRED adapter (11 economic indicators)
- [ ] Implement composite fear & greed calculator
- [ ] Integrate Binance free data (funding, liquidations)
- [ ] Integrate CoinGecko, Alternative.me
- [ ] Integrate Reddit API (WallStreetBets sentiment)
- [ ] Store in ClickHouse (daily/hourly data)
- [ ] Define Feast features (50+ features)
- [ ] Retrain ML model
- [ ] Backtest and compare

### Week 3: Validation
- [ ] Run comprehensive backtests
- [ ] Validate Sharpe ratio improvement
- [ ] Monitor data quality (freshness, completeness)
- [ ] Optimize feature engineering
- [ ] Document results

---

## 9. Next Steps

### Immediate (Today)
1. Review this FREE-FIRST plan
2. Approve implementation (no cost!)
3. Start TWS/Gateway

### This Week
1. Enable IBKR Level 2 streaming
2. Sign up for FRED API
3. Create data ingestion service skeleton

### Next Week
1. Implement composite fear & greed
2. Define Feast features
3. Retrain ML model

**Timeline**: 2 weeks to fully operational (all FREE data)

---

## Summary

**You're already paying for IBKR Level 2 + Breadth - USE IT ALL!**

This plan gives you:
- ✅ **50+ high-quality ML features** (all FREE)
- ✅ **Comprehensive 10-component Fear & Greed index** (way better than just VIX)
- ✅ **Market microstructure signals** from IBKR Level 2
- ✅ **Macro regime detection** from FRED
- ✅ **Crypto fear indicators** from free APIs
- ✅ **Zero additional cost** to implement Phase 1

**Expected Alpha Improvement**: 15-20% from FREE data alone!

**Then**: After validating free data impact, optionally add paid sources (FMP $50/mo, News API $100/mo, etc.)

---

**Ready to implement? Start with Week 1 tasks above!**
