/**
 * Comparison View Component
 * Side-by-side comparison of two scans
 */

import React from 'react';
import { DualAxisHeatmap } from '../Heatmap/DualAxisHeatmap';
import type { HeatmapData } from '../../api/screenerApi';

interface ScanData {
  name: string;
  results: any[];
  heatmap_data: HeatmapData;
}

interface ComparisonViewProps {
  scanA: ScanData;
  scanB: ScanData;
}

export const ComparisonView: React.FC<ComparisonViewProps> = ({ scanA, scanB }) => {
  // Find consensus stocks (appear in both scans)
  const consensusStocks = scanA.results.filter(stockA =>
    scanB.results.some(stockB => stockB.ticker === stockA.ticker)
  );

  // Find unique stocks in each scan
  const uniqueToA = scanA.results.filter(stockA =>
    !scanB.results.some(stockB => stockB.ticker === stockA.ticker)
  );

  const uniqueToB = scanB.results.filter(stockB =>
    !scanA.results.some(stockA => stockA.ticker === stockB.ticker)
  );

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
          <div className="text-sm text-blue-400 mb-1">Consensus Stocks</div>
          <div className="text-3xl font-bold text-white">{consensusStocks.length}</div>
          <div className="text-xs text-gray-400 mt-1">Appear in both scans</div>
        </div>

        <div className="bg-purple-900/20 border border-purple-700 rounded-lg p-4">
          <div className="text-sm text-purple-400 mb-1">Unique to {scanA.name}</div>
          <div className="text-3xl font-bold text-white">{uniqueToA.length}</div>
          <div className="text-xs text-gray-400 mt-1">Only in first scan</div>
        </div>

        <div className="bg-orange-900/20 border border-orange-700 rounded-lg p-4">
          <div className="text-sm text-orange-400 mb-1">Unique to {scanB.name}</div>
          <div className="text-3xl font-bold text-white">{uniqueToB.length}</div>
          <div className="text-xs text-gray-400 mt-1">Only in second scan</div>
        </div>
      </div>

      {/* Consensus Stocks */}
      {consensusStocks.length > 0 && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <h3 className="text-xl font-semibold text-white mb-4">
            🎯 Consensus Opportunities
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {consensusStocks.map((stock) => (
              <div
                key={stock.ticker}
                className="bg-green-900/20 border border-green-700 rounded px-3 py-2 text-center"
              >
                <div className="font-mono font-bold text-green-400">{stock.ticker}</div>
                <div className="text-xs text-gray-400">{stock.company_name}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Side-by-Side Heatmaps */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Scan A */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="mb-4">
            <h3 className="text-xl font-semibold text-white">{scanA.name}</h3>
            <p className="text-sm text-gray-400">{scanA.results.length} stocks</p>
          </div>
          <div className="max-h-[600px] overflow-auto">
            <DualAxisHeatmap data={scanA.heatmap_data} />
          </div>
        </div>

        {/* Scan B */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="mb-4">
            <h3 className="text-xl font-semibold text-white">{scanB.name}</h3>
            <p className="text-sm text-gray-400">{scanB.results.length} stocks</p>
          </div>
          <div className="max-h-[600px] overflow-auto">
            <DualAxisHeatmap data={scanB.heatmap_data} />
          </div>
        </div>
      </div>

      {/* Unique Stocks */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Unique to A */}
        {uniqueToA.length > 0 && (
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              Only in {scanA.name}
            </h3>
            <div className="space-y-2">
              {uniqueToA.slice(0, 10).map((stock) => (
                <div
                  key={stock.ticker}
                  className="flex items-center justify-between bg-dark-bg rounded px-3 py-2"
                >
                  <div className="font-mono font-bold text-white">{stock.ticker}</div>
                  <div className="text-sm text-gray-400">
                    Score: {stock.composite_score?.toFixed(1) || 'N/A'}
                  </div>
                </div>
              ))}
              {uniqueToA.length > 10 && (
                <div className="text-center text-sm text-gray-500 pt-2">
                  +{uniqueToA.length - 10} more
                </div>
              )}
            </div>
          </div>
        )}

        {/* Unique to B */}
        {uniqueToB.length > 0 && (
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              Only in {scanB.name}
            </h3>
            <div className="space-y-2">
              {uniqueToB.slice(0, 10).map((stock) => (
                <div
                  key={stock.ticker}
                  className="flex items-center justify-between bg-dark-bg rounded px-3 py-2"
                >
                  <div className="font-mono font-bold text-white">{stock.ticker}</div>
                  <div className="text-sm text-gray-400">
                    Score: {stock.composite_score?.toFixed(1) || 'N/A'}
                  </div>
                </div>
              ))}
              {uniqueToB.length > 10 && (
                <div className="text-center text-sm text-gray-500 pt-2">
                  +{uniqueToB.length - 10} more
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
