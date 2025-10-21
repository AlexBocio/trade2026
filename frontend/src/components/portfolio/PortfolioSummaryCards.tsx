/**
 * Portfolio Summary Cards - Top-level metrics display
 */

import { TrendingUp, DollarSign, Target, Award } from 'lucide-react';

interface PortfolioSummary {
  accountValue: number;
  todayPnL: number;
  todayPnLPct: number;
  totalPnL: number;
  totalPnLPct: number;
  winRate: number;
  sharpeRatio: number;
  maxDrawdown: number;
}

export function PortfolioSummaryCards({ summary }: { summary: PortfolioSummary }) {
  return (
    <div className="grid grid-cols-4 gap-6 mb-6">
      {/* Account Value */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-gray-400">Account Value</div>
          <DollarSign className="w-5 h-5 text-gray-400" />
        </div>
        <div className="text-3xl font-bold mb-1">${summary.accountValue.toLocaleString()}</div>
        <div className="text-sm text-gray-400">Total equity</div>
      </div>

      {/* Today's P&L */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-gray-400">Today's P&L</div>
          <TrendingUp
            className={`w-5 h-5 ${summary.todayPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}
          />
        </div>
        <div
          className={`text-3xl font-bold mb-1 ${summary.todayPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}
        >
          {summary.todayPnL >= 0 ? '+' : ''}${summary.todayPnL.toLocaleString()}
        </div>
        <div className={`text-sm ${summary.todayPnLPct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {summary.todayPnLPct >= 0 ? '+' : ''}
          {summary.todayPnLPct.toFixed(2)}%
        </div>
      </div>

      {/* Total P&L */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-gray-400">Total P&L</div>
          <Target className={`w-5 h-5 ${summary.totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`} />
        </div>
        <div
          className={`text-3xl font-bold mb-1 ${summary.totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}
        >
          {summary.totalPnL >= 0 ? '+' : ''}${summary.totalPnL.toLocaleString()}
        </div>
        <div className={`text-sm ${summary.totalPnLPct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {summary.totalPnLPct >= 0 ? '+' : ''}
          {summary.totalPnLPct.toFixed(2)}% All-time
        </div>
      </div>

      {/* Win Rate */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-gray-400">Win Rate</div>
          <Award className="w-5 h-5 text-yellow-400" />
        </div>
        <div className="text-3xl font-bold mb-1">{summary.winRate.toFixed(1)}%</div>
        <div className="text-sm text-gray-400">Sharpe: {summary.sharpeRatio.toFixed(2)}</div>
      </div>
    </div>
  );
}
