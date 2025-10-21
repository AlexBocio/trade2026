/**
 * Stock Card Component
 * Displays individual stock with key metrics and signals
 */

import React from 'react';
import { TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';
import type { StockResult } from '../../api/screenerApi';

interface StockCardProps {
  stock: StockResult;
  onViewDetails?: (ticker: string) => void;
}

export const StockCard: React.FC<StockCardProps> = ({ stock, onViewDetails }) => {
  const isPositive = stock.change_pct >= 0;

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-400 bg-green-900/30';
      case 'medium': return 'text-yellow-400 bg-yellow-900/30';
      case 'high': return 'text-red-400 bg-red-900/30';
      default: return 'text-gray-400 bg-gray-900/30';
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'bullish':
      case 'strong':
      case 'positive':
        return 'text-green-400';
      case 'bearish':
      case 'weak':
      case 'negative':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-4 hover:border-blue-500 transition cursor-pointer">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold text-white font-mono">{stock.ticker}</h3>
            <span className={`text-sm px-2 py-0.5 rounded ${getRiskColor(stock.risk_level)}`}>
              {stock.risk_level}
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-1">{stock.company_name}</p>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold text-white">${stock.price.toFixed(2)}</div>
          <div className={`text-sm flex items-center justify-end gap-1 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
            {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            {isPositive ? '+' : ''}{stock.change_pct.toFixed(2)}%
          </div>
        </div>
      </div>

      {/* Composite Score */}
      <div className="mb-3">
        <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
          <span>Composite Score</span>
          <span className="font-bold text-white">{stock.composite_score}/100</span>
        </div>
        <div className="w-full bg-dark-bg rounded-full h-2">
          <div
            className={`h-2 rounded-full ${
              stock.composite_score >= 80 ? 'bg-green-500' :
              stock.composite_score >= 60 ? 'bg-blue-500' :
              stock.composite_score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${stock.composite_score}%` }}
          />
        </div>
      </div>

      {/* Factor Scores - Mini Bars */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        {Object.entries(stock.factor_scores).slice(0, 6).map(([factor, score]) => (
          <div key={factor} className="text-xs">
            <div className="text-gray-400 capitalize mb-1">{factor}</div>
            <div className="w-full bg-dark-bg rounded h-1.5">
              <div
                className="h-1.5 rounded bg-blue-400"
                style={{ width: `${score}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Signals */}
      <div className="grid grid-cols-3 gap-2 mb-3 text-xs">
        <div className="text-center">
          <div className="text-gray-500 mb-1">Technical</div>
          <div className={`font-semibold capitalize ${getSignalColor(stock.signals.technical)}`}>
            {stock.signals.technical}
          </div>
        </div>
        <div className="text-center border-x border-dark-border">
          <div className="text-gray-500 mb-1">Fundamental</div>
          <div className={`font-semibold capitalize ${getSignalColor(stock.signals.fundamental)}`}>
            {stock.signals.fundamental}
          </div>
        </div>
        <div className="text-center">
          <div className="text-gray-500 mb-1">Sentiment</div>
          <div className={`font-semibold capitalize ${getSignalColor(stock.signals.sentiment)}`}>
            {stock.signals.sentiment}
          </div>
        </div>
      </div>

      {/* Catalyst (if exists) */}
      {stock.catalyst && (
        <div className="mb-3 p-2 bg-blue-900/20 border border-blue-700 rounded text-xs">
          <span className="text-blue-400 font-semibold">Catalyst: </span>
          <span className="text-gray-300">{stock.catalyst}</span>
        </div>
      )}

      {/* Sector/Industry */}
      <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
        <span>{stock.sector}</span>
        <span className="text-gray-600">|</span>
        <span>{stock.industry}</span>
      </div>

      {/* View Details Button */}
      <button
        onClick={() => onViewDetails?.(stock.ticker)}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm py-2 rounded flex items-center justify-center gap-2 transition"
      >
        View Details
        <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  );
};
