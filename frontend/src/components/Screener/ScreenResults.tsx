/**
 * Screen Results Component
 * Sortable table displaying all screening results
 */

import React, { useState } from 'react';
import { ChevronUp, ChevronDown, TrendingUp, TrendingDown } from 'lucide-react';
import type { StockResult } from '../../api/screenerApi';

interface ScreenResultsProps {
  results: StockResult[];
}

type SortKey = 'ticker' | 'price' | 'change_pct' | 'volume' | 'composite_score';
type SortDirection = 'asc' | 'desc';

export const ScreenResults: React.FC<ScreenResultsProps> = ({ results }) => {
  const [sortKey, setSortKey] = useState<SortKey>('composite_score');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('desc');
    }
  };

  const sortedResults = [...results].sort((a, b) => {
    const aValue = a[sortKey];
    const bValue = b[sortKey];

    if (typeof aValue === 'string' && typeof bValue === 'string') {
      return sortDirection === 'asc'
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue);
    }

    return sortDirection === 'asc'
      ? (aValue as number) - (bValue as number)
      : (bValue as number) - (aValue as number);
  });

  const SortIcon = ({ column }: { column: SortKey }) => {
    if (sortKey !== column) return null;
    return sortDirection === 'asc' ? (
      <ChevronUp className="w-4 h-4" />
    ) : (
      <ChevronDown className="w-4 h-4" />
    );
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg overflow-hidden">
      <div className="p-4 border-b border-dark-border">
        <h3 className="text-xl font-semibold text-white">
          All Results ({results.length} stocks)
        </h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-dark-bg">
            <tr>
              <th
                className="px-4 py-3 text-left text-sm font-semibold text-gray-300 cursor-pointer hover:bg-dark-border transition"
                onClick={() => handleSort('ticker')}
              >
                <div className="flex items-center gap-2">
                  Ticker
                  <SortIcon column="ticker" />
                </div>
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-300">
                Company
              </th>
              <th
                className="px-4 py-3 text-right text-sm font-semibold text-gray-300 cursor-pointer hover:bg-dark-border transition"
                onClick={() => handleSort('price')}
              >
                <div className="flex items-center justify-end gap-2">
                  Price
                  <SortIcon column="price" />
                </div>
              </th>
              <th
                className="px-4 py-3 text-right text-sm font-semibold text-gray-300 cursor-pointer hover:bg-dark-border transition"
                onClick={() => handleSort('change_pct')}
              >
                <div className="flex items-center justify-end gap-2">
                  Change
                  <SortIcon column="change_pct" />
                </div>
              </th>
              <th
                className="px-4 py-3 text-right text-sm font-semibold text-gray-300 cursor-pointer hover:bg-dark-border transition"
                onClick={() => handleSort('volume')}
              >
                <div className="flex items-center justify-end gap-2">
                  Volume
                  <SortIcon column="volume" />
                </div>
              </th>
              <th
                className="px-4 py-3 text-right text-sm font-semibold text-gray-300 cursor-pointer hover:bg-dark-border transition"
                onClick={() => handleSort('composite_score')}
              >
                <div className="flex items-center justify-end gap-2">
                  Score
                  <SortIcon column="composite_score" />
                </div>
              </th>
              <th className="px-4 py-3 text-center text-sm font-semibold text-gray-300">
                Signals
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-300">
                Sector
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-border">
            {sortedResults.map((stock) => {
              const isPositive = stock.change_pct >= 0;
              return (
                <tr key={stock.ticker} className="hover:bg-dark-bg transition">
                  <td className="px-4 py-3">
                    <span className="font-mono font-bold text-white">{stock.ticker}</span>
                  </td>
                  <td className="px-4 py-3 text-gray-300 text-sm max-w-xs truncate">
                    {stock.company_name}
                  </td>
                  <td className="px-4 py-3 text-right text-white font-medium">
                    ${stock.price.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className={`flex items-center justify-end gap-1 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                      {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                      {isPositive ? '+' : ''}{stock.change_pct.toFixed(2)}%
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right text-gray-300 text-sm">
                    {(stock.volume / 1000000).toFixed(2)}M
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className={`font-bold ${
                      stock.composite_score >= 80 ? 'text-green-400' :
                      stock.composite_score >= 60 ? 'text-blue-400' :
                      stock.composite_score >= 40 ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {stock.composite_score}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-center gap-2 text-xs">
                      <span className={`px-2 py-1 rounded ${
                        stock.signals.technical === 'bullish' ? 'bg-green-900/30 text-green-400' :
                        stock.signals.technical === 'bearish' ? 'bg-red-900/30 text-red-400' :
                        'bg-gray-900/30 text-gray-400'
                      }`}>
                        T
                      </span>
                      <span className={`px-2 py-1 rounded ${
                        stock.signals.fundamental === 'strong' ? 'bg-green-900/30 text-green-400' :
                        stock.signals.fundamental === 'weak' ? 'bg-red-900/30 text-red-400' :
                        'bg-gray-900/30 text-gray-400'
                      }`}>
                        F
                      </span>
                      <span className={`px-2 py-1 rounded ${
                        stock.signals.sentiment === 'positive' ? 'bg-green-900/30 text-green-400' :
                        stock.signals.sentiment === 'negative' ? 'bg-red-900/30 text-red-400' :
                        'bg-gray-900/30 text-gray-400'
                      }`}>
                        S
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-sm">
                    {stock.sector}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
