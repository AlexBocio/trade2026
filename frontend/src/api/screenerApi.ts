/**
 * Stock Screener API Service
 * Connects to backend on Port 5008
 */

const SCREENER_API = 'http://localhost:5008/api/screener';

export interface ScreenerParams {
  universe: 'sp500' | 'small_caps' | 'mid_caps' | 'micro_caps' | 'nasdaq100' | 'all';
  timeframe: 'intraday' | 'swing' | 'position';
  top_n?: number;
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
  scan_timestamp: string;
}

export interface CustomScreenParams {
  universe: string;
  timeframe: string;
  filters: {
    min_market_cap?: number;
    max_market_cap?: number;
    min_volume?: number;
    sectors?: string[];
    factor_weights?: Record<string, number>;
  };
}

export interface FactorAnalysisParams {
  ticker: string;
}

export interface FactorAnalysisResponse {
  ticker: string;
  factor_breakdown: {
    momentum: {
      score: number;
      components: {
        rsi: number;
        macd: number;
        price_vs_ma: number;
      };
    };
    value: {
      score: number;
      components: {
        pe_ratio: number;
        pb_ratio: number;
        ev_ebitda: number;
      };
    };
    quality: {
      score: number;
      components: {
        roa: number;
        roe: number;
        debt_to_equity: number;
      };
    };
    growth: {
      score: number;
      components: {
        revenue_growth: number;
        earnings_growth: number;
        analyst_upgrades: number;
      };
    };
  };
}

// Prediction Heatmap Interfaces
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
  timeframes: string[];
  matrix: number[][];
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

export const screenerApi = {
  /**
   * Run stock screener scan
   */
  scan: async (params: ScreenerParams): Promise<ScreenerResponse> => {
    const response = await fetch(`${SCREENER_API}/scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Screener scan failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Run custom screen with advanced filters
   */
  customScan: async (params: CustomScreenParams): Promise<ScreenerResponse> => {
    const response = await fetch(`${SCREENER_API}/custom-scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Custom scan failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get detailed factor analysis for a stock
   */
  getFactorAnalysis: async (params: FactorAnalysisParams): Promise<FactorAnalysisResponse> => {
    const response = await fetch(`${SCREENER_API}/factor-analysis/${params.ticker}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      throw new Error(`Factor analysis failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await fetch(`${SCREENER_API}/health`);
    if (!response.ok) {
      throw new Error('Screener service is not available');
    }
    return response.json();
  },

  /**
   * Scan stocks and generate multi-timeframe prediction heatmap
   */
  scanAndPredict: async (params: ScanAndPredictParams): Promise<ScanAndPredictResponse> => {
    const response = await fetch(`${SCREENER_API}/scan-and-predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Scan and predict failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Generate prediction heatmap for specific tickers
   */
  generateHeatmap: async (tickers: string[]): Promise<HeatmapData> => {
    const response = await fetch(`${SCREENER_API}/generate-heatmap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tickers }),
    });
    if (!response.ok) {
      throw new Error(`Generate heatmap failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get saved presets
   */
  getPresets: async (): Promise<{ presets: any[] }> => {
    const response = await fetch(`${SCREENER_API}/presets`);
    if (!response.ok) {
      throw new Error('Failed to fetch presets');
    }
    return response.json();
  },

  /**
   * Save a new preset
   */
  savePreset: async (params: { name: string; description: string; config: any }): Promise<{ preset_id: string }> => {
    const response = await fetch(`${SCREENER_API}/presets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error('Failed to save preset');
    }
    return response.json();
  },

  /**
   * Run a saved preset
   */
  runPreset: async (presetId: string): Promise<ScanAndPredictResponse> => {
    const response = await fetch(`${SCREENER_API}/presets/${presetId}/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) {
      throw new Error('Failed to run preset');
    }
    return response.json();
  },

  /**
   * Export heatmap in various formats
   */
  exportHeatmap: async (format: 'png' | 'csv' | 'html' | 'json', params: any): Promise<Blob> => {
    const response = await fetch(`${SCREENER_API}/export/${format}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`);
    }
    return response.blob();
  },

  /**
   * Subscribe to real-time updates
   */
  subscribeToUpdates: async (params: { scan_config: any; update_interval_seconds: number }): Promise<{ scan_id: string }> => {
    const response = await fetch(`${SCREENER_API}/subscribe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error('Failed to subscribe to updates');
    }
    return response.json();
  },
};
