/**
 * PTRC (Position Tracker) API Client
 * Connects to PTRC service on port 8109
 * Handles P&L calculations, position tracking, and reports
 */

import axios, { AxiosInstance } from 'axios';

// Get PTRC URL from environment or use default
const PTRC_URL = import.meta.env.VITE_PTRC_URL || 'http://localhost:8109';

/**
 * Position with P&L data
 */
export interface PTRCPosition {
  symbol: string;
  quantity: number;
  avg_entry_price: number;
  current_price?: number;
  unrealized_pnl: number;
  realized_pnl: number;
  total_pnl: number;
  pnl_percentage: number;
  side: 'long' | 'short';
  entry_date: string;
  last_updated: string;
  account: string;
}

/**
 * P&L Summary
 */
export interface PnLSummary {
  account: string;
  total_unrealized_pnl: number;
  total_realized_pnl: number;
  total_pnl: number;
  daily_pnl: number;
  weekly_pnl: number;
  monthly_pnl: number;
  ytd_pnl: number;
  timestamp: string;
}

/**
 * Trade/Fill with P&L
 */
export interface PTRCTrade {
  trade_id: string;
  order_id: string;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  price: number;
  commission: number;
  pnl?: number;
  timestamp: string;
  account: string;
}

/**
 * Report request
 */
export interface ReportRequest {
  report_type: 'daily' | 'weekly' | 'monthly' | 'ytd' | 'custom';
  start_date?: string;
  end_date?: string;
  account?: string;
  symbols?: string[];
}

/**
 * Report response
 */
export interface ReportResponse {
  report_type: string;
  start_date: string;
  end_date: string;
  account: string;
  summary: {
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    total_pnl: number;
    win_rate: number;
    avg_win: number;
    avg_loss: number;
    largest_win: number;
    largest_loss: number;
    sharpe_ratio?: number;
  };
  positions: PTRCPosition[];
  trades: PTRCTrade[];
  generated_at: string;
}

/**
 * Position history
 */
export interface PositionHistory {
  symbol: string;
  snapshots: {
    timestamp: string;
    quantity: number;
    avg_price: number;
    current_price: number;
    unrealized_pnl: number;
    realized_pnl: number;
  }[];
}

class PTRCApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: PTRC_URL,
      timeout: 15000, // Longer timeout for reports
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
        console.log(`[PTRC API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('[PTRC API] Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[PTRC API] Response:`, response.status);
        return response;
      },
      (error) => {
        console.error('[PTRC API] Response error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get all positions with P&L
   */
  async getPositions(account?: string): Promise<PTRCPosition[]> {
    try {
      const params = account ? { account } : {};
      const response = await this.client.get<PTRCPosition[]>('/positions', { params });
      return response.data;
    } catch (error) {
      console.error('[PTRC API] Failed to fetch positions:', error);
      throw error;
    }
  }

  /**
   * Get specific position with P&L
   */
  async getPosition(symbol: string, account?: string): Promise<PTRCPosition | null> {
    try {
      const params = account ? { account } : {};
      const response = await this.client.get<PTRCPosition>(`/positions/${symbol}`, { params });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      console.error(`[PTRC API] Failed to fetch position for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Get P&L summary
   */
  async getPnLSummary(account?: string): Promise<PnLSummary> {
    try {
      const params = account ? { account } : {};
      const response = await this.client.get<PnLSummary>('/pnl/summary', { params });
      return response.data;
    } catch (error) {
      console.error('[PTRC API] Failed to fetch P&L summary:', error);
      throw error;
    }
  }

  /**
   * Get trades/fills with P&L
   */
  async getTrades(account?: string, symbol?: string, limit?: number): Promise<PTRCTrade[]> {
    try {
      const params: any = {};
      if (account) params.account = account;
      if (symbol) params.symbol = symbol;
      if (limit) params.limit = limit;

      const response = await this.client.get<PTRCTrade[]>('/trades', { params });
      return response.data;
    } catch (error) {
      console.error('[PTRC API] Failed to fetch trades:', error);
      throw error;
    }
  }

  /**
   * Generate report
   */
  async generateReport(request: ReportRequest): Promise<ReportResponse> {
    try {
      const response = await this.client.post<ReportResponse>('/reports/generate', request);
      return response.data;
    } catch (error) {
      console.error('[PTRC API] Failed to generate report:', error);
      throw error;
    }
  }

  /**
   * Get daily P&L report
   */
  async getDailyReport(account?: string): Promise<ReportResponse> {
    const today = new Date().toISOString().split('T')[0];
    return await this.generateReport({
      report_type: 'daily',
      start_date: today,
      end_date: today,
      account,
    });
  }

  /**
   * Get weekly P&L report
   */
  async getWeeklyReport(account?: string): Promise<ReportResponse> {
    const today = new Date();
    const weekAgo = new Date(today);
    weekAgo.setDate(weekAgo.getDate() - 7);

    return await this.generateReport({
      report_type: 'weekly',
      start_date: weekAgo.toISOString().split('T')[0],
      end_date: today.toISOString().split('T')[0],
      account,
    });
  }

  /**
   * Get monthly P&L report
   */
  async getMonthlyReport(account?: string): Promise<ReportResponse> {
    const today = new Date();
    const monthAgo = new Date(today);
    monthAgo.setMonth(monthAgo.getMonth() - 1);

    return await this.generateReport({
      report_type: 'monthly',
      start_date: monthAgo.toISOString().split('T')[0],
      end_date: today.toISOString().split('T')[0],
      account,
    });
  }

  /**
   * Get position history (time series)
   */
  async getPositionHistory(symbol: string, account?: string): Promise<PositionHistory> {
    try {
      const params = account ? { account } : {};
      const response = await this.client.get<PositionHistory>(`/positions/${symbol}/history`, {
        params,
      });
      return response.data;
    } catch (error) {
      console.error(`[PTRC API] Failed to fetch position history for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Get P&L chart data
   */
  async getPnLChart(
    period: 'day' | 'week' | 'month' | 'ytd' = 'week',
    account?: string
  ): Promise<{ timestamp: string; pnl: number; cumulative_pnl: number }[]> {
    try {
      const params: any = { period };
      if (account) params.account = account;

      const response = await this.client.get('/pnl/chart', { params });
      return response.data;
    } catch (error) {
      console.error('[PTRC API] Failed to fetch P&L chart data:', error);
      throw error;
    }
  }

  /**
   * Recalculate P&L for all positions
   */
  async recalculatePnL(account?: string): Promise<{ success: boolean; message: string }> {
    try {
      const params = account ? { account } : {};
      const response = await this.client.post('/pnl/recalculate', {}, { params });
      return response.data;
    } catch (error) {
      console.error('[PTRC API] Failed to recalculate P&L:', error);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      console.error('[PTRC API] Health check failed:', error);
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
      console.error('[PTRC API] Failed to fetch stats:', error);
      throw error;
    }
  }
}

// Export singleton instance
const ptrcApi = new PTRCApiClient();
export default ptrcApi;
