/**
 * PBO (Probability of Backtest Overfitting) API Service
 * Connects to backend on Port 5003
 */

const PBO_API = 'http://localhost:5003/api/backtest';

export interface PBOParams {
  ticker: string;
  strategy: string;
  param_grid: Record<string, number[]>;
  n_splits?: number;
  embargo_pct?: number;
  start_date?: string;
  end_date?: string;
}

export interface PBOResponse {
  pbo: number;
  pbo_percentage: number;
  interpretation: string;
  rank_correlation: number;
  n_trials: number;
  best_is_sharpe: number;
  best_is_oos_sharpe: number;
  median_oos_sharpe: number;
  rank_plot_data: {
    ranks_is: number[];
    ranks_oos: number[];
    best_is_idx: number;
  };
  parameter_combinations: Array<{
    params: Record<string, any>;
    is_sharpe: number;
    oos_sharpe: number;
  }>;
}

export interface DeflatedSharpeParams {
  observed_sharpe: number;
  n_trials: number;
  n_observations: number;
  skewness?: number;
  kurtosis?: number;
}

export interface DeflatedSharpeResponse {
  deflated_sharpe: number;
  p_value: number;
  interpretation: string;
  trials_effect: number;
}

export interface CombinatorialCVParams {
  ticker: string;
  strategy: string;
  params: Record<string, any>;
  n_splits?: number;
  embargo_pct?: number;
  start_date?: string;
  end_date?: string;
}

export interface CombinatorialCVResponse {
  mean_sharpe: number;
  std_sharpe: number;
  fold_results: Array<{
    fold_id: number;
    train_sharpe: number;
    test_sharpe: number;
    train_return: number;
    test_return: number;
  }>;
  consistency_score: number;
}

export interface StochasticDominanceParams {
  ticker: string;
  strategy_a: string;
  strategy_b: string;
  params_a: Record<string, any>;
  params_b: Record<string, any>;
  order?: number;
  start_date?: string;
  end_date?: string;
}

export interface StochasticDominanceResponse {
  dominates: boolean;
  dominant_strategy: string;
  order: number;
  test_statistic: number;
  p_value: number;
  interpretation: string;
}

export const pboApi = {
  /**
   * Calculate Probability of Backtest Overfitting
   */
  calculatePBO: async (params: PBOParams): Promise<PBOResponse> => {
    const response = await fetch(`${PBO_API}/pbo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`PBO calculation failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Calculate Deflated Sharpe Ratio
   */
  deflatedSharpe: async (params: DeflatedSharpeParams): Promise<DeflatedSharpeResponse> => {
    const response = await fetch(`${PBO_API}/deflated-sharpe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Deflated Sharpe calculation failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Run Combinatorial Purged Cross-Validation (CPCV)
   */
  combinatorialCV: async (params: CombinatorialCVParams): Promise<CombinatorialCVResponse> => {
    const response = await fetch(`${PBO_API}/combinatorial-cv`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`CPCV failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Test Stochastic Dominance between two strategies
   */
  stochasticDominance: async (params: StochasticDominanceParams): Promise<StochasticDominanceResponse> => {
    const response = await fetch(`${PBO_API}/stochastic-dominance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Stochastic dominance test failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Health check for PBO service
   */
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await fetch(`${PBO_API}/health`);
    if (!response.ok) {
      throw new Error('PBO service is not available');
    }
    return response.json();
  },
};
