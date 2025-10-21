/**
 * Stock Result Card Component
 * Expandable card showing individual stock result with full regime hierarchy
 */

import React, { useState } from 'react';
import RegimeBadge from '../Regime/RegimeBadge';
import RegimeHierarchyView from './RegimeHierarchyView';
import TradeSetupCard from './TradeSetupCard';
import { formatCriteriaName, formatCriteriaValue } from '../../utils/formatters';

interface StockResultCardProps {
  stock: any;
  index?: number;
}

interface MetricProps {
  label: string;
  value: string;
  color: 'blue' | 'green' | 'red' | 'yellow' | 'white';
}

function Metric({ label, value, color }: MetricProps) {
  const colors = {
    blue: 'text-blue-400',
    green: 'text-green-400',
    red: 'text-red-400',
    yellow: 'text-yellow-400',
    white: 'text-white',
  };

  return (
    <div className="text-center">
      <div className="text-xs text-gray-400 mb-1">{label}</div>
      <div className={`font-semibold ${colors[color]}`}>{value}</div>
    </div>
  );
}

export default function StockResultCard({ stock, index }: StockResultCardProps) {
  const [expanded, setExpanded] = useState(false);

  const symbol = stock.symbol || stock.ticker;
  const rank = stock.rank || index !== undefined ? index + 1 : 0;

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden hover:ring-2 hover:ring-blue-500 transition-all">
      {/* Collapsed View */}
      <div className="p-4 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-center justify-between">
          {/* Left: Stock Info */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center justify-center w-12 h-12 bg-blue-600 rounded-lg text-white font-bold text-lg">
              #{rank}
            </div>

            <div>
              <div className="flex items-center space-x-2">
                <span className="text-white font-bold text-lg">{symbol}</span>
                <RegimeBadge
                  regime={
                    stock.regime_hierarchy?.stock?.regime ||
                    stock.primary_regime ||
                    stock.regime
                  }
                />
              </div>
              <div className="text-sm text-gray-400">
                Alignment: {(stock.alignment_score || 0).toFixed(1)}/10
              </div>
            </div>
          </div>

          {/* Center: Key Metrics */}
          <div className="hidden md:flex items-center space-x-6">
            <Metric
              label="Score"
              value={(stock.composite_score || 0).toFixed(1)}
              color="blue"
            />
            <Metric
              label="Momentum 20d"
              value={`${((stock.criteria_scores?.momentum_20d || 0) * 100).toFixed(1)}%`}
              color={(stock.criteria_scores?.momentum_20d || 0) > 0 ? 'green' : 'red'}
            />
            <Metric
              label="Volume"
              value={`${(stock.criteria_scores?.volume_surge || 0).toFixed(1)}x`}
              color="yellow"
            />
          </div>

          {/* Right: Expand Button */}
          <div className="flex items-center space-x-3">
            <div className="text-right hidden lg:block">
              <div className="text-xs text-gray-400">Failed Criteria</div>
              <div className="text-white font-semibold">
                {stock.failed_criteria?.length || 0}
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

      {/* Expanded View */}
      {expanded && (
        <div className="border-t border-gray-700 p-4 space-y-4 bg-gray-750 animate-in slide-in-from-top">
          {/* Regime Hierarchy */}
          {stock.regime_hierarchy && (
            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
                <span>🏗️</span>
                <span>Regime Hierarchy</span>
              </h3>
              <RegimeHierarchyView hierarchy={stock.regime_hierarchy} />
            </div>
          )}

          {/* All Criteria Scores */}
          {stock.criteria_scores && Object.keys(stock.criteria_scores).length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
                <span>📊</span>
                <span>Criteria Breakdown</span>
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {Object.entries(stock.criteria_scores).map(([key, value]) => (
                  <div key={key} className="bg-gray-800 rounded-lg p-3">
                    <div className="text-xs text-gray-400 mb-1">
                      {formatCriteriaName(key)}
                    </div>
                    <div className="text-white font-semibold">
                      {formatCriteriaValue(key, value)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Failed Criteria (if any) */}
          {stock.failed_criteria && stock.failed_criteria.length > 0 && (
            <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-red-400 mb-2 flex items-center space-x-2">
                <span>⚠️</span>
                <span>Failed Criteria ({stock.failed_criteria.length})</span>
              </h4>
              <div className="flex flex-wrap gap-2">
                {stock.failed_criteria.map((criteria: string, idx: number) => (
                  <span
                    key={idx}
                    className="text-xs bg-red-800 text-red-200 px-2 py-1 rounded"
                  >
                    {criteria}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Trade Setup */}
          <TradeSetupCard stock={stock} />

          {/* Actions */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
            <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center justify-center space-x-2">
              <span>📊</span>
              <span>View Chart</span>
            </button>
            <button className="flex-1 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center justify-center space-x-2">
              <span>📝</span>
              <span>Add to Watchlist</span>
            </button>
            <button className="flex-1 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center justify-center space-x-2">
              <span>🔗</span>
              <span>Trade Setup</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
