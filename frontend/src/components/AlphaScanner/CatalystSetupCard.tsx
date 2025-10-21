/**
 * Catalyst Setup Card Component
 * Display catalyst event with setup analysis
 */

import { useState } from 'react';
import RegimeBadge from './RegimeBadge';

interface CatalystSetupCardProps {
  setup: any;
}

export default function CatalystSetupCard({ setup }: CatalystSetupCardProps) {
  const [expanded, setExpanded] = useState(false);

  const getCatalystIcon = (type: string) => {
    const icons: Record<string, string> = {
      EARNINGS: '📊',
      FDA: '💊',
      PRODUCT_LAUNCH: '🚀',
      CONFERENCE: '🎤',
      MERGER: '🤝',
      DIVIDEND: '💰',
      SPLIT: '✂️',
      OTHER: '📅',
    };
    return icons[type] || '📅';
  };

  const getSetupScoreColor = (score: number) => {
    if (score >= 8.5) return 'text-green-400';
    if (score >= 7.0) return 'text-yellow-400';
    return 'text-orange-400';
  };

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700 hover:border-blue-600 transition-all">
      <div
        className="p-4 cursor-pointer hover:bg-gray-750 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          {/* Stock & Catalyst Info */}
          <div className="flex items-center space-x-4">
            <div className="text-4xl">{getCatalystIcon(setup.catalyst.type)}</div>
            <div>
              <div className="text-white font-bold text-lg">{setup.symbol}</div>
              <div className="text-sm text-gray-300">{setup.catalyst.type}</div>
              <div className="text-xs text-gray-400">{setup.catalyst.date}</div>
            </div>
          </div>

          {/* Scores */}
          <div className="flex items-center space-x-6">
            <div className="text-right hidden md:block">
              <div className="text-xs text-gray-400">Days Until</div>
              <div className="text-blue-400 font-bold text-xl">{setup.days_until}</div>
            </div>

            <div className="text-right">
              <div className="text-xs text-gray-400">Setup Score</div>
              <div className={`font-bold text-2xl ${getSetupScoreColor(setup.setup_score)}`}>
                {setup.setup_score.toFixed(1)}
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
          {/* Catalyst Details */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
              <span>{getCatalystIcon(setup.catalyst.type)}</span>
              <span>Catalyst Details</span>
            </h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-gray-400 mb-1">Event Type:</div>
                <div className="text-white font-semibold">{setup.catalyst.type}</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Event Date:</div>
                <div className="text-white font-semibold">{setup.catalyst.date}</div>
              </div>
              {setup.catalyst.description && (
                <div className="col-span-2">
                  <div className="text-gray-400 mb-1">Description:</div>
                  <div className="text-white text-sm">{setup.catalyst.description}</div>
                </div>
              )}
            </div>
          </div>

          {/* Current Regime Context */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
              <span>📈</span>
              <span>Current Regime Context</span>
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-gray-400 text-xs mb-1">Current Regime:</div>
                <RegimeBadge regime={setup.regime_context.current_regime} size="sm" />
              </div>
              <div>
                <div className="text-gray-400 text-xs mb-1">Regime Strength:</div>
                <div className="text-white font-semibold">
                  {setup.regime_context.regime_strength.toFixed(1)}
                </div>
              </div>
              <div>
                <div className="text-gray-400 text-xs mb-1">Volatility:</div>
                <div className="text-white font-semibold">
                  {(setup.regime_context.volatility * 100).toFixed(1)}%
                </div>
              </div>
              <div>
                <div className="text-gray-400 text-xs mb-1">Alignment:</div>
                <div className="text-white font-semibold">
                  {setup.regime_context.fractal_alignment.toFixed(1)}/10
                </div>
              </div>
            </div>
          </div>

          {/* Historical Pattern */}
          {setup.historical_pattern && (
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
                <span>📊</span>
                <span>Historical Pattern</span>
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-gray-400 mb-1">Pattern Type:</div>
                  <div className="text-white font-semibold">
                    {setup.historical_pattern.pattern_type}
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Success Rate:</div>
                  <div className="text-green-400 font-semibold">
                    {(setup.historical_pattern.success_rate * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Avg Move:</div>
                  <div className="text-green-400 font-semibold">
                    {(setup.historical_pattern.avg_move * 100).toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Sample Size:</div>
                  <div className="text-white font-semibold">
                    {setup.historical_pattern.sample_size}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Trade Plan */}
          <div
            className={`rounded-lg p-4 ${
              setup.expected_outcome === 'BULLISH'
                ? 'bg-green-900/20 border border-green-700/50'
                : setup.expected_outcome === 'BEARISH'
                ? 'bg-red-900/20 border border-red-700/50'
                : 'bg-yellow-900/20 border border-yellow-700/50'
            }`}
          >
            <div className="flex items-center space-x-2 mb-3">
              <span className="text-2xl">💡</span>
              <span className="text-white font-semibold">Trade Plan</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
              <div>
                <div className="text-sm mb-2">
                  <span className="text-gray-400">Expected Outcome:</span>
                  <span
                    className={`ml-2 font-semibold ${
                      setup.expected_outcome === 'BULLISH'
                        ? 'text-green-400'
                        : setup.expected_outcome === 'BEARISH'
                        ? 'text-red-400'
                        : 'text-yellow-400'
                    }`}
                  >
                    {setup.expected_outcome}
                  </span>
                </div>
                <div className="text-sm mb-2">
                  <span className="text-gray-400">Confidence:</span>
                  <span className="ml-2 text-white font-semibold">
                    {(setup.trade_plan.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-400">Risk/Reward:</span>
                  <span className="ml-2 text-white font-semibold">
                    {setup.trade_plan.risk_reward_ratio.toFixed(2)}
                  </span>
                </div>
              </div>

              <div>
                <div className="text-sm mb-2">
                  <span className="text-gray-400">Entry:</span>
                  <span className="ml-2 text-white font-semibold">
                    ${setup.trade_plan.entry.toFixed(2)}
                  </span>
                </div>
                <div className="text-sm mb-2">
                  <span className="text-gray-400">Target:</span>
                  <span className="ml-2 text-green-400 font-semibold">
                    ${setup.trade_plan.target.toFixed(2)}
                  </span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-400">Stop:</span>
                  <span className="ml-2 text-red-400 font-semibold">
                    ${setup.trade_plan.stop.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>

            <div className="text-sm text-gray-300 border-t border-gray-700 pt-3">
              <strong>Strategy:</strong> {setup.trade_plan.strategy}
            </div>
          </div>

          {/* Risk Factors */}
          {setup.risk_factors && setup.risk_factors.length > 0 && (
            <div className="bg-red-900/10 border border-red-700/30 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-red-400 mb-2 flex items-center space-x-2">
                <span>⚠️</span>
                <span>Risk Factors</span>
              </h4>
              <ul className="text-xs text-gray-300 space-y-1">
                {setup.risk_factors.map((risk: string, i: number) => (
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
