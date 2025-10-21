/**
 * Pair Card Component
 * Display pairs trading opportunity with spread analysis
 */

import { useState } from 'react';
import SpreadChart from './SpreadChart';

interface PairCardProps {
  pair: any;
}

export default function PairCard({ pair }: PairCardProps) {
  const [expanded, setExpanded] = useState(false);

  const getZscoreColor = (zscore: number) => {
    const absZ = Math.abs(zscore);
    if (absZ >= 3.0) return 'text-red-400';
    if (absZ >= 2.5) return 'text-orange-400';
    if (absZ >= 2.0) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getZscoreBg = (zscore: number) => {
    const absZ = Math.abs(zscore);
    if (absZ >= 3.0) return 'bg-red-900/20 border-red-700/50';
    if (absZ >= 2.5) return 'bg-orange-900/20 border-orange-700/50';
    if (absZ >= 2.0) return 'bg-yellow-900/20 border-yellow-700/50';
    return 'bg-green-900/20 border-green-700/50';
  };

  const getTradeDirection = (zscore: number) => {
    if (zscore > 0) {
      return {
        action: 'SHORT',
        stock1: pair.stock_a,
        stock2: pair.stock_b,
        direction1: 'SHORT',
        direction2: 'LONG',
        color: 'text-red-400',
      };
    } else {
      return {
        action: 'LONG',
        stock1: pair.stock_a,
        stock2: pair.stock_b,
        direction1: 'LONG',
        direction2: 'SHORT',
        color: 'text-green-400',
      };
    }
  };

  const trade = getTradeDirection(pair.current_zscore);

  return (
    <div className={`rounded-lg overflow-hidden border transition-all ${getZscoreBg(pair.current_zscore)}`}>
      <div
        className="p-4 cursor-pointer hover:bg-gray-750 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          {/* Pair Info */}
          <div className="flex items-center space-x-4">
            <div>
              <div className="flex items-center space-x-2 mb-1">
                <span className="text-white font-bold text-lg">{pair.stock_a}</span>
                <span className="text-gray-400">↔</span>
                <span className="text-white font-bold text-lg">{pair.stock_b}</span>
              </div>
              <div className="text-sm text-gray-300">
                Correlation: {pair.correlation.toFixed(3)}
              </div>
              {pair.sector && (
                <div className="text-xs text-gray-400">{pair.sector}</div>
              )}
            </div>
          </div>

          {/* Z-Score & Trade Direction */}
          <div className="flex items-center space-x-6">
            <div className="text-right hidden md:block">
              <div className="text-xs text-gray-400">Half-Life</div>
              <div className="text-white font-bold text-lg">
                {pair.half_life.toFixed(1)} days
              </div>
            </div>

            <div className="text-right">
              <div className="text-xs text-gray-400">Z-Score</div>
              <div className={`font-bold text-3xl ${getZscoreColor(pair.current_zscore)}`}>
                {pair.current_zscore.toFixed(2)}
              </div>
              <div className={`text-xs font-semibold ${trade.color}`}>
                {trade.action} SPREAD
              </div>
            </div>

            <button className="text-gray-400 hover:text-white transition-transform">
              <span className={`inline-block transition-transform ${expanded ? 'rotate-90' : ''}`}>
                ▶
              </span>
            </button>
          </div>
        </div>
      </div>

      {expanded && (
        <div className="border-t border-gray-700 p-4 bg-gray-800 space-y-4">
          {/* Spread Chart */}
          <div className="bg-gray-750 rounded-lg p-4 border border-gray-700">
            <h4 className="text-sm font-semibold text-gray-400 mb-3">📈 Spread History</h4>
            <SpreadChart data={pair.spread_history} zscore={pair.current_zscore} />
          </div>

          {/* Pair Statistics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-750 rounded-lg p-3 border border-gray-700">
              <div className="text-xs text-gray-400 mb-1">Correlation</div>
              <div className="text-white font-bold text-lg">
                {pair.correlation.toFixed(3)}
              </div>
            </div>
            <div className="bg-gray-750 rounded-lg p-3 border border-gray-700">
              <div className="text-xs text-gray-400 mb-1">Half-Life</div>
              <div className="text-white font-bold text-lg">
                {pair.half_life.toFixed(1)}d
              </div>
            </div>
            <div className="bg-gray-750 rounded-lg p-3 border border-gray-700">
              <div className="text-xs text-gray-400 mb-1">Spread Mean</div>
              <div className="text-white font-bold text-lg">
                {pair.spread_mean.toFixed(3)}
              </div>
            </div>
            <div className="bg-gray-750 rounded-lg p-3 border border-gray-700">
              <div className="text-xs text-gray-400 mb-1">Spread StdDev</div>
              <div className="text-white font-bold text-lg">
                {pair.spread_std.toFixed(3)}
              </div>
            </div>
          </div>

          {/* Cointegration Test */}
          {pair.cointegration_test && (
            <div className="bg-gray-750 rounded-lg p-4 border border-gray-700">
              <h4 className="text-sm font-semibold text-gray-400 mb-3">
                🔬 Cointegration Test (ADF)
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <div className="text-gray-400 mb-1">Test Statistic:</div>
                  <div className="text-white font-semibold">
                    {pair.cointegration_test.statistic.toFixed(4)}
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">P-Value:</div>
                  <div className={`font-semibold ${
                    pair.cointegration_test.p_value < 0.05 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {pair.cointegration_test.p_value.toFixed(4)}
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Cointegrated:</div>
                  <div className={`font-semibold ${
                    pair.cointegration_test.is_cointegrated ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {pair.cointegration_test.is_cointegrated ? '✓ Yes' : '✗ No'}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Trade Setup */}
          <div className={`rounded-lg p-4 border ${
            trade.action === 'LONG' ? 'bg-green-900/20 border-green-700/50' : 'bg-red-900/20 border-red-700/50'
          }`}>
            <div className="flex items-center space-x-2 mb-3">
              <span className="text-2xl">💡</span>
              <span className="text-white font-semibold">Trade Setup</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
              <div className="bg-gray-800 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">Stock A:</span>
                  <span className="text-white font-bold">{trade.stock1}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-sm">Action:</span>
                  <span className={`font-bold ${
                    trade.direction1 === 'LONG' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {trade.direction1}
                  </span>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">Stock B:</span>
                  <span className="text-white font-bold">{trade.stock2}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-sm">Action:</span>
                  <span className={`font-bold ${
                    trade.direction2 === 'LONG' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {trade.direction2}
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="text-sm">
                <div className="text-gray-400 mb-1">Entry Z-Score:</div>
                <div className="text-white font-semibold">
                  {pair.current_zscore.toFixed(2)}σ
                </div>
              </div>
              <div className="text-sm">
                <div className="text-gray-400 mb-1">Target (Mean):</div>
                <div className="text-green-400 font-semibold">
                  0.00σ
                </div>
              </div>
              <div className="text-sm">
                <div className="text-gray-400 mb-1">Stop Loss:</div>
                <div className="text-red-400 font-semibold">
                  {pair.current_zscore > 0 ? '+' : ''}{(pair.current_zscore * 1.5).toFixed(2)}σ
                </div>
              </div>
            </div>

            <div className="mt-3 pt-3 border-t border-gray-700 text-sm text-gray-300">
              <strong>Strategy:</strong> The spread is currently {Math.abs(pair.current_zscore).toFixed(2)}
              standard deviations from its mean. Trade to profit from mean reversion with expected
              convergence in ~{pair.half_life.toFixed(1)} days.
            </div>
          </div>

          {/* Risk Factors */}
          {pair.warnings && pair.warnings.length > 0 && (
            <div className="bg-red-900/10 border border-red-700/30 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-red-400 mb-2 flex items-center space-x-2">
                <span>⚠️</span>
                <span>Warnings</span>
              </h4>
              <ul className="text-xs text-gray-300 space-y-1">
                {pair.warnings.map((warning: string, i: number) => (
                  <li key={i}>• {warning}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
