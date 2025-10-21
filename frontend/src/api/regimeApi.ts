/**
 * Regime Detection API Service
 * Connects to regime detection backend on Port 5008
 */

import type {
  RegimeDetectionResult,
  TemporalContext,
  MacroRegime,
  SectorRegimeData,
  IndustryRegimeData,
  MarketRegimes,
  FullHierarchy,
} from '../types/regime';

const REGIME_API_BASE = 'http://localhost:5008';

export const regimeApi = {
  /**
   * Detect current regime for a single symbol
   */
  getCurrentRegime: async (symbol: string, lookbackDays: number = 60): Promise<RegimeDetectionResult> => {
    const response = await fetch(`${REGIME_API_BASE}/api/regime/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol, lookback_days: lookbackDays }),
    });
    if (!response.ok) {
      throw new Error(`Regime detection failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get full regime hierarchy for a symbol
   */
  getFullHierarchy: async (symbol: string): Promise<FullHierarchy> => {
    const response = await fetch(`${REGIME_API_BASE}/api/regime/hierarchy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol }),
    });
    if (!response.ok) {
      throw new Error(`Hierarchy fetch failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get temporal context (calendar-based patterns)
   */
  getTemporalContext: async (): Promise<TemporalContext> => {
    const response = await fetch(`${REGIME_API_BASE}/api/regime/temporal`);
    if (!response.ok) {
      throw new Error(`Temporal context fetch failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get macro regime (Fed, inflation, economic cycle)
   */
  getMacroRegime: async (): Promise<MacroRegime> => {
    const response = await fetch(`${REGIME_API_BASE}/api/regime/macro`);
    if (!response.ok) {
      throw new Error(`Macro regime fetch failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get sector regimes (all 11 sectors)
   */
  getSectorRegimes: async (): Promise<SectorRegimeData> => {
    const response = await fetch(`${REGIME_API_BASE}/api/regime/sector-scan`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Sector scan failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get industry regimes (top N industries)
   */
  getIndustryRegimes: async (topN: number = 30): Promise<IndustryRegimeData> => {
    const response = await fetch(`${REGIME_API_BASE}/api/regime/industry-scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ top_n: topN }),
    });
    if (!response.ok) {
      throw new Error(`Industry scan failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Batch detect regimes for multiple symbols
   */
  batchDetect: async (symbols: string[], lookbackDays: number = 60): Promise<MarketRegimes> => {
    const response = await fetch(`${REGIME_API_BASE}/api/regime/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbols, lookback_days: lookbackDays }),
    });
    if (!response.ok) {
      throw new Error(`Batch detection failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string; version: string }> => {
    const response = await fetch(`${REGIME_API_BASE}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  },
};
