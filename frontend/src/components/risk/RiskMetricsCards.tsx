/**
 * Risk Metrics Cards - Top-level risk indicators
 */

import { TrendingDown, Activity, BarChart3, Zap } from 'lucide-react';

interface RiskMetrics {
  portfolioVaR: number;
  maxDrawdown: number;
  beta: number;
  volatility: number;
}

export function RiskMetricsCards({ metrics }: { metrics: RiskMetrics }) {
  return (
    <div className="grid grid-cols-4 gap-6 mb-6">
      {/* Portfolio VaR */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-gray-400">Portfolio VaR (95%)</div>
          <TrendingDown className="w-5 h-5 text-red-400" />
        </div>
        <div className="text-3xl font-bold mb-1 text-red-400">${metrics.portfolioVaR.toLocaleString()}</div>
        <div className="text-sm text-gray-400">Daily risk exposure</div>
      </div>

      {/* Max Drawdown */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-gray-400">Max Drawdown</div>
          <BarChart3 className="w-5 h-5 text-yellow-400" />
        </div>
        <div className="text-3xl font-bold mb-1 text-yellow-400">{metrics.maxDrawdown.toFixed(1)}%</div>
        <div className="text-sm text-gray-400">Peak to trough</div>
      </div>

      {/* Beta */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-gray-400">Portfolio Beta</div>
          <Activity className="w-5 h-5 text-blue-400" />
        </div>
        <div className="text-3xl font-bold mb-1 text-blue-400">{metrics.beta.toFixed(2)}</div>
        <div className="text-sm text-gray-400">vs S&P 500</div>
      </div>

      {/* Volatility */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-gray-400">Volatility</div>
          <Zap className="w-5 h-5 text-purple-400" />
        </div>
        <div className="text-3xl font-bold mb-1 text-purple-400">{metrics.volatility.toFixed(1)}%</div>
        <div className="text-sm text-gray-400">Annualized</div>
      </div>
    </div>
  );
}
