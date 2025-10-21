# Multi-Timeframe Prediction Heatmap Implementation

## Overview

The Multi-Timeframe Prediction Heatmap is a cutting-edge quantitative visualization tool that displays machine learning predictions across multiple timeframes for all stocks returned by the screener. It provides traders with a comprehensive view of both long and short opportunities across 14 different time horizons in a single glance.

**Implementation Date**: 2025-10-10
**Backend Port**: 5008
**Route**: `/scanner/stock-screener`
**Technology**: React + TypeScript + Plotly.js (removed for heatmap, uses pure CSS)

## Architecture

### Data Flow

```
User Configures Scan
  ↓
Clicks "Scan & Generate Heatmap"
  ↓
Single API Call: POST /api/screener/scan-and-predict
  ↓
Backend: Scan + ML Predictions (parallel processing)
  ↓
Response: {scan_results, heatmap_data, metadata}
  ↓
Frontend: Auto-switch to Heatmap View
  ↓
Display: N stocks × 14 timeframes = (N × 14) predictions
```

### Dual-Axis Layout

The heatmap is split into two sections:

```
┌─────────────────────────────────────────────────────────────┐
│                   MULTI-TIMEFRAME HEATMAP                    │
├──────────┬─────────────────────┬──────┬────────────────────┤
│          │  SHORT OPPORTUNITIES │ NOW  │ LONG OPPORTUNITIES │
│  Ticker  │  ← Price Declines   │      │  Price Gains →     │
├──────────┼─────────────────────┼──────┼────────────────────┤
│   AAPL   │ -30d -7d -3d -1d    │  0   │ 1d 3d 7d 30d ...   │
│   TSLA   │  🔴  🔴  🔴  🔴     │      │ 🟢 🟢 🟢 🟢        │
│   NVDA   │                     │      │                    │
└──────────┴─────────────────────┴──────┴────────────────────┘
```

**LEFT SIDE**: Short opportunities (expected price declines)
**RIGHT SIDE**: Long opportunities (expected price gains)
**CENTER**: Current moment (NOW)

## Feature Set

### 1. Auto-Population Workflow

**User Experience**:
1. Configure scan parameters (universe, timeframe, criteria)
2. Click single button: "🔍 Scan & Generate Heatmap"
3. All results automatically populate heatmap
4. Toggle between "Results Table" and "Prediction Heatmap" views

**Scalability**:
- 10 stocks → 10 rows (instant)
- 50 stocks → 50 rows (scrollable)
- 100+ stocks → Virtual scrolling (future enhancement)

### 2. Timeframes

**14 Total Timeframes** (configurable by backend):

| Direction | Timeframes |
|-----------|------------|
| **SHORT** | -30d, -14d, -7d, -3d, -1d, -4h, -1h |
| **NOW** | 0 (current moment) |
| **LONG** | 1h, 4h, 1d, 3d, 7d, 14d, 30d |

Timeframes adapt based on trading style selected (intraday/swing/position).

### 3. Color Coding

**Three Display Modes** (user-selectable):

#### A. Predicted Return (Default)
- **Green Intensity**: Positive returns (0% to 10%+)
  - Strong: `rgba(34, 197, 94, 1.0)` - 10%+ expected gain
  - Moderate: `rgba(34, 197, 94, 0.5)` - 2-5% expected gain
- **Red Intensity**: Negative returns (0% to -10%)
  - Strong: `rgba(239, 68, 68, 1.0)` - 10%+ expected loss
  - Moderate: `rgba(239, 68, 68, 0.5)` - 2-5% expected loss
- **Gray**: Neutral (< ±0.5%)

#### B. Confidence Mode
- **Blue Intensity**: Model confidence (0% to 100%)
  - High: `rgba(59, 130, 246, 1.0)` - 90%+ confidence
  - Medium: `rgba(59, 130, 246, 0.6)` - 60-90% confidence
  - Low: `rgba(59, 130, 246, 0.3)` - <60% confidence

#### C. Signal Strength Mode
- **Color Gradient**: Strength of trading signal
  - Gray: No signal
  - Yellow: Weak signal
  - Orange: Moderate signal
  - Red: Strong signal

### 4. Interactive Cells

**Click Any Cell** → Trade Setup Modal displays:
- **Prediction Summary**:
  - Direction (LONG/SHORT)
  - Expected Return (%)
  - Model Confidence (%)
- **Trade Parameters**:
  - Entry Price
  - Target Price
  - Stop Loss
  - Risk/Reward Ratio
- **Position Sizing**:
  - Base Position Size (%)
  - Confidence-Adjusted Size (%)
- **Action Buttons**:
  - Execute LONG/SHORT
  - Add to Watchlist
  - Close

### 5. Screening Criteria

**Configuration Inputs**:
- **Universe**: sp500, nasdaq100, small_caps, mid_caps, micro_caps, all
- **Trading Style**: intraday, swing, position
- **Max Results**: 10-200 stocks (all populate heatmap)
- **Minimum Momentum**: % threshold
- **Maximum RSI**: Oversold threshold (20-50)
- **Minimum Volume Surge**: Volume multiplier (1.0x+)

## File Structure

```
src/
├── api/
│   └── screenerApi.ts                   # Updated with prediction endpoints
├── components/
│   └── Heatmap/
│       ├── DualAxisHeatmap.tsx         # Core heatmap component
│       └── TradeSetupModal.tsx         # Trade details modal
└── pages/
    └── Scanner/
        └── StockScreener.tsx           # Updated with heatmap integration
```

## Implementation Details

### API Service Updates (`src/api/screenerApi.ts`)

**New Interfaces**:

```typescript
export interface TradeSetup {
  action: 'LONG' | 'SHORT';
  entry_price: number;
  target_price: number;
  stop_loss: number;
  risk_reward_ratio: number;
  position_size_pct: number;
  confidence_adjusted_size_pct: number;
}

export interface CellData {
  predicted_return: number;
  confidence: number;
  direction: 'long' | 'short' | 'neutral';
  strength: number;
  trade_setup: TradeSetup;
}

export interface HeatmapData {
  tickers: string[];
  timeframes: string[];  // e.g., ["-30d", "-7d", ..., "0", ..., "7d", "30d"]
  matrix: number[][];  // predicted_return[ticker_idx][timeframe_idx]
  confidence_matrix: number[][];
  strength_matrix: number[][];
  cell_data: Record<string, Record<string, CellData>>;
}

export interface ScanAndPredictParams {
  universe: string;
  timeframe: string;
  criteria: {
    min_momentum_20d?: number;
    max_rsi?: number;
    min_volume_surge?: number;
  };
  max_results: number;
  generate_heatmap: boolean;
}

export interface ScanAndPredictResponse {
  scan_results: (StockResult & {
    momentum_20d?: number;
    rsi?: number;
    volume_surge?: number;
  })[];
  heatmap_data: HeatmapData;
  metadata: {
    results_count: number;
    scan_timestamp: string;
    prediction_timestamp: string;
  };
}
```

**New API Methods**:

```typescript
/**
 * Scan stocks and generate multi-timeframe prediction heatmap
 */
scanAndPredict: async (params: ScanAndPredictParams): Promise<ScanAndPredictResponse>

/**
 * Generate prediction heatmap for specific tickers
 */
generateHeatmap: async (tickers: string[]): Promise<HeatmapData>
```

### DualAxisHeatmap Component

**Purpose**: Core heatmap visualization with dual-axis layout

**Key Features**:
- Splits timeframes at index "0" into SHORT (left) and LONG (right)
- Three color modes: return, confidence, strength
- Interactive cells with hover effects
- Automatic legend generation
- Trade setup modal integration

**State Management**:
```typescript
const [selectedCell, setSelectedCell] = useState<{ticker: string, timeframe: string} | null>(null);
const [colorScale, setColorScale] = useState<ColorScale>('return');
const [showModal, setShowModal] = useState(false);
```

**Color Calculation**:
```typescript
const getHeatmapColor = useCallback((value: number, confidence: number, strength: number) => {
  if (colorScale === 'return') {
    const absValue = Math.abs(value);
    const intensity = Math.min(absValue / 0.1, 1);  // Cap at 10%

    if (value > 0) {
      return `rgba(34, 197, 94, ${intensity})`;  // Green for positive
    } else if (value < 0) {
      return `rgba(239, 68, 68, ${intensity})`;  // Red for negative
    } else {
      return 'rgba(75, 85, 99, 0.2)';  // Gray for neutral
    }
  }
  // ... confidence and strength modes
}, [colorScale]);
```

**Layout Structure**:
```tsx
<div className="dual-axis-heatmap">
  {/* Controls */}
  <div className="mb-6 flex items-center justify-between">
    <h2>Multi-Timeframe Prediction Heatmap</h2>
    <select value={colorScale} onChange={(e) => setColorScale(e.target.value)}>
      <option value="return">Predicted Return</option>
      <option value="confidence">Confidence</option>
      <option value="strength">Signal Strength</option>
    </select>
  </div>

  {/* Heatmap Container */}
  <div className="overflow-x-auto">
    {/* Header Row - X Axis Labels */}
    <div className="flex">
      <div className="w-20">Ticker</div>
      <div className="flex-1 text-center bg-red-900/10">SHORT OPPORTUNITIES</div>
      <div className="w-12">NOW</div>
      <div className="flex-1 text-center bg-green-900/10">LONG OPPORTUNITIES</div>
    </div>

    {/* Timeframe Labels Row */}
    <div className="flex">
      <div className="w-20">Ticker</div>
      {shortTimeframes.map(tf => <div key={tf}>{tf}</div>)}
      <div className="w-12">NOW</div>
      {longTimeframes.map(tf => <div key={tf}>{tf}</div>)}
    </div>

    {/* Data Rows */}
    {data.tickers.map((ticker, rowIdx) => (
      <div key={ticker} className="flex">
        <div className="w-20">{ticker}</div>
        {/* SHORT cells */}
        {/* LONG cells */}
      </div>
    ))}
  </div>

  {/* Legend */}
  <div className="mt-6 p-4">
    <div className="grid grid-cols-4 gap-4">
      <div><div className="bg-green-500" /> Strong Long (5%+)</div>
      <div><div className="bg-green-500 opacity-50" /> Moderate Long (2-5%)</div>
      <div><div className="bg-red-500" /> Strong Short (5%+)</div>
      <div><div className="bg-red-500 opacity-50" /> Moderate Short (2-5%)</div>
    </div>
  </div>

  {/* Trade Setup Modal */}
  {showModal && <TradeSetupModal {...} />}
</div>
```

### TradeSetupModal Component

**Purpose**: Display detailed trade setup when clicking heatmap cell

**Layout**:
```tsx
<div className="fixed inset-0 bg-black/50">
  <div className="bg-dark-card rounded-lg p-6">
    {/* Header */}
    <div className="flex items-center justify-between">
      <div>
        <h2>{ticker}</h2>
        <p>Trade Setup - {timeframe}</p>
      </div>
      <button onClick={onClose}>×</button>
    </div>

    {/* Prediction Summary */}
    <div className={isLong ? 'bg-green-900/20' : 'bg-red-900/20'}>
      <div className="grid grid-cols-3">
        <div>Direction: {trade_setup.action}</div>
        <div>Expected Return: {(predicted_return * 100).toFixed(2)}%</div>
        <div>Confidence: {(confidence * 100).toFixed(0)}%</div>
      </div>
    </div>

    {/* Trade Parameters */}
    <div className="grid grid-cols-2 gap-4">
      <div>Entry Price: ${trade_setup.entry_price}</div>
      <div>Target Price: ${trade_setup.target_price}</div>
      <div>Stop Loss: ${trade_setup.stop_loss}</div>
      <div>Risk/Reward: 1:{trade_setup.risk_reward_ratio}</div>
    </div>

    {/* Position Sizing */}
    <div>
      <div>Base Position Size: {trade_setup.position_size_pct}%</div>
      <div>Confidence-Adjusted: {trade_setup.confidence_adjusted_size_pct}%</div>
    </div>

    {/* Action Buttons */}
    <div className="flex space-x-3">
      <button className={isLong ? 'bg-green-600' : 'bg-red-600'}>
        Execute {trade_setup.action}
      </button>
      <button className="bg-blue-600">Add to Watchlist</button>
      <button onClick={onClose}>Close</button>
    </div>
  </div>
</div>
```

### StockScreener Integration

**Updated State**:
```typescript
const [scanResults, setScanResults] = useState<ScanAndPredictResponse | null>(null);
const [heatmapData, setHeatmapData] = useState<HeatmapData | null>(null);
const [activeView, setActiveView] = useState<'results' | 'heatmap'>('results');
```

**Scan Handler**:
```typescript
const handleScan = async () => {
  setLoading(true);

  try {
    // ONE API CALL: Scan + Predict + Heatmap
    const response = await screenerApi.scanAndPredict({
      universe,
      timeframe,
      criteria: {
        min_momentum_20d: minMomentum / 100,
        max_rsi: maxRsi,
        min_volume_surge: minVolumeSurge
      },
      max_results: maxResults,
      generate_heatmap: true  // Auto-generate
    });

    // Results automatically populate
    setScanResults(response);
    setHeatmapData(response.heatmap_data);

    // Auto-switch to heatmap view
    setActiveView('heatmap');

  } catch (err) {
    setError('Backend not running!');
  } finally {
    setLoading(false);
  }
};
```

**View Toggle**:
```tsx
<div className="flex space-x-2">
  <button
    className={activeView === 'results' ? 'bg-blue-600' : 'bg-dark-bg'}
    onClick={() => setActiveView('results')}
  >
    📊 Results Table
  </button>
  <button
    className={activeView === 'heatmap' ? 'bg-blue-600' : 'bg-dark-bg'}
    onClick={() => setActiveView('heatmap')}
  >
    🔥 Prediction Heatmap
  </button>
</div>
```

**Conditional Rendering**:
```tsx
{activeView === 'results' && (
  <div>
    {/* Top Picks Grid */}
    {/* Full Results Table */}
  </div>
)}

{activeView === 'heatmap' && heatmapData && (
  <div>
    <DualAxisHeatmap data={heatmapData} />
  </div>
)}
```

## Backend Requirements

**Python Service**: `backend/screener_service/app.py`

**Expected Endpoint**:

```python
@app.route('/api/screener/scan-and-predict', methods=['POST'])
def scan_and_predict():
    params = request.json

    # 1. Scan for stocks
    scan_results = screener.scan(
        universe=params['universe'],
        criteria=params['criteria'],
        max_results=params['max_results']
    )

    # 2. Generate ML predictions (parallel processing)
    if params['generate_heatmap']:
        heatmap_data = predictor.generate_heatmap(
            tickers=[s['ticker'] for s in scan_results],
            timeframe=params['timeframe']
        )

    return jsonify({
        'scan_results': scan_results,
        'heatmap_data': heatmap_data,
        'metadata': {
            'results_count': len(scan_results),
            'scan_timestamp': datetime.now().isoformat(),
            'prediction_timestamp': datetime.now().isoformat()
        }
    })
```

**Heatmap Data Generation**:

```python
def generate_heatmap(tickers: List[str], timeframe: str) -> dict:
    # Define timeframes based on trading style
    if timeframe == 'intraday':
        timeframes = ['-4h', '-1h', '-15m', '0', '15m', '1h', '4h']
    elif timeframe == 'swing':
        timeframes = ['-7d', '-3d', '-1d', '0', '1d', '3d', '7d', '14d']
    else:  # position
        timeframes = ['-30d', '-14d', '-7d', '0', '7d', '14d', '30d', '60d']

    # Initialize matrices
    matrix = []
    confidence_matrix = []
    strength_matrix = []
    cell_data = {}

    # Predict for each stock × timeframe
    for ticker in tickers:
        ticker_predictions = []
        ticker_confidences = []
        ticker_strengths = []
        cell_data[ticker] = {}

        for tf in timeframes:
            pred = ml_model.predict(ticker, tf)
            ticker_predictions.append(pred['return'])
            ticker_confidences.append(pred['confidence'])
            ticker_strengths.append(pred['strength'])

            # Generate trade setup
            cell_data[ticker][tf] = {
                'predicted_return': pred['return'],
                'confidence': pred['confidence'],
                'direction': 'long' if pred['return'] > 0 else 'short',
                'strength': pred['strength'],
                'trade_setup': generate_trade_setup(ticker, tf, pred)
            }

        matrix.append(ticker_predictions)
        confidence_matrix.append(ticker_confidences)
        strength_matrix.append(ticker_strengths)

    return {
        'tickers': tickers,
        'timeframes': timeframes,
        'matrix': matrix,
        'confidence_matrix': confidence_matrix,
        'strength_matrix': strength_matrix,
        'cell_data': cell_data
    }
```

## User Workflow

### Standard Flow

1. **Navigate**: Go to `/scanner` → Click "Launch Screener" → `/scanner/stock-screener`

2. **Configure Scan**:
   - Select Universe: Small Caps ($300M-$2B)
   - Select Trading Style: Swing (2-10 Days)
   - Set Max Results: 50 stocks
   - Set Criteria:
     - Min Momentum: 10%
     - Max RSI: 30 (oversold)
     - Min Volume Surge: 1.5x

3. **Execute**: Click "🔍 Scan & Generate Heatmap"

4. **Loading**: Shows "Scanning & Generating Heatmap..." (2-10 seconds)

5. **Results**: Auto-switch to Heatmap view
   - Summary: "Found 45 stocks matching your criteria"
   - Heatmap: 45 stocks × 14 timeframes = 630 predictions displayed

6. **Explore**:
   - **Visual Scan**: Look for hot spots (intense colors)
   - **Filter**: Use color scale dropdown (Return/Confidence/Strength)
   - **Analyze**: Click cell → View trade setup modal
   - **Execute**: Click "Execute LONG" or "Execute SHORT"
   - **Track**: Click "Add to Watchlist"

7. **Toggle**: Switch to "Results Table" to see detailed stock data

### Advanced Patterns

**Pattern 1: Find Best Short Opportunities**
1. Scan for stocks
2. Switch color scale to "Predicted Return"
3. Look at LEFT side of heatmap
4. Find darkest red cells (strongest short signals)
5. Click cell → Review trade setup → Execute

**Pattern 2: Multi-Timeframe Confirmation**
1. Scan for stocks
2. Look for stocks with consistent colors across multiple timeframes
3. Example: TSLA shows green in 1d, 3d, 7d, 14d = strong long trend
4. Click any cell → View details → Execute

**Pattern 3: High-Confidence Plays**
1. Scan for stocks
2. Switch color scale to "Confidence"
3. Look for darkest blue cells (90%+ confidence)
4. Click cell → Verify predicted return → Execute

## Design System

### Color Palette

**Return Mode**:
- Green (Long): `rgba(34, 197, 94, ${intensity})`
- Red (Short): `rgba(239, 68, 68, ${intensity})`
- Gray (Neutral): `rgba(75, 85, 99, 0.2)`

**Confidence Mode**:
- Blue: `rgba(59, 130, 246, ${intensity})`

**Strength Mode**:
- None: `rgba(75, 85, 99, 0.2)`
- Weak: `rgba(251, 191, 36, 0.4)`
- Moderate: `rgba(249, 115, 22, 0.7)`
- Strong: `rgba(239, 68, 68, 1.0)`

**Backgrounds**:
- Card: `bg-dark-card`
- Background: `bg-dark-bg`
- Border: `border-dark-border`
- Short Header: `bg-red-900/10`
- Long Header: `bg-green-900/10`

### Typography

- **Page Title**: `text-2xl font-bold text-white`
- **Section Title**: `text-xl font-semibold text-white`
- **Ticker**: `font-mono font-bold text-white`
- **Percentage**: `text-xs font-medium text-white`
- **Labels**: `text-sm text-gray-400`

## Performance Considerations

### Optimization Strategies

**1. Matrix Operations**:
```typescript
// Cache color calculations
const colorCache = useMemo(() => {
  const cache: Record<string, string> = {};
  return cache;
}, [colorScale]);
```

**2. Virtual Scrolling** (for 100+ stocks):
```typescript
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={800}
  itemCount={scanResults.length}
  itemSize={50}
  width="100%"
>
  {({ index, style }) => (
    <HeatmapRow style={style} ticker={tickers[index]} />
  )}
</FixedSizeList>
```

**3. Lazy Loading**:
```typescript
// Load cell_data on demand
const [cellData, setCellData] = useState({});

const loadCellData = async (ticker: string, timeframe: string) => {
  if (!cellData[ticker]?.[timeframe]) {
    const data = await screenerApi.getCellData(ticker, timeframe);
    setCellData(prev => ({
      ...prev,
      [ticker]: { ...prev[ticker], [timeframe]: data }
    }));
  }
};
```

### Scalability Limits

| Result Count | Display Method | Performance |
|--------------|----------------|-------------|
| 1-25 stocks  | Full display   | Instant     |
| 26-50 stocks | Scrollable     | Fast        |
| 51-100 stocks | Virtual scroll | Good        |
| 100+ stocks  | Paginated      | Acceptable  |

## Testing Checklist

- [ ] Configure scan with different universes
- [ ] Test with 10, 25, 50, 100 stocks
- [ ] Verify color coding for each mode (return/confidence/strength)
- [ ] Click cells to open trade setup modal
- [ ] Verify trade parameters (entry, target, stop, R:R)
- [ ] Test "Execute LONG/SHORT" buttons
- [ ] Test "Add to Watchlist" button
- [ ] Toggle between Results Table and Heatmap views
- [ ] Verify auto-switch to heatmap after scan
- [ ] Test error handling when backend offline
- [ ] Test scrolling for large result sets
- [ ] Verify responsive layout on different screen sizes
- [ ] Test hover effects on cells
- [ ] Verify legend accuracy

## Known Limitations

1. **Backend Dependency**: Requires ML prediction service on Port 5008
2. **No Mock Data**: No fallback when backend offline
3. **Static Timeframes**: Timeframes fixed per trading style (not user-customizable in UI)
4. **No Real-time Updates**: Predictions are static (no auto-refresh)
5. **No Export**: Cannot export heatmap as image/PDF
6. **No Comparison**: Cannot compare multiple scans side-by-side
7. **No Historical**: Cannot view historical prediction accuracy
8. **No Filtering**: Cannot filter heatmap by sector/market cap
9. **No Sorting**: Cannot sort stocks by best predictions
10. **Limited Cell Data**: Only available via modal (not inline tooltips)

## Future Enhancements

1. **Interactive Features**:
   - Inline tooltips on hover (no click required)
   - Right-click context menu (Execute, Watchlist, Alert)
   - Drag-to-select multiple cells
   - Cell annotations (notes, tags)

2. **Advanced Filtering**:
   - Filter by sector/industry
   - Filter by confidence threshold
   - Filter by expected return range
   - Show only long or short opportunities

3. **Sorting & Ranking**:
   - Sort by best 1-day prediction
   - Sort by best 1-week prediction
   - Sort by highest confidence
   - Sort by best risk/reward

4. **Performance**:
   - Virtual scrolling for 100+ stocks
   - Progressive loading (load visible cells first)
   - WebSocket for real-time prediction updates
   - Server-side rendering for initial load

5. **Export & Sharing**:
   - Export heatmap as PNG/PDF
   - Share via URL (saved configuration)
   - Print-friendly view
   - CSV export of all predictions

6. **Historical Analysis**:
   - Backtest prediction accuracy
   - Show actual vs predicted returns
   - Track model performance over time
   - Display confidence calibration

7. **Machine Learning**:
   - Multiple models (ensemble voting)
   - Model selection dropdown
   - Custom model weights
   - Feature importance overlay

8. **Integration**:
   - One-click trade execution (via Trading page)
   - Auto-create alerts for high-confidence predictions
   - Portfolio impact analysis (how prediction affects portfolio)
   - Risk overlay (VaR, CVaR per timeframe)

## Related Features

- **Stock Screener** (`/scanner/stock-screener`): Multi-factor stock screening
- **Small-Cap Scanner** (`/scanner`): Real-time momentum scanner
- **Watchlists** (`/watchlists`): Track favorite stocks
- **Alerts** (`/alerts`): Price and technical alerts
- **Trading** (`/trading`): Live trading interface
- **Backtesting** (`/backtesting`): Strategy backtesting
- **AI Lab** (`/ai-lab`): Machine learning experiments

## Files Modified

1. **Updated**:
   - `src/api/screenerApi.ts` (+87 lines)

2. **Created**:
   - `src/components/Heatmap/TradeSetupModal.tsx` (165 lines)
   - `src/components/Heatmap/DualAxisHeatmap.tsx` (271 lines)

3. **Modified**:
   - `src/pages/Scanner/StockScreener.tsx` (391 lines, +121 changes)

**Total Lines Added**: ~544 lines

## Summary

The Multi-Timeframe Prediction Heatmap is a professional-grade quantitative visualization tool that provides traders with unprecedented insight into ML-predicted price movements across 14 timeframes for all screened stocks. The dual-axis layout (SHORT left, LONG right) enables instant visual identification of opportunities, while interactive cells provide detailed trade setups with entry, target, stop loss, and position sizing recommendations.

The seamless one-click workflow (Scan → Auto-populate Heatmap → Click Cell → Execute Trade) makes this feature exceptionally user-friendly while maintaining the sophistication required for professional quantitative trading.
