/**
 * Portfolio Optimization API Service
 * Connects to backend on Port 5001
 */

const PORTFOLIO_API = 'http://localhost:5001/api/portfolio';

export interface OptimizeParams {
  tickers: string[];
  start_date?: string;
  end_date?: string;
  use_cleaned_cov?: boolean;
}

export interface OptimizeResponse {
  weights: Record<string, number>;
  expected_return: number;
  volatility: number;
  sharpe_ratio: number;
  method: string;
}

export interface HERCParams {
  tickers: string[];
  start_date?: string;
  end_date?: string;
  risk_measure?: 'volatility' | 'cvar';
  linkage_method?: string;
}

export interface HERCResponse {
  weights: Record<string, number>;
  risk_contributions: Record<string, number>;
  portfolio_metrics: {
    volatility: number;
    cvar: number | null;
    diversification_ratio: number;
  };
  clusters: Record<string, string[]>;
  dendrogram: number[][];
}

export interface HERCvsHRPParams {
  tickers: string[];
  start_date?: string;
  end_date?: string;
}

export interface HERCvsHRPResponse {
  herc: {
    weights: Record<string, number>;
    risk_contributions: Record<string, number>;
  };
  hrp: {
    weights: Record<string, number>;
    risk_contributions: Record<string, number>;
  };
  comparison: {
    herc_vol: number;
    hrp_vol: number;
    herc_cvar: number;
    hrp_cvar: number;
    rc_concentration_herc: number;
    rc_concentration_hrp: number;
    recommendation: string;
    tail_risk_winner: string;
  };
  tickers: string[];
}

export interface RiskContributionParams {
  tickers: string[];
  weights: Record<string, number>;
  start_date?: string;
  end_date?: string;
}

export interface RiskContributionResponse {
  risk_contributions: Record<string, number>;
  total_risk: number;
}

export const portfolioApi = {
  /**
   * Mean-Variance Optimization
   */
  meanVariance: async (params: OptimizeParams): Promise<OptimizeResponse> => {
    const response = await fetch(`${PORTFOLIO_API}/optimize/mean-variance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Mean-variance optimization failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Risk Parity Optimization
   */
  riskParity: async (params: OptimizeParams): Promise<OptimizeResponse> => {
    const response = await fetch(`${PORTFOLIO_API}/optimize/risk-parity`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Risk parity optimization failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Hierarchical Risk Parity (HRP)
   */
  hrp: async (params: OptimizeParams): Promise<OptimizeResponse> => {
    const response = await fetch(`${PORTFOLIO_API}/optimize/hrp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`HRP optimization failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Hierarchical Equal Risk Contribution (HERC)
   */
  herc: async (params: HERCParams): Promise<HERCResponse> => {
    const response = await fetch(`${PORTFOLIO_API}/herc`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`HERC optimization failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * HERC vs HRP Comparison
   */
  hercVsHrp: async (params: HERCvsHRPParams): Promise<HERCvsHRPResponse> => {
    const response = await fetch(`${PORTFOLIO_API}/herc-vs-hrp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`HERC vs HRP comparison failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Calculate Risk Contribution
   */
  riskContribution: async (params: RiskContributionParams): Promise<RiskContributionResponse> => {
    const response = await fetch(`${PORTFOLIO_API}/risk-contribution`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Risk contribution calculation failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get Efficient Frontier
   */
  efficientFrontier: async (params: { tickers: string[]; n_points?: number }): Promise<any> => {
    const response = await fetch(`${PORTFOLIO_API}/optimize/efficient-frontier`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Efficient frontier calculation failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await fetch(`${PORTFOLIO_API}/health`);
    if (!response.ok) {
      throw new Error('Portfolio service is not available');
    }
    return response.json();
  },
};
