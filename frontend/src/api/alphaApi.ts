/**
 * Alpha API Client
 * Connects to Port 5008 alpha methods endpoints for advanced scanning
 */

const ALPHA_API_BASE = 'http://localhost:5008';

export const alphaApi = {
  // Time Machine Pattern Matching
  timeMachine: {
    /**
     * Find stocks that match a reference pattern
     */
    findMatches: async (
      referencePatternId: string,
      universe: string[],
      matchThreshold: number = 0.8
    ) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/time-machine/find-matches`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reference_pattern_id: referencePatternId,
          universe,
          match_threshold: matchThreshold,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to find matches: ${response.statusText}`);
      }

      return response.json();
    },

    /**
     * Create a custom pattern from historical data
     */
    createPattern: async (symbol: string, startDate: string, endDate: string) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/time-machine/create-pattern`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          start_date: startDate,
          end_date: endDate,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create pattern: ${response.statusText}`);
      }

      return response.json();
    },

    /**
     * Get all available patterns from library
     */
    getPatterns: async () => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/time-machine/patterns`);

      if (!response.ok) {
        throw new Error(`Failed to get patterns: ${response.statusText}`);
      }

      return response.json();
    },
  },

  // Correlation Breakdown Scanner
  correlation: {
    /**
     * Scan for correlation breakdowns
     */
    scan: async (
      universe: string,
      historicalWindow: number = 60,
      recentWindow: number = 10,
      minBreakdown: number = 0.4,
      direction: string = 'BOTH'
    ) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/correlation/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          universe,
          historical_window: historicalWindow,
          recent_window: recentWindow,
          min_breakdown: minBreakdown,
          direction,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to scan correlations: ${response.statusText}`);
      }

      return response.json();
    },

    /**
     * Get correlation history for a stock
     */
    getHistory: async (symbol: string, sector: string, lookback: number = 252) => {
      const response = await fetch(
        `${ALPHA_API_BASE}/api/alpha/correlation/history/${symbol}?sector=${sector}&lookback=${lookback}`
      );

      if (!response.ok) {
        throw new Error(`Failed to get correlation history: ${response.statusText}`);
      }

      return response.json();
    },
  },

  // Liquidity Vacuum Scanner
  liquidityVacuum: {
    /**
     * Scan for liquidity vacuum setups
     */
    scan: async (
      universe: string,
      lookbackDays: number = 20,
      minVacuumScore: number = 7.0,
      requireCatalyst: boolean = true
    ) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/liquidity-vacuum/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          universe,
          lookback_days: lookbackDays,
          min_vacuum_score: minVacuumScore,
          require_catalyst: requireCatalyst,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to scan liquidity vacuums: ${response.statusText}`);
      }

      return response.json();
    },
  },

  // Smart Money Tracker
  smartMoney: {
    /**
     * Track smart money across multiple signals
     */
    track: async (symbols: string[], lookbackDays: number = 5, minSignals: number = 2) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/smart-money/track`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbols,
          lookback_days: lookbackDays,
          min_signals: minSignals,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to track smart money: ${response.statusText}`);
      }

      return response.json();
    },

    /**
     * Get dark pool activity for a symbol
     */
    getDarkPool: async (symbol: string) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/smart-money/dark-pool/${symbol}`);

      if (!response.ok) {
        throw new Error(`Failed to get dark pool data: ${response.statusText}`);
      }

      return response.json();
    },

    /**
     * Get unusual options flow for a symbol
     */
    getOptions: async (symbol: string) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/smart-money/options/${symbol}`);

      if (!response.ok) {
        throw new Error(`Failed to get options data: ${response.statusText}`);
      }

      return response.json();
    },

    /**
     * Get insider activity for a symbol
     */
    getInsider: async (symbol: string) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/smart-money/insider/${symbol}`);

      if (!response.ok) {
        throw new Error(`Failed to get insider data: ${response.statusText}`);
      }

      return response.json();
    },
  },

  // Sentiment Divergence Scanner
  sentiment: {
    /**
     * Scan for sentiment divergences
     */
    scan: async (
      universe: string,
      divergenceType: string = 'BOTH',
      minDivergenceScore: number = 7.0,
      minMagnitude: number = 0.4
    ) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/sentiment/divergence/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          universe,
          divergence_type: divergenceType,
          min_divergence_score: minDivergenceScore,
          min_magnitude: minMagnitude,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to scan sentiment divergences: ${response.statusText}`);
      }

      return response.json();
    },

    /**
     * Get aggregate sentiment for a symbol
     */
    getSentiment: async (symbol: string) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/sentiment/aggregate/${symbol}`);

      if (!response.ok) {
        throw new Error(`Failed to get sentiment data: ${response.statusText}`);
      }

      return response.json();
    },
  },

  // Fractal Regime Scanner
  fractal: {
    /**
     * Scan for fractal regime alignment
     */
    scan: async (
      universe: string[],
      targetRegime: string = 'BULLISH',
      minAlignment: number = 8.0
    ) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/fractal/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          universe,
          target_regime: targetRegime,
          min_alignment: minAlignment,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to scan fractal alignment: ${response.statusText}`);
      }

      return response.json();
    },

    /**
     * Analyze fractal regime for a symbol
     */
    analyze: async (symbol: string) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/fractal/analyze/${symbol}`);

      if (!response.ok) {
        throw new Error(`Failed to analyze fractal regime: ${response.statusText}`);
      }

      return response.json();
    },
  },

  // Catalyst Calendar Scanner
  catalyst: {
    /**
     * Scan for catalyst setups
     */
    scan: async (
      universe: string,
      catalystTypes: string[],
      minDays: number = 7,
      maxDays: number = 30,
      minSetupScore: number = 7.5,
      regimeFilter?: string
    ) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/catalyst/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          universe,
          catalyst_types: catalystTypes,
          min_days: minDays,
          max_days: maxDays,
          min_setup_score: minSetupScore,
          regime_filter: regimeFilter,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to scan catalyst setups: ${response.statusText}`);
      }

      return response.json();
    },

    /**
     * Get catalyst calendar for symbols
     */
    getCalendar: async (symbols: string[], daysAhead: number = 60) => {
      const response = await fetch(
        `${ALPHA_API_BASE}/api/alpha/catalyst/calendar?symbols=${symbols.join(',')}&days_ahead=${daysAhead}`
      );

      if (!response.ok) {
        throw new Error(`Failed to get catalyst calendar: ${response.statusText}`);
      }

      return response.json();
    },
  },

  // Intermarket Relay Scanner
  intermarket: {
    /**
     * Scan for intermarket relay opportunities
     */
    scanRelay: async () => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/intermarket/relay/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error(`Failed to scan intermarket relays: ${response.statusText}`);
      }

      return response.json();
    },

    /**
     * Get lead-lag relationship details
     */
    getRelationship: async (leadSymbol: string) => {
      const response = await fetch(
        `${ALPHA_API_BASE}/api/alpha/intermarket/relationship/${leadSymbol}`
      );

      if (!response.ok) {
        throw new Error(`Failed to get intermarket relationship: ${response.statusText}`);
      }

      return response.json();
    },
  },

  // Pairs Trading Scanner
  pairs: {
    /**
     * Find pairs trading opportunities
     */
    find: async (
      universe: string,
      sector?: string,
      minCorrelation: number = 0.7,
      minZscore: number = 2.0,
      maxHalfLife: number = 15
    ) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/pairs/find`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          universe,
          sector,
          min_correlation: minCorrelation,
          min_zscore: minZscore,
          max_half_life: maxHalfLife,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to find pairs: ${response.statusText}`);
      }

      return response.json();
    },

    /**
     * Monitor specific pair
     */
    monitor: async (stockA: string, stockB: string) => {
      const response = await fetch(
        `${ALPHA_API_BASE}/api/alpha/pairs/monitor/${stockA}/${stockB}`
      );

      if (!response.ok) {
        throw new Error(`Failed to monitor pair: ${response.statusText}`);
      }

      return response.json();
    },
  },

  // Scenario Analysis Scanner
  scenario: {
    /**
     * Analyze stocks for specific scenario
     */
    analyze: async (scenario: string, universe: string) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/scenario/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario, universe }),
      });

      if (!response.ok) {
        throw new Error(`Failed to analyze scenario: ${response.statusText}`);
      }

      return response.json();
    },

    /**
     * List available scenarios
     */
    list: async () => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/scenario/list`);

      if (!response.ok) {
        throw new Error(`Failed to list scenarios: ${response.statusText}`);
      }

      return response.json();
    },

    /**
     * Run custom scenario analysis
     */
    custom: async (scenarioDefinition: any) => {
      const response = await fetch(`${ALPHA_API_BASE}/api/alpha/scenario/custom`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scenarioDefinition),
      });

      if (!response.ok) {
        throw new Error(`Failed to run custom scenario: ${response.statusText}`);
      }

      return response.json();
    },
  },
};

/**
 * Helper function to get universe stock list
 */
export async function getUniverseStocks(universe: string): Promise<string[]> {
  // This would typically fetch from an API or config
  // For now, return mock data based on universe
  const universes: Record<string, string[]> = {
    sp500: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'WMT'],
    sp400: ['CFR', 'STRL', 'IBCP', 'ONTO', 'CADE'],
    sp600: ['AMSF', 'HEES', 'MGRC', 'MCFT', 'PLAY'],
    nasdaq100: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'PYPL', 'NFLX', 'ADBE'],
  };

  return universes[universe] || universes.sp500;
}
