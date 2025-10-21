/**
 * Temporal Context Card Component
 * Displays calendar-based patterns and seasonal regimes
 */

import React from 'react';
import type { TemporalContext } from '../../types/regime';
import RegimeBadge from './RegimeBadge';
import EventBadge from './EventBadge';

interface TemporalContextCardProps {
  data: TemporalContext | null;
}

function getSeasonalDescription(regime: string): string {
  const descriptions: Record<string, string> = {
    BULL_TRENDING: 'Historically bullish period with strong upward momentum',
    BEAR_TRENDING: 'Historically bearish period with downward pressure',
    NEUTRAL: 'Mixed historical performance with no clear directional bias',
    HIGH_VOLATILITY: 'Expect increased volatility during this period',
  };
  return descriptions[regime] || 'Analyzing seasonal patterns...';
}

export default function TemporalContextCard({ data }: TemporalContextCardProps) {
  if (!data) {
    return (
      <div className="bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">📅 Temporal Context</h2>
        <div className="text-gray-400">Loading temporal data...</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
      <h2 className="text-xl font-bold text-white mb-4">📅 Temporal Context</h2>

      <div className="space-y-4">
        {/* Current Date Info */}
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Current Date:</span>
          <span className="text-white font-semibold">
            {data.month_name} {data.day_of_month}, {data.day_of_week}
          </span>
        </div>

        {/* Seasonal Regime */}
        <div className="bg-gray-750 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Seasonal Regime:</span>
            <RegimeBadge regime={data.seasonal_regime} />
          </div>
          <p className="text-sm text-gray-300">
            {getSeasonalDescription(data.seasonal_regime)}
          </p>
        </div>

        {/* Day-of-Week Pattern */}
        <div className="bg-gray-750 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Day Pattern:</span>
            <RegimeBadge regime={data.day_regime} />
          </div>
          <p className="text-sm text-gray-300">
            {data.day_of_week} typically shows {data.day_regime.toLowerCase().replace('_', ' ')} behavior
          </p>
        </div>

        {/* Event Calendar */}
        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-2">Upcoming Events:</h3>
          <div className="space-y-2">
            <EventBadge label="Earnings Season" active={data.is_earnings_season} color="blue" />
            <EventBadge label="Options Expiration Week" active={data.is_opex_week} color="yellow" />
            <EventBadge label="Fed Week" active={data.is_fed_week} color="red" />
            {!data.is_earnings_season && !data.is_opex_week && !data.is_fed_week && (
              <span className="text-sm text-gray-500">No major events this week</span>
            )}
          </div>
        </div>

        {/* Days to Next Events */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-700">
          <div>
            <div className="text-xs text-gray-400">Next Fed Decision</div>
            <div className="text-lg font-semibold text-white">{data.days_to_next_fed} days</div>
          </div>
          <div>
            <div className="text-xs text-gray-400">Next CPI Print</div>
            <div className="text-lg font-semibold text-white">{data.days_to_next_cpi} days</div>
          </div>
        </div>

        {/* Historical Month Performance */}
        <div className="bg-gray-750 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-gray-400 mb-2">
            Historical {data.month_name} Performance:
          </h4>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-300">SPY Avg Return:</span>
            <span
              className={`font-semibold ${
                data.historical_month_performance.SPY_avg_return > 0
                  ? 'text-green-400'
                  : 'text-red-400'
              }`}
            >
              {(data.historical_month_performance.SPY_avg_return * 100).toFixed(1)}%
            </span>
          </div>
          <div className="flex items-center justify-between mt-2">
            <span className="text-sm text-gray-300">Volatility Percentile:</span>
            <span className="text-white font-semibold">
              {data.historical_month_performance.volatility_percentile}th
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
