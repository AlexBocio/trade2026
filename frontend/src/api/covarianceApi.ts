/**
 * Covariance Analysis API Service
 * Connects to backend on Port 5001
 */

const COV_API = 'http://localhost:5001/api/covariance';

export interface CleanParams {
  tickers: string[];
  start_date?: string;
  end_date?: string;
  detone?: boolean;
  detrend?: boolean;
  denoise_method?: 'marchenko_pastur' | 'constant_residual' | 'target_shrinkage';
  kde_bwidth?: number;
  alpha?: number;
}

export interface CleanResponse {
  original_cov: number[][];
  cleaned_cov: number[][];
  tickers: string[];
  eigenvalues_original: number[];
  eigenvalues_cleaned: number[];
  condition_number_original: number;
  condition_number_cleaned: number;
  detoning_applied: boolean;
  detrending_applied: boolean;
  denoising_applied: boolean;
}

export interface CompareParams {
  tickers: string[];
  start_date?: string;
  end_date?: string;
  initial_capital?: number;
}

export interface CompareResponse {
  original_weights: Record<string, number>;
  cleaned_weights: Record<string, number>;
  original_sharpe: number;
  cleaned_sharpe: number;
  original_volatility: number;
  cleaned_volatility: number;
  diversification_ratio_original: number;
  diversification_ratio_cleaned: number;
  tickers: string[];
}

export interface EigenvalueAnalysisResponse {
  eigenvalues: number[];
  variance_explained: number[];
  cumulative_variance: number[];
  marchenko_pastur_min: number;
  marchenko_pastur_max: number;
  n_components_above_threshold: number;
}

export const covarianceApi = {
  /**
   * Clean covariance matrix using detoning, detrending, RMT denoising
   */
  clean: async (params: CleanParams): Promise<CleanResponse> => {
    const response = await fetch(`${COV_API}/clean`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Clean failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Compare portfolio optimization with original vs cleaned covariance
   */
  compare: async (params: CompareParams): Promise<CompareResponse> => {
    const response = await fetch(`${COV_API}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Compare failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get eigenvalue spectrum analysis
   */
  eigenvalueAnalysis: async (params: CleanParams): Promise<EigenvalueAnalysisResponse> => {
    const response = await fetch(`${COV_API}/eigenvalue-analysis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Eigenvalue analysis failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await fetch(`${COV_API}/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return response.json();
  },
};
