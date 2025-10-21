/**
 * Sector Heatmap Component
 * Displays 11 sectors with color-coded regime strength
 */

import React from 'react';
import type { SectorRegimeData } from '../../types/regime';
import RegimeBadge from './RegimeBadge';

interface SectorHeatmapProps {
  data: SectorRegimeData | null;
}

function getStrengthColor(strength: number): string {
  if (strength >= 8) return 'bg-green-700';
  if (strength >= 6) return 'bg-green-800';
  if (strength >= 4) return 'bg-yellow-800';
  if (strength >= 2) return 'bg-orange-800';
  return 'bg-red-800';
}

export default function SectorHeatmap({ data }: SectorHeatmapProps) {
  if (!data) {
    return (
      <div className="bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">🏭 Sector Heatmap</h2>
        <div className="text-gray-400">Loading sector data...</div>
      </div>
    );
  }

  // Sort sectors by strength
  const sortedSectors = Object.entries(data.sectors).sort(
    ([, a], [, b]) => b.strength - a.strength
  );

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">🏭 Sector Heatmap</h2>
        <div className="text-sm text-gray-400">Sorted by strength</div>
      </div>

      {/* Heatmap Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {sortedSectors.map(([symbol, sector], index) => {
          const strengthColor = getStrengthColor(sector.strength);

          return (
            <div
              key={symbol}
              className={`rounded-lg p-4 ${strengthColor} transition-all hover:scale-105 cursor-pointer border border-gray-700`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-bold">{symbol}</span>
                {index < 3 && (
                  <span className="text-xs bg-white/20 px-2 py-0.5 rounded">#{index + 1}</span>
                )}
              </div>

              <div className="mb-2">
                <RegimeBadge regime={sector.regime} />
              </div>

              <div className="mt-3 space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-200">Strength:</span>
                  <span className="text-white font-semibold">{sector.strength.toFixed(1)}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-200">vs SPY (20d):</span>
                  <span
                    className={
                      sector.vs_spy_return_20d > 0 ? 'text-green-300' : 'text-red-300'
                    }
                  >
                    {(sector.vs_spy_return_20d * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Top 3 / Bottom 3 Summary */}
      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="bg-green-900/20 border border-green-700/50 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-green-400 mb-2">💪 Strongest Sectors</h3>
          <div className="space-y-1">
            {data.strongest_sectors.map((symbol) => (
              <div key={symbol} className="text-sm text-gray-300">
                {symbol}
              </div>
            ))}
          </div>
        </div>

        <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-red-400 mb-2">⚠️ Weakest Sectors</h3>
          <div className="space-y-1">
            {data.weakest_sectors.map((symbol) => (
              <div key={symbol} className="text-sm text-gray-300">
                {symbol}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Divergence Score */}
      <div className="mt-4 bg-gray-750 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400">Sector Divergence Score:</span>
          <span className="text-white font-bold text-lg">
            {data.divergence_score.toFixed(1)}/10
          </span>
        </div>
        <div className="text-xs text-gray-500 mt-1">
          {data.divergence_score > 7
            ? 'High divergence - Sector rotation active'
            : data.divergence_score > 4
            ? 'Moderate divergence - Mixed sector performance'
            : 'Low divergence - Broad market move'}
        </div>
      </div>
    </div>
  );
}
