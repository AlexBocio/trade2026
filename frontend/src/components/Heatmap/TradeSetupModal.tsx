/**
 * Trade Setup Modal
 * Shows detailed trade setup when clicking on a heatmap cell
 */

import React from 'react';
import { X } from 'lucide-react';
import type { CellData } from '../../api/screenerApi';

interface TradeSetupModalProps {
  ticker: string;
  timeframe: string;
  cellData: CellData | null;
  onClose: () => void;
}

export const TradeSetupModal: React.FC<TradeSetupModalProps> = ({
  ticker,
  timeframe,
  cellData,
  onClose
}) => {
  if (!cellData) return null;

  const { predicted_return, confidence, direction, trade_setup } = cellData;
  const isLong = direction === 'long';

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card rounded-lg p-6 max-w-2xl w-full mx-4 border border-dark-border"
        onClick={(e) => e.stopPropagation()}
      >

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white">{ticker}</h2>
            <p className="text-gray-400">Trade Setup - {timeframe}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-dark-border rounded"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Prediction Summary */}
        <div className={`p-4 rounded-lg mb-6 ${
          isLong
            ? 'bg-green-900/20 border border-green-700'
            : 'bg-red-900/20 border border-red-700'
        }`}>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <div className="text-sm text-gray-400 mb-1">Direction</div>
              <div className={`text-2xl font-bold ${
                isLong ? 'text-green-400' : 'text-red-400'
              }`}>
                {trade_setup.action}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">Expected Return</div>
              <div className="text-2xl font-bold text-white">
                {(predicted_return * 100).toFixed(2)}%
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">Confidence</div>
              <div className="text-2xl font-bold text-blue-400">
                {(confidence * 100).toFixed(0)}%
              </div>
            </div>
          </div>
        </div>

        {/* Trade Parameters */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-dark-bg rounded p-4 border border-dark-border">
            <div className="text-sm text-gray-400 mb-1">Entry Price</div>
            <div className="text-xl font-bold text-white">
              ${trade_setup.entry_price.toFixed(2)}
            </div>
          </div>
          <div className="bg-dark-bg rounded p-4 border border-dark-border">
            <div className="text-sm text-gray-400 mb-1">Target Price</div>
            <div className="text-xl font-bold text-green-400">
              ${trade_setup.target_price.toFixed(2)}
            </div>
          </div>
          <div className="bg-dark-bg rounded p-4 border border-dark-border">
            <div className="text-sm text-gray-400 mb-1">Stop Loss</div>
            <div className="text-xl font-bold text-red-400">
              ${trade_setup.stop_loss.toFixed(2)}
            </div>
          </div>
          <div className="bg-dark-bg rounded p-4 border border-dark-border">
            <div className="text-sm text-gray-400 mb-1">Risk/Reward</div>
            <div className="text-xl font-bold text-white">
              1:{trade_setup.risk_reward_ratio.toFixed(2)}
            </div>
          </div>
        </div>

        {/* Position Sizing */}
        <div className="bg-dark-bg rounded p-4 mb-6 border border-dark-border">
          <h3 className="text-white font-semibold mb-3">Position Sizing</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Base Position Size:</span>
              <span className="text-white">{trade_setup.position_size_pct.toFixed(2)}%</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Confidence-Adjusted:</span>
              <span className="text-green-400 font-semibold">
                {trade_setup.confidence_adjusted_size_pct.toFixed(2)}%
              </span>
            </div>
            <div className="text-xs text-gray-500 mt-2">
              Adjust position size based on your risk tolerance and portfolio size
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-3">
          <button className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
            isLong
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-red-600 hover:bg-red-700 text-white'
          }`}>
            Execute {trade_setup.action}
          </button>
          <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-medium transition-colors">
            Add to Watchlist
          </button>
          <button
            onClick={onClose}
            className="px-6 bg-gray-600 hover:bg-gray-500 text-white py-3 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
