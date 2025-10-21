/**
 * Real API service - connects to Trade2026 backend services
 * Integrates OMS, Risk, Gateway, and Live Gateway APIs
 */

import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type { ScannerResult, Position, Account, PortfolioMetrics } from '../../types/trading.types';
import type { Strategy, Backtest, StrategyTemplate } from '../../types/strategy.types';
import type { DatabaseTable, TierMetrics } from '../../types/database.types';

// Import backend API clients
import omsApi, { type OrderRequest, type OrderResponse, type PositionResponse, type FillResponse } from '../../api/omsApi';
import riskApi, { type RiskCheckRequest, type RiskCheckResponse, type RiskLimits, type RiskMetrics } from '../../api/riskApi';
import gatewayApi, { type Ticker, type Candle, type OrderBook, type Trade as MarketTrade, type SymbolInfo } from '../../api/gatewayApi';
import liveGatewayApi, { type RouteOrderRequest, type RouteOrderResponse, type ExchangeOrderStatus, type ExchangeStatus } from '../../api/liveGatewayApi';
import authApi, { type LoginRequest, type LoginResponse, type UserProfile, type RegisterRequest } from '../../api/authApi';
import ptrcApi, { type PTRCPosition, type PnLSummary, type PTRCTrade, type ReportRequest, type ReportResponse } from '../../api/ptrcApi';

export class RealAPI {
  private client: AxiosInstance;

  // Expose backend API clients
  public oms = omsApi;
  public risk = riskApi;
  public gateway = gatewayApi;
  public liveGateway = liveGatewayApi;
  public auth = authApi;
  public ptrc = ptrcApi;

  constructor() {
    // Configure axios client for legacy endpoints (strategies, backtests, etc.)
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for authentication
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          console.error('Unauthorized - please login');
        }
        return Promise.reject(error);
      }
    );

    console.log('[RealAPI] Initialized with Trade2026 backend services');
  }

  // ===== TRADING ENDPOINTS (OMS Integration) =====

  /**
   * Submit an order
   */
  async submitOrder(order: OrderRequest): Promise<OrderResponse> {
    // First, perform risk check
    const riskCheck = await this.risk.checkOrder({
      symbol: order.symbol,
      side: order.side,
      quantity: order.quantity,
      price: order.price,
      account: order.account,
      order_type: order.order_type,
    });

    if (!riskCheck.approved) {
      throw new Error(`Risk check failed: ${riskCheck.rejection_reason}`);
    }

    // If risk check passes, submit to OMS
    return await this.oms.submitOrder(order);
  }

  /**
   * Get all orders
   */
  async getOrders(account?: string): Promise<OrderResponse[]> {
    return await this.oms.getOrders(account);
  }

  /**
   * Cancel an order
   */
  async cancelOrder(orderId: string): Promise<{ success: boolean; message?: string }> {
    return await this.oms.cancelOrder(orderId);
  }

  /**
   * Get all fills
   */
  async getFills(account?: string): Promise<FillResponse[]> {
    return await this.oms.getFills(account);
  }

  // ===== POSITION ENDPOINTS (OMS Integration) =====

  /**
   * Get positions (OMS integration)
   * Maps to frontend Position type
   */
  async getPositions(): Promise<Position[]> {
    const positions = await this.oms.getPositions();

    // Map backend positions to frontend Position type
    return positions.map((pos: PositionResponse) => ({
      id: `pos-${pos.symbol}`,
      symbol: pos.symbol,
      side: pos.side,
      quantity: pos.quantity,
      entryPrice: pos.avg_price,
      currentPrice: pos.current_price || pos.avg_price,
      unrealizedPnL: pos.unrealized_pnl || 0,
      unrealizedPnLPct: pos.unrealized_pnl ? (pos.unrealized_pnl / (pos.avg_price * pos.quantity)) * 100 : 0,
      stopLoss: 0, // TODO: Get from strategy
      profitTarget: 0, // TODO: Get from strategy
      daysHeld: 0, // TODO: Calculate
      entryDate: new Date().toISOString().split('T')[0], // TODO: Get actual entry date
    }));
  }

  /**
   * Get a specific position
   */
  async getPosition(id: string): Promise<Position | null> {
    // Extract symbol from position ID (format: pos-SYMBOL)
    const symbol = id.replace('pos-', '');
    const pos = await this.oms.getPosition(symbol);

    if (!pos) return null;

    return {
      id,
      symbol: pos.symbol,
      side: pos.side,
      quantity: pos.quantity,
      entryPrice: pos.avg_price,
      currentPrice: pos.current_price || pos.avg_price,
      unrealizedPnL: pos.unrealized_pnl || 0,
      unrealizedPnLPct: pos.unrealized_pnl ? (pos.unrealized_pnl / (pos.avg_price * pos.quantity)) * 100 : 0,
      stopLoss: 0,
      profitTarget: 0,
      daysHeld: 0,
      entryDate: new Date().toISOString().split('T')[0],
    };
  }

  // ===== MARKET DATA ENDPOINTS (Gateway Integration) =====

  /**
   * Get ticker data
   */
  async getTicker(symbol: string): Promise<Ticker> {
    return await this.gateway.getTicker(symbol);
  }

  /**
   * Get multiple tickers
   */
  async getTickers(symbols?: string[]): Promise<Ticker[]> {
    return await this.gateway.getTickers(symbols);
  }

  /**
   * Get candle/OHLCV data
   */
  async getCandles(symbol: string, timeframe: string = '1m', limit?: number): Promise<Candle[]> {
    return await this.gateway.getCandles(symbol, timeframe, limit);
  }

  /**
   * Get order book
   */
  async getOrderBook(symbol: string, depth?: number): Promise<OrderBook> {
    return await this.gateway.getOrderBook(symbol, depth);
  }

  /**
   * Search symbols
   */
  async searchSymbols(query: string): Promise<SymbolInfo[]> {
    return await this.gateway.searchSymbols(query);
  }

  // ===== RISK ENDPOINTS (Risk Integration) =====

  /**
   * Check order against risk limits
   */
  async checkRisk(order: RiskCheckRequest): Promise<RiskCheckResponse> {
    return await this.risk.checkOrder(order);
  }

  /**
   * Get risk limits
   */
  async getRiskLimits(account?: string): Promise<RiskLimits> {
    return await this.risk.getLimits(account);
  }

  /**
   * Get risk metrics
   */
  async getRiskMetrics(account?: string): Promise<RiskMetrics> {
    return await this.risk.getMetrics(account);
  }

  // ===== ACCOUNT ENDPOINTS (PTRC Integration) =====

  /**
   * Get account info
   * Uses PTRC P&L summary
   */
  async getAccount(): Promise<Account> {
    try {
      const pnlSummary = await this.ptrc.getPnLSummary();

      // Map PTRC data to Account type
      return {
        id: pnlSummary.account,
        name: `Account ${pnlSummary.account}`,
        balance: 100000, // TODO: Get from account service
        equity: 100000 + pnlSummary.total_pnl,
        buying_power: 50000, // TODO: Get from risk service
        currency: 'USD',
      } as Account;
    } catch (error) {
      console.error('[RealAPI] Failed to fetch account info:', error);
      // Return placeholder on error
      return {
        id: 'acc-001',
        name: 'Trade2026 Account',
        balance: 100000,
        equity: 100000,
        buying_power: 50000,
        currency: 'USD',
      } as Account;
    }
  }

  /**
   * Get portfolio metrics
   * Uses PTRC P&L summary and positions
   */
  async getPortfolioMetrics(): Promise<PortfolioMetrics> {
    try {
      const [pnlSummary, positions] = await Promise.all([
        this.ptrc.getPnLSummary(),
        this.ptrc.getPositions(),
      ]);

      return {
        total_value: 100000 + pnlSummary.total_pnl,
        total_pnl: pnlSummary.total_pnl,
        total_pnl_pct: (pnlSummary.total_pnl / 100000) * 100,
        positions_count: positions.length,
        unrealized_pnl: pnlSummary.total_unrealized_pnl,
        realized_pnl: pnlSummary.total_realized_pnl,
        daily_pnl: pnlSummary.daily_pnl,
      } as PortfolioMetrics;
    } catch (error) {
      console.error('[RealAPI] Failed to fetch portfolio metrics:', error);
      // Return placeholder on error
      return {
        total_value: 100000,
        total_pnl: 0,
        total_pnl_pct: 0,
        positions_count: 0,
      } as PortfolioMetrics;
    }
  }

  // ===== HEALTH CHECK ENDPOINTS =====

  /**
   * Check health of all backend services
   */
  async healthCheckAll(): Promise<{
    oms: { status: string };
    risk: { status: string };
    gateway: { status: string };
    liveGateway: { status: string };
    auth: { status: string };
    ptrc: { status: string };
  }> {
    const results = await Promise.allSettled([
      this.oms.healthCheck(),
      this.risk.healthCheck(),
      this.gateway.healthCheck(),
      this.liveGateway.healthCheck(),
      this.auth.healthCheck(),
      this.ptrc.healthCheck(),
    ]);

    return {
      oms: results[0].status === 'fulfilled' ? results[0].value : { status: 'error' },
      risk: results[1].status === 'fulfilled' ? results[1].value : { status: 'error' },
      gateway: results[2].status === 'fulfilled' ? results[2].value : { status: 'error' },
      liveGateway: results[3].status === 'fulfilled' ? results[3].value : { status: 'error' },
      auth: results[4].status === 'fulfilled' ? results[4].value : { status: 'error' },
      ptrc: results[5].status === 'fulfilled' ? results[5].value : { status: 'error' },
    };
  }

  // ===== LEGACY ENDPOINTS (Keep existing implementations) =====

  // Scanner endpoints
  async getScannerResults(): Promise<ScannerResult[]> {
    const response = await this.client.get<ScannerResult[]>('/scanner/results');
    return response.data;
  }

  // Strategy endpoints
  async getStrategies(): Promise<Strategy[]> {
    const response = await this.client.get<Strategy[]>('/strategies');
    return response.data;
  }

  async getStrategy(id: string): Promise<Strategy | null> {
    try {
      const response = await this.client.get<Strategy>(`/strategies/${id}`);
      return response.data;
    } catch {
      return null;
    }
  }

  async getStrategyTemplates(): Promise<StrategyTemplate[]> {
    const response = await this.client.get<StrategyTemplate[]>('/strategies/templates');
    return response.data;
  }

  async createStrategy(strategy: Omit<Strategy, 'id' | 'createdAt' | 'updatedAt'>): Promise<Strategy> {
    const response = await this.client.post<Strategy>('/strategies', strategy);
    return response.data;
  }

  async updateStrategy(id: string, updates: Partial<Strategy>): Promise<Strategy | null> {
    try {
      const response = await this.client.patch<Strategy>(`/strategies/${id}`, updates);
      return response.data;
    } catch {
      return null;
    }
  }

  async deleteStrategy(id: string): Promise<boolean> {
    try {
      await this.client.delete(`/strategies/${id}`);
      return true;
    } catch {
      return false;
    }
  }

  // Backtest endpoints
  async getBacktests(): Promise<Backtest[]> {
    const response = await this.client.get<Backtest[]>('/backtests');
    return response.data;
  }

  async getBacktest(id: string): Promise<Backtest | null> {
    try {
      const response = await this.client.get<Backtest>(`/backtests/${id}`);
      return response.data;
    } catch {
      return null;
    }
  }

  async createBacktest(backtest: Omit<Backtest, 'id' | 'createdAt'>): Promise<Backtest> {
    const response = await this.client.post<Backtest>('/backtests', backtest);
    return response.data;
  }

  // Position endpoints
  async getPositions(): Promise<Position[]> {
    const response = await this.client.get<Position[]>('/positions');
    return response.data;
  }

  async getPosition(id: string): Promise<Position | null> {
    try {
      const response = await this.client.get<Position>(`/positions/${id}`);
      return response.data;
    } catch {
      return null;
    }
  }

  // Account endpoints
  async getAccount(): Promise<Account> {
    const response = await this.client.get<Account>('/account');
    return response.data;
  }

  async getPortfolioMetrics(): Promise<PortfolioMetrics> {
    const response = await this.client.get<PortfolioMetrics>('/portfolio/metrics');
    return response.data;
  }

  // Database endpoints
  async getDatabaseTables(): Promise<DatabaseTable[]> {
    const response = await this.client.get<DatabaseTable[]>('/database/tables');
    return response.data;
  }

  async getDatabaseTable(name: string): Promise<DatabaseTable | null> {
    try {
      const response = await this.client.get<DatabaseTable>(`/database/tables/${name}`);
      return response.data;
    } catch {
      return null;
    }
  }

  async getTierMetrics(): Promise<TierMetrics[]> {
    const response = await this.client.get<TierMetrics[]>('/database/tiers/metrics');
    return response.data;
  }

  async queryDatabase(sql: string): Promise<unknown> {
    const response = await this.client.post('/database/query', { sql });
    return response.data;
  }
}

export default new RealAPI();
