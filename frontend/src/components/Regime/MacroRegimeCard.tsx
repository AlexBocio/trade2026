/**
 * Macro Regime Card Component
 * Displays Fed policy, inflation, economic cycle regimes
 */

import React from 'react';
import type { MacroRegime } from '../../types/regime';
import RegimeBadge from './RegimeBadge';
import ProgressBar from './ProgressBar';
import MetricCard from './MetricCard';

interface MacroRegimeCardProps {
  data: MacroRegime | null;
}

interface MacroRegimeRowProps {
  label: string;
  regime: string;
  metric: string;
  value: string;
}

function MacroRegimeRow({ label, regime, metric, value }: MacroRegimeRowProps) {
  return (
    <div className="bg-gray-750 rounded-lg p-3">
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm text-gray-300">{label}:</span>
        <RegimeBadge regime={regime as any} />
      </div>
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-400">{metric}:</span>
        <span className="text-sm text-white font-semibold">{value}</span>
      </div>
    </div>
  );
}

export default function MacroRegimeCard({ data }: MacroRegimeCardProps) {
  if (!data) {
    return (
      <div className="bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">🌍 Macro Regime</h2>
        <div className="text-gray-400">Loading macro data...</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
      <h2 className="text-xl font-bold text-white mb-4">🌍 Macro Regime</h2>

      <div className="space-y-4">
        {/* Overall Macro Assessment */}
        <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-lg p-4 border border-blue-700/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-300 text-sm">Overall Macro:</span>
            <RegimeBadge regime={data.overall_macro} large />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-xs">Confidence:</span>
            <div className="flex-1 ml-4">
              <ProgressBar value={data.confidence * 100} showLabel={true} />
            </div>
          </div>
        </div>

        {/* Individual Regimes */}
        <div className="grid grid-cols-1 gap-3">
          <MacroRegimeRow
            label="Fed Policy"
            regime={data.fed_policy_regime}
            metric="Fed Funds Rate"
            value={`${data.metrics.fed_funds_rate.toFixed(2)}%`}
          />

          <MacroRegimeRow
            label="Economic Cycle"
            regime={data.economic_cycle}
            metric="GDP Growth"
            value={`${data.metrics.gdp_growth.toFixed(1)}%`}
          />

          <MacroRegimeRow
            label="Inflation"
            regime={data.inflation_regime}
            metric="CPI (YoY)"
            value={`${data.metrics.cpi_yoy.toFixed(1)}%`}
          />

          <MacroRegimeRow
            label="Geopolitical"
            regime={data.geopolitical_regime}
            metric="Risk Level"
            value="Moderate"
          />
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-700">
          <MetricCard
            label="Unemployment"
            value={`${data.metrics.unemployment.toFixed(1)}%`}
            trend={data.metrics.unemployment < 4 ? 'down' : 'up'}
          />
          <MetricCard
            label="Yield Curve (2s10s)"
            value={`${data.metrics.yield_curve_2s10s.toFixed(2)}%`}
            trend={data.metrics.yield_curve_2s10s > 0 ? 'up' : 'down'}
            subtitle={data.metrics.yield_curve_2s10s > 0 ? 'Normal' : 'Inverted'}
          />
        </div>
      </div>
    </div>
  );
}
