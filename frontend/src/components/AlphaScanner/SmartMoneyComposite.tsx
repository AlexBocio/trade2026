/**
 * Smart Money Composite Component
 * Comprehensive display combining dark pool, options, and insider signals
 */

import React, { useState } from 'react';
import DarkPoolActivityCard from './DarkPoolActivityCard';
import OptionsFlowCard from './OptionsFlowCard';
import InsiderActivityCard from './InsiderActivityCard';

interface CatalystCheck {
  next_earnings: string;
  days_until: number;
}

interface SmartMoneyData {
  symbol: string;
  smart_money_score: number;
  signal_strength: 'STRONG' | 'MODERATE' | 'WEAK';
  interpretation: string;
  dark_pool?: any;
  unusual_options?: any;
  insider_activity?: any;
  recommendation: string;
  confidence: number;
  catalyst_check?: CatalystCheck;
}

interface SmartMoneyCompositeProps {
  data: SmartMoneyData;
}

export default function SmartMoneyComposite({ data }: SmartMoneyCompositeProps) {
  const [expanded, setExpanded] = useState(false);

  // Determine signal strength colors
  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-400';
    if (score >= 6) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getSignalBadge = (strength: string) => {
    const colors = {
      STRONG: 'bg-green-600',
      MODERATE: 'bg-yellow-600',
      WEAK: 'bg-gray-600',
    };
    return colors[strength as keyof typeof colors] || 'bg-gray-600';
  };

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
              <div className="text-white font-bold text-xl">{data.symbol}</div>
              <div className="flex items-center space-x-2 mt-1">
                <span
                  className={`px-3 py-1 rounded text-xs font-semibold ${getSignalBadge(
                    data.signal_strength
                  )}`}
                >
                  {data.signal_strength}
                </span>
                <span className="text-sm text-gray-400">{data.interpretation}</span>
              </div>
            </div>
          </div>

          {/* Composite Score */}
          <div className="flex items-center space-x-6">
            {/* Individual Signals */}
            <div className="hidden md:flex items-center space-x-4">
              {data.dark_pool && (
                <div className="text-center">
                  <div className="text-xs text-gray-400">Dark Pool</div>
                  <div className={`font-bold ${getScoreColor(data.dark_pool.activity_score)}`}>
                    {data.dark_pool.activity_score.toFixed(1)}
                  </div>
                </div>
              )}

              {data.unusual_options && (
                <div className="text-center">
                  <div className="text-xs text-gray-400">Options</div>
                  <div
                    className={`font-bold ${getScoreColor(data.unusual_options.options_score)}`}
                  >
                    {data.unusual_options.options_score.toFixed(1)}
                  </div>
                </div>
              )}

              {data.insider_activity && (
                <div className="text-center">
                  <div className="text-xs text-gray-400">Insider</div>
                  <div
                    className={`font-bold ${getScoreColor(data.insider_activity.insider_score)}`}
                  >
                    {data.insider_activity.insider_score.toFixed(1)}
                  </div>
                </div>
              )}
            </div>

            {/* Composite */}
            <div className="text-right">
              <div className="text-xs text-gray-400">Smart Money Score</div>
              <div className={`text-3xl font-bold ${getScoreColor(data.smart_money_score)}`}>
                {data.smart_money_score.toFixed(1)}
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
        <div className="border-t border-gray-700 p-4 bg-gray-750 space-y-4 animate-in slide-in-from-top">
          {/* Dark Pool Activity */}
          {data.dark_pool && <DarkPoolActivityCard data={data.dark_pool} />}

          {/* Unusual Options */}
          {data.unusual_options && <OptionsFlowCard data={data.unusual_options} />}

          {/* Insider Activity */}
          {data.insider_activity && <InsiderActivityCard data={data.insider_activity} />}

          {/* Recommendation */}
          <div
            className={`rounded-lg p-4 ${
              data.signal_strength === 'STRONG'
                ? 'bg-green-900/20 border border-green-700/50'
                : 'bg-yellow-900/20 border border-yellow-700/50'
            }`}
          >
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-2xl">💡</span>
              <span className="text-white font-semibold">Recommendation</span>
            </div>
            <p className="text-sm text-gray-300 mb-3">{data.recommendation}</p>
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">Confidence:</span>
              <span className="text-white font-semibold">
                {(data.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Catalyst Check */}
          {data.catalyst_check && (
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-600">
              <div className="text-sm text-gray-400 mb-2 flex items-center space-x-2">
                <span>📅</span>
                <span>Upcoming Events:</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-300">Next Earnings:</span>
                <span className="text-white font-semibold">
                  {data.catalyst_check.next_earnings} ({data.catalyst_check.days_until} days)
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
