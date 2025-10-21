/**
 * Stock Details Panel - Shows detailed info and quick trade buttons
 */

import { useNavigate } from 'react-router-dom';
import { TrendingUp, DollarSign, BarChart3, Target, Award } from 'lucide-react';
import type { Stock } from '../../../services/mock-data/scanner-data';
import { formatCurrency, getColorClass } from '../../../utils/helpers';

interface StockDetailsPanelProps {
  stock: Stock;
}

export function StockDetailsPanel({ stock }: StockDetailsPanelProps) {
  const navigate = useNavigate();

  const handleBuy = () => {
    navigate(`/trading?symbol=${stock.symbol}&action=buy`);
  };

  const handleSell = () => {
    navigate(`/trading?symbol=${stock.symbol}&action=sell`);
  };

  const formatMarketCap = (cap: number): string => {
    if (cap >= 1000000000) return `$${(cap / 1000000000).toFixed(2)}B`;
    if (cap >= 1000000) return `$${(cap / 1000000).toFixed(2)}M`;
    return `$${(cap / 1000).toFixed(2)}K`;
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">{stock.symbol}</h2>
          <p className="text-sm text-gray-400 mt-1">{stock.companyName}</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-white">{formatCurrency(stock.price)}</div>
          <div className={`text-sm font-semibold ${getColorClass(stock.change)}`}>
            {stock.change > 0 ? '+' : ''}
            {stock.change.toFixed(2)}% ({stock.change > 0 ? '+' : ''}
            {formatCurrency(stock.changeDollar)})
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-4">
        <div className="p-3 bg-gray-800 rounded">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign size={16} className="text-blue-400" />
            <span className="text-xs text-gray-500">Market Cap</span>
          </div>
          <div className="text-lg font-semibold text-white">
            {formatMarketCap(stock.marketCap)}
          </div>
        </div>

        <div className="p-3 bg-gray-800 rounded">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 size={16} className="text-purple-400" />
            <span className="text-xs text-gray-500">Volume</span>
          </div>
          <div className="text-lg font-semibold text-white">
            {(stock.volume / 1000000).toFixed(2)}M
          </div>
          <div className="text-xs text-gray-500">
            {stock.volumeSurge.toFixed(1)}x avg
          </div>
        </div>

        <div className="p-3 bg-gray-800 rounded">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={16} className="text-green-400" />
            <span className="text-xs text-gray-500">Momentum</span>
          </div>
          <div className="text-lg font-semibold text-white">
            {stock.momentumScore.toFixed(0)}/100
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2 mt-1">
            <div
              className={`h-2 rounded-full ${
                stock.momentumScore > 85
                  ? 'bg-green-500'
                  : stock.momentumScore > 70
                  ? 'bg-yellow-500'
                  : 'bg-orange-500'
              }`}
              style={{ width: `${stock.momentumScore}%` }}
            />
          </div>
        </div>

        <div className="p-3 bg-gray-800 rounded">
          <div className="flex items-center gap-2 mb-2">
            <Target size={16} className="text-yellow-400" />
            <span className="text-xs text-gray-500">Liquidity</span>
          </div>
          <div className="text-lg font-semibold text-white">
            {(stock.liquidity / 1000).toFixed(0)}K
          </div>
        </div>
      </div>

      {/* Pattern & Catalyst */}
      <div className="grid grid-cols-2 gap-4">
        <div className="p-3 bg-blue-900/20 border border-blue-700 rounded">
          <div className="flex items-center gap-2 mb-2">
            <Award size={16} className="text-blue-400" />
            <span className="text-xs text-gray-500">Pattern</span>
          </div>
          <div className="text-sm font-semibold text-white">{stock.pattern}</div>
          <div className="text-xs text-gray-400 mt-1">
            {stock.patternConfidence.toFixed(0)}% confidence
          </div>
        </div>

        <div
          className={`p-3 rounded border ${
            stock.catalyst
              ? 'bg-green-900/20 border-green-700'
              : 'bg-gray-800 border-gray-700'
          }`}
        >
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={16} className={stock.catalyst ? 'text-green-400' : 'text-gray-500'} />
            <span className="text-xs text-gray-500">Catalyst</span>
          </div>
          <div className="text-sm font-semibold text-white">
            {stock.catalyst || 'None'}
          </div>
          {stock.catalystType && (
            <div className="text-xs text-gray-400 mt-1 capitalize">{stock.catalystType}</div>
          )}
        </div>
      </div>

      {/* Additional Info */}
      <div className="p-3 bg-gray-800 rounded">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Sector:</span>
            <span className="text-white ml-2">{stock.sector}</span>
          </div>
          <div>
            <span className="text-gray-500">Breakout:</span>
            <span className="text-white ml-2 capitalize">{stock.breakoutType.replace('_', ' ')}</span>
          </div>
        </div>
      </div>

      {/* Quick Trade Buttons */}
      <div className="grid grid-cols-2 gap-3 pt-2">
        <button
          onClick={handleBuy}
          className="px-4 py-3 bg-green-700 hover:bg-green-600 text-white font-semibold rounded transition-colors"
        >
          Quick Buy
        </button>
        <button
          onClick={handleSell}
          className="px-4 py-3 bg-red-700 hover:bg-red-600 text-white font-semibold rounded transition-colors"
        >
          Quick Sell
        </button>
      </div>
    </div>
  );
}
