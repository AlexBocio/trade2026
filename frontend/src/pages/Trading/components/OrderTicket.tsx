/**
 * Order Ticket Component - Advanced order entry with risk metrics
 */

import { useState, useEffect } from 'react';
import { Calculator, AlertCircle } from 'lucide-react';
import { useTradingStore } from '../../../store/useTradingStore';

interface OrderTicketProps {
  symbol: string;
  currentPrice: number;
}

export function OrderTicket({ symbol, currentPrice }: OrderTicketProps) {
  const { submitOrder, isLoading } = useTradingStore();
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [orderType, setOrderType] = useState<'market' | 'limit' | 'stop'>('limit');
  const [quantity, setQuantity] = useState(1000);
  const [limitPrice, setLimitPrice] = useState(currentPrice);
  const [stopLoss, setStopLoss] = useState(currentPrice * 0.93); // -7%
  const [profitTarget, setProfitTarget] = useState(currentPrice * 1.2); // +20%
  const [timeInForce, setTimeInForce] = useState<'DAY' | 'GTC' | 'IOC'>('DAY');

  // Update limit price when currentPrice changes
  useEffect(() => {
    setLimitPrice(currentPrice);
    setStopLoss(currentPrice * 0.93);
    setProfitTarget(currentPrice * 1.2);
  }, [currentPrice]);

  // Auto-calculate risk metrics
  const positionValue = limitPrice * quantity;
  const riskAmount = Math.abs((limitPrice - stopLoss) * quantity);
  const rewardAmount = Math.abs((profitTarget - limitPrice) * quantity);
  const riskRewardRatio = riskAmount > 0 ? rewardAmount / riskAmount : 0;
  const accountValue = 50000; // From store or config
  const positionPct = (positionValue / accountValue) * 100;
  const riskPct = (riskAmount / accountValue) * 100;

  const handleSubmit = async () => {
    const order = {
      symbol,
      side,
      orderType,
      quantity,
      limitPrice: orderType === 'limit' ? limitPrice : undefined,
      stopPrice: orderType === 'stop' ? limitPrice : undefined,
      stopLoss,
      profitTarget,
      timeInForce,
    };

    await submitOrder(order);
  };

  return (
    <div className="w-80 bg-gray-800 border-r border-gray-700 p-4 overflow-y-auto">
      <h2 className="text-xl font-bold mb-4">Order Entry</h2>

      {/* Buy/Sell Tabs */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <button
          onClick={() => setSide('buy')}
          className={`py-3 rounded-lg font-semibold transition ${
            side === 'buy'
              ? 'bg-green-600 text-white'
              : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
          }`}
        >
          BUY
        </button>
        <button
          onClick={() => setSide('sell')}
          className={`py-3 rounded-lg font-semibold transition ${
            side === 'sell'
              ? 'bg-red-600 text-white'
              : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
          }`}
        >
          SELL
        </button>
      </div>

      {/* Symbol (read-only) */}
      <div className="mb-4">
        <label className="block text-sm text-gray-400 mb-2">Symbol</label>
        <input
          type="text"
          value={symbol}
          readOnly
          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white font-mono"
        />
      </div>

      {/* Order Type */}
      <div className="mb-4">
        <label className="block text-sm text-gray-400 mb-2">Order Type</label>
        <select
          value={orderType}
          onChange={(e) => setOrderType(e.target.value as any)}
          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white"
        >
          <option value="market">Market</option>
          <option value="limit">Limit</option>
          <option value="stop">Stop</option>
        </select>
      </div>

      {/* Quantity */}
      <div className="mb-4">
        <label className="block text-sm text-gray-400 mb-2">Quantity</label>
        <input
          type="number"
          value={quantity}
          onChange={(e) => setQuantity(Number(e.target.value))}
          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white font-mono"
        />
      </div>

      {/* Limit Price (if limit order) */}
      {orderType === 'limit' && (
        <div className="mb-4">
          <label className="block text-sm text-gray-400 mb-2">Limit Price</label>
          <input
            type="number"
            step="0.01"
            value={limitPrice}
            onChange={(e) => setLimitPrice(Number(e.target.value))}
            className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white font-mono"
          />
        </div>
      )}

      {/* Stop Loss */}
      <div className="mb-4">
        <label className="block text-sm text-gray-400 mb-2">
          Stop Loss (-{(((limitPrice - stopLoss) / limitPrice) * 100).toFixed(1)}%)
        </label>
        <input
          type="number"
          step="0.01"
          value={stopLoss.toFixed(2)}
          onChange={(e) => setStopLoss(Number(e.target.value))}
          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white font-mono"
        />
      </div>

      {/* Profit Target */}
      <div className="mb-4">
        <label className="block text-sm text-gray-400 mb-2">
          Profit Target (+{(((profitTarget - limitPrice) / limitPrice) * 100).toFixed(1)}%)
        </label>
        <input
          type="number"
          step="0.01"
          value={profitTarget.toFixed(2)}
          onChange={(e) => setProfitTarget(Number(e.target.value))}
          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white font-mono"
        />
      </div>

      {/* Time in Force */}
      <div className="mb-4">
        <label className="block text-sm text-gray-400 mb-2">Time in Force</label>
        <select
          value={timeInForce}
          onChange={(e) => setTimeInForce(e.target.value as any)}
          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white"
        >
          <option value="DAY">Day</option>
          <option value="GTC">Good Till Cancel</option>
          <option value="IOC">Immediate or Cancel</option>
        </select>
      </div>

      {/* Risk Metrics */}
      <div className="bg-gray-900 rounded-lg p-4 mb-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Position Size</span>
          <span className="font-mono">
            ${positionValue.toFixed(0)} ({positionPct.toFixed(1)}%)
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Risk Amount</span>
          <span className="font-mono text-red-400">
            ${riskAmount.toFixed(0)} ({riskPct.toFixed(2)}%)
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Reward Amount</span>
          <span className="font-mono text-green-400">${rewardAmount.toFixed(0)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Risk/Reward</span>
          <span
            className={`font-mono font-bold ${
              riskRewardRatio >= 2 ? 'text-green-400' : 'text-yellow-400'
            }`}
          >
            {riskRewardRatio.toFixed(2)}:1
          </span>
        </div>
      </div>

      {/* Risk Warning (if risk too high) */}
      {riskPct > 2.5 && (
        <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-3 mb-4 flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-yellow-200">
            Warning: This trade risks {riskPct.toFixed(2)}% of your account. Consider reducing
            position size.
          </div>
        </div>
      )}

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={isLoading}
        className={`w-full py-4 rounded-lg font-bold text-lg transition ${
          side === 'buy'
            ? 'bg-green-600 hover:bg-green-700'
            : 'bg-red-600 hover:bg-red-700'
        } disabled:bg-gray-700 disabled:cursor-not-allowed`}
      >
        {isLoading
          ? 'Submitting...'
          : `${side === 'buy' ? '🚀 BUY' : '📉 SELL'} ${quantity} @ $${limitPrice.toFixed(2)}`}
      </button>

      {/* Position Size Calculator */}
      <button className="w-full mt-2 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm flex items-center justify-center gap-2 transition">
        <Calculator className="w-4 h-4" />
        Position Size Calculator
      </button>
    </div>
  );
}
