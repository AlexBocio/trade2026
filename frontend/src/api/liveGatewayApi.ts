/**
 * Live Gateway API Client
 * Connects to Live Order Gateway service on port 8200
 * Handles order routing to exchanges
 */

import axios, { AxiosInstance } from 'axios';

// Get Live Gateway URL from environment or use default
const LIVE_GATEWAY_URL = import.meta.env.VITE_LIVE_GATEWAY_URL || 'http://localhost:8200';

/**
 * Order routing request
 */
export interface RouteOrderRequest {
  order_id: string;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  order_type: 'market' | 'limit' | 'stop' | 'stop_limit';
  price?: number;
  stop_price?: number;
  time_in_force?: 'DAY' | 'GTC' | 'IOC' | 'FOK';
  exchange?: string;
}

/**
 * Order routing response
 */
export interface RouteOrderResponse {
  order_id: string;
  exchange_order_id?: string;
  status: 'routed' | 'pending' | 'failed';
  exchange?: string;
  message?: string;
  timestamp: string;
}

/**
 * Order status from exchange
 */
export interface ExchangeOrderStatus {
  order_id: string;
  exchange_order_id: string;
  status: 'pending' | 'open' | 'filled' | 'partially_filled' | 'cancelled' | 'rejected';
  filled_quantity: number;
  remaining_quantity: number;
  avg_fill_price?: number;
  last_update: string;
}

/**
 * Exchange connection status
 */
export interface ExchangeStatus {
  exchange: string;
  connected: boolean;
  last_heartbeat?: string;
  orders_pending: number;
  latency_ms?: number;
}

class LiveGatewayApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: LIVE_GATEWAY_URL,
      timeout: 15000, // Longer timeout for order routing
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
        console.log(`[Live Gateway API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('[Live Gateway API] Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[Live Gateway API] Response:`, response.status);
        return response;
      },
      (error) => {
        console.error('[Live Gateway API] Response error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Route order to exchange
   */
  async routeOrder(order: RouteOrderRequest): Promise<RouteOrderResponse> {
    try {
      const response = await this.client.post<RouteOrderResponse>('/route', order);
      return response.data;
    } catch (error) {
      console.error('[Live Gateway API] Order routing failed:', error);
      throw error;
    }
  }

  /**
   * Cancel order on exchange
   */
  async cancelOrder(orderId: string): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await this.client.delete(`/route/${orderId}`);
      return response.data;
    } catch (error) {
      console.error(`[Live Gateway API] Failed to cancel order ${orderId}:`, error);
      throw error;
    }
  }

  /**
   * Get order status from exchange
   */
  async getOrderStatus(orderId: string): Promise<ExchangeOrderStatus> {
    try {
      const response = await this.client.get<ExchangeOrderStatus>(`/status/${orderId}`);
      return response.data;
    } catch (error) {
      console.error(`[Live Gateway API] Failed to get status for order ${orderId}:`, error);
      throw error;
    }
  }

  /**
   * Get exchange connection statuses
   */
  async getExchangeStatuses(): Promise<ExchangeStatus[]> {
    try {
      const response = await this.client.get<ExchangeStatus[]>('/exchanges/status');
      return response.data;
    } catch (error) {
      console.error('[Live Gateway API] Failed to fetch exchange statuses:', error);
      throw error;
    }
  }

  /**
   * Get specific exchange status
   */
  async getExchangeStatus(exchange: string): Promise<ExchangeStatus> {
    try {
      const response = await this.client.get<ExchangeStatus>(`/exchanges/${exchange}/status`);
      return response.data;
    } catch (error) {
      console.error(`[Live Gateway API] Failed to get status for ${exchange}:`, error);
      throw error;
    }
  }

  /**
   * Subscribe to order updates via WebSocket
   */
  createOrderUpdatesWebSocket(
    orderId: string,
    onMessage: (status: ExchangeOrderStatus) => void
  ): WebSocket {
    const wsUrl = LIVE_GATEWAY_URL.replace('http', 'ws') + `/ws/orders/${orderId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log(`[Live Gateway WS] Connected to order updates for ${orderId}`);
    };

    ws.onmessage = (event) => {
      try {
        const status = JSON.parse(event.data);
        onMessage(status);
      } catch (error) {
        console.error('[Live Gateway WS] Failed to parse order update:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[Live Gateway WS] WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log(`[Live Gateway WS] Disconnected from order updates for ${orderId}`);
    };

    return ws;
  }

  /**
   * Subscribe to all order updates
   */
  createAllOrdersWebSocket(onMessage: (status: ExchangeOrderStatus) => void): WebSocket {
    const wsUrl = LIVE_GATEWAY_URL.replace('http', 'ws') + '/ws/orders';
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('[Live Gateway WS] Connected to all order updates');
    };

    ws.onmessage = (event) => {
      try {
        const status = JSON.parse(event.data);
        onMessage(status);
      } catch (error) {
        console.error('[Live Gateway WS] Failed to parse order update:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[Live Gateway WS] WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('[Live Gateway WS] Disconnected from all order updates');
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
      console.error('[Live Gateway API] Health check failed:', error);
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
      console.error('[Live Gateway API] Failed to fetch stats:', error);
      throw error;
    }
  }
}

// Export singleton instance
const liveGatewayApi = new LiveGatewayApiClient();
export default liveGatewayApi;
