/**
 * Cross-Asset Matrix Component
 * Grid showing all asset class regimes (equities, bonds, commodities)
 */

import React from 'react';
import type { MarketRegimes } from '../../types/regime';
import RegimeBadge from './RegimeBadge';
import RegimeStrengthBar from './RegimeStrengthBar';

interface CrossAssetMatrixProps {
  equities: MarketRegimes | null;
  bonds?: any;
  commodities?: any;
}

interface Asset {
  symbol: string;
  name: string;
  regime: any;
}

function getCrossAssetInterpretation(equities: any, bonds: any, commodities: any): string {
  // Simple interpretation based on equity regimes
  if (!equities) return 'Loading market data...';

  const spyRegime = equities.SPY?.primary_regime;

  if (spyRegime === 'BULL_TRENDING') {
    return 'Risk-on environment: Equities showing strong bullish momentum. Consider growth assets.';
  } else if (spyRegime === 'BEAR_TRENDING') {
    return 'Risk-off environment: Equities under pressure. Consider defensive positioning and bonds.';
  } else if (spyRegime === 'HIGH_VOLATILITY') {
    return 'High volatility regime: Consider hedging positions and reducing leverage.';
  } else if (spyRegime === 'RANGE_BOUND') {
    return 'Choppy market: Consider mean-reversion strategies and range-bound trading.';
  }

  return 'Mixed market conditions: Monitor for regime shifts across asset classes.';
}

export default function CrossAssetMatrix({ equities, bonds, commodities }: CrossAssetMatrixProps) {
  const assetClasses = [
    {
      name: 'Equities',
      assets: [
        { symbol: 'SPY', name: 'S&P 500', regime: equities?.SPY },
        { symbol: 'QQQ', name: 'Nasdaq', regime: equities?.QQQ },
        { symbol: 'IWM', name: 'Small Cap', regime: equities?.IWM },
      ],
    },
    {
      name: 'Bonds',
      assets: [
        { symbol: 'TLT', name: '20Y Treasury', regime: bonds?.TLT },
        { symbol: 'HYG', name: 'High Yield', regime: bonds?.HYG },
      ],
    },
    {
      name: 'Commodities',
      assets: [
        { symbol: 'GLD', name: 'Gold', regime: commodities?.GLD },
        { symbol: 'USO', name: 'Oil', regime: commodities?.USO },
      ],
    },
  ];

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
      <h2 className="text-xl font-bold text-white mb-4">🔀 Cross-Asset Regime Matrix</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {assetClasses.map((assetClass) => (
          <div key={assetClass.name} className="space-y-3">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
              {assetClass.name}
            </h3>

            {assetClass.assets.map((asset: Asset) => (
              <div
                key={asset.symbol}
                className="bg-gray-750 rounded-lg p-4 hover:bg-gray-700 transition-colors cursor-pointer"
              >
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <div className="text-white font-semibold">{asset.symbol}</div>
                    <div className="text-xs text-gray-400">{asset.name}</div>
                  </div>
                  <RegimeBadge regime={asset.regime?.primary_regime} />
                </div>

                {asset.regime && (
                  <div className="mt-3">
                    <div className="text-xs text-gray-400 mb-1">Strength</div>
                    <RegimeStrengthBar strength={asset.regime.regime_strength} max={10} />
                  </div>
                )}

                {!asset.regime && (
                  <div className="text-xs text-gray-500 mt-2">No data available</div>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Overall Cross-Asset Interpretation */}
      <div className="mt-6 pt-6 border-t border-gray-700">
        <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-blue-400 text-2xl">💡</span>
            <span className="text-white font-semibold">Market Interpretation:</span>
          </div>
          <p className="text-gray-300 text-sm">
            {getCrossAssetInterpretation(equities, bonds, commodities)}
          </p>
        </div>
      </div>
    </div>
  );
}
