/**
 * Overview Tab - Strategy description, key metrics, and signals
 */

import { TrendingUp, Award, DollarSign, BarChart3, Clock, AlertCircle } from 'lucide-react';
import type { StrategyExtended } from '../../../services/mock-data/strategy-data';
import { formatCurrency, formatPercent, getColorClass } from '../../../utils/helpers';
import { format } from 'date-fns';

interface OverviewTabProps {
  strategy: StrategyExtended;
}

export function OverviewTab({ strategy }: OverviewTabProps) {
  // Mock recent signals for this strategy
  const recentSignals = [
    {
      id: '1',
      timestamp: new Date(Date.now() - 1000 * 60 * 30),
      symbol: 'AAPL',
      action: 'BUY',
      price: 178.25,
      confidence: 0.87,
    },
    {
      id: '2',
      timestamp: new Date(Date.now() - 1000 * 60 * 120),
      symbol: 'MSFT',
      action: 'SELL',
      price: 412.33,
      confidence: 0.92,
    },
    {
      id: '3',
      timestamp: new Date(Date.now() - 1000 * 60 * 240),
      symbol: 'GOOGL',
      action: 'BUY',
      price: 141.82,
      confidence: 0.78,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Description Card */}
      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-3">Description</h2>
        <p className="text-gray-300 leading-relaxed">{strategy.description}</p>
        <div className="mt-4 pt-4 border-t border-gray-700 flex items-center gap-6 text-sm">
          <div>
            <span className="text-gray-500">Category:</span>
            <span className="text-white ml-2">{strategy.category}</span>
          </div>
          <div>
            <span className="text-gray-500">Author:</span>
            <span className="text-white ml-2">{strategy.author}</span>
          </div>
          {strategy.deployedAt && (
            <div>
              <span className="text-gray-500">Deployed:</span>
              <span className="text-white ml-2">
                {format(new Date(strategy.deployedAt), 'MMM d, yyyy')}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">Key Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-blue-900/30 rounded">
                <Award className="text-blue-400" size={20} />
              </div>
              <div className="text-sm text-gray-500">Win Rate</div>
            </div>
            <div className="text-2xl font-bold text-white">
              {strategy.performance.winRate.toFixed(1)}%
            </div>
            <div className="mt-2 text-xs text-gray-500">
              {strategy.performance.totalTrades} trades
            </div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-purple-900/30 rounded">
                <TrendingUp className="text-purple-400" size={20} />
              </div>
              <div className="text-sm text-gray-500">Sharpe Ratio</div>
            </div>
            <div className="text-2xl font-bold text-white">
              {strategy.performance.sharpeRatio.toFixed(2)}
            </div>
            <div className="mt-2 text-xs text-gray-500">Risk-adjusted return</div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-green-900/30 rounded">
                <DollarSign className={getColorClass(strategy.performance.totalPnL)} size={20} />
              </div>
              <div className="text-sm text-gray-500">Total P&L</div>
            </div>
            <div className={`text-2xl font-bold ${getColorClass(strategy.performance.totalPnL)}`}>
              {formatCurrency(strategy.performance.totalPnL)}
            </div>
            <div className="mt-2 text-xs text-gray-500">All-time</div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-yellow-900/30 rounded">
                <BarChart3 className="text-yellow-400" size={20} />
              </div>
              <div className="text-sm text-gray-500">Total Trades</div>
            </div>
            <div className="text-2xl font-bold text-white">
              {strategy.performance.totalTrades}
            </div>
            <div className="mt-2 text-xs text-gray-500">
              ~{strategy.avgHoldingDays} days avg hold
            </div>
          </div>
        </div>
      </div>

      {/* Recent Signals */}
      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Recent Signals</h2>
        {recentSignals.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No recent signals</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm text-gray-500 border-b border-gray-700">
                  <th className="pb-3 font-medium">Time</th>
                  <th className="pb-3 font-medium">Symbol</th>
                  <th className="pb-3 font-medium">Action</th>
                  <th className="pb-3 font-medium">Price</th>
                  <th className="pb-3 font-medium">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {recentSignals.map((signal) => (
                  <tr key={signal.id} className="border-b border-gray-800 last:border-0">
                    <td className="py-3 text-sm text-gray-400">
                      {format(signal.timestamp, 'MMM d, HH:mm')}
                    </td>
                    <td className="py-3 text-sm font-semibold text-white">{signal.symbol}</td>
                    <td className="py-3">
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded ${
                          signal.action === 'BUY'
                            ? 'bg-green-900/30 text-green-400'
                            : 'bg-red-900/30 text-red-400'
                        }`}
                      >
                        {signal.action}
                      </span>
                    </td>
                    <td className="py-3 text-sm text-white">{formatCurrency(signal.price)}</td>
                    <td className="py-3">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 max-w-[100px] bg-gray-700 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              signal.confidence >= 0.8
                                ? 'bg-green-500'
                                : signal.confidence >= 0.6
                                ? 'bg-yellow-500'
                                : 'bg-red-500'
                            }`}
                            style={{ width: `${signal.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-400">
                          {(signal.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Risk Profile */}
      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Risk Profile</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Max Drawdown</span>
              <span className="text-sm font-semibold text-red-400">
                {formatPercent(strategy.performance.maxDrawdown)}
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-red-500 h-2 rounded-full"
                style={{ width: `${Math.abs(strategy.performance.maxDrawdown)}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Avg Holding Period</span>
              <span className="text-sm font-semibold text-white">
                {strategy.avgHoldingDays} days
              </span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
              <Clock size={14} />
              <span>Medium-term strategy</span>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Position Size</span>
              <span className="text-sm font-semibold text-white">
                {strategy.parameters?.positionSize || '10%'}
              </span>
            </div>
            <p className="text-xs text-gray-500">Per trade allocation</p>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Stop Loss</span>
              <span className="text-sm font-semibold text-white">
                {strategy.parameters?.stopLoss || '2%'}
              </span>
            </div>
            <p className="text-xs text-gray-500">Maximum loss per trade</p>
          </div>
        </div>

        {strategy.status === 'ERROR' && (
          <div className="mt-6 p-4 bg-red-900/20 border border-red-700 rounded flex items-start gap-3">
            <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <div className="text-sm font-semibold text-red-400">Strategy Error</div>
              <p className="text-sm text-gray-300 mt-1">
                This strategy has encountered an error. Check configuration and logs.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
