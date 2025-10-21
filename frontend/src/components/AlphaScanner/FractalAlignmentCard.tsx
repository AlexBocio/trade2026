/**
 * Fractal Alignment Card Component
 * Display multi-timeframe regime alignment analysis
 */

import { useState } from 'react';
import TimeframeRegimeRow from './TimeframeRegimeRow';

interface FractalAlignmentCardProps {
  stock: any;
}

export default function FractalAlignmentCard({ stock }: FractalAlignmentCardProps) {
  const [expanded, setExpanded] = useState(false);

  const timeframes = [
    { name: '5-day', key: '5d', label: 'Micro' },
    { name: '20-day', key: '20d', label: 'Swing' },
    { name: '60-day', key: '60d', label: 'Intermediate' },
    { name: '252-day', key: '252d', label: 'Long-term' },
  ];

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700 hover:border-green-600 transition-all">
      <div
        className="p-4 cursor-pointer hover:bg-gray-750 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          {/* Stock Info */}
          <div className="flex items-center space-x-4">
            <div>
              <div className="text-white font-bold text-xl">{stock.symbol}</div>
              <div className="text-sm text-gray-400">{stock.coherence_level}</div>
            </div>
          </div>

          {/* Alignment Score */}
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-xs text-gray-400">Fractal Alignment</div>
              <div className="text-green-400 font-bold text-3xl">
                {stock.fractal_alignment_score.toFixed(1)}
                <span className="text-lg">/10</span>
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
        <div className="border-t border-gray-700 p-4 bg-gray-750 space-y-4">
          {/* Timeframe Breakdown */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
              <span>⏱️</span>
              <span>Multi-Timeframe Analysis</span>
            </h4>
            <div className="space-y-2">
              {timeframes.map((tf) => {
                const data = stock.timeframes[tf.key];
                return <TimeframeRegimeRow key={tf.key} timeframe={tf} data={data} />;
              })}
            </div>
          </div>

          {/* Alignment Analysis */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
                <span>🎯</span>
                <span>Regime Alignment</span>
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Regime Matches:</span>
                  <span className="text-white font-semibold">
                    {stock.alignment_analysis.regime_matches}/4
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">All Trending Up:</span>
                  <span
                    className={
                      stock.alignment_analysis.all_trending_up ? 'text-green-400' : 'text-red-400'
                    }
                  >
                    {stock.alignment_analysis.all_trending_up ? '✓ Yes' : '✗ No'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Regime Coherence:</span>
                  <span className="text-white font-semibold">
                    {(stock.alignment_analysis.regime_coherence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Directional Coherence:</span>
                  <span className="text-white font-semibold">
                    {(stock.alignment_analysis.directional_coherence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
                <span>💡</span>
                <span>Trade Implications</span>
              </h4>
              <div className="space-y-2 text-sm">
                <div>
                  <div className="text-gray-400 mb-1">Trend Strength:</div>
                  <div
                    className={`font-semibold ${
                      stock.trade_implications.trend_strength === 'VERY_STRONG'
                        ? 'text-green-400'
                        : stock.trade_implications.trend_strength === 'STRONG'
                        ? 'text-green-400'
                        : 'text-yellow-400'
                    }`}
                  >
                    {stock.trade_implications.trend_strength.replace(/_/g, ' ')}
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Continuation Probability:</div>
                  <div className="text-white font-semibold">
                    {(stock.trade_implications.continuation_probability * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Suggested Timeframe:</div>
                  <div className="text-white font-semibold text-xs">
                    {stock.trade_implications.suggested_timeframe.replace(/_/g, ' ')}
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Risk Level:</div>
                  <div
                    className={`font-semibold ${
                      stock.trade_implications.risk_level === 'LOW'
                        ? 'text-green-400'
                        : stock.trade_implications.risk_level === 'MEDIUM'
                        ? 'text-yellow-400'
                        : 'text-red-400'
                    }`}
                  >
                    {stock.trade_implications.risk_level}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Interpretation */}
          <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-xl">💡</span>
              <span className="text-blue-400 font-semibold">Interpretation</span>
            </div>
            <p className="text-sm text-gray-300">{stock.interpretation}</p>
          </div>
        </div>
      )}
    </div>
  );
}
