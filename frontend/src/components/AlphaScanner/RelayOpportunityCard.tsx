/**
 * Relay Opportunity Card Component
 * Display intermarket lead-lag relationship opportunities
 */

import { useState } from 'react';

interface RelayOpportunityCardProps {
  opportunity: any;
}

export default function RelayOpportunityCard({ opportunity }: RelayOpportunityCardProps) {
  const [expanded, setExpanded] = useState(false);

  const getUrgencyColor = (daysUntil: number) => {
    if (daysUntil <= 1) return 'text-red-400 animate-pulse';
    if (daysUntil <= 2) return 'text-orange-400';
    if (daysUntil <= 3) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getUrgencyBg = (daysUntil: number) => {
    if (daysUntil <= 1) return 'bg-red-900/20 border-red-700/50';
    if (daysUntil <= 2) return 'bg-orange-900/20 border-orange-700/50';
    if (daysUntil <= 3) return 'bg-yellow-900/20 border-yellow-700/50';
    return 'bg-green-900/20 border-green-700/50';
  };

  const getDirectionIcon = (direction: string) => {
    if (direction === 'UP') return '📈';
    if (direction === 'DOWN') return '📉';
    return '➡️';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-400';
    if (confidence >= 0.6) return 'text-yellow-400';
    return 'text-orange-400';
  };

  return (
    <div className={`rounded-lg overflow-hidden border transition-all ${getUrgencyBg(opportunity.days_until_flip)}`}>
      <div
        className="p-4 cursor-pointer hover:bg-gray-750 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          {/* Lead/Lag Info */}
          <div className="flex items-center space-x-4">
            <div className="text-4xl">{getDirectionIcon(opportunity.lead_direction)}</div>
            <div>
              <div className="flex items-center space-x-2 mb-1">
                <span className="text-white font-bold text-lg">{opportunity.lead_market}</span>
                <span className="text-gray-400">→</span>
                <span className="text-blue-400 font-bold text-lg">{opportunity.lag_market}</span>
              </div>
              <div className="text-sm text-gray-300">
                Lag: {opportunity.lag_days} day{opportunity.lag_days !== 1 ? 's' : ''}
              </div>
              <div className="text-xs text-gray-400">
                Correlation: {opportunity.correlation.toFixed(2)}
              </div>
            </div>
          </div>

          {/* Timing & Urgency */}
          <div className="flex items-center space-x-6">
            <div className="text-right hidden md:block">
              <div className="text-xs text-gray-400">Confidence</div>
              <div className={`font-bold text-xl ${getConfidenceColor(opportunity.confidence)}`}>
                {(opportunity.confidence * 100).toFixed(0)}%
              </div>
            </div>

            <div className="text-right">
              <div className="text-xs text-gray-400">Days Until Flip</div>
              <div className={`font-bold text-3xl ${getUrgencyColor(opportunity.days_until_flip)}`}>
                {opportunity.days_until_flip}
              </div>
              {opportunity.days_until_flip <= 1 && (
                <div className="text-xs text-red-400 font-semibold animate-pulse">
                  🚨 IMMINENT
                </div>
              )}
            </div>

            <button className="text-gray-400 hover:text-white transition-transform">
              <span className={`inline-block transition-transform ${expanded ? 'rotate-90' : ''}`}>
                ▶
              </span>
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
            <span>Lead Market Moved</span>
            <span>{opportunity.days_since_lead_move} day{opportunity.days_since_lead_move !== 1 ? 's' : ''} ago</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                opportunity.days_until_flip <= 1
                  ? 'bg-red-500'
                  : opportunity.days_until_flip <= 2
                  ? 'bg-orange-500'
                  : 'bg-blue-500'
              }`}
              style={{
                width: `${Math.min(100, (opportunity.days_since_lead_move / opportunity.lag_days) * 100)}%`,
              }}
            />
          </div>
        </div>
      </div>

      {expanded && (
        <div className="border-t border-gray-700 p-4 bg-gray-800 space-y-4">
          {/* Lead Market Analysis */}
          <div className="bg-gray-750 rounded-lg p-4 border border-gray-700">
            <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
              <span>📊</span>
              <span>Lead Market Analysis</span>
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-gray-400 mb-1">Symbol:</div>
                <div className="text-white font-semibold">{opportunity.lead_market}</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Direction:</div>
                <div className="text-white font-semibold">
                  {getDirectionIcon(opportunity.lead_direction)} {opportunity.lead_direction}
                </div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Move Size:</div>
                <div className="text-white font-semibold">
                  {(opportunity.lead_move_size * 100).toFixed(1)}%
                </div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Days Ago:</div>
                <div className="text-white font-semibold">
                  {opportunity.days_since_lead_move}
                </div>
              </div>
            </div>
          </div>

          {/* Lag Market Analysis */}
          <div className="bg-gray-750 rounded-lg p-4 border border-gray-700">
            <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
              <span>🎯</span>
              <span>Lag Market Analysis</span>
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-gray-400 mb-1">Symbol:</div>
                <div className="text-blue-400 font-semibold">{opportunity.lag_market}</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Expected Direction:</div>
                <div className="text-white font-semibold">
                  {getDirectionIcon(opportunity.lead_direction)} {opportunity.lead_direction}
                </div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Expected Move:</div>
                <div className="text-green-400 font-semibold">
                  {(opportunity.expected_lag_move * 100).toFixed(1)}%
                </div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Historical Lag:</div>
                <div className="text-white font-semibold">
                  {opportunity.lag_days} day{opportunity.lag_days !== 1 ? 's' : ''}
                </div>
              </div>
            </div>
          </div>

          {/* Historical Success */}
          <div className="bg-gray-750 rounded-lg p-4 border border-gray-700">
            <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
              <span>📈</span>
              <span>Historical Performance</span>
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-gray-400 mb-1">Success Rate:</div>
                <div className="text-green-400 font-semibold text-lg">
                  {(opportunity.historical_success_rate * 100).toFixed(0)}%
                </div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Avg Follow Move:</div>
                <div className="text-white font-semibold text-lg">
                  {(opportunity.avg_follow_move * 100).toFixed(1)}%
                </div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Sample Size:</div>
                <div className="text-white font-semibold text-lg">
                  {opportunity.sample_size}
                </div>
              </div>
            </div>
          </div>

          {/* Stocks to Watch */}
          {opportunity.stocks_to_watch && opportunity.stocks_to_watch.length > 0 && (
            <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-blue-400 mb-3 flex items-center space-x-2">
                <span>👀</span>
                <span>Stocks to Watch in {opportunity.lag_market}</span>
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                {opportunity.stocks_to_watch.map((stock: string) => (
                  <div
                    key={stock}
                    className="bg-gray-800 px-3 py-2 rounded text-white font-mono text-sm text-center hover:bg-gray-700 transition-colors"
                  >
                    {stock}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Trade Plan */}
          {opportunity.trade_plan && (
            <div className={`rounded-lg p-4 border ${
              opportunity.lead_direction === 'UP'
                ? 'bg-green-900/20 border-green-700/50'
                : 'bg-red-900/20 border-red-700/50'
            }`}>
              <div className="flex items-center space-x-2 mb-3">
                <span className="text-2xl">💡</span>
                <span className="text-white font-semibold">Trade Plan</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                <div>
                  <div className="text-sm mb-2">
                    <span className="text-gray-400">Direction:</span>
                    <span className={`ml-2 font-semibold ${
                      opportunity.lead_direction === 'UP' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {getDirectionIcon(opportunity.lead_direction)} {opportunity.lead_direction}
                    </span>
                  </div>
                  <div className="text-sm mb-2">
                    <span className="text-gray-400">Confidence:</span>
                    <span className={`ml-2 font-semibold ${getConfidenceColor(opportunity.confidence)}`}>
                      {(opportunity.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-400">Risk/Reward:</span>
                    <span className="ml-2 text-white font-semibold">
                      {opportunity.trade_plan.risk_reward.toFixed(2)}
                    </span>
                  </div>
                </div>

                <div>
                  <div className="text-sm mb-2">
                    <span className="text-gray-400">Entry:</span>
                    <span className="ml-2 text-white font-semibold">
                      {opportunity.trade_plan.entry_type}
                    </span>
                  </div>
                  <div className="text-sm mb-2">
                    <span className="text-gray-400">Target:</span>
                    <span className="ml-2 text-green-400 font-semibold">
                      {(opportunity.trade_plan.target_return * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-400">Stop:</span>
                    <span className="ml-2 text-red-400 font-semibold">
                      -{(opportunity.trade_plan.stop_loss * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="text-sm text-gray-300 border-t border-gray-700 pt-3">
                <strong>Strategy:</strong> {opportunity.trade_plan.strategy}
              </div>
            </div>
          )}

          {/* Risk Factors */}
          {opportunity.risk_factors && opportunity.risk_factors.length > 0 && (
            <div className="bg-red-900/10 border border-red-700/30 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-red-400 mb-2 flex items-center space-x-2">
                <span>⚠️</span>
                <span>Risk Factors</span>
              </h4>
              <ul className="text-xs text-gray-300 space-y-1">
                {opportunity.risk_factors.map((risk: string, i: number) => (
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
