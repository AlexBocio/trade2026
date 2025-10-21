/**
 * Scanner Configuration Types
 * Type definitions for the Custom Scanner Builder
 */

export type ScanningMode = 'ALIGNMENT' | 'DIVERGENCE' | 'HYBRID' | 'TRANSITION';

export interface RegimeLayer {
  enabled: boolean;
  weight: number;
  criteria: Record<string, any>;
}

export interface RegimeLayers {
  temporal: RegimeLayer & {
    criteria: {
      month_seasonality: boolean;
      day_of_week: boolean;
      earnings_season: boolean;
      fomc_week: boolean;
      opex_week: boolean;
    };
  };
  macro: RegimeLayer & {
    criteria: {
      fed_policy: boolean;
      inflation: boolean;
      economic_cycle: boolean;
      yield_curve: boolean;
    };
  };
  cross_asset: RegimeLayer & {
    assets: string[];
    criteria: {
      bonds: boolean;
      commodities: boolean;
      currencies: boolean;
      volatility: boolean;
    };
  };
  market: RegimeLayer & {
    criteria: {
      breadth: boolean;
      vix_regime: boolean;
      advance_decline: boolean;
      new_highs_lows: boolean;
    };
  };
  sector: RegimeLayer & {
    criteria: {
      rotation: boolean;
      leadership: boolean;
      correlation: boolean;
    };
  };
  industry: RegimeLayer & {
    criteria: {
      relative_strength: boolean;
      momentum: boolean;
    };
  };
  stock_specific: RegimeLayer & {
    criteria: {
      earnings: boolean;
      analyst_ratings: boolean;
      insider_activity: boolean;
      short_interest: boolean;
    };
  };
}

export interface CriteriaRange {
  enabled: boolean;
  min: number;
  max: number;
}

export interface TechnicalCriteria {
  momentum: {
    return_20d: CriteriaRange;
    return_60d: CriteriaRange;
    return_252d: CriteriaRange;
    hurst: CriteriaRange;
    autocorr: CriteriaRange;
  };
  mean_reversion: {
    zscore: CriteriaRange;
    rsi: CriteriaRange;
    bollinger_position: CriteriaRange;
    mean_reversion_speed: CriteriaRange;
  };
  volatility: {
    atr_percentile: CriteriaRange;
    volume_surge: CriteriaRange;
    garch_vol: CriteriaRange;
    implied_vol: CriteriaRange;
  };
  trend: {
    price_vs_sma50: CriteriaRange;
    price_vs_sma200: CriteriaRange;
    sma_slope: CriteriaRange;
    adx: CriteriaRange;
  };
  liquidity: {
    avg_volume: CriteriaRange;
    dollar_volume: CriteriaRange;
    spread: CriteriaRange;
    float: CriteriaRange;
  };
}

export interface Filters {
  sectors: {
    exclude: string[];
  };
  symbols: {
    blacklist: string[];
  };
  market_cap: {
    min: number;
    max: number;
  };
  price: {
    min: number;
    max: number;
  };
  composite_score: {
    min: number;
  };
}

export interface Ranking {
  primary_sort: string;
  secondary_sort: string;
  sort_order: 'asc' | 'desc';
}

export interface OutputOptions {
  max_results: number;
  include_regime_scores: boolean;
  include_factor_breakdown: boolean;
  export_format: 'json' | 'csv' | 'excel';
}

export interface ScannerConfig {
  name: string;
  universe: string;
  mode: ScanningMode;
  regime_layers: RegimeLayers;
  technical_criteria: TechnicalCriteria;
  filters: Filters;
  ranking: Ranking;
  output: OutputOptions;
}

export interface ScanResult {
  ticker: string;
  company_name: string;
  sector: string;
  industry: string;
  price: number;
  market_cap: number;
  composite_score: number;
  regime_scores: Record<string, number>;
  factor_scores: Record<string, number>;
  signals: {
    technical: 'bullish' | 'bearish' | 'neutral';
    regime_alignment: number;
  };
}

export interface ScanResponse {
  results: ScanResult[];
  metadata: {
    scan_timestamp: string;
    results_count: number;
    universe_size: number;
    config_name: string;
  };
}

// Default configuration
export const defaultScannerConfig: ScannerConfig = {
  name: 'Untitled Scan',
  universe: 'sp500',
  mode: 'ALIGNMENT',
  regime_layers: {
    temporal: {
      enabled: true,
      weight: 0.15,
      criteria: {
        month_seasonality: true,
        day_of_week: true,
        earnings_season: true,
        fomc_week: true,
        opex_week: true,
      },
    },
    macro: {
      enabled: true,
      weight: 0.20,
      criteria: {
        fed_policy: true,
        inflation: true,
        economic_cycle: true,
        yield_curve: true,
      },
    },
    cross_asset: {
      enabled: true,
      weight: 0.15,
      assets: ['TLT', 'GLD', 'DXY', 'VIX'],
      criteria: {
        bonds: true,
        commodities: true,
        currencies: true,
        volatility: true,
      },
    },
    market: {
      enabled: true,
      weight: 0.20,
      criteria: {
        breadth: true,
        vix_regime: true,
        advance_decline: true,
        new_highs_lows: true,
      },
    },
    sector: {
      enabled: true,
      weight: 0.15,
      criteria: {
        rotation: true,
        leadership: true,
        correlation: true,
      },
    },
    industry: {
      enabled: true,
      weight: 0.10,
      criteria: {
        relative_strength: true,
        momentum: true,
      },
    },
    stock_specific: {
      enabled: true,
      weight: 0.05,
      criteria: {
        earnings: true,
        analyst_ratings: true,
        insider_activity: false,
        short_interest: false,
      },
    },
  },
  technical_criteria: {
    momentum: {
      return_20d: { enabled: false, min: -100, max: 100 },
      return_60d: { enabled: false, min: -100, max: 100 },
      return_252d: { enabled: false, min: -100, max: 100 },
      hurst: { enabled: false, min: 0, max: 1 },
      autocorr: { enabled: false, min: -1, max: 1 },
    },
    mean_reversion: {
      zscore: { enabled: false, min: -3, max: 3 },
      rsi: { enabled: false, min: 0, max: 100 },
      bollinger_position: { enabled: false, min: 0, max: 1 },
      mean_reversion_speed: { enabled: false, min: 0, max: 1 },
    },
    volatility: {
      atr_percentile: { enabled: false, min: 0, max: 100 },
      volume_surge: { enabled: false, min: 0, max: 10 },
      garch_vol: { enabled: false, min: 0, max: 100 },
      implied_vol: { enabled: false, min: 0, max: 100 },
    },
    trend: {
      price_vs_sma50: { enabled: false, min: -50, max: 50 },
      price_vs_sma200: { enabled: false, min: -50, max: 50 },
      sma_slope: { enabled: false, min: -10, max: 10 },
      adx: { enabled: false, min: 0, max: 100 },
    },
    liquidity: {
      avg_volume: { enabled: false, min: 0, max: 100000000 },
      dollar_volume: { enabled: false, min: 0, max: 1000000000 },
      spread: { enabled: false, min: 0, max: 1 },
      float: { enabled: false, min: 0, max: 1000000000 },
    },
  },
  filters: {
    sectors: {
      exclude: [],
    },
    symbols: {
      blacklist: [],
    },
    market_cap: {
      min: 0,
      max: 10000000000000,
    },
    price: {
      min: 1,
      max: 10000,
    },
    composite_score: {
      min: 0,
    },
  },
  ranking: {
    primary_sort: 'composite_score',
    secondary_sort: 'market_cap',
    sort_order: 'desc',
  },
  output: {
    max_results: 50,
    include_regime_scores: true,
    include_factor_breakdown: true,
    export_format: 'json',
  },
};
