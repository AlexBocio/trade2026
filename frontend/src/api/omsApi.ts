/**
 * OMS (Order Management System) API Client
 * Connects to OMS service on port 8099
 */

import axios, { AxiosInstance } from 'axios';

// Get OMS URL from environment or use default
const OMS_URL = import.meta.env.VITE_OMS_URL || 'http://localhost:8099';

/**
 * Order submission request
 */
export interface OrderRequest {
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  order_type: 'market' | 'limit' | 'stop' | 'stop_limit';
  price?: number;
  stop_price?: number;
  time_in_force?: 'DAY' | 'GTC' | 'IOC' | 'FOK';
  account?: string;
}

/**
 * Order response from OMS
 */
export interface OrderResponse {
  order_id: string;
  symbol: string;
  side: string;
  quantity: number;
  order_type: string;
  status: string;
  price?: number;
  stop_price?: number;
  created_at: string;
  updated_at?: string;
}

/**
 * Position from OMS
 */
export interface PositionResponse {
  symbol: string;
  quantity: number;
  avg_price: number;
  current_price?: number;
  unrealized_pnl?: number;
  realized_pnl?: number;
  side: 'long' | 'short';
  account: string;
}

/**
 * Fill/Execution from OMS
 */
export interface FillResponse {
  fill_id: string;
  order_id: string;
  symbol: string;
  side: string;
  quantity: number;
  price: number;
  filled_at: string;
  commission?: number;
}

class OMSApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: OMS_URL,
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
        console.log(`[OMS API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('[OMS API] Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[OMS API] Response:`, response.status);
        return response;
      },
      (error) => {
        console.error('[OMS API] Response error:', error.response?.data || error.message);
        if (error.response?.status === 401) {
          // Handle unauthorized
          console.error('[OMS API] Unauthorized - token may be invalid');
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Submit a new order
   */
  async submitOrder(order: OrderRequest): Promise<OrderResponse> {
    try {
      const response = await this.client.post<OrderResponse>('/orders', order);
      return response.data;
    } catch (error) {
      console.error('[OMS API] Order submission failed:', error);
      throw error;
    }
  }

  /**
   * Get all orders
   */
  async getOrders(account?: string): Promise<OrderResponse[]> {
    try {
      const params = account ? { account } : {};
      const response = await this.client.get<OrderResponse[]>('/orders', { params });
      return response.data;
    } catch (error) {
      console.error('[OMS API] Failed to fetch orders:', error);
      throw error;
    }
  }

  /**
   * Get a specific order by ID
   */
  async getOrder(orderId: string): Promise<OrderResponse> {
    try {
      const response = await this.client.get<OrderResponse>(`/orders/${orderId}`);
      return response.data;
    } catch (error) {
      console.error(`[OMS API] Failed to fetch order ${orderId}:`, error);
      throw error;
    }
  }

  /**
   * Cancel an order
   */
  async cancelOrder(orderId: string): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await this.client.delete(`/orders/${orderId}`);
      return response.data;
    } catch (error) {
      console.error(`[OMS API] Failed to cancel order ${orderId}:`, error);
      throw error;
    }
  }

  /**
   * Get all positions
   */
  async getPositions(account?: string): Promise<PositionResponse[]> {
    try {
      const params = account ? { account } : {};
      const response = await this.client.get<PositionResponse[]>('/positions', { params });
      return response.data;
    } catch (error) {
      console.error('[OMS API] Failed to fetch positions:', error);
      throw error;
    }
  }

  /**
   * Get a specific position for a symbol
   */
  async getPosition(symbol: string, account?: string): Promise<PositionResponse | null> {
    try {
      const params = account ? { account } : {};
      const response = await this.client.get<PositionResponse>(`/positions/${symbol}`, { params });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null; // No position for this symbol
      }
      console.error(`[OMS API] Failed to fetch position for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Get all fills/executions
   */
  async getFills(account?: string): Promise<FillResponse[]> {
    try {
      const params = account ? { account } : {};
      const response = await this.client.get<FillResponse[]>('/fills', { params });
      return response.data;
    } catch (error) {
      console.error('[OMS API] Failed to fetch fills:', error);
      throw error;
    }
  }

  /**
   * Get fills for a specific order
   */
  async getOrderFills(orderId: string): Promise<FillResponse[]> {
    try {
      const response = await this.client.get<FillResponse[]>(`/orders/${orderId}/fills`);
      return response.data;
    } catch (error) {
      console.error(`[OMS API] Failed to fetch fills for order ${orderId}:`, error);
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
      console.error('[OMS API] Health check failed:', error);
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
      console.error('[OMS API] Failed to fetch stats:', error);
      throw error;
    }
  }
}

// Export singleton instance
const omsApi = new OMSApiClient();
export default omsApi;
