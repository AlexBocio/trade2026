/**
 * Gateway API Client
 * Connects to Market Data Gateway service on port 8080
 */

import axios, { AxiosInstance } from 'axios';

// Get Gateway URL from environment or use default
const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:8080';

/**
 * Ticker/Quote data
 */
export interface Ticker {
  symbol: string;
  last_price: number;
  bid: number;
  ask: number;
  bid_size: number;
  ask_size: number;
  volume: number;
  timestamp: string;
  exchange?: string;
}

/**
 * OHLCV Candle data
 */
export interface Candle {
  symbol: string;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

/**
 * Order book level
 */
export interface OrderBookLevel {
  price: number;
  size: number;
  num_orders?: number;
}

/**
 * Order book (depth of market)
 */
export interface OrderBook {
  symbol: string;
  timestamp: string;
  bids: OrderBookLevel[];
  asks: OrderBookLevel[];
}

/**
 * Trade/tick data
 */
export interface Trade {
  symbol: string;
  timestamp: string;
  price: number;
  size: number;
  side?: 'buy' | 'sell';
  trade_id?: string;
}

/**
 * Symbol/instrument info
 */
export interface SymbolInfo {
  symbol: string;
  name?: string;
  exchange?: string;
  asset_type?: string;
  tradable?: boolean;
  min_order_size?: number;
  max_order_size?: number;
  price_increment?: number;
  size_increment?: number;
}

class GatewayApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: GATEWAY_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        console.log(`[Gateway API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('[Gateway API] Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[Gateway API] Response:`, response.status);
        return response;
      },
      (error) => {
        console.error('[Gateway API] Response error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get current ticker/quote for a symbol
   */
  async getTicker(symbol: string): Promise<Ticker> {
    try {
      const response = await this.client.get<Ticker>(`/tickers/${symbol}`);
      return response.data;
    } catch (error) {
      console.error(`[Gateway API] Failed to fetch ticker for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Get tickers for multiple symbols
   */
  async getTickers(symbols?: string[]): Promise<Ticker[]> {
    try {
      const params = symbols ? { symbols: symbols.join(',') } : {};
      const response = await this.client.get<Ticker[]>('/tickers', { params });
      return response.data;
    } catch (error) {
      console.error('[Gateway API] Failed to fetch tickers:', error);
      throw error;
    }
  }

  /**
   * Get historical candles (OHLCV)
   */
  async getCandles(
    symbol: string,
    timeframe: string = '1m',
    limit?: number,
    start?: string,
    end?: string
  ): Promise<Candle[]> {
    try {
      const params: any = { timeframe };
      if (limit) params.limit = limit;
      if (start) params.start = start;
      if (end) params.end = end;

      const response = await this.client.get<Candle[]>(`/candles/${symbol}`, { params });
      return response.data;
    } catch (error) {
      console.error(`[Gateway API] Failed to fetch candles for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Get order book (depth of market)
   */
  async getOrderBook(symbol: string, depth: number = 20): Promise<OrderBook> {
    try {
      const response = await this.client.get<OrderBook>(`/orderbook/${symbol}`, {
        params: { depth },
      });
      return response.data;
    } catch (error) {
      console.error(`[Gateway API] Failed to fetch order book for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Get recent trades
   */
  async getTrades(symbol: string, limit: number = 100): Promise<Trade[]> {
    try {
      const response = await this.client.get<Trade[]>(`/trades/${symbol}`, {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      console.error(`[Gateway API] Failed to fetch trades for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Get symbol/instrument information
   */
  async getSymbolInfo(symbol: string): Promise<SymbolInfo> {
    try {
      const response = await this.client.get<SymbolInfo>(`/symbols/${symbol}`);
      return response.data;
    } catch (error) {
      console.error(`[Gateway API] Failed to fetch symbol info for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Search for symbols
   */
  async searchSymbols(query: string): Promise<SymbolInfo[]> {
    try {
      const response = await this.client.get<SymbolInfo[]>('/symbols/search', {
        params: { q: query },
      });
      return response.data;
    } catch (error) {
      console.error(`[Gateway API] Failed to search symbols for "${query}":`, error);
      throw error;
    }
  }

  /**
   * Get all available symbols
   */
  async getAllSymbols(): Promise<SymbolInfo[]> {
    try {
      const response = await this.client.get<SymbolInfo[]>('/symbols');
      return response.data;
    } catch (error) {
      console.error('[Gateway API] Failed to fetch all symbols:', error);
      throw error;
    }
  }

  /**
   * Subscribe to real-time ticker updates via WebSocket
   * Returns WebSocket connection
   */
  createTickerWebSocket(symbol: string, onMessage: (ticker: Ticker) => void): WebSocket {
    const wsUrl = GATEWAY_URL.replace('http', 'ws') + `/ws/ticker/${symbol}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log(`[Gateway WS] Connected to ticker stream for ${symbol}`);
    };

    ws.onmessage = (event) => {
      try {
        const ticker = JSON.parse(event.data);
        onMessage(ticker);
      } catch (error) {
        console.error('[Gateway WS] Failed to parse ticker message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[Gateway WS] WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log(`[Gateway WS] Disconnected from ticker stream for ${symbol}`);
    };

    return ws;
  }

  /**
   * Subscribe to real-time trade updates via WebSocket
   */
  createTradesWebSocket(symbol: string, onMessage: (trade: Trade) => void): WebSocket {
    const wsUrl = GATEWAY_URL.replace('http', 'ws') + `/ws/trades/${symbol}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log(`[Gateway WS] Connected to trades stream for ${symbol}`);
    };

    ws.onmessage = (event) => {
      try {
        const trade = JSON.parse(event.data);
        onMessage(trade);
      } catch (error) {
        console.error('[Gateway WS] Failed to parse trade message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[Gateway WS] WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log(`[Gateway WS] Disconnected from trades stream for ${symbol}`);
    };

    return ws;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      console.error('[Gateway API] Health check failed:', error);
      throw error;
    }
  }

  /**
   * Get service stats
   */
  async getStats(): Promise<any> {
    try {
      const response = await this.client.get('/stats');
      return response.data;
    } catch (error) {
      console.error('[Gateway API] Failed to fetch stats:', error);
      throw error;
    }
  }
}

// Export singleton instance
const gatewayApi = new GatewayApiClient();
export default gatewayApi;
