/**
 * Liquidity Metrics Component
 * Visual display of liquidity compression indicators
 */

import React from 'react';

interface LiquidityMetrics {
  current_spread: number;
  avg_spread_20d: number;
  spread_expansion: number;
  current_volume: number;
  avg_volume_20d: number;
  volume_contraction: number;
  current_atr: number;
  avg_atr_20d: number;
  atr_compression: number;
}

interface LiquidityMetricsProps {
  metrics: LiquidityMetrics;
}

interface CompressionMetric {
  label: string;
  current: string;
  avg: string;
  multiplier: number;
  icon: string;
}

export default function LiquidityMetrics({ metrics }: LiquidityMetricsProps) {
  const compressionMetrics: CompressionMetric[] = [
    {
      label: 'Spread Expansion',
      current: (metrics.current_spread * 100).toFixed(2) + '%',
      avg: (metrics.avg_spread_20d * 100).toFixed(2) + '%',
      multiplier: metrics.spread_expansion,
      icon: '📏',
    },
    {
      label: 'Volume Contraction',
      current: metrics.current_volume.toLocaleString(),
      avg: metrics.avg_volume_20d.toLocaleString(),
      multiplier: metrics.volume_contraction,
      icon: '📊',
    },
    {
      label: 'ATR Compression',
      current: (metrics.current_atr * 100).toFixed(2) + '%',
      avg: (metrics.avg_atr_20d * 100).toFixed(2) + '%',
      multiplier: metrics.atr_compression,
      icon: '📐',
    },
  ];

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
        <span>🌀</span>
        <span>Liquidity Compression Metrics</span>
      </h4>

      <div className="space-y-4">
        {compressionMetrics.map((metric) => (
          <div key={metric.label} className="bg-gray-750 rounded-lg p-3 border border-gray-600">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span>{metric.icon}</span>
                <span className="text-sm text-gray-300">{metric.label}</span>
              </div>
              <span
                className={`text-sm font-bold ${
                  metric.multiplier > 2
                    ? 'text-red-400'
                    : metric.multiplier > 1.5
                    ? 'text-orange-400'
                    : 'text-yellow-400'
                }`}
              >
                {metric.multiplier.toFixed(2)}x
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <div className="text-gray-400 mb-1">Current:</div>
                <div className="text-white font-semibold">{metric.current}</div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">20d Avg:</div>
                <div className="text-white font-semibold">{metric.avg}</div>
              </div>
            </div>

            {/* Visual Bar */}
            <div className="mt-2 bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  metric.multiplier > 2
                    ? 'bg-red-600'
                    : metric.multiplier > 1.5
                    ? 'bg-orange-600'
                    : 'bg-yellow-600'
                }`}
                style={{ width: `${Math.min(metric.multiplier * 20, 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
