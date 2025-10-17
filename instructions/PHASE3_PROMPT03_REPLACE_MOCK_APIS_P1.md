# Phase 3 - Prompt 03: Replace Mock APIs - Priority 1 (Core Trading)

**Phase**: 3 - Frontend Integration  
**Prompt**: 03 of 08  
**Purpose**: Replace core trading mock APIs with real backend integration  
**Duration**: 10-12 hours  
**Status**: ⏸️ Ready after Prompt 02 complete

---

## 🛑 PREREQUISITES

- [ ] Prompt 02 complete (frontend copied and build verified)
- [ ] Phase 2 complete (all backend services operational)
- [ ] Backend APIs tested and accessible
- [ ] Frontend development environment working

---

## 🎯 TASK OVERVIEW

### What This Prompt Does

Replace Priority 1 (core trading) mock APIs with real backend integration:

**Services to Integrate**:
1. **OMS** (port 8099) - Order management
2. **Risk** (port 8103) - Risk checks
3. **Gateway** (port 8080) - Market data
4. **Live Gateway** (port 8200) - Order execution

**Pages to Update**:
- Dashboard
- Orders page
- Positions page
- Market data display
- Order entry form

**Result**: Core trading functionality operational with real data

---

## 📋 INTEGRATION SEQUENCE

### Integration 1: OMS (Order Management System)

**Duration**: 4 hours  
**Priority**: CRITICAL

#### Step 1: Create Real API Client

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\frontend\src\api

# Open omsApi.ts (or create if doesn't exist)
```

**Current (Mock) Implementation**:
```typescript
// src/api/omsApi.ts - BEFORE
export const submitOrder = async (order: Order) => {
  return Promise.resolve({
    success: true,
    orderId: `mock-${Date.now()}`,
    status: 'submitted'
  });
};

export const getOrders = async (account: string) => {
  return Promise.resolve([
    { orderId: '1', symbol: 'BTCUSDT', side: 'buy', quantity: 0.1, status: 'filled' },
    { orderId: '2', symbol: 'ETHUSDT', side: 'sell', quantity: 1.0, status: 'pending' }
  ]);
};

export const getPositions = async (account: string) => {
  return Promise.resolve([
    { symbol: 'BTCUSDT', quantity: 0.5, avgPrice: 45000, unrealizedPnL: 250 },
    { symbol: 'ETHUSDT', quantity: 2.0, avgPrice: 3000, unrealizedPnL: 150 }
  ]);
};
```

**New (Real) Implementation**:
```typescript
// src/api/omsApi.ts - AFTER
import axios, { AxiosError } from 'axios';

const OMS_URL = import.meta.env.VITE_OMS_URL || 'http://localhost:8099';
const API_TIMEOUT = 5000;

// Configure axios instance
const omsClient = axios.create({
  baseURL: OMS_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for auth
omsClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for error handling
omsClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    console.error('OMS API Error:', error);
    throw error;
  }
);

// Types
export interface Order {
  account: string;
  symbol: string;
  side: 'buy' | 'sell';
  type: 'market' | 'limit' | 'stop' | 'stop_limit';
  quantity: number;
  price?: number;
  stopPrice?: number;
  timeInForce?: 'GTC' | 'IOC' | 'FOK';
}

export interface OrderResponse {
  orderId: string;
  status: 'submitted' | 'pending' | 'filled' | 'cancelled' | 'rejected';
  message?: string;
}

export interface Position {
  symbol: string;
  quantity: number;
  avgPrice: number;
  currentPrice?: number;
  unrealizedPnL: number;
  realizedPnL: number;
}

// API Functions

/**
 * Submit a new order
 */
export const submitOrder = async (order: Order): Promise<OrderResponse> => {
  try {
    const response = await omsClient.post<OrderResponse>('/orders', order);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || 'Failed to submit order');
    }
    throw error;
  }
};

/**
 * Get all orders for an account
 */
export const getOrders = async (account: string, status?: string): Promise<any[]> => {
  try {
    const params = status ? { status } : {};
    const response = await omsClient.get(`/orders/${account}`, { params });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || 'Failed to fetch orders');
    }
    throw error;
  }
};

/**
 * Get a specific order
 */
export const getOrder = async (orderId: string): Promise<any> => {
  try {
    const response = await omsClient.get(`/order/${orderId}`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || 'Failed to fetch order');
    }
    throw error;
  }
};

/**
 * Cancel an order
 */
export const cancelOrder = async (orderId: string): Promise<void> => {
  try {
    await omsClient.delete(`/order/${orderId}`);
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || 'Failed to cancel order');
    }
    throw error;
  }
};

/**
 * Get all positions for an account
 */
export const getPositions = async (account: string): Promise<Position[]> => {
  try {
    const response = await omsClient.get<Position[]>(`/positions/${account}`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || 'Failed to fetch positions');
    }
    throw error;
  }
};

/**
 * Get fills for an account
 */
export const getFills = async (account: string, startDate?: Date, endDate?: Date): Promise<any[]> => {
  try {
    const params: any = {};
    if (startDate) params.start = startDate.toISOString();
    if (endDate) params.end = endDate.toISOString();
    
    const response = await omsClient.get(`/fills/${account}`, { params });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || 'Failed to fetch fills');
    }
    throw error;
  }
};
```

**Checklist**:
- [ ] omsApi.ts updated with real implementation
- [ ] All API functions converted
- [ ] Error handling added
- [ ] TypeScript types defined
- [ ] Auth token handling added

---

#### Step 2: Update Orders Page Component

```typescript
// src/pages/Orders.tsx - Update to use real API

import { useState, useEffect } from 'react';
import { getOrders, cancelOrder } from '../api/omsApi';
import { toast } from 'react-toastify'; // or your toast library

export const OrdersPage = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const account = 'test_account'; // Get from auth context

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await getOrders(account);
      setOrders(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load orders';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelOrder = async (orderId: string) => {
    try {
      await cancelOrder(orderId);
      toast.success('Order cancelled');
      loadOrders(); // Refresh
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to cancel order';
      toast.error(message);
    }
  };

  if (loading) return <div>Loading orders...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Orders</h1>
      <table>
        <thead>
          <tr>
            <th>Order ID</th>
            <th>Symbol</th>
            <th>Side</th>
            <th>Quantity</th>
            <th>Price</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order: any) => (
            <tr key={order.orderId}>
              <td>{order.orderId}</td>
              <td>{order.symbol}</td>
              <td>{order.side}</td>
              <td>{order.quantity}</td>
              <td>{order.price || 'Market'}</td>
              <td>{order.status}</td>
              <td>
                {order.status === 'pending' && (
                  <button onClick={() => handleCancelOrder(order.orderId)}>
                    Cancel
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

**Checklist**:
- [ ] Orders.tsx updated
- [ ] Real API calls implemented
- [ ] Loading states added
- [ ] Error handling added
- [ ] Toast notifications added

---

#### Step 3: Update Positions Page Component

```typescript
// src/pages/Positions.tsx

import { useState, useEffect } from 'react';
import { getPositions } from '../api/omsApi';
import { toast } from 'react-toastify';

export const PositionsPage = () => {
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const account = 'test_account';

  useEffect(() => {
    loadPositions();
    
    // Refresh every 5 seconds
    const interval = setInterval(loadPositions, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadPositions = async () => {
    setLoading(true);
    
    try {
      const data = await getPositions(account);
      setPositions(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load positions';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Positions</h1>
      {loading && <div>Refreshing...</div>}
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Quantity</th>
            <th>Avg Price</th>
            <th>Current Price</th>
            <th>Unrealized P&L</th>
            <th>Realized P&L</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((pos: any) => (
            <tr key={pos.symbol}>
              <td>{pos.symbol}</td>
              <td>{pos.quantity}</td>
              <td>${pos.avgPrice.toFixed(2)}</td>
              <td>${pos.currentPrice?.toFixed(2) || '-'}</td>
              <td className={pos.unrealizedPnL >= 0 ? 'positive' : 'negative'}>
                ${pos.unrealizedPnL.toFixed(2)}
              </td>
              <td className={pos.realizedPnL >= 0 ? 'positive' : 'negative'}>
                ${pos.realizedPnL.toFixed(2)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

**Checklist**:
- [ ] Positions.tsx updated
- [ ] Auto-refresh implemented
- [ ] P&L display working

---

#### Step 4: Update Order Entry Form

```typescript
// src/components/OrderForm.tsx

import { useState } from 'react';
import { submitOrder } from '../api/omsApi';
import { checkRisk } from '../api/riskApi'; // We'll create this next
import { toast } from 'react-toastify';

export const OrderForm = () => {
  const [formData, setFormData] = useState({
    symbol: 'BTCUSDT',
    side: 'buy',
    type: 'limit',
    quantity: 0,
    price: 0
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      // Step 1: Risk check
      const riskResult = await checkRisk({
        account: 'test_account',
        ...formData
      });

      if (!riskResult.approved) {
        toast.error(`Risk check failed: ${riskResult.reason}`);
        return;
      }

      // Step 2: Submit order
      const result = await submitOrder({
        account: 'test_account',
        ...formData
      });

      toast.success(`Order submitted: ${result.orderId}`);
      
      // Reset form
      setFormData({
        symbol: 'BTCUSDT',
        side: 'buy',
        type: 'limit',
        quantity: 0,
        price: 0
      });
      
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Order failed';
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Symbol</label>
        <input
          type="text"
          value={formData.symbol}
          onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
          required
        />
      </div>

      <div>
        <label>Side</label>
        <select
          value={formData.side}
          onChange={(e) => setFormData({ ...formData, side: e.target.value as 'buy' | 'sell' })}
        >
          <option value="buy">Buy</option>
          <option value="sell">Sell</option>
        </select>
      </div>

      <div>
        <label>Type</label>
        <select
          value={formData.type}
          onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
        >
          <option value="market">Market</option>
          <option value="limit">Limit</option>
        </select>
      </div>

      <div>
        <label>Quantity</label>
        <input
          type="number"
          step="0.001"
          value={formData.quantity}
          onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) })}
          required
        />
      </div>

      {formData.type === 'limit' && (
        <div>
          <label>Price</label>
          <input
            type="number"
            step="0.01"
            value={formData.price}
            onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
            required
          />
        </div>
      )}

      <button type="submit" disabled={submitting}>
        {submitting ? 'Submitting...' : 'Submit Order'}
      </button>
    </form>
  );
};
```

**Checklist**:
- [ ] OrderForm.tsx updated
- [ ] Risk check before submission
- [ ] Loading state during submission
- [ ] Form validation
- [ ] Success/error feedback

---

### Integration 2: Risk Service

**Duration**: 2 hours

#### Step 1: Create Risk API Client

```typescript
// src/api/riskApi.ts

import axios from 'axios';

const RISK_URL = import.meta.env.VITE_RISK_URL || 'http://localhost:8103';

const riskClient = axios.create({
  baseURL: RISK_URL,
  timeout: 2000, // Risk checks must be fast
  headers: {
    'Content-Type': 'application/json'
  }
});

export interface RiskCheckRequest {
  account: string;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  price?: number;
}

export interface RiskCheckResponse {
  approved: boolean;
  reason?: string;
  checks: {
    positionLimit: boolean;
    orderSize: boolean;
    buyingPower: boolean;
    concentration: boolean;
    var: boolean;
  };
}

/**
 * Check if order passes risk checks
 */
export const checkRisk = async (order: RiskCheckRequest): Promise<RiskCheckResponse> => {
  try {
    const response = await riskClient.post<RiskCheckResponse>('/check', order);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      // Risk check failure should fail closed
      return {
        approved: false,
        reason: error.response?.data?.message || 'Risk check failed',
        checks: {
          positionLimit: false,
          orderSize: false,
          buyingPower: false,
          concentration: false,
          var: false
        }
      };
    }
    throw error;
  }
};

/**
 * Get risk limits for an account
 */
export const getRiskLimits = async (account: string): Promise<any> => {
  try {
    const response = await riskClient.get(`/limits/${account}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};
```

**Checklist**:
- [ ] riskApi.ts created
- [ ] Risk check function implemented
- [ ] Fail-closed error handling
- [ ] Fast timeout (< 2s)

---

### Integration 3: Gateway (Market Data)

**Duration**: 3 hours

#### Step 1: Create Market Data API Client

```typescript
// src/api/marketDataApi.ts

import axios from 'axios';

const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:8080';

const gatewayClient = axios.create({
  baseURL: GATEWAY_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export interface Ticker {
  symbol: string;
  exchange: string;
  last: number;
  bid: number;
  ask: number;
  volume: number;
  timestamp: number;
}

export interface Candle {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

/**
 * Get ticker for a symbol
 */
export const getTicker = async (exchange: string, symbol: string): Promise<Ticker> => {
  try {
    const response = await gatewayClient.get<Ticker>(`/ticker/${exchange}/${symbol}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get all tickers
 */
export const getAllTickers = async (exchange?: string): Promise<Ticker[]> => {
  try {
    const params = exchange ? { exchange } : {};
    const response = await gatewayClient.get<Ticker[]>('/tickers', { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get candles/OHLCV data
 */
export const getCandles = async (
  symbol: string,
  interval: string = '1m',
  limit: number = 100
): Promise<Candle[]> => {
  try {
    const response = await gatewayClient.get<Candle[]>('/candles', {
      params: { symbol, interval, limit }
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Subscribe to ticker updates (WebSocket)
 * Returns cleanup function
 */
export const subscribeToTicker = (
  symbol: string,
  callback: (ticker: Ticker) => void
): (() => void) => {
  const ws = new WebSocket(`${GATEWAY_URL.replace('http', 'ws')}/ws/ticker/${symbol}`);
  
  ws.onmessage = (event) => {
    const ticker = JSON.parse(event.data);
    callback(ticker);
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  // Return cleanup function
  return () => {
    ws.close();
  };
};
```

**Checklist**:
- [ ] marketDataApi.ts created
- [ ] Ticker functions implemented
- [ ] Candle functions implemented
- [ ] WebSocket support added (if needed)

---

#### Step 2: Update Market Data Page

```typescript
// src/pages/MarketData.tsx

import { useState, useEffect } from 'react';
import { getTicker, getAllTickers } from '../api/marketDataApi';

export const MarketDataPage = () => {
  const [tickers, setTickers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTickers();
    
    // Auto-refresh every 5 seconds
    const interval = setInterval(loadTickers, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadTickers = async () => {
    setLoading(true);
    
    try {
      const data = await getAllTickers('binance');
      setTickers(data);
    } catch (err) {
      console.error('Failed to load tickers:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Market Data</h1>
      {loading && <span>Refreshing...</span>}
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Last</th>
            <th>Bid</th>
            <th>Ask</th>
            <th>Volume</th>
          </tr>
        </thead>
        <tbody>
          {tickers.map((ticker) => (
            <tr key={ticker.symbol}>
              <td>{ticker.symbol}</td>
              <td>${ticker.last.toFixed(2)}</td>
              <td>${ticker.bid.toFixed(2)}</td>
              <td>${ticker.ask.toFixed(2)}</td>
              <td>{ticker.volume.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

**Checklist**:
- [ ] MarketData.tsx updated
- [ ] Real ticker data displaying
- [ ] Auto-refresh working

---

#### Step 3: Update Dashboard with Market Data

```typescript
// src/pages/Dashboard.tsx

import { useEffect, useState } from 'react';
import { getPositions } from '../api/omsApi';
import { getTicker } from '../api/marketDataApi';

export const Dashboard = () => {
  const [positions, setPositions] = useState<any[]>([]);
  const [tickers, setTickers] = useState<Record<string, any>>({});

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000); // Every 10s
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      // Load positions
      const posData = await getPositions('test_account');
      setPositions(posData);

      // Load current prices for each position
      const tickerPromises = posData.map((pos: any) =>
        getTicker('binance', pos.symbol)
      );
      const tickerData = await Promise.all(tickerPromises);
      
      const tickerMap: Record<string, any> = {};
      tickerData.forEach((ticker) => {
        tickerMap[ticker.symbol] = ticker;
      });
      setTickers(tickerMap);
      
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    }
  };

  const totalPnL = positions.reduce((sum, pos) => sum + pos.unrealizedPnL, 0);

  return (
    <div>
      <h1>Dashboard</h1>
      
      <div className="summary">
        <div>Total Unrealized P&L: ${totalPnL.toFixed(2)}</div>
        <div>Positions: {positions.length}</div>
      </div>

      <h2>Current Positions</h2>
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Quantity</th>
            <th>Avg Price</th>
            <th>Current Price</th>
            <th>P&L</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((pos) => {
            const currentPrice = tickers[pos.symbol]?.last || pos.avgPrice;
            const pnl = (currentPrice - pos.avgPrice) * pos.quantity;
            
            return (
              <tr key={pos.symbol}>
                <td>{pos.symbol}</td>
                <td>{pos.quantity}</td>
                <td>${pos.avgPrice.toFixed(2)}</td>
                <td>${currentPrice.toFixed(2)}</td>
                <td className={pnl >= 0 ? 'positive' : 'negative'}>
                  ${pnl.toFixed(2)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
```

**Checklist**:
- [ ] Dashboard.tsx updated
- [ ] Positions with current prices
- [ ] Total P&L calculation

---

### Integration 4: Live Gateway

**Duration**: 3 hours

```typescript
// src/api/liveGatewayApi.ts

import axios from 'axios';

const LIVE_GATEWAY_URL = import.meta.env.VITE_LIVE_GATEWAY_URL || 'http://localhost:8200';

const liveGatewayClient = axios.create({
  baseURL: LIVE_GATEWAY_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * Get order status from exchange
 */
export const getOrderStatus = async (orderId: string): Promise<any> => {
  try {
    const response = await liveGatewayClient.get(`/order/${orderId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get exchange connectivity status
 */
export const getExchangeStatus = async (): Promise<any> => {
  try {
    const response = await liveGatewayClient.get('/status');
    return response.data;
  } catch (error) {
    throw error;
  }
};
```

**Checklist**:
- [ ] liveGatewayApi.ts created
- [ ] Order status tracking
- [ ] Exchange connectivity check

---

## ✅ TESTING CHECKLIST

### Test Each Integration

**OMS Integration**:
- [ ] Can submit order via UI
- [ ] Order appears in orders table
- [ ] Can cancel pending order
- [ ] Positions load and display
- [ ] Position data accurate
- [ ] Auto-refresh working

**Risk Integration**:
- [ ] Risk check executes before order
- [ ] Approved orders proceed
- [ ] Rejected orders show error
- [ ] Risk check latency < 2s

**Gateway Integration**:
- [ ] Tickers load and display
- [ ] Market data refreshes
- [ ] Candles/charts display (if implemented)
- [ ] WebSocket updates (if implemented)

**Live Gateway Integration**:
- [ ] Order status updates
- [ ] Exchange status visible

### End-to-End Test

**Complete Order Flow**:
1. Login to app
2. Navigate to Orders page
3. Click "New Order"
4. Fill form: BTCUSDT, Buy, 0.001, Limit, 45000
5. Submit
6. Verify risk check passes
7. Verify order submitted
8. Verify order appears in table
9. Navigate to Positions
10. Verify position updates (when filled)
11. Check Dashboard
12. Verify position and P&L display

**Success Criteria**:
- [ ] Complete flow works end-to-end
- [ ] No errors in browser console
- [ ] All data displays correctly
- [ ] Auto-refresh working
- [ ] Performance acceptable

---

## 🚦 VALIDATION GATE

### Prompt 03 Complete?

**Checklist**:
- [ ] All 4 services integrated (OMS, Risk, Gateway, Live Gateway)
- [ ] All mock APIs replaced in P1 pages
- [ ] Orders page functional
- [ ] Positions page functional
- [ ] Market data displaying
- [ ] Order form working
- [ ] Dashboard updated
- [ ] End-to-end test passed
- [ ] No critical errors
- [ ] Performance acceptable

**Decision**:
- ✅ ALL COMPLETE → Proceed to Prompt 04
- ❌ ISSUES → Fix before proceeding

---

## 📊 PROMPT 03 COMPLETION CRITERIA

Prompt 03 complete when:

- [ ] OMS fully integrated
- [ ] Risk service integrated
- [ ] Gateway integrated
- [ ] Live Gateway integrated
- [ ] Core trading pages functional
- [ ] End-to-end order flow working
- [ ] Testing passed
- [ ] COMPLETION_TRACKER.md updated

**Next Prompt**: PHASE3_PROMPT04_REPLACE_MOCK_APIS_P2.md

---

**Prompt Status**: ⏸️ READY (after Prompt 02)

**Estimated Time**: 10-12 hours

**Outcome**: Core trading functionality with real backend integration
