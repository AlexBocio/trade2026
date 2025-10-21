/**
 * Results Table Component
 * Compact table view of scanner results
 */

import React from 'react';
import RegimeBadge from '../Regime/RegimeBadge';

interface ResultsTableProps {
  results: any[];
  onRowClick?: (stock: any) => void;
}

export default function ResultsTable({ results, onRowClick }: ResultsTableProps) {
  if (!results || results.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-8 text-center">
        <div className="text-gray-400">No results to display</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-750">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Rank
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Symbol
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Regime
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Score
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Alignment
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                20d Return
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Volume
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                RSI
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {results.map((stock, index) => {
              const symbol = stock.symbol || stock.ticker;
              const rank = stock.rank || index + 1;
              const regime =
                stock.regime_hierarchy?.stock?.regime ||
                stock.primary_regime ||
                stock.regime;
              const momentum20d = stock.criteria_scores?.momentum_20d || 0;
              const volumeSurge = stock.criteria_scores?.volume_surge || 0;
              const rsi = stock.criteria_scores?.rsi || 50;

              return (
                <tr
                  key={symbol}
                  onClick={() => onRowClick?.(stock)}
                  className="hover:bg-gray-750 transition-colors cursor-pointer"
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-center w-8 h-8 bg-blue-600 rounded text-white font-bold text-sm">
                      #{rank}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-white font-semibold text-sm">{symbol}</span>
                  </td>
                  <td className="px-4 py-3">
                    <RegimeBadge regime={regime as any} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-white font-semibold">
                      {(stock.composite_score || 0).toFixed(1)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-white">{(stock.alignment_score || 0).toFixed(1)}</span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span
                      className={`font-semibold ${
                        momentum20d > 0 ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {(momentum20d * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-white">{volumeSurge.toFixed(1)}x</span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span
                      className={`${
                        rsi > 70
                          ? 'text-red-400'
                          : rsi < 30
                          ? 'text-green-400'
                          : 'text-gray-300'
                      }`}
                    >
                      {rsi.toFixed(0)}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Table Footer */}
      <div className="bg-gray-750 border-t border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <span>Total Results: {results.length}</span>
          <span>Click row to view details</span>
        </div>
      </div>
    </div>
  );
}
