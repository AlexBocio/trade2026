/**
 * Advanced Order Ticket - Support for advanced order types
 */

import { useState } from 'react';
import { X, Info } from 'lucide-react';

type OrderType =
  | 'market'
  | 'limit'
  | 'stop'
  | 'stop_limit'
  | 'bracket'
  | 'oco'
  | 'trailing_stop'
  | 'iceberg';

interface AdvancedOrderTicketProps {
  symbol: string;
  currentPrice: number;
  onClose: () => void;
  onSubmit: (order: any) => void;
}

export function AdvancedOrderTicket({ symbol, currentPrice, onClose, onSubmit }: AdvancedOrderTicketProps) {
  const [orderType, setOrderType] = useState<OrderType>('market');
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [quantity, setQuantity] = useState<number>(100);
  const [limitPrice, setLimitPrice] = useState<number>(currentPrice);
  const [stopPrice, setStopPrice] = useState<number>(currentPrice * 0.95);

  // Bracket order fields
  const [profitTarget, setProfitTarget] = useState<number>(currentPrice * 1.05);
  const [stopLoss, setStopLoss] = useState<number>(currentPrice * 0.95);

  // OCO fields
  const [ocoPrice1, setOcoPrice1] = useState<number>(currentPrice * 1.05);
  const [ocoPrice2, setOcoPrice2] = useState<number>(currentPrice * 0.95);

  // Trailing stop fields
  const [trailAmount, setTrailAmount] = useState<number>(0.50);
  const [trailType, setTrailType] = useState<'dollar' | 'percent'>('dollar');

  // Iceberg fields
  const [displaySize, setDisplaySize] = useState<number>(10);

  const handleSubmit = () => {
    const baseOrder = {
      symbol,
      side,
      quantity,
      type: orderType,
    };

    let order;

    switch (orderType) {
      case 'bracket':
        order = {
          ...baseOrder,
          entry: { type: 'limit', price: limitPrice },
          profitTarget: { type: 'limit', price: profitTarget },
          stopLoss: { type: 'stop', price: stopLoss },
        };
        break;

      case 'oco':
        order = {
          ...baseOrder,
          orders: [
            { type: 'limit', price: ocoPrice1 },
            { type: 'stop', price: ocoPrice2 },
          ],
        };
        break;

      case 'trailing_stop':
        order = {
          ...baseOrder,
          trailAmount,
          trailType,
        };
        break;

      case 'iceberg':
        order = {
          ...baseOrder,
          totalQuantity: quantity,
          displaySize,
        };
        break;

      default:
        order = {
          ...baseOrder,
          limitPrice: orderType === 'limit' || orderType === 'stop_limit' ? limitPrice : undefined,
          stopPrice: orderType === 'stop' || orderType === 'stop_limit' ? stopPrice : undefined,
        };
    }

    onSubmit(order);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-dark-card border border-dark-border rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Advanced Order - {symbol}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Order Type Selection */}
        <div className="mb-6">
          <label className="block text-sm text-gray-400 mb-2">Order Type</label>
          <select
            value={orderType}
            onChange={(e) => setOrderType(e.target.value as OrderType)}
            className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
          >
            <option value="market">Market Order</option>
            <option value="limit">Limit Order</option>
            <option value="stop">Stop Order</option>
            <option value="stop_limit">Stop-Limit Order</option>
            <option value="bracket">Bracket Order (Entry + Target + Stop)</option>
            <option value="oco">OCO (One-Cancels-Other)</option>
            <option value="trailing_stop">Trailing Stop</option>
            <option value="iceberg">Iceberg Order</option>
          </select>
        </div>

        {/* Side Selection */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <button
            onClick={() => setSide('buy')}
            className={`py-3 rounded-lg font-semibold transition ${
              side === 'buy'
                ? 'bg-green-600 text-white'
                : 'bg-dark-border text-gray-400 hover:bg-gray-700'
            }`}
          >
            BUY
          </button>
          <button
            onClick={() => setSide('sell')}
            className={`py-3 rounded-lg font-semibold transition ${
              side === 'sell'
                ? 'bg-red-600 text-white'
                : 'bg-dark-border text-gray-400 hover:bg-gray-700'
            }`}
          >
            SELL
          </button>
        </div>

        {/* Quantity */}
        <div className="mb-6">
          <label className="block text-sm text-gray-400 mb-2">Quantity</label>
          <input
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(Number(e.target.value))}
            className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
          />
        </div>

        {/* Conditional Fields Based on Order Type */}
        {orderType === 'bracket' && (
          <>
            <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4 mb-4">
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-semibold text-blue-400">Bracket Order</span>
              </div>
              <p className="text-sm text-gray-300">
                Places 3 orders simultaneously: entry, profit target, and stop loss. When one executes, the others are cancelled.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-6">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Entry Price</label>
                <input
                  type="number"
                  step="0.01"
                  value={limitPrice}
                  onChange={(e) => setLimitPrice(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Profit Target</label>
                <input
                  type="number"
                  step="0.01"
                  value={profitTarget}
                  onChange={(e) => setProfitTarget(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-dark-bg border border-green-700 rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Stop Loss</label>
                <input
                  type="number"
                  step="0.01"
                  value={stopLoss}
                  onChange={(e) => setStopLoss(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-dark-bg border border-red-700 rounded-lg text-white"
                />
              </div>
            </div>
          </>
        )}

        {orderType === 'oco' && (
          <>
            <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4 mb-4">
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-semibold text-blue-400">OCO Order</span>
              </div>
              <p className="text-sm text-gray-300">
                One-Cancels-Other: Places two orders. When one executes, the other is automatically cancelled.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Limit Price</label>
                <input
                  type="number"
                  step="0.01"
                  value={ocoPrice1}
                  onChange={(e) => setOcoPrice1(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Stop Price</label>
                <input
                  type="number"
                  step="0.01"
                  value={ocoPrice2}
                  onChange={(e) => setOcoPrice2(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                />
              </div>
            </div>
          </>
        )}

        {orderType === 'trailing_stop' && (
          <>
            <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4 mb-4">
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-semibold text-blue-400">Trailing Stop</span>
              </div>
              <p className="text-sm text-gray-300">
                Stop loss that follows the price. Moves up as price increases, but never moves down.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Trail Amount</label>
                <input
                  type="number"
                  step="0.01"
                  value={trailAmount}
                  onChange={(e) => setTrailAmount(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Trail Type</label>
                <select
                  value={trailType}
                  onChange={(e) => setTrailType(e.target.value as 'dollar' | 'percent')}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                >
                  <option value="dollar">Dollar ($)</option>
                  <option value="percent">Percent (%)</option>
                </select>
              </div>
            </div>
          </>
        )}

        {orderType === 'iceberg' && (
          <>
            <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4 mb-4">
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-semibold text-blue-400">Iceberg Order</span>
              </div>
              <p className="text-sm text-gray-300">
                Hide large orders by only displaying a small portion at a time. Useful for avoiding market impact.
              </p>
            </div>

            <div className="mb-6">
              <label className="block text-sm text-gray-400 mb-2">Display Size (visible quantity)</label>
              <input
                type="number"
                value={displaySize}
                onChange={(e) => setDisplaySize(Number(e.target.value))}
                className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              />
              <p className="text-xs text-gray-500 mt-1">
                Total: {quantity} shares, Display: {displaySize} shares at a time
              </p>
            </div>
          </>
        )}

        {/* Standard limit/stop fields for simple orders */}
        {(orderType === 'limit' || orderType === 'stop_limit') && (
          <div className="mb-6">
            <label className="block text-sm text-gray-400 mb-2">Limit Price</label>
            <input
              type="number"
              step="0.01"
              value={limitPrice}
              onChange={(e) => setLimitPrice(Number(e.target.value))}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            />
          </div>
        )}

        {(orderType === 'stop' || orderType === 'stop_limit') && (
          <div className="mb-6">
            <label className="block text-sm text-gray-400 mb-2">Stop Price</label>
            <input
              type="number"
              step="0.01"
              value={stopPrice}
              onChange={(e) => setStopPrice(Number(e.target.value))}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            />
          </div>
        )}

        {/* Submit Buttons */}
        <div className="flex gap-3">
          <button
            onClick={handleSubmit}
            className={`flex-1 py-3 rounded-lg font-semibold transition ${
              side === 'buy'
                ? 'bg-green-600 hover:bg-green-700'
                : 'bg-red-600 hover:bg-red-700'
            }`}
          >
            Place {orderType.replace('_', ' ').toUpperCase()} Order
          </button>
          <button
            onClick={onClose}
            className="px-6 py-3 bg-dark-border hover:bg-gray-700 rounded-lg font-semibold transition"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
