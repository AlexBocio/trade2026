/**
 * Risk API Client
 * Connects to Risk Management service on port 8103
 */

import axios, { AxiosInstance } from 'axios';

// Get Risk URL from environment or use default
const RISK_URL = import.meta.env.VITE_RISK_URL || 'http://localhost:8103';

/**
 * Risk check request for order submission
 */
export interface RiskCheckRequest {
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  price?: number;
  account?: string;
  order_type?: string;
}

/**
 * Risk check response
 */
export interface RiskCheckResponse {
  approved: boolean;
  order_id?: string;
  rejection_reason?: string;
  risk_metrics?: {
    position_value?: number;
    portfolio_exposure?: number;
    buying_power_used?: number;
    margin_requirement?: number;
  };
  warnings?: string[];
}

/**
 * Risk limits for account
 */
export interface RiskLimits {
  account: string;
  max_order_size: number;
  max_position_size: number;
  max_portfolio_exposure: number;
  max_daily_loss: number;
  max_concentration: number;
  allowed_symbols?: string[];
  blocked_symbols?: string[];
}

/**
 * Current risk metrics
 */
export interface RiskMetrics {
  account: string;
  total_exposure: number;
  buying_power: number;
  buying_power_used: number;
  margin_used: number;
  current_positions: number;
  daily_pnl: number;
  breaches: RiskBreach[];
}

/**
 * Risk breach/violation
 */
export interface RiskBreach {
  breach_type: string;
  severity: 'warning' | 'error' | 'critical';
  description: string;
  timestamp: string;
  value?: number;
  limit?: number;
}

class RiskApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: RISK_URL,
      timeout: 5000, // Risk checks should be fast
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
        console.log(`[Risk API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('[Risk API] Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[Risk API] Response:`, response.status);
        return response;
      },
      (error) => {
        console.error('[Risk API] Response error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Perform risk check before order submission
   * This is the most critical risk function
   */
  async checkOrder(order: RiskCheckRequest): Promise<RiskCheckResponse> {
    try {
      const response = await this.client.post<RiskCheckResponse>('/check', order);
      return response.data;
    } catch (error) {
      console.error('[Risk API] Risk check failed:', error);
      throw error;
    }
  }

  /**
   * Get risk limits for an account
   */
  async getLimits(account?: string): Promise<RiskLimits> {
    try {
      const params = account ? { account } : {};
      const response = await this.client.get<RiskLimits>('/limits', { params });
      return response.data;
    } catch (error) {
      console.error('[Risk API] Failed to fetch limits:', error);
      throw error;
    }
  }

  /**
   * Update risk limits for an account
   */
  async updateLimits(account: string, limits: Partial<RiskLimits>): Promise<RiskLimits> {
    try {
      const response = await this.client.put<RiskLimits>(`/limits/${account}`, limits);
      return response.data;
    } catch (error) {
      console.error(`[Risk API] Failed to update limits for ${account}:`, error);
      throw error;
    }
  }

  /**
   * Get current risk metrics for an account
   */
  async getMetrics(account?: string): Promise<RiskMetrics> {
    try {
      const params = account ? { account } : {};
      const response = await this.client.get<RiskMetrics>('/metrics', { params });
      return response.data;
    } catch (error) {
      console.error('[Risk API] Failed to fetch metrics:', error);
      throw error;
    }
  }

  /**
   * Get risk breaches/violations
   */
  async getBreaches(account?: string): Promise<RiskBreach[]> {
    try {
      const params = account ? { account } : {};
      const response = await this.client.get<RiskBreach[]>('/breaches', { params });
      return response.data;
    } catch (error) {
      console.error('[Risk API] Failed to fetch breaches:', error);
      throw error;
    }
  }

  /**
   * Clear/acknowledge a breach
   */
  async clearBreach(breachId: string): Promise<{ success: boolean }> {
    try {
      const response = await this.client.delete(`/breaches/${breachId}`);
      return response.data;
    } catch (error) {
      console.error(`[Risk API] Failed to clear breach ${breachId}:`, error);
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
      console.error('[Risk API] Health check failed:', error);
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
      console.error('[Risk API] Failed to fetch stats:', error);
      throw error;
    }
  }
}

// Export singleton instance
const riskApi = new RiskApiClient();
export default riskApi;
