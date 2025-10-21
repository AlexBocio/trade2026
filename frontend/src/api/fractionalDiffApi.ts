/**
 * Fractional Differentiation API
 * Service for time series stationarity transformation
 */

const FRACDIFF_API = 'http://localhost:5006/api/fracdiff';

export interface TransformParams {
  ticker: string;
  d: number;
  start_date?: string;
  end_date?: string;
  method?: 'ffd' | 'standard';
}

export interface OptimalDParams {
  ticker: string;
  d_min?: number;
  d_max?: number;
  step?: number;
  start_date?: string;
}

export interface CompareParams {
  ticker: string;
  d_values: number[];
  start_date?: string;
}

export interface BatchParams {
  tickers: string[];
  d: number;
  start_date?: string;
}

export const fractionalDiffApi = {
  /**
   * Transform a time series with fractional differentiation
   */
  transform: async (params: TransformParams) => {
    const response = await fetch(`${FRACDIFF_API}/transform`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Transform failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Find optimal d value that achieves stationarity
   */
  findOptimalD: async (params: OptimalDParams) => {
    const response = await fetch(`${FRACDIFF_API}/find-optimal-d`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Optimal d search failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Compare multiple d values
   */
  compare: async (params: CompareParams) => {
    const response = await fetch(`${FRACDIFF_API}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Comparison failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Batch transform multiple tickers
   */
  batchTransform: async (params: BatchParams) => {
    const response = await fetch(`${FRACDIFF_API}/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Batch transform failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Health check
   */
  healthCheck: async () => {
    try {
      const response = await fetch(`${FRACDIFF_API}/health`);
      return response.ok;
    } catch {
      return false;
    }
  },
};
