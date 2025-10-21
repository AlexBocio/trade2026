/**
 * Stock Fit Card Component
 * Display how well a stock fits a macro scenario
 */

import { useState } from 'react';

interface StockFitCardProps {
  stock: any;
}

export default function StockFitCard({ stock }: StockFitCardProps) {
  const [expanded, setExpanded] = useState(false);

  const getFitScoreColor = (score: number) => {
    if (score >= 8.5) return 'text-green-400';
    if (score >= 7.0) return 'text-yellow-400';
    return 'text-orange-400';
  };

  const getFitScoreBg = (score: number) => {
    if (score >= 8.5) return 'bg-green-900/20 border-green-700/50';
    if (score >= 7.0) return 'bg-yellow-900/20 border-yellow-700/50';
    return 'bg-orange-900/20 border-orange-700/50';
  };

  return (
    <div className={`rounded-lg overflow-hidden border transition-all ${getFitScoreBg(stock.fit_score)}`}>
      <div
        className="p-4 cursor-pointer hover:bg-gray-750 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          {/* Stock Info */}
          <div className="flex items-center space-x-4">
            <div>
              <div className="text-white font-bold text-lg mb-1">{stock.symbol}</div>
              <div className="text-sm text-gray-300">{stock.company_name}</div>
              <div className="text-xs text-gray-400">{stock.sector}</div>
            </div>
          </div>

          {/* Fit Score */}
          <div className="flex items-center space-x-6">
            <div className="text-right hidden md:block">
              <div className="text-xs text-gray-400">Expected Return</div>
              <div className={`font-bold text-lg ${
                stock.expected_return > 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {stock.expected_return > 0 ? '+' : ''}{(stock.expected_return * 100).toFixed(1)}%
              </div>
            </div>

            <div className="text-right">
              <div className="text-xs text-gray-400">Fit Score</div>
              <div className={`font-bold text-3xl ${getFitScoreColor(stock.fit_score)}`}>
                {stock.fit_score.toFixed(1)}
              </div>
              <div className="text-xs text-gray-400">/10</div>
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
          {/* Fit Breakdown */}
          <div className="bg-gray-750 rounded-lg p-4 border border-gray-700">
            <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
              <span>🎯</span>
              <span>Scenario Fit Breakdown</span>
            </h4>
            <div className="space-y-3">
              {stock.fit_factors && stock.fit_factors.map((factor: any, i: number) => (
                <div key={i}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-300">{factor.name}</span>
                    <span className={`text-sm font-semibold ${
                      factor.score >= 7 ? 'text-green-400' :
                      factor.score >= 5 ? 'text-yellow-400' :
                      'text-red-400'
                    }`}>
                      {factor.score.toFixed(1)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        factor.score >= 7 ? 'bg-green-500' :
                        factor.score >= 5 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${(factor.score / 10) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Historical Performance in Scenario */}
          {stock.historical_performance && (
            <div className="bg-gray-750 rounded-lg p-4 border border-gray-700">
              <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
                <span>📊</span>
                <span>Historical Performance in This Scenario</span>
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-gray-400 mb-1">Avg Return:</div>
                  <div className={`font-semibold ${
                    stock.historical_performance.avg_return > 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {stock.historical_performance.avg_return > 0 ? '+' : ''}
                    {(stock.historical_performance.avg_return * 100).toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Win Rate:</div>
                  <div className="text-white font-semibold">
                    {(stock.historical_performance.win_rate * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Max Drawdown:</div>
                  <div className="text-red-400 font-semibold">
                    {(stock.historical_performance.max_drawdown * 100).toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Sample Size:</div>
                  <div className="text-white font-semibold">
                    {stock.historical_performance.sample_size}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Current Metrics */}
          <div className="bg-gray-750 rounded-lg p-4 border border-gray-700">
            <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
              <span>💼</span>
              <span>Current Metrics</span>
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              {stock.current_price && (
                <div>
                  <div className="text-gray-400 mb-1">Current Price:</div>
                  <div className="text-white font-semibold">
                    ${stock.current_price.toFixed(2)}
                  </div>
                </div>
              )}
              {stock.beta && (
                <div>
                  <div className="text-gray-400 mb-1">Beta:</div>
                  <div className="text-white font-semibold">
                    {stock.beta.toFixed(2)}
                  </div>
                </div>
              )}
              {stock.volatility && (
                <div>
                  <div className="text-gray-400 mb-1">30d Volatility:</div>
                  <div className="text-white font-semibold">
                    {(stock.volatility * 100).toFixed(1)}%
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Recommendation */}
          <div className={`rounded-lg p-4 border ${
            stock.recommendation === 'STRONG_BUY' || stock.recommendation === 'BUY'
              ? 'bg-green-900/20 border-green-700/50'
              : stock.recommendation === 'SELL' || stock.recommendation === 'STRONG_SELL'
              ? 'bg-red-900/20 border-red-700/50'
              : 'bg-yellow-900/20 border-yellow-700/50'
          }`}>
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-2xl">💡</span>
              <span className="text-white font-semibold">Recommendation</span>
            </div>

            <div className="mb-3">
              <span className={`text-lg font-bold ${
                stock.recommendation === 'STRONG_BUY' || stock.recommendation === 'BUY'
                  ? 'text-green-400'
                  : stock.recommendation === 'SELL' || stock.recommendation === 'STRONG_SELL'
                  ? 'text-red-400'
                  : 'text-yellow-400'
              }`}>
                {stock.recommendation.replace(/_/g, ' ')}
              </span>
            </div>

            <div className="text-sm text-gray-300">
              {stock.rationale}
            </div>
          </div>

          {/* Risks */}
          {stock.risks && stock.risks.length > 0 && (
            <div className="bg-red-900/10 border border-red-700/30 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-red-400 mb-2 flex items-center space-x-2">
                <span>⚠️</span>
                <span>Key Risks</span>
              </h4>
              <ul className="text-xs text-gray-300 space-y-1">
                {stock.risks.map((risk: string, i: number) => (
                  <li key={i}>• {risk}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
