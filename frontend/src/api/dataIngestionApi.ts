/**
 * Data Ingestion API Client
 * Connects to the data-ingestion service for IBKR market data and FRED economic indicators
 */

import axios, { type AxiosInstance } from 'axios';

// ===== TYPES =====

export interface IBKRTicker {
  symbol: string;
  bid: number;
  ask: number;
  last: number;
  volume: number;
  high: number;
  low: number;
  close: number;
  timestamp: string;
}

export interface FREDIndicator {
  series_id: string;
  title: string;
  value: number;
  units: string;
  date: string;
  timestamp: string;
  updated_at: number;
}

export interface DataIngestionStatus {
  service: string;
  version: string;
  running: boolean;
  adapters: {
    ibkr: {
      connected: boolean;
      ibkr_connected: boolean;
      subscriptions: number;
      reconnect_attempts: number;
      valkey_connected: boolean;
      questdb_connected: boolean;
    };
    fred: {
      running: boolean;
      series_count: number;
      metadata_cached: number;
      valkey_connected: boolean;
      questdb_connected: boolean;
      update_interval_minutes: number;
    };
  };
}

// ===== API CLIENT =====

class DataIngestionAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: 'http://localhost:8500',
      timeout: 5000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Get service health status
   */
  async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  /**
   * Get detailed service status
   */
  async getStatus(): Promise<DataIngestionStatus> {
    const response = await this.client.get<DataIngestionStatus>('/status');
    return response.data;
  }

  /**
   * Get all IBKR market data from Valkey cache
   * Fetches real-time market data for all subscribed symbols
   */
  async getIBKRMarketData(): Promise<IBKRTicker[]> {
    try {
      const response = await this.client.get<IBKRTicker[]>('/api/market-data');
      return response.data;
    } catch (error) {
      console.error('[DataIngestionAPI] Failed to fetch IBKR market data:', error);
      return [];
    }
  }

  /**
   * Get all FRED economic indicators from Valkey cache
   * Fetches latest economic indicator values
   */
  async getFREDIndicators(): Promise<FREDIndicator[]> {
    try {
      const response = await this.client.get<FREDIndicator[]>('/api/economic-indicators');
      return response.data;
    } catch (error) {
      console.error('[DataIngestionAPI] Failed to fetch FRED indicators:', error);
      return [];
    }
  }
}

export default new DataIngestionAPI();
