# Stock Screener Implementation

## Overview

The Stock Screener is an advanced multi-factor quantitative stock screening system that allows traders to identify the best trading opportunities across multiple market universes using a composite scoring algorithm that combines 6 key factors.

**Implementation Date**: 2025-10-10
**Backend Port**: 5008
**Route**: `/scanner/stock-screener`

## Architecture

### Navigation Structure

The Stock Screener is implemented as a nested route under the Scanner tab:

```
/scanner (Small-Cap Scanner - existing)
/scanner/stock-screener (Advanced Stock Screener - new)
```

Both scanners are accessible from the main Scanner page, which displays a promotion card with a "Launch Screener" button to navigate to the Stock Screener.

### Technology Stack

- **React 18.2** with TypeScript
- **React Router v6** for nested routing
- **Plotly.js** for radar chart factor visualization
- **Lucide React** icons
- **TailwindCSS** for styling
- **RESTful API** on Port 5008

## Feature Set

### 1. Stock Universes

Six distinct stock universes are available for screening:

- **S&P 500**: 500 large-cap stocks
- **NASDAQ 100**: 100 largest non-financial NASDAQ stocks
- **Small Caps (Russell 2000)**: ~2000 small-cap stocks
- **Mid Caps (Russell Mid-Cap)**: ~800 mid-cap stocks
- **Micro Caps**: Smallest public companies
- **All Stocks**: All publicly traded stocks

### 2. Trading Timeframes

Three timeframe-optimized screening strategies:

- **Intraday** (Minutes-Hours): High liquidity, fast moves
- **Swing** (2-10 Days): Momentum + technical patterns (default)
- **Position** (Weeks-Months): Fundamental + growth factors

### 3. Multi-Factor Scoring System

Each stock receives a **Composite Score (0-100)** based on 6 factors:

| Factor | Description | Weight |
|--------|-------------|--------|
| **Momentum** | Price trend strength and direction | Variable |
| **Value** | Fundamental valuation metrics (P/E, P/B) | Variable |
| **Quality** | Balance sheet health and profitability | Variable |
| **Growth** | Revenue and earnings growth rates | Variable |
| **Volatility** | Price stability (lower = better) | Variable |
| **Liquidity** | Trading volume and spread | Variable |

Factor weights are dynamically adjusted based on the selected timeframe.

### 4. Signal Types

Three independent signal categories:

- **Technical**: bullish / bearish / neutral
- **Fundamental**: strong / weak / neutral
- **Sentiment**: positive / negative / neutral

### 5. Advanced Filters

- **Min Daily Volume**: Filter by minimum trading volume (default: 1,000,000)
- **Min Price**: Minimum stock price (default: $5)
- **Max Price**: Maximum stock price (default: $1000)
- **Top N Stocks**: Number of top picks to return (default: 20)

## File Structure

```
src/
├── api/
│   └── screenerApi.ts              # API service (Port 5008)
├── components/
│   └── Screener/
│       ├── StockCard.tsx           # Individual stock display card
│       ├── FactorBreakdown.tsx     # Radar chart + factor bars
│       └── ScreenResults.tsx       # Sortable results table
├── pages/
│   └── Scanner/
│       ├── Scanner.tsx             # Main scanner (with navigation card)
│       └── StockScreener.tsx       # Stock screener main page
└── Router.tsx                      # Nested route configuration
```

## Implementation Details

### API Service (`src/api/screenerApi.ts`)

**Base URL**: `http://localhost:5008/api/screener`

**Interfaces**:

```typescript
export interface ScreenerParams {
  universe: 'sp500' | 'nasdaq100' | 'small_caps' | 'mid_caps' | 'micro_caps' | 'all';
  timeframe: 'intraday' | 'swing' | 'position';
  top_n: number;
  min_volume?: number;
  min_price?: number;
  max_price?: number;
}

export interface StockResult {
  ticker: string;
  company_name: string;
  sector: string;
  industry: string;
  price: number;
  change_pct: number;
  volume: number;
  market_cap: number;
  composite_score: number;
  factor_scores: {
    momentum: number;
    value: number;
    quality: number;
    growth: number;
    volatility: number;
    liquidity: number;
  };
  signals: {
    technical: 'bullish' | 'bearish' | 'neutral';
    fundamental: 'strong' | 'weak' | 'neutral';
    sentiment: 'positive' | 'negative' | 'neutral';
  };
  catalyst?: string;
  risk_level: 'low' | 'medium' | 'high';
}

export interface ScreenerResponse {
  top_picks: StockResult[];
  all_results: StockResult[];
  universe_stats: {
    total_stocks: number;
    avg_score: number;
    top_sector: string;
  };
  scan_params: ScreenerParams;
  timestamp: string;
}
```

**API Methods**:

- `scan(params)`: Primary screening endpoint
- `customScan(params)`: Custom factor weight screening
- `getFactorAnalysis(ticker, timeframe)`: Detailed factor analysis
- `healthCheck()`: Backend health status

### Components

#### 1. StockCard (`src/components/Screener/StockCard.tsx`)

**Purpose**: Display individual stock picks in a card layout

**Features**:
- Composite score progress bar with color coding
- 6-factor mini progress bars
- Signal indicators (T/F/S badges)
- Risk level badge
- Price and change percentage
- Catalyst display
- "View Details" button

**Score Color Coding**:
- 80-100: Green (Excellent)
- 60-79: Blue (Good)
- 40-59: Yellow (Fair)
- 0-39: Red (Poor)

#### 2. FactorBreakdown (`src/components/Screener/FactorBreakdown.tsx`)

**Purpose**: Visualize factor scores with Plotly radar chart

**Features**:
- Radar chart (scatterpolar) showing all 6 factors
- Individual factor progress bars
- Factor interpretation guide
- Color-coded scoring

**Plotly Configuration**:
```typescript
type: 'scatterpolar'
fill: 'toself'
radialaxis.range: [0, 100]
theme: Dark (#1a1f2e background)
```

#### 3. ScreenResults (`src/components/Screener/ScreenResults.tsx`)

**Purpose**: Sortable table for all screening results

**Features**:
- Sortable columns (ticker, price, change, volume, score)
- Signal badges (Technical, Fundamental, Sentiment)
- Color-coded change percentages
- Sector/industry display
- Responsive sorting with ChevronUp/Down icons

**Columns**:
1. Ticker (sortable)
2. Company Name
3. Price (sortable)
4. Change % (sortable, color-coded)
5. Volume (sortable, in millions)
6. Composite Score (sortable, color-coded)
7. Signals (T/F/S badges)
8. Sector

#### 4. StockScreener (`src/pages/Scanner/StockScreener.tsx`)

**Purpose**: Main stock screener page

**Layout**:

1. **Header**: Title + back button to Scanner
2. **Error Banner**: Backend connection status
3. **Configuration Panel**:
   - Universe selector (6 options)
   - Timeframe selector (3 options)
   - Top N stocks input
   - Advanced filters (collapsible)
   - "Scan for Stocks" button
4. **Results Section** (conditional):
   - Universe stats (3 cards)
   - Top picks grid (3 columns)
   - Selected stock factor breakdown
   - Full results table

**State Management**:
```typescript
const [universe, setUniverse] = useState<ScreenerParams['universe']>('sp500');
const [timeframe, setTimeframe] = useState<ScreenerParams['timeframe']>('swing');
const [topN, setTopN] = useState(20);
const [minVolume, setMinVolume] = useState(1000000);
const [minPrice, setMinPrice] = useState(5);
const [maxPrice, setMaxPrice] = useState(1000);
const [results, setResults] = useState<ScreenerResponse | null>(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [selectedStock, setSelectedStock] = useState<string | null>(null);
```

**Error Handling**:
```typescript
try {
  const data = await screenerApi.scan(params);
  setResults(data);
} catch (err) {
  setError('Backend not running! Start: python backend/screener_service/app.py');
}
```

### Routing Configuration

**Modified `src/Router.tsx`** (Lines 64-76):

```typescript
{
  path: 'scanner',
  children: [
    {
      index: true,
      element: <Scanner />,
    },
    {
      path: 'stock-screener',
      element: <StockScreener />,
    },
  ],
},
```

### Navigation Integration

**Modified `src/pages/Scanner/Scanner.tsx`** (Lines 187-211):

Added promotion card with gradient background and "Launch Screener" button:

```tsx
{/* Advanced Screener Promotion Card */}
<div className="card bg-gradient-to-r from-blue-900/30 to-purple-900/30 border-blue-500/50">
  <div className="flex items-center justify-between">
    <div className="flex items-center gap-4">
      <div className="p-3 bg-blue-600 rounded-lg">
        <TrendingUp className="w-6 h-6 text-white" />
      </div>
      <div>
        <h3 className="text-lg font-semibold text-white mb-1">
          Advanced Stock Screener
        </h3>
        <p className="text-sm text-gray-300">
          Multi-factor quantitative analysis across 6 universes - S&P 500, NASDAQ, Small Caps & more
        </p>
      </div>
    </div>
    <button
      onClick={() => navigate('/scanner/stock-screener')}
      className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition flex items-center gap-2 whitespace-nowrap"
    >
      <Search className="w-5 h-5" />
      Launch Screener
    </button>
  </div>
</div>
```

## User Workflow

1. **Access Screener**: Navigate to `/scanner`, click "Launch Screener" button
2. **Configure Scan**:
   - Select stock universe (default: S&P 500)
   - Select timeframe (default: Swing)
   - Set top N stocks (default: 20)
   - Optionally expand Advanced Filters
3. **Execute Scan**: Click "Scan for Stocks" button
4. **Review Universe Stats**: View total stocks scanned, average score, top sector
5. **Explore Top Picks**: Browse top-scoring stocks in card grid
6. **View Factor Details**: Click "View Details" on any stock to see radar chart
7. **Analyze Full Results**: Sort and filter all results in the table

## Backend Requirements

**Python Service**: `backend/screener_service/app.py`

**Expected Endpoints**:

```python
POST /api/screener/scan
{
  "universe": "sp500",
  "timeframe": "swing",
  "top_n": 20,
  "min_volume": 1000000,
  "min_price": 5,
  "max_price": 1000
}

Response:
{
  "top_picks": [...],
  "all_results": [...],
  "universe_stats": {
    "total_stocks": 500,
    "avg_score": 62.3,
    "top_sector": "Technology"
  },
  "scan_params": {...},
  "timestamp": "2025-10-10T19:28:00Z"
}

POST /api/screener/custom-scan
GET /api/screener/factor-analysis/{ticker}?timeframe=swing
GET /api/screener/health
```

## Design System

### Color Palette

**Score Colors**:
- Excellent (80-100): `bg-green-500` / `text-green-400`
- Good (60-79): `bg-blue-500` / `text-blue-400`
- Fair (40-59): `bg-yellow-500` / `text-yellow-400`
- Poor (0-39): `bg-red-500` / `text-red-400`

**Signal Colors**:
- Bullish/Strong/Positive: `bg-green-900/30 text-green-400`
- Bearish/Weak/Negative: `bg-red-900/30 text-red-400`
- Neutral: `bg-gray-900/30 text-gray-400`

**Card Backgrounds**:
- Standard: `bg-dark-card border-dark-border`
- Promotion: `bg-gradient-to-r from-blue-900/30 to-purple-900/30 border-blue-500/50`

### Typography

- **Page Title**: `text-2xl font-bold text-white`
- **Card Title**: `text-xl font-semibold text-white`
- **Section Title**: `text-lg font-semibold text-white`
- **Body Text**: `text-sm text-gray-300`
- **Labels**: `text-sm font-medium text-gray-400`

## Testing Checklist

- [ ] Navigate from Scanner to Stock Screener
- [ ] Select each universe and verify parameter passing
- [ ] Select each timeframe and verify parameter passing
- [ ] Adjust Top N and advanced filters
- [ ] Execute scan and verify loading state
- [ ] Verify error handling when backend is offline
- [ ] View universe stats display
- [ ] Browse top picks cards
- [ ] Click "View Details" to see factor breakdown
- [ ] Verify radar chart renders correctly
- [ ] Sort results table by each column
- [ ] Verify signal badges (T/F/S) display correctly
- [ ] Check color coding on scores and changes
- [ ] Test responsive layout on different screen sizes

## Known Limitations

1. **Backend Dependency**: Requires Python service on Port 5008
2. **Mock Data**: No mock data fallback (shows error banner)
3. **Factor Weights**: Fixed by timeframe (not user-customizable in UI)
4. **Real-time Updates**: No auto-refresh or WebSocket support
5. **Export**: No PDF/CSV export functionality
6. **Watchlist Integration**: Cannot add stocks to watchlist from screener
7. **Chart Integration**: No direct link to Trading page charts

## Future Enhancements

1. **Custom Factor Weights**: UI sliders for manual factor weight adjustment
2. **Saved Scans**: Save/load screening configurations
3. **Alerts**: Create price alerts directly from screener results
4. **Backtesting**: Backtest screening strategies historically
5. **Export**: PDF/CSV export of results
6. **Watchlist Integration**: One-click add to watchlist
7. **Chart Links**: Direct navigation to Trading page with symbol pre-loaded
8. **Auto-Refresh**: Configurable auto-refresh interval
9. **Custom Universes**: Define custom stock universes
10. **Comparison Mode**: Side-by-side comparison of multiple stocks

## Performance Considerations

- **Lazy Loading**: Screener components load only when route accessed
- **Memoization**: `useMemo` for column definitions and filtered data
- **Debouncing**: Consider debouncing filter inputs for better UX
- **Pagination**: Large result sets (>100 stocks) may benefit from pagination
- **Chart Optimization**: Plotly charts are heavy; consider React.memo for FactorBreakdown

## Related Features

- **Scanner** (`/scanner`): Small-cap momentum scanner with real-time updates
- **Watchlists** (`/watchlists`): Track favorite stocks
- **Alerts** (`/alerts`): Price and technical alerts
- **Trading** (`/trading`): Live trading interface
- **Analytics** (`/analytics/factors`): Factor analysis tools

## Files Modified

1. **Created**:
   - `src/api/screenerApi.ts` (157 lines)
   - `src/components/Screener/StockCard.tsx` (165 lines)
   - `src/components/Screener/FactorBreakdown.tsx` (95 lines)
   - `src/components/Screener/ScreenResults.tsx` (183 lines)
   - `src/pages/Scanner/StockScreener.tsx` (265 lines)

2. **Modified**:
   - `src/Router.tsx` (Line 20, Lines 64-76)
   - `src/pages/Scanner/Scanner.tsx` (Lines 5-6, Line 20, Lines 187-211)

**Total Lines Added**: 865+ lines

## Summary

The Stock Screener provides a professional-grade quantitative screening tool with multi-factor analysis, flexible universe selection, and comprehensive result visualization. The implementation follows the TRADER2025 design system and integrates seamlessly with the existing Scanner tab using React Router nested routes.
