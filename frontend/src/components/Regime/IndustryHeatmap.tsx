/**
 * Industry Heatmap Component
 * Displays top 30 industries grouped by sector
 */

import React, { useState } from 'react';
import type { IndustryRegimeData } from '../../types/regime';
import RegimeBadge from './RegimeBadge';

interface IndustryHeatmapProps {
  data: IndustryRegimeData | null;
}

function getStrengthColor(strength: number): string {
  if (strength >= 8) return 'bg-green-700';
  if (strength >= 6) return 'bg-green-800';
  if (strength >= 4) return 'bg-yellow-800';
  if (strength >= 2) return 'bg-orange-800';
  return 'bg-red-800';
}

export default function IndustryHeatmap({ data }: IndustryHeatmapProps) {
  const [groupBy, setGroupBy] = useState<'strength' | 'sector'>('strength');

  if (!data) {
    return (
      <div className="bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">🏢 Industry Heatmap</h2>
        <div className="text-gray-400">Loading industry data...</div>
      </div>
    );
  }

  // Group industries by sector if needed
  const groupedIndustries =
    groupBy === 'sector'
      ? data.industries.reduce((acc, industry) => {
          if (!acc[industry.sector]) acc[industry.sector] = [];
          acc[industry.sector].push(industry);
          return acc;
        }, {} as Record<string, typeof data.industries>)
      : { All: data.industries };

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">🏢 Industry Heatmap (Top 30)</h2>

        {/* Group By Toggle */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">Group by:</span>
          <button
            onClick={() => setGroupBy('strength')}
            className={`px-3 py-1 rounded text-sm ${
              groupBy === 'strength'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
            }`}
          >
            Strength
          </button>
          <button
            onClick={() => setGroupBy('sector')}
            className={`px-3 py-1 rounded text-sm ${
              groupBy === 'sector'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
            }`}
          >
            Sector
          </button>
        </div>
      </div>

      {/* Industry Grid */}
      <div className="space-y-6">
        {Object.entries(groupedIndustries).map(([groupName, industries]) => (
          <div key={groupName}>
            {groupBy === 'sector' && (
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
                {groupName}
              </h3>
            )}

            <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3">
              {industries.map((industry, index) => {
                const strengthColor = getStrengthColor(industry.strength);

                return (
                  <div
                    key={industry.symbol}
                    className={`rounded-lg p-3 ${strengthColor} transition-all hover:scale-105 cursor-pointer border border-gray-700`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-bold text-sm">{industry.symbol}</span>
                      {index < 5 && groupBy === 'strength' && (
                        <span className="text-xs bg-white/20 px-1.5 py-0.5 rounded">
                          #{index + 1}
                        </span>
                      )}
                    </div>

                    <div className="mb-2">
                      <RegimeBadge regime={industry.regime} />
                    </div>

                    <div className="space-y-1 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-200">Strength:</span>
                        <span className="text-white font-semibold">
                          {industry.strength.toFixed(1)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-200">vs Sector:</span>
                        <span
                          className={
                            industry.vs_sector_return > 0 ? 'text-green-300' : 'text-red-300'
                          }
                        >
                          {(industry.vs_sector_return * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-200">Momentum:</span>
                        <span className="text-white font-semibold">
                          {industry.momentum_score.toFixed(0)}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Top/Bottom Summary */}
      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="bg-green-900/20 border border-green-700/50 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-green-400 mb-2">🚀 Top Industries</h3>
          <div className="space-y-1">
            {data.top_industries.slice(0, 5).map((symbol) => (
              <div key={symbol} className="text-sm text-gray-300">
                {symbol}
              </div>
            ))}
          </div>
        </div>

        <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-red-400 mb-2">📉 Bottom Industries</h3>
          <div className="space-y-1">
            {data.bottom_industries.slice(0, 5).map((symbol) => (
              <div key={symbol} className="text-sm text-gray-300">
                {symbol}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
