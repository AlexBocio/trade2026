/**
 * Divergence Card Component
 * Display sentiment divergence analysis
 */

import { useState } from 'react';
import RegimeBadge from './RegimeBadge';

interface DivergenceCardProps {
  divergence: any;
}

export default function DivergenceCard({ divergence }: DivergenceCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700 hover:border-orange-600 transition-all">
      <div
        className="p-4 cursor-pointer hover:bg-gray-750 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          {/* Stock Info */}
          <div className="flex items-center space-x-4">
            <div>
              <div className="text-white font-bold text-lg">{divergence.symbol}</div>
              <div
                className={`text-sm font-semibold ${
                  divergence.divergence_type === 'BULLISH' ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {divergence.divergence_type} DIVERGENCE
              </div>
            </div>
          </div>

          {/* Scores */}
          <div className="flex items-center space-x-6">
            <div className="text-right hidden md:block">
              <div className="text-xs text-gray-400">Divergence Score</div>
              <div className="text-orange-400 font-bold text-xl">
                {divergence.divergence_score.toFixed(1)}
              </div>
            </div>

            <div className="text-right">
              <div className="text-xs text-gray-400">Magnitude</div>
              <div className="text-white font-bold text-xl">
                {divergence.divergence_magnitude.toFixed(2)}
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
          {/* Sentiment vs Price */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Sentiment */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
                <span>💭</span>
                <span>Sentiment</span>
              </h4>
              <div className="text-center mb-3">
                <div
                  className={`text-4xl font-bold ${
                    divergence.sentiment.composite < -0.3
                      ? 'text-red-400'
                      : divergence.sentiment.composite > 0.3
                      ? 'text-green-400'
                      : 'text-yellow-400'
                  }`}
                >
                  {divergence.sentiment.label}
                </div>
                <div className="text-gray-400 text-sm mt-1">
                  Score: {divergence.sentiment.composite.toFixed(2)}
                </div>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">News:</span>
                  <span className="text-white">
                    {divergence.sentiment.sources.news.toFixed(2)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Social:</span>
                  <span className="text-white">
                    {divergence.sentiment.sources.social.toFixed(2)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Analyst:</span>
                  <span className="text-white">
                    {divergence.sentiment.sources.analyst.toFixed(2)}
                  </span>
                </div>
              </div>

              {divergence.sentiment.key_bearish_topics && (
                <div className="mt-3 pt-3 border-t border-gray-700">
                  <div className="text-xs text-gray-400 mb-1">Key Topics:</div>
                  <div className="flex flex-wrap gap-1">
                    {divergence.sentiment.key_bearish_topics.map((topic: string, i: number) => (
                      <span
                        key={i}
                        className="text-xs bg-red-900/30 text-red-400 px-2 py-0.5 rounded"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Price Action */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
                <span>📈</span>
                <span>Price Action</span>
              </h4>
              <div className="space-y-3">
                <div>
                  <div className="text-xs text-gray-400 mb-1">20-Day Return</div>
                  <div
                    className={`text-3xl font-bold ${
                      divergence.price_action.return_20d > 0 ? 'text-green-400' : 'text-red-400'
                    }`}
                  >
                    {(divergence.price_action.return_20d * 100).toFixed(1)}%
                  </div>
                </div>

                <div>
                  <div className="text-xs text-gray-400 mb-1">5-Day Return</div>
                  <div
                    className={`text-xl font-bold ${
                      divergence.price_action.return_5d > 0 ? 'text-green-400' : 'text-red-400'
                    }`}
                  >
                    {(divergence.price_action.return_5d * 100).toFixed(1)}%
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-700">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-gray-400">Regime:</span>
                    <RegimeBadge regime={divergence.price_action.regime} size="sm" />
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Strength:</span>
                    <span className="text-white font-semibold">
                      {divergence.price_action.regime_strength.toFixed(1)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Volume Confirmation */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Volume Confirmation:</span>
              <div className="flex items-center space-x-2">
                <span className="text-white font-bold text-lg">
                  {divergence.volume.volume_trend.toFixed(1)}x
                </span>
                <span
                  className={`text-sm ${
                    divergence.volume.volume_score > 0.7 ? 'text-green-400' : 'text-yellow-400'
                  }`}
                >
                  {divergence.volume.volume_score > 0.7 ? '✓ Strong' : '○ Moderate'}
                </span>
              </div>
            </div>
          </div>

          {/* Interpretation */}
          <div
            className={`rounded-lg p-4 ${
              divergence.divergence_type === 'BULLISH'
                ? 'bg-green-900/20 border border-green-700/50'
                : 'bg-red-900/20 border border-red-700/50'
            }`}
          >
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-2xl">💡</span>
              <span className="text-white font-semibold">{divergence.interpretation}</span>
            </div>
            <p className="text-sm text-gray-300 mb-3">{divergence.explanation}</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
              <div>
                <span className="text-gray-400">Action:</span>
                <span className="text-white font-semibold ml-2">{divergence.action}</span>
              </div>
              <div>
                <span className="text-gray-400">Confidence:</span>
                <span className="text-white font-semibold ml-2">
                  {(divergence.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <div>
                <span className="text-gray-400">Risk Level:</span>
                <span
                  className={`font-semibold ml-2 ${
                    divergence.risk_level === 'HIGH'
                      ? 'text-red-400'
                      : divergence.risk_level === 'MEDIUM'
                      ? 'text-yellow-400'
                      : 'text-green-400'
                  }`}
                >
                  {divergence.risk_level}
                </span>
              </div>
            </div>
          </div>

          {/* Historical Similar */}
          {divergence.similar_historical && (
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
                <span>📊</span>
                <span>Historical Pattern</span>
              </h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-gray-400 mb-1">Success Rate:</div>
                  <div className="text-white font-semibold text-lg">
                    {(divergence.similar_historical.success_rate * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Avg 30d Return:</div>
                  <div className="text-green-400 font-semibold text-lg">
                    {(divergence.similar_historical.avg_forward_return_30d * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
