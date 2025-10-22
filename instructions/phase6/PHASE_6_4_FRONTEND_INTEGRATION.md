# Phase 6.4: Frontend Integration - Dashboard & UI Components

**Timeline**: Week 4 (5-7 days)  
**Dependencies**: Phase 6.1-6.3 complete (APIs operational)

---

## Overview

**Goal**: Create comprehensive frontend dashboard to visualize data augmentation insights for swing trading decisions.

**Key Components**:
1. Market Regime Dashboard (Fear & Greed + Macro)
2. Sector Rotation Heatmap
3. Swing Opportunities Table (6-Point Screener Results)
4. Money Flow Widgets (Stock Detail Page)
5. Real-Time Updates (WebSocket/Polling)

---

## Architecture: Backend → Frontend Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND APIs                             │
│                                                                  │
│  Port 8400: Data Ingestion Service                              │
│  ├─ GET /api/v1/fear-greed                                      │
│  │  Response: {                                                 │
│  │    composite_score: 68.5,                                    │
│  │    regime: "GREED",                                          │
│  │    components: {volatility: 72, putcall: 65, ...}           │
│  │  }                                                           │
│  │                                                              │
│  ├─ GET /api/v1/sectors/rotation                               │
│  │  Response: [                                                 │
│  │    {sector: "XLK", rank: 1, score: 85.2, ...},             │
│  │    {sector: "XLV", rank: 2, score: 78.1, ...}              │
│  │  ]                                                           │
│  │                                                              │
│  ├─ GET /api/v1/swing-opportunities?limit=20                   │
│  │  Response: [                                                 │
│  │    {symbol: "NVDA", score: 6, reasons: [...], ...},        │
│  │    {symbol: "AMD", score: 6, reasons: [...], ...}          │
│  │  ]                                                           │
│  │                                                              │
│  └─ GET /api/v1/money-flow/{symbol}                            │
│     Response: {                                                 │
│       composite: 78.5,                                          │
│       market: 65, sector: 85, stock: 82,                       │
│       signal: "BUY"                                             │
│     }                                                           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ HTTP/WebSocket
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React/Next.js)                      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              React Components (New)                      │  │
│  │                                                          │  │
│  │  1. MarketRegimePage                                    │  │
│  │     └─ FearGreedGauge                                   │  │
│  │     └─ ComponentBreakdown                               │  │
│  │     └─ MacroIndicatorsTable                             │  │
│  │                                                          │  │
│  │  2. SectorRotationPage                                  │  │
│  │     └─ SectorHeatmap (11 sectors)                       │  │
│  │     └─ SectorRankingTable                               │  │
│  │     └─ LeveragedETFSignals                              │  │
│  │                                                          │  │
│  │  3. SwingOpportunitiesPage                              │  │
│  │     └─ OpportunitiesTable (sortable, filterable)        │  │
│  │     └─ ChecklistBreakdown                               │  │
│  │     └─ QuickActionButtons (Add to watchlist, Trade)     │  │
│  │                                                          │  │
│  │  4. StockDetailPage (Enhanced)                          │  │
│  │     └─ MoneyFlowWidget (NEW)                            │  │
│  │     └─ RelativeStrengthWidget (NEW)                     │  │
│  │     └─ SectorContextWidget (NEW)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              State Management (Redux/Zustand)            │  │
│  │                                                          │  │
│  │  Slices:                                                │  │
│  │  • fearGreedSlice - F&G composite + components          │  │
│  │  • sectorRotationSlice - 11 sectors + rankings         │  │
│  │  • swingOpportunitiesSlice - Screener results          │  │
│  │  • moneyFlowSlice - Per-symbol money flow scores       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              API Client (axios/fetch)                    │  │
│  │                                                          │  │
│  │  Services:                                              │  │
│  │  • fearGreedService.ts                                  │  │
│  │  • sectorRotationService.ts                             │  │
│  │  • swingScreenerService.ts                              │  │
│  │  • moneyFlowService.ts                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Real-Time Updates                           │  │
│  │                                                          │  │
│  │  Options:                                               │  │
│  │  1. WebSocket (preferred): Port 8400/ws                 │  │
│  │  2. Polling (fallback): Every 30-60 seconds             │  │
│  │  3. Server-Sent Events (SSE)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Specifications

### 1. Market Regime Dashboard

**Route**: `/dashboard/market-regime`

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  MARKET REGIME DASHBOARD                              [Refresh] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         FEAR & GREED COMPOSITE                             │ │
│  │                                                            │ │
│  │              [========|--------]   68.5                    │ │
│  │               0    50    100                               │ │
│  │                                                            │ │
│  │              Regime: GREED 😊                              │ │
│  │              Updated: 2 min ago                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         10 COMPONENT BREAKDOWN                             │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ Volatility     [======|-----] 72.0  (35% weight)    │  │ │
│  │  │ Put/Call       [====|-------] 65.0  (20% weight)    │  │ │
│  │  │ Breadth        [=======|----] 80.0  (25% weight)    │  │ │
│  │  │ Credit Spread  [===|--------] 55.0  (20% weight)    │  │ │
│  │  │ Safe Haven     [====|-------] 60.0  (15% weight)    │  │ │
│  │  │ Crypto         [======|-----] 75.0  (10% weight)    │  │ │
│  │  │ Sentiment      [=====|------] 70.0  (5% weight)     │  │ │
│  │  │ Flow           [====|-------] 62.0  (5% weight)     │  │ │
│  │  │ Macro          [===|--------] 58.0  (8% weight)     │  │ │
│  │  │ Technical      [======|-----] 73.0  (5% weight)     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         KEY MACRO INDICATORS                               │ │
│  │  ┌──────────────┬──────────┬──────────┬─────────────────┐ │ │
│  │  │ Indicator    │ Current  │ 1W Ago   │ Interpretation  │ │ │
│  │  ├──────────────┼──────────┼──────────┼─────────────────┤ │ │
│  │  │ VIX          │ 14.5     │ 16.2     │ Low Fear ✅     │ │ │
│  │  │ 10Y Yield    │ 4.25%    │ 4.18%    │ Rates Rising ⚠️ │ │ │
│  │  │ Yield Curve  │ +0.45%   │ +0.38%   │ Normal ✅       │ │ │
│  │  │ HY Spread    │ 385 bps  │ 410 bps  │ Risk-On ✅      │ │ │
│  │  │ TED Spread   │ 18 bps   │ 22 bps   │ Credit OK ✅    │ │ │
│  │  └──────────────┴──────────┴──────────┴─────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         TRADING RECOMMENDATION                             │ │
│  │                                                            │ │
│  │  Current Regime: GREED (68.5)                              │ │
│  │  Position Sizing: LARGE (15-20% per position)              │ │
│  │  Sectors to Trade: Growth (XLK, XLY, XLC)                  │ │
│  │  Stop Loss: WIDER (5-7%)                                   │ │
│  │  Strategy: AGGRESSIVE SWINGS - Ride momentum               │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**React Component Structure**:
```tsx
// frontend/src/pages/MarketRegime/index.tsx

import { FearGreedGauge } from './components/FearGreedGauge';
import { ComponentBreakdown } from './components/ComponentBreakdown';
import { MacroIndicatorsTable } from './components/MacroIndicatorsTable';
import { TradingRecommendation } from './components/TradingRecommendation';

export function MarketRegimePage() {
  const { data: fearGreed, isLoading } = useFearGreed(); // Custom hook
  
  if (isLoading) return <LoadingSpinner />;
  
  return (
    <div className="market-regime-page">
      <PageHeader title="Market Regime Dashboard" />
      
      <div className="grid grid-cols-1 gap-6">
        <FearGreedGauge 
          score={fearGreed.composite_score} 
          regime={fearGreed.regime} 
        />
        
        <ComponentBreakdown 
          components={fearGreed.components} 
        />
        
        <MacroIndicatorsTable 
          indicators={fearGreed.macro_indicators} 
        />
        
        <TradingRecommendation 
          regime={fearGreed.regime}
          score={fearGreed.composite_score}
        />
      </div>
    </div>
  );
}
```

**Custom Hook** (API Integration):
```tsx
// frontend/src/hooks/useFearGreed.ts

import { useQuery } from '@tanstack/react-query';
import { fearGreedService } from '../services/fearGreedService';

export function useFearGreed() {
  return useQuery({
    queryKey: ['fearGreed'],
    queryFn: () => fearGreedService.getCurrent(),
    refetchInterval: 30000, // Refresh every 30 seconds
    staleTime: 30000,
  });
}
```

**API Service**:
```tsx
// frontend/src/services/fearGreedService.ts

const API_BASE = 'http://localhost:8400/api/v1';

export const fearGreedService = {
  async getCurrent() {
    const response = await fetch(`${API_BASE}/fear-greed`);
    if (!response.ok) throw new Error('Failed to fetch fear & greed');
    return response.json();
  },
  
  async getHistory(days: number = 30) {
    const response = await fetch(`${API_BASE}/fear-greed/history?days=${days}`);
    if (!response.ok) throw new Error('Failed to fetch history');
    return response.json();
  }
};
```

---

### 2. Sector Rotation Heatmap

**Route**: `/dashboard/sector-rotation`

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  SECTOR ROTATION                                      [Refresh] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         SECTOR HEATMAP (11 Sectors)                        │ │
│  │                                                            │ │
│  │   ┌──────────┬──────────┬──────────┬──────────┐          │ │
│  │   │   XLK    │   XLY    │   XLF    │   XLC    │          │ │
│  │   │  Tech    │  Discr.  │  Financ. │  Comm.   │          │ │
│  │   │   #1     │   #3     │   #5     │   #7     │          │ │
│  │   │  🔥 85.2 │  🔥 78.1 │  😐 65.3 │  😐 58.2 │          │ │
│  │   └──────────┴──────────┴──────────┴──────────┘          │ │
│  │   ┌──────────┬──────────┬──────────┬──────────┐          │ │
│  │   │   XLV    │   XLI    │   XLE    │   XLB    │          │ │
│  │   │  Health  │  Industr.│  Energy  │  Mater.  │          │ │
│  │   │   #2     │   #4     │   #9     │   #10    │          │ │
│  │   │  🔥 80.5 │  😐 70.2 │  ❄️ 42.1 │  ❄️ 38.5 │          │ │
│  │   └──────────┴──────────┴──────────┴──────────┘          │ │
│  │   ┌──────────┬──────────┬──────────┐                      │ │
│  │   │   XLP    │   XLU    │  XLRE    │                      │ │
│  │   │  Staples │ Utilities│  RealEst │                      │ │
│  │   │   #6     │   #8     │   #11    │                      │ │
│  │   │  😐 62.0 │  ❄️ 48.3 │  ❄️ 35.1 │                      │ │
│  │   └──────────┴──────────┴──────────┘                      │ │
│  │                                                            │ │
│  │  Legend: 🔥 Hot (>70)  😐 Neutral (40-70)  ❄️ Cold (<40) │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         SECTOR RANKING TABLE                               │ │
│  │  ┌──────┬─────────┬──────────┬─────────┬──────────────┐  │ │
│  │  │ Rank │ Sector  │ Score    │ Rel.    │ Status       │  │ │
│  │  │      │         │          │ Strength│              │  │ │
│  │  ├──────┼─────────┼──────────┼─────────┼──────────────┤  │ │
│  │  │  1   │ XLK     │ 85.2     │ 1.15x   │ 🔥 HOT       │  │ │
│  │  │  2   │ XLV     │ 80.5     │ 1.08x   │ 🔥 HOT       │  │ │
│  │  │  3   │ XLY     │ 78.1     │ 1.06x   │ 🔥 HOT       │  │ │
│  │  │  4   │ XLI     │ 70.2     │ 1.01x   │ 😐 NEUTRAL   │  │ │
│  │  │  5   │ XLF     │ 65.3     │ 0.98x   │ 😐 NEUTRAL   │  │ │
│  │  │  ...                                                │  │ │
│  │  │  11  │ XLRE    │ 35.1     │ 0.82x   │ ❄️ COLD      │  │ │
│  │  └──────┴─────────┴──────────┴─────────┴──────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         LEVERAGED ETF CONFIRMATION                         │ │
│  │  ┌──────────────┬──────────┬──────────┬─────────────────┐ │ │
│  │  │ Leveraged    │ Today %  │ Volume   │ Signal          │ │ │
│  │  ├──────────────┼──────────┼──────────┼─────────────────┤ │ │
│  │  │ TQQQ (3xQQQ) │ +4.2%    │ 2.3x avg │ ✅ Confirming   │ │ │
│  │  │ SOXL (3xSemi)│ +5.1%    │ 3.1x avg │ ✅ Confirming   │ │ │
│  │  │ TECL (3xTech)│ +3.8%    │ 1.8x avg │ ✅ Confirming   │ │ │
│  │  │ FAS (3xFinan)│ -0.5%    │ 0.9x avg │ ⚠️ Divergence   │ │ │
│  │  └──────────────┴──────────┴──────────┴─────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**React Component**:
```tsx
// frontend/src/pages/SectorRotation/index.tsx

export function SectorRotationPage() {
  const { data: sectors } = useSectorRotation();
  
  return (
    <div className="sector-rotation-page">
      <SectorHeatmap sectors={sectors} />
      <SectorRankingTable sectors={sectors} />
      <LeveragedETFSignals />
    </div>
  );
}
```

---

### 3. Swing Opportunities Table

**Route**: `/dashboard/swing-opportunities`

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  SWING OPPORTUNITIES (6-Point Screener)           [Refresh]     │
│  Last Scan: 3:25 PM | Next Scan: 3:30 PM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Filters: [All Sectors ▼] [Min Score: 6 ▼] [Market Cap: Any ▼] │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Symbol  │ Score │ Sector │ Money │  RS   │ Leveraged │    │ │
│  │          │  /6   │        │ Flow  │       │ Conf.     │    │ │
│  ├──────────┼───────┼────────┼───────┼───────┼───────────┤    │ │
│  │  NVDA    │  6/6  │  XLK   │  82   │  88   │    ✅     │ 👁 │ │
│  │  AMD     │  6/6  │  XLK   │  78   │  85   │    ✅     │ 👁 │ │
│  │  AVGO    │  6/6  │  XLK   │  75   │  82   │    ✅     │ 👁 │ │
│  │  AAPL    │  5/6  │  XLK   │  71   │  78   │    ✅     │ 👁 │ │
│  │  MSFT    │  5/6  │  XLK   │  68   │  75   │    ✅     │ 👁 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         DETAILED BREAKDOWN (Click to expand)               │ │
│  │                                                            │ │
│  │  NVDA - Score 6/6                                          │ │
│  │  ├─ ✅ Market Regime: GREED (68.5)                         │ │
│  │  ├─ ✅ Sector Rank: XLK #1 (hot)                           │ │
│  │  ├─ ✅ Money Flow: 82/100 (strong buy pressure)            │ │
│  │  ├─ ✅ Relative Strength: 88/100 (top 10%)                 │ │
│  │  ├─ ✅ Leveraged ETF: SOXL confirming (+5.1%)              │ │
│  │  └─ ✅ Technical: Breakout above $500 with 2.3x volume     │ │
│  │                                                            │ │
│  │  Recommendation:                                           │ │
│  │  Entry: $502-505 (current: $503)                           │ │
│  │  Stop: $477 (5% below)                                     │ │
│  │  Target: $543 (8% gain)                                    │ │
│  │  Position Size: 15% of account                             │ │
│  │                                                            │ │
│  │  [Add to Watchlist]  [Create Order]                        │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**React Component**:
```tsx
// frontend/src/pages/SwingOpportunities/index.tsx

export function SwingOpportunitiesPage() {
  const { data: opportunities } = useSwingOpportunities();
  const [selectedStock, setSelectedStock] = useState(null);
  
  return (
    <div className="swing-opportunities-page">
      <PageHeader title="Swing Opportunities" />
      
      <FiltersBar />
      
      <OpportunitiesTable 
        opportunities={opportunities}
        onSelectStock={setSelectedStock}
      />
      
      {selectedStock && (
        <DetailedBreakdown 
          stock={selectedStock}
          onAddToWatchlist={handleAddToWatchlist}
          onCreateOrder={handleCreateOrder}
        />
      )}
    </div>
  );
}
```

---

### 4. Money Flow Widget (Stock Detail Page)

**Integration**: Add to existing `/stocks/{symbol}` page

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  STOCK DETAIL: NVDA                                              │
├─────────────────────────────────────────────────────────────────┤
│  [Existing content: Chart, Order Entry, etc.]                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         MONEY FLOW ANALYSIS (NEW WIDGET)                   │ │
│  │                                                            │ │
│  │  Composite Score: 82/100  [========|--]  Signal: BUY 🔥   │ │
│  │                                                            │ │
│  │  Breakdown:                                                │ │
│  │  ├─ Market-Level (20%):    [======|----] 65/100           │ │
│  │  │  └─ SPY trending up, positive OBV                      │ │
│  │  │                                                         │ │
│  │  ├─ Sector-Level (40%):    [========|--] 85/100           │ │
│  │  │  └─ XLK ranked #1, strong rotation into tech           │ │
│  │  │                                                         │ │
│  │  ├─ Industry-Level (20%):  [=======|---] 88/100           │ │
│  │  │  └─ SOXX (semis) outperforming XLK by 3%               │ │
│  │  │                                                         │ │
│  │  └─ Stock-Level (20%):     [========|--] 82/100           │ │
│  │     └─ Relative volume 2.3x, order book bid-heavy         │ │
│  │                                                            │ │
│  │  Last Updated: 30 seconds ago                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         RELATIVE STRENGTH (NEW WIDGET)                     │ │
│  │                                                            │ │
│  │  Composite: 88/100  Rank: #15 out of 500 (Top 3%)        │ │
│  │                                                            │ │
│  │  vs Market (SPY):     +12.5% (5-day)  [========|--]       │ │
│  │  vs Sector (XLK):     +5.2% (5-day)   [======|----]       │ │
│  │  vs Industry (SOXX):  +2.8% (5-day)   [=====|-----]       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         SECTOR CONTEXT (NEW WIDGET)                        │ │
│  │                                                            │ │
│  │  Sector: Technology (XLK)  Rank: #1 / 11 sectors 🔥       │ │
│  │  Industry: Semiconductors (SOXX)                           │ │
│  │  Leveraged: SOXL +5.1% today (3x volume) ✅ Confirming    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**React Component**:
```tsx
// frontend/src/components/StockDetail/MoneyFlowWidget.tsx

export function MoneyFlowWidget({ symbol }: { symbol: string }) {
  const { data: moneyFlow } = useMoneyFlow(symbol);
  
  if (!moneyFlow) return <LoadingSkeleton />;
  
  return (
    <Card className="money-flow-widget">
      <CardHeader>
        <h3>Money Flow Analysis</h3>
      </CardHeader>
      
      <CardBody>
        <CompositeScoreBar score={moneyFlow.composite} />
        
        <div className="breakdown">
          <MoneyFlowLevel 
            level="Market" 
            score={moneyFlow.market} 
            weight={20}
          />
          <MoneyFlowLevel 
            level="Sector" 
            score={moneyFlow.sector} 
            weight={40}
          />
          <MoneyFlowLevel 
            level="Industry" 
            score={moneyFlow.industry} 
            weight={20}
          />
          <MoneyFlowLevel 
            level="Stock" 
            score={moneyFlow.stock} 
            weight={20}
          />
        </div>
        
        <SignalBadge signal={moneyFlow.signal} />
      </CardBody>
    </Card>
  );
}
```

---

## Real-Time Updates

### Option 1: WebSocket (Recommended)

**Backend WebSocket Server**:
```python
# backend/apps/data_ingestion/websocket_server.py

from fastapi import WebSocket, WebSocketDisconnect
import asyncio

class DataWebSocketManager:
    def __init__(self):
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, data: dict):
        """Broadcast data to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except:
                pass

# FastAPI endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# Broadcast updates every 30 seconds
async def broadcast_updates():
    while True:
        fear_greed = await get_fear_greed()
        sectors = await get_sector_rotation()
        
        await ws_manager.broadcast({
            'type': 'fear_greed_update',
            'data': fear_greed
        })
        
        await ws_manager.broadcast({
            'type': 'sector_rotation_update',
            'data': sectors
        })
        
        await asyncio.sleep(30)
```

**Frontend WebSocket Client**:
```tsx
// frontend/src/hooks/useWebSocket.ts

import { useEffect, useState } from 'react';

export function useWebSocket<T>(url: string, onMessage: (data: T) => void) {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  
  useEffect(() => {
    const websocket = new WebSocket(url);
    
    websocket.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      // Reconnect after 5 seconds
      setTimeout(() => {
        setWs(new WebSocket(url));
      }, 5000);
    };
    
    setWs(websocket);
    
    return () => {
      websocket.close();
    };
  }, [url]);
  
  return { ws, isConnected };
}

// Usage in component
export function MarketRegimePage() {
  const [fearGreed, setFearGreed] = useState(null);
  
  useWebSocket('ws://localhost:8400/ws', (data) => {
    if (data.type === 'fear_greed_update') {
      setFearGreed(data.data);
    }
  });
  
  return <FearGreedGauge score={fearGreed?.composite_score} />;
}
```

---

### Option 2: Polling (Fallback)

**React Query with Polling**:
```tsx
// frontend/src/hooks/useFearGreed.ts

export function useFearGreed() {
  return useQuery({
    queryKey: ['fearGreed'],
    queryFn: () => fearGreedService.getCurrent(),
    refetchInterval: 30000, // Poll every 30 seconds
    staleTime: 30000,
  });
}
```

---

## State Management

### Redux Toolkit Slices

```tsx
// frontend/src/store/slices/fearGreedSlice.ts

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface FearGreedState {
  composite_score: number;
  regime: string;
  components: {
    volatility: number;
    putcall: number;
    // ... etc
  };
  last_updated: string;
}

const fearGreedSlice = createSlice({
  name: 'fearGreed',
  initialState: {} as FearGreedState,
  reducers: {
    setFearGreed: (state, action: PayloadAction<FearGreedState>) => {
      return action.payload;
    },
  },
});

export const { setFearGreed } = fearGreedSlice.actions;
export default fearGreedSlice.reducer;
```

```tsx
// frontend/src/store/slices/sectorRotationSlice.ts

interface SectorRotationState {
  sectors: Array<{
    sector: string;
    rank: number;
    score: number;
    rel_strength: number;
  }>;
}

const sectorRotationSlice = createSlice({
  name: 'sectorRotation',
  initialState: { sectors: [] } as SectorRotationState,
  reducers: {
    setSectorRotation: (state, action) => {
      state.sectors = action.payload;
    },
  },
});
```

---

## Routing

**Add to existing router**:
```tsx
// frontend/src/App.tsx or routes.tsx

<Routes>
  {/* Existing routes */}
  <Route path="/" element={<Dashboard />} />
  <Route path="/stocks/:symbol" element={<StockDetail />} />
  
  {/* NEW ROUTES - Phase 6 */}
  <Route path="/market-regime" element={<MarketRegimePage />} />
  <Route path="/sector-rotation" element={<SectorRotationPage />} />
  <Route path="/swing-opportunities" element={<SwingOpportunitiesPage />} />
</Routes>
```

**Navigation Menu**:
```tsx
// Add to sidebar/navbar

<NavItem to="/market-regime" icon={<GaugeIcon />}>
  Market Regime
</NavItem>

<NavItem to="/sector-rotation" icon={<HeatmapIcon />}>
  Sector Rotation
</NavItem>

<NavItem to="/swing-opportunities" icon={<SearchIcon />}>
  Swing Opportunities
</NavItem>
```

---

## Summary: Frontend Integration

### New Pages (3)
1. **Market Regime Dashboard** (`/market-regime`)
2. **Sector Rotation** (`/sector-rotation`)
3. **Swing Opportunities** (`/swing-opportunities`)

### Enhanced Existing Page (1)
4. **Stock Detail** - Add Money Flow, RS, Sector Context widgets

### New Components (~15)
- `FearGreedGauge`
- `ComponentBreakdown`
- `MacroIndicatorsTable`
- `SectorHeatmap`
- `SectorRankingTable`
- `LeveragedETFSignals`
- `OpportunitiesTable`
- `DetailedBreakdown`
- `MoneyFlowWidget`
- `RelativeStrengthWidget`
- `SectorContextWidget`

### API Services (4)
- `fearGreedService`
- `sectorRotationService`
- `swingScreenerService`
- `moneyFlowService`

### State Management (4 slices)
- `fearGreedSlice`
- `sectorRotationSlice`
- `swingOpportunitiesSlice`
- `moneyFlowSlice`

### Real-Time Updates
- WebSocket (primary) or Polling (fallback)
- 30-60 second update intervals

---

**Implementation Time**: 5-7 days  
**Dependencies**: Backend APIs from Phase 6.1-6.3 must be complete  
**Cost**: $0 (uses existing frontend stack)

---

**Ready for Phase 6 implementation!** 🚀
