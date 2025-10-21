/**
 * Dual-Axis Heatmap Component
 * Multi-timeframe prediction heatmap with SHORT (left) and LONG (right) opportunities
 */

import React, { useState, useCallback } from 'react';
import { TradeSetupModal } from './TradeSetupModal';
import type { HeatmapData } from '../../api/screenerApi';

interface DualAxisHeatmapProps {
  data: HeatmapData;
}

type ColorScale = 'return' | 'confidence' | 'strength';

export const DualAxisHeatmap: React.FC<DualAxisHeatmapProps> = ({ data }) => {
  const [selectedCell, setSelectedCell] = useState<{ticker: string, timeframe: string} | null>(null);
  const [colorScale, setColorScale] = useState<ColorScale>('return');
  const [showModal, setShowModal] = useState(false);

  // Split timeframes into SHORT (left) and LONG (right)
  const zeroIndex = data.timeframes.indexOf('0');
  const shortTimeframes = data.timeframes.slice(0, zeroIndex).reverse();  // Far to near
  const longTimeframes = data.timeframes.slice(zeroIndex + 1);  // Near to far

  // Color mapping
  const getHeatmapColor = useCallback((value: number, confidence: number, strength: number) => {
    if (colorScale === 'return') {
      // Red (negative) to Green (positive)
      const absValue = Math.abs(value);
      const intensity = Math.min(absValue / 0.1, 1);  // Cap at 10%

      if (value > 0) {
        // Green shades for positive returns
        return `rgba(34, 197, 94, ${intensity})`;  // green-500
      } else if (value < 0) {
        // Red shades for negative returns
        return `rgba(239, 68, 68, ${intensity})`;  // red-500
      } else {
        return 'rgba(75, 85, 99, 0.2)';  // gray-600 for neutral
      }
    } else if (colorScale === 'confidence') {
      // Blue intensity based on confidence
      return `rgba(59, 130, 246, ${confidence})`;  // blue-500
    } else {  // strength
      // Yellow to Orange to Red
      const strengthColors = [
        'rgba(75, 85, 99, 0.2)',      // gray for none
        'rgba(251, 191, 36, 0.4)',    // yellow for weak
        'rgba(249, 115, 22, 0.7)',    // orange for moderate
        'rgba(239, 68, 68, 1.0)'      // red for strong
      ];
      return strengthColors[strength] || strengthColors[0];
    }
  }, [colorScale]);

  const handleCellClick = (ticker: string, timeframe: string) => {
    setSelectedCell({ ticker, timeframe });
    setShowModal(true);
  };

  return (
    <div className="dual-axis-heatmap bg-dark-card rounded-lg p-6 border border-dark-border">

      {/* Controls */}
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">
          Multi-Timeframe Prediction Heatmap
        </h2>

        <div className="flex items-center space-x-4">
          <label className="text-sm text-gray-400">Color By:</label>
          <select
            className="bg-dark-bg text-white border border-dark-border rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
            value={colorScale}
            onChange={(e) => setColorScale(e.target.value as ColorScale)}
          >
            <option value="return">Predicted Return</option>
            <option value="confidence">Confidence</option>
            <option value="strength">Signal Strength</option>
          </select>
        </div>
      </div>

      {/* Heatmap Container */}
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">

          {/* Header Row - X Axis Labels */}
          <div className="flex">
            {/* Ticker column header */}
            <div className="w-20 flex-shrink-0 border-r-2 border-gray-600" />

            {/* SHORT side header */}
            <div className="flex-1 text-center border-r-2 border-gray-600 py-2 bg-red-900/10">
              <div className="text-red-400 font-semibold text-sm">
                SHORT OPPORTUNITIES
              </div>
              <div className="text-xs text-gray-500">
                ← Expected Price Declines
              </div>
            </div>

            {/* Zero column */}
            <div className="w-12 flex-shrink-0 border-r-2 border-gray-600" />

            {/* LONG side header */}
            <div className="flex-1 text-center py-2 bg-green-900/10">
              <div className="text-green-400 font-semibold text-sm">
                LONG OPPORTUNITIES
              </div>
              <div className="text-xs text-gray-500">
                Expected Price Gains →
              </div>
            </div>
          </div>

          {/* Timeframe Labels Row */}
          <div className="flex text-xs text-gray-400 border-b border-gray-700 pb-1">
            {/* Ticker column */}
            <div className="w-20 flex-shrink-0 border-r-2 border-gray-600 font-semibold text-white py-2 px-2">
              Ticker
            </div>

            {/* SHORT timeframes (right to left: near to far) */}
            {shortTimeframes.map((tf, idx) => (
              <div
                key={`short-${idx}`}
                className="flex-1 text-center border-r border-gray-700 text-red-400 py-2"
                style={{ minWidth: '50px' }}
              >
                {tf}
              </div>
            ))}

            {/* Zero column */}
            <div className="w-12 flex-shrink-0 border-r-2 border-gray-600 text-center text-gray-500 py-2">
              NOW
            </div>

            {/* LONG timeframes (left to right: near to far) */}
            {longTimeframes.map((tf, idx) => (
              <div
                key={`long-${idx}`}
                className="flex-1 text-center border-r border-gray-700 text-green-400 py-2"
                style={{ minWidth: '50px' }}
              >
                {tf}
              </div>
            ))}
          </div>

          {/* Data Rows */}
          {data.tickers.map((ticker, rowIdx) => (
            <div key={ticker} className="flex border-b border-gray-700 hover:bg-dark-bg/50 transition-colors">

              {/* Ticker Label */}
              <div className="w-20 flex-shrink-0 border-r-2 border-gray-600 py-3 px-2 font-mono font-bold text-white flex items-center">
                {ticker}
              </div>

              {/* SHORT cells */}
              {shortTimeframes.map((tf, colIdx) => {
                const originalColIdx = data.timeframes.indexOf(tf);
                const value = data.matrix[rowIdx][originalColIdx];
                const confidence = data.confidence_matrix[rowIdx][originalColIdx];
                const strength = data.strength_matrix[rowIdx][originalColIdx];
                const bgColor = getHeatmapColor(value, confidence, strength);

                return (
                  <div
                    key={`short-${colIdx}`}
                    className="flex-1 border-r border-gray-700 cursor-pointer hover:opacity-80 transition-opacity"
                    style={{
                      backgroundColor: bgColor,
                      minWidth: '50px',
                      minHeight: '50px'
                    }}
                    onClick={() => handleCellClick(ticker, tf)}
                    title={`${ticker} ${tf}: ${(value * 100).toFixed(2)}%`}
                  >
                    <div className="h-full flex items-center justify-center text-xs font-medium text-white drop-shadow-md">
                      {value !== 0 && Math.abs(value) > 0.005 ? `${(value * 100).toFixed(1)}%` : ''}
                    </div>
                  </div>
                );
              })}

              {/* Zero column */}
              <div className="w-12 flex-shrink-0 border-r-2 border-gray-600 bg-dark-bg" />

              {/* LONG cells */}
              {longTimeframes.map((tf, colIdx) => {
                const originalColIdx = data.timeframes.indexOf(tf);
                const value = data.matrix[rowIdx][originalColIdx];
                const confidence = data.confidence_matrix[rowIdx][originalColIdx];
                const strength = data.strength_matrix[rowIdx][originalColIdx];
                const bgColor = getHeatmapColor(value, confidence, strength);

                return (
                  <div
                    key={`long-${colIdx}`}
                    className="flex-1 border-r border-gray-700 cursor-pointer hover:opacity-80 transition-opacity"
                    style={{
                      backgroundColor: bgColor,
                      minWidth: '50px',
                      minHeight: '50px'
                    }}
                    onClick={() => handleCellClick(ticker, tf)}
                    title={`${ticker} ${tf}: ${(value * 100).toFixed(2)}%`}
                  >
                    <div className="h-full flex items-center justify-center text-xs font-medium text-white drop-shadow-md">
                      {value !== 0 && Math.abs(value) > 0.005 ? `${(value * 100).toFixed(1)}%` : ''}
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-6 p-4 bg-dark-bg rounded border border-dark-border">
        <div className="text-sm font-medium text-white mb-3">Legend</div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-gray-300">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 rounded" />
            <span>Strong Long Signal (5%+)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 opacity-50 rounded" />
            <span>Moderate Long (2-5%)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500 rounded" />
            <span>Strong Short Signal (5%+)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500 opacity-50 rounded" />
            <span>Moderate Short (2-5%)</span>
          </div>
        </div>
      </div>

      {/* Trade Setup Modal */}
      {showModal && selectedCell && (
        <TradeSetupModal
          ticker={selectedCell.ticker}
          timeframe={selectedCell.timeframe}
          cellData={data.cell_data[selectedCell.ticker]?.[selectedCell.timeframe]}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
};
