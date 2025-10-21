/**
 * Market Regimes Card Component
 * Displays regimes for major market indices (SPY, QQQ, IWM, DIA)
 */

import React from 'react';
import type { MarketRegimes } from '../../types/regime';
import RegimeBadge from './RegimeBadge';
import RegimeStrengthBar from './RegimeStrengthBar';

interface MarketRegimesCardProps {
  data: MarketRegimes | null;
}

export default function MarketRegimesCard({ data }: MarketRegimesCardProps) {
  if (!data) {
    return (
      <div className="bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">📈 Market Regimes</h2>
        <div className="text-gray-400">Loading market data...</div>
      </div>
    );
  }

  const markets = [
    { symbol: 'SPY', name: 'S&P 500', data: data.SPY },
    { symbol: 'QQQ', name: 'Nasdaq-100', data: data.QQQ },
    { symbol: 'IWM', name: 'Russell 2000', data: data.IWM },
    { symbol: 'DIA', name: 'Dow Jones', data: data.DIA },
  ];

  // Identify leader (highest strength)
  const leader = markets.reduce((prev, curr) => {
    if (!prev.data || !curr.data) return prev;
    return curr.data.regime_strength > prev.data.regime_strength ? curr : prev;
  });

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
      <h2 className="text-xl font-bold text-white mb-4">📈 Market Regimes</h2>

      <div className="space-y-4">
        {markets.map((market) => {
          if (!market.data) {
            return (
              <div key={market.symbol} className="bg-gray-750 rounded-lg p-4">
                <div className="text-white font-bold text-lg">{market.symbol}</div>
                <div className="text-sm text-gray-500 mt-2">No data available</div>
              </div>
            );
          }

          const isLeader = market.symbol === leader.symbol;

          return (
            <div
              key={market.symbol}
              className={`bg-gray-750 rounded-lg p-4 ${
                isLeader ? 'ring-2 ring-green-500' : ''
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-white font-bold text-lg">{market.symbol}</span>
                    {isLeader && (
                      <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded">
                        LEADING
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-400">{market.name}</div>
                </div>

                <RegimeBadge regime={market.data.primary_regime} large />
              </div>

              {/* Regime Strength Bar */}
              <div className="mb-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-400">Strength:</span>
                  <span className="text-xs text-white">
                    {market.data.regime_strength.toFixed(1)}/10
                  </span>
                </div>
                <RegimeStrengthBar strength={market.data.regime_strength} max={10} />
              </div>

              {/* Key Characteristics */}
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div>
                  <div className="text-gray-400">Trend</div>
                  <div className="text-white font-semibold">
                    {market.data.characteristics.trend_strength.toFixed(0)}
                  </div>
                </div>
                <div>
                  <div className="text-gray-400">Volatility</div>
                  <div className="text-white font-semibold">
                    {(market.data.characteristics.volatility * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div className="text-gray-400">RSI</div>
                  <div className="text-white font-semibold">
                    {market.data.characteristics.rsi.toFixed(0)}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
