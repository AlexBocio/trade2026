/**
 * Meta-Labeling API Service
 * Connects to backend on Port 5007
 */

const META_API = 'http://localhost:5007/api/meta-labeling';

export interface TrainParams {
  primary_strategy: string;
  features: string[];
  start_date?: string;
  end_date?: string;
  model_type?: 'random_forest' | 'xgboost' | 'lightgbm';
  n_estimators?: number;
  max_depth?: number;
  cv_folds?: number;
}

export interface TrainResponse {
  model_id: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  feature_importance: Record<string, number>;
  confusion_matrix: number[][];
  training_samples: number;
  test_samples: number;
  best_params: Record<string, any>;
}

export interface BacktestParams {
  model_id: string;
  primary_strategy: string;
  start_date?: string;
  end_date?: string;
  initial_capital?: number;
}

export interface BacktestResponse {
  primary_only: {
    total_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
    num_trades: number;
    avg_trade_return: number;
  };
  with_meta_labeling: {
    total_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
    num_trades: number;
    avg_trade_return: number;
  };
  improvement: {
    return_improvement: number;
    sharpe_improvement: number;
    drawdown_improvement: number;
    trades_filtered: number;
  };
  equity_curves: {
    dates: string[];
    primary_only: number[];
    with_meta_labeling: number[];
  };
}

export interface PredictParams {
  model_id: string;
  features: Record<string, number>;
}

export interface PredictResponse {
  signal: 'TRADE' | 'NO_TRADE';
  probability: number;
  confidence: number;
  features_used: string[];
  model_id: string;
}

export interface ModelInfo {
  model_id: string;
  created_at: string;
  primary_strategy: string;
  model_type: string;
  accuracy: number;
  f1_score: number;
  features: string[];
}

export const metaLabelingApi = {
  /**
   * Train a meta-labeling model
   */
  train: async (params: TrainParams): Promise<TrainResponse> => {
    const response = await fetch(`${META_API}/train`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Training failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Backtest primary strategy vs meta-labeling enhanced
   */
  backtest: async (params: BacktestParams): Promise<BacktestResponse> => {
    const response = await fetch(`${META_API}/backtest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Backtest failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get live prediction for current market conditions
   */
  predict: async (params: PredictParams): Promise<PredictResponse> => {
    const response = await fetch(`${META_API}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      throw new Error(`Prediction failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * List all trained models
   */
  listModels: async (): Promise<ModelInfo[]> => {
    const response = await fetch(`${META_API}/models`);
    if (!response.ok) {
      throw new Error('Failed to fetch models');
    }
    return response.json();
  },

  /**
   * Get model details
   */
  getModel: async (modelId: string): Promise<TrainResponse> => {
    const response = await fetch(`${META_API}/models/${modelId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch model details');
    }
    return response.json();
  },

  /**
   * Delete a model
   */
  deleteModel: async (modelId: string): Promise<void> => {
    const response = await fetch(`${META_API}/models/${modelId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete model');
    }
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await fetch(`${META_API}/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return response.json();
  },
};
