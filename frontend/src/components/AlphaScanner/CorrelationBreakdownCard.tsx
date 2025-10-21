/**
 * Correlation Breakdown Card Component
 * Display correlation breakdown details with regime analysis and action recommendations
 */

import React, { useState } from 'react';
import RegimeBadge from '../Regime/RegimeBadge';
import CorrelationChart from './CorrelationChart';

interface RegimeAnalysis {
  stock_regime: string;
  sector_regime: string;
  regime_divergence_score: number;
}

interface CauseAnalysis {
  primary_cause: string;
  catalyst_description?: string;
  volume_confirmation: number;
}

interface CorrelationBreakdown {
  symbol: string;
  sector: string;
  divergence_direction: 'POSITIVE' | 'NEGATIVE';
  correlation_delta: number;
  historical_correlation: number;
  recent_correlation: number;
  breakdown_type: string;
  stock_return_10d: number;
  sector_return_10d: number;
  regime_analysis: RegimeAnalysis;
  cause_analysis: CauseAnalysis;
  actionable: boolean;
  action_recommendation?: string;
  risk_level?: 'LOW' | 'MEDIUM' | 'HIGH';
}

interface CorrelationBreakdownCardProps {
  breakdown: CorrelationBreakdown;
}

export default function CorrelationBreakdownCard({ breakdown }: CorrelationBreakdownCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [showChart, setShowChart] = useState(false);

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700 hover:border-blue-600 transition-all">
      <div
        className="p-4 cursor-pointer hover:bg-gray-750 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          {/* Stock Info */}
          <div className="flex items-center space-x-4">
            <div>
              <div className="text-white font-bold text-lg">{breakdown.symbol}</div>
              <div className="text-sm text-gray-400">Sector: {breakdown.sector}</div>
            </div>

            <div
              className={`px-3 py-1 rounded text-sm font-semibold ${
                breakdown.divergence_direction === 'POSITIVE'
                  ? 'bg-green-900/30 text-green-400 border border-green-700/50'
                  : 'bg-red-900/30 text-red-400 border border-red-700/50'
              }`}
            >
              {breakdown.divergence_direction === 'POSITIVE' ? '📈 Outperforming' : '📉 Underperforming'}
            </div>
          </div>

          {/* Correlation Delta */}
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-xs text-gray-400">Correlation Δ</div>
              <div className="text-red-400 font-bold text-lg">
                {breakdown.correlation_delta.toFixed(2)}
              </div>
            </div>

            <button className="text-gray-400 hover:text-white transition-transform">
              <span
                className={`inline-block transition-transform ${expanded ? 'rotate-90' : ''}`}
              >
                ▶
              </span>
            </button>
          </div>
        </div>
      </div>

      {expanded && (
        <div className="border-t border-gray-700 p-4 bg-gray-750 space-y-4 animate-in slide-in-from-top">
          {/* Correlation Metrics */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="text-xs text-gray-400 mb-1">Historical (60d)</div>
              <div className="text-white font-bold text-xl">
                {breakdown.historical_correlation.toFixed(2)}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="text-xs text-gray-400 mb-1">Recent (10d)</div>
              <div className="text-white font-bold text-xl">
                {breakdown.recent_correlation.toFixed(2)}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="text-xs text-gray-400 mb-1">Breakdown Type</div>
              <div className="text-orange-400 font-semibold">{breakdown.breakdown_type}</div>
            </div>
          </div>

          {/* Returns Comparison */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
              <span>📊</span>
              <span>Recent Performance (10d)</span>
            </h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs text-gray-400 mb-1">{breakdown.symbol} Return</div>
                <div
                  className={`font-bold text-xl ${
                    breakdown.stock_return_10d > 0 ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  {(breakdown.stock_return_10d * 100).toFixed(1)}%
                </div>
              </div>

              <div>
                <div className="text-xs text-gray-400 mb-1">{breakdown.sector} Return</div>
                <div
                  className={`font-bold text-xl ${
                    breakdown.sector_return_10d > 0 ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  {(breakdown.sector_return_10d * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          </div>

          {/* Regime Analysis */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
              <span>🎯</span>
              <span>Regime Analysis</span>
            </h4>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs text-gray-400 mb-1">Stock Regime</div>
                <RegimeBadge regime={breakdown.regime_analysis.stock_regime as any} />
              </div>

              <div className="text-gray-600 text-2xl">→</div>

              <div>
                <div className="text-xs text-gray-400 mb-1">Sector Regime</div>
                <RegimeBadge regime={breakdown.regime_analysis.sector_regime as any} />
              </div>

              <div className="text-right">
                <div className="text-xs text-gray-400 mb-1">Divergence Score</div>
                <div className="text-orange-400 font-bold text-lg">
                  {breakdown.regime_analysis.regime_divergence_score.toFixed(1)}/10
                </div>
              </div>
            </div>
          </div>

          {/* Cause Analysis */}
          <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-blue-400 mb-2 flex items-center space-x-2">
              <span>💡</span>
              <span>Cause Analysis</span>
            </h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-300">Primary Cause:</span>
                <span className="text-white font-semibold">
                  {breakdown.cause_analysis.primary_cause.replace(/_/g, ' ')}
                </span>
              </div>

              {breakdown.cause_analysis.catalyst_description && (
                <p className="text-sm text-gray-300">
                  {breakdown.cause_analysis.catalyst_description}
                </p>
              )}

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-300">Volume Confirmation:</span>
                <span className="text-white font-semibold">
                  {breakdown.cause_analysis.volume_confirmation.toFixed(1)}x
                </span>
              </div>
            </div>
          </div>

          {/* Action Recommendation */}
          {breakdown.actionable && breakdown.action_recommendation && (
            <div
              className={`rounded-lg p-4 ${
                breakdown.divergence_direction === 'POSITIVE'
                  ? 'bg-green-900/20 border border-green-700/50'
                  : 'bg-red-900/20 border border-red-700/50'
              }`}
            >
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-xl">⚡</span>
                <span className="text-white font-semibold">Action Recommendation</span>
              </div>
              <p className="text-sm text-gray-300 mb-2">{breakdown.action_recommendation}</p>
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">Risk Level:</span>
                <span
                  className={`font-semibold ${
                    breakdown.risk_level === 'HIGH'
                      ? 'text-red-400'
                      : breakdown.risk_level === 'MEDIUM'
                      ? 'text-yellow-400'
                      : 'text-green-400'
                  }`}
                >
                  {breakdown.risk_level}
                </span>
              </div>
            </div>
          )}

          {/* Chart Toggle */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowChart(!showChart);
            }}
            className="w-full bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
          >
            {showChart ? '📊 Hide' : '📊 Show'} Correlation History Chart
          </button>

          {showChart && <CorrelationChart symbol={breakdown.symbol} sector={breakdown.sector} />}
        </div>
      )}
    </div>
  );
}
