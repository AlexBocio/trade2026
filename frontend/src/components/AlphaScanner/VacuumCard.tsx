/**
 * Vacuum Card Component
 * Display individual liquidity vacuum setup details
 */

import React, { useState } from 'react';
import LiquidityMetrics from './LiquidityMetrics';

interface CatalystAnalysis {
  has_catalyst: boolean;
  catalyst_type?: string;
  days_until?: number;
  options_iv?: number;
  iv_percentile?: number;
}

interface VacuumData {
  symbol: string;
  vacuum_type: string;
  vacuum_score: number;
  liquidity_metrics: any;
  catalyst_analysis: CatalystAnalysis;
  interpretation: string;
  expected_move: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  strategy_suggestion: string;
}

interface VacuumCardProps {
  vacuum: VacuumData;
}

export default function VacuumCard({ vacuum }: VacuumCardProps) {
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
              <div className="text-white font-bold text-lg">{vacuum.symbol}</div>
              <div className="text-sm text-gray-400">
                {vacuum.vacuum_type.replace(/_/g, ' ')}
              </div>
            </div>
          </div>

          {/* Vacuum Score */}
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-xs text-gray-400">Vacuum Score</div>
              <div className="text-orange-400 font-bold text-xl">
                {vacuum.vacuum_score.toFixed(1)}/10
              </div>
            </div>

            {vacuum.catalyst_analysis.has_catalyst && (
              <div className="bg-blue-600 px-3 py-1 rounded text-sm font-semibold">
                📅 Catalyst in {vacuum.catalyst_analysis.days_until}d
              </div>
            )}

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
          {/* Liquidity Metrics */}
          <LiquidityMetrics metrics={vacuum.liquidity_metrics} />

          {/* Catalyst Analysis */}
          {vacuum.catalyst_analysis.has_catalyst && (
            <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-blue-400 mb-3 flex items-center space-x-2">
                <span>📅</span>
                <span>Upcoming Catalyst</span>
              </h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-300">Type:</span>
                  <span className="text-white font-semibold">
                    {vacuum.catalyst_analysis.catalyst_type?.replace(/_/g, ' ')}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-300">Days Until:</span>
                  <span className="text-white font-semibold">
                    {vacuum.catalyst_analysis.days_until}
                  </span>
                </div>
                {vacuum.catalyst_analysis.options_iv && (
                  <>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-300">Options IV:</span>
                      <span className="text-orange-400 font-semibold">
                        {(vacuum.catalyst_analysis.options_iv * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-300">IV Percentile:</span>
                      <span className="text-white font-semibold">
                        {vacuum.catalyst_analysis.iv_percentile}th
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Interpretation */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-600">
            <h4 className="text-sm font-semibold text-gray-400 mb-2 flex items-center space-x-2">
              <span>💡</span>
              <span>Interpretation</span>
            </h4>
            <p className="text-sm text-gray-300 mb-3">{vacuum.interpretation}</p>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <div className="text-gray-400 mb-1">Expected Move:</div>
                <div className="text-white font-semibold">{vacuum.expected_move}</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Risk Level:</div>
                <div
                  className={`font-semibold ${
                    vacuum.risk_level === 'HIGH'
                      ? 'text-red-400'
                      : vacuum.risk_level === 'MEDIUM'
                      ? 'text-yellow-400'
                      : 'text-green-400'
                  }`}
                >
                  {vacuum.risk_level}
                </div>
              </div>
            </div>
          </div>

          {/* Strategy Suggestion */}
          <div className="bg-purple-900/20 border border-purple-700/50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-xl">⚡</span>
              <span className="text-purple-400 font-semibold">Strategy Suggestion</span>
            </div>
            <p className="text-sm text-gray-300">{vacuum.strategy_suggestion}</p>
          </div>
        </div>
      )}
    </div>
  );
}
