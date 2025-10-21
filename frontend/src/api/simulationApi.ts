/**
 * Simulation API Service - Handles all simulation-related API calls
 * Backend: http://localhost:5005/api/simulation
 */

const SIMULATION_API = 'http://localhost:5005/api/simulation';

export interface BootstrapParams {
  ticker: string;
  method: 'standard' | 'block' | 'circular' | 'stationary' | 'wild';
  n_simulations: number;
  block_size?: number;
  start_date: string;
  end_date: string;
}

export interface MonteCarloParams {
  ticker: string;
  method: 'garch' | 'copula' | 'jump-diffusion' | 'regime-switching';
  n_simulations: number;
  horizon: number;
}

export interface WalkForwardParams {
  ticker: string;
  strategy_type: 'momentum' | 'mean-reversion' | 'custom';
  methods: ('anchored' | 'rolling' | 'expanding')[];
  train_size: number;
  test_size: number;
  step: number;
}

export interface ScenarioParams {
  portfolio: { ticker: string; weight: number }[];
  scenarios: ('2008' | '2020' | 'dotcom' | '1987' | 'custom')[];
  custom_shocks?: Record<string, number>;
}

export interface SyntheticParams {
  ticker: string;
  method: 'gan' | 'vae';
  n_samples: number;
  validation_tests: boolean;
}

export const simulationApi = {
  /**
   * Bootstrap Resampling Simulation
   */
  runBootstrap: async (params: BootstrapParams) => {
    const response = await fetch(`${SIMULATION_API}/bootstrap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`Bootstrap simulation failed: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Advanced Monte Carlo Simulation
   */
  runMonteCarlo: async (params: MonteCarloParams) => {
    const response = await fetch(`${SIMULATION_API}/monte-carlo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`Monte Carlo simulation failed: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Walk-Forward Method Comparison
   */
  compareWalkForward: async (params: WalkForwardParams) => {
    const response = await fetch(`${SIMULATION_API}/walk-forward/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`Walk-forward comparison failed: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Scenario Analysis (Stress Testing)
   */
  runScenario: async (params: ScenarioParams) => {
    const response = await fetch(`${SIMULATION_API}/scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`Scenario analysis failed: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Synthetic Data Generation
   */
  generateSynthetic: async (params: SyntheticParams) => {
    const response = await fetch(`${SIMULATION_API}/synthetic`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`Synthetic data generation failed: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Health check for simulation service
   */
  healthCheck: async () => {
    try {
      const response = await fetch(`${SIMULATION_API}/health`);
      return response.ok;
    } catch {
      return false;
    }
  },
};
