/**
 * Regime Detection Types
 * TypeScript interfaces for regime detection system
 */

export type RegimeType =
  | 'BULL_TRENDING'
  | 'BEAR_TRENDING'
  | 'MOMENTUM'
  | 'MEAN_REVERTING'
  | 'HIGH_VOLATILITY'
  | 'LOW_VOLATILITY'
  | 'RANGE_BOUND'
  | 'CRISIS'
  | 'EXPANSION'
  | 'CONTRACTION'
  | 'NEUTRAL';

export interface RegimeDetectionResult {
  symbol: string;
  primary_regime: RegimeType;
  secondary_regime?: RegimeType;
  regime_strength: number;
  confidence: number;
  characteristics: {
    trend_strength: number;
    volatility: number;
    momentum: number;
    rsi: number;
    volume_profile: string;
  };
  timestamp: string;
}

export interface TemporalContext {
  month_name: string;
  month_number: number;
  day_of_month: number;
  day_of_week: string;
  seasonal_regime: RegimeType;
  day_regime: RegimeType;
  is_earnings_season: boolean;
  is_opex_week: boolean;
  is_fed_week: boolean;
  days_to_next_fed: number;
  days_to_next_cpi: number;
  historical_month_performance: {
    SPY_avg_return: number;
    volatility_percentile: number;
  };
}

export interface MacroRegime {
  overall_macro: RegimeType;
  confidence: number;
  fed_policy_regime: RegimeType;
  economic_cycle: RegimeType;
  inflation_regime: RegimeType;
  geopolitical_regime: RegimeType;
  metrics: {
    fed_funds_rate: number;
    gdp_growth: number;
    cpi_yoy: number;
    unemployment: number;
    yield_curve_2s10s: number;
  };
}

export interface SectorRegimeData {
  sectors: Record<string, {
    symbol: string;
    name: string;
    regime: RegimeType;
    strength: number;
    vs_spy_return_20d: number;
    vs_spy_return_60d: number;
  }>;
  strongest_sectors: string[];
  weakest_sectors: string[];
  divergence_score: number;
}

export interface IndustryRegimeData {
  industries: Array<{
    symbol: string;
    name: string;
    sector: string;
    regime: RegimeType;
    strength: number;
    vs_sector_return: number;
    momentum_score: number;
  }>;
  top_industries: string[];
  bottom_industries: string[];
}

export interface MarketRegimes {
  [symbol: string]: RegimeDetectionResult;
}

export interface FullHierarchy {
  symbol: string;
  temporal: TemporalContext;
  macro: MacroRegime;
  market: RegimeDetectionResult;
  sector: {
    regime: RegimeType;
    strength: number;
  };
  industry: {
    regime: RegimeType;
    strength: number;
  };
  stock: RegimeDetectionResult;
  alignment_score: number;
  divergence_points: string[];
}
