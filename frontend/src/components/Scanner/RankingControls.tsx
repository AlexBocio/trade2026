/**
 * Ranking Controls Component
 * Ranking and output options
 */

import React from 'react';
import type { Ranking, OutputOptions } from '../../types/scanner';

interface RankingControlsProps {
  ranking: Ranking;
  output: OutputOptions;
  onChange: (ranking: Ranking, output: OutputOptions) => void;
}

const SORT_OPTIONS = [
  { value: 'composite_score', label: 'Composite Score' },
  { value: 'market_cap', label: 'Market Cap' },
  { value: 'volume', label: 'Volume' },
  { value: 'return_20d', label: '20-day Return' },
  { value: 'return_60d', label: '60-day Return' },
  { value: 'volatility', label: 'Volatility' },
  { value: 'momentum', label: 'Momentum Factor' },
  { value: 'value', label: 'Value Factor' },
  { value: 'quality', label: 'Quality Factor' },
];

export default function RankingControls({ ranking, output, onChange }: RankingControlsProps) {
  return (
    <div className="p-4 space-y-6">
      {/* Ranking Options */}
      <div className="bg-gray-750 rounded-lg p-4">
        <h3 className="text-white font-semibold mb-4">📊 Ranking Options</h3>

        <div className="space-y-4">
          {/* Primary Sort */}
          <div>
            <label className="text-sm text-gray-400 mb-2 block">Primary Sort By</label>
            <select
              value={ranking.primary_sort}
              onChange={(e) =>
                onChange(
                  { ...ranking, primary_sort: e.target.value },
                  output
                )
              }
              className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Secondary Sort */}
          <div>
            <label className="text-sm text-gray-400 mb-2 block">Secondary Sort By</label>
            <select
              value={ranking.secondary_sort}
              onChange={(e) =>
                onChange(
                  { ...ranking, secondary_sort: e.target.value },
                  output
                )
              }
              className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Sort Order */}
          <div>
            <label className="text-sm text-gray-400 mb-2 block">Sort Order</label>
            <div className="flex gap-2">
              <button
                onClick={() =>
                  onChange(
                    { ...ranking, sort_order: 'desc' },
                    output
                  )
                }
                className={`flex-1 px-4 py-2 rounded font-medium transition-colors ${
                  ranking.sort_order === 'desc'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                ↓ Descending (High to Low)
              </button>
              <button
                onClick={() =>
                  onChange(
                    { ...ranking, sort_order: 'asc' },
                    output
                  )
                }
                className={`flex-1 px-4 py-2 rounded font-medium transition-colors ${
                  ranking.sort_order === 'asc'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                ↑ Ascending (Low to High)
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Output Options */}
      <div className="bg-gray-750 rounded-lg p-4">
        <h3 className="text-white font-semibold mb-4">📤 Output Options</h3>

        <div className="space-y-4">
          {/* Max Results */}
          <div>
            <label className="text-sm text-gray-400 mb-2 block">
              Maximum Results
            </label>
            <input
              type="number"
              value={output.max_results}
              onChange={(e) =>
                onChange(ranking, {
                  ...output,
                  max_results: Number(e.target.value),
                })
              }
              min={1}
              max={500}
              step={10}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Min: 1</span>
              <span>Max: 500</span>
            </div>
          </div>

          {/* Include Options */}
          <div className="space-y-2">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={output.include_regime_scores}
                onChange={(e) =>
                  onChange(ranking, {
                    ...output,
                    include_regime_scores: e.target.checked,
                  })
                }
                className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500 focus:ring-offset-gray-800"
              />
              <span className="text-white text-sm">Include regime scores</span>
            </label>

            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={output.include_factor_breakdown}
                onChange={(e) =>
                  onChange(ranking, {
                    ...output,
                    include_factor_breakdown: e.target.checked,
                  })
                }
                className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500 focus:ring-offset-gray-800"
              />
              <span className="text-white text-sm">Include factor breakdown</span>
            </label>
          </div>

          {/* Export Format */}
          <div>
            <label className="text-sm text-gray-400 mb-2 block">Export Format</label>
            <div className="grid grid-cols-3 gap-2">
              {(['json', 'csv', 'excel'] as const).map((format) => (
                <button
                  key={format}
                  onClick={() =>
                    onChange(ranking, {
                      ...output,
                      export_format: format,
                    })
                  }
                  className={`px-3 py-2 rounded font-medium transition-colors ${
                    output.export_format === format
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {format.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Presets */}
      <div className="bg-gray-750 rounded-lg p-4">
        <h3 className="text-white font-semibold mb-3">⚡ Quick Presets</h3>
        <div className="grid grid-cols-2 gap-2">
          <QuickPresetButton
            label="Top 25 by Score"
            onClick={() => {
              onChange(
                { primary_sort: 'composite_score', secondary_sort: 'market_cap', sort_order: 'desc' },
                { ...output, max_results: 25 }
              );
            }}
          />
          <QuickPresetButton
            label="Top 50 Momentum"
            onClick={() => {
              onChange(
                { primary_sort: 'return_60d', secondary_sort: 'composite_score', sort_order: 'desc' },
                { ...output, max_results: 50 }
              );
            }}
          />
          <QuickPresetButton
            label="High Quality Top 100"
            onClick={() => {
              onChange(
                { primary_sort: 'quality', secondary_sort: 'composite_score', sort_order: 'desc' },
                { ...output, max_results: 100 }
              );
            }}
          />
          <QuickPresetButton
            label="All Results"
            onClick={() => {
              onChange(
                ranking,
                { ...output, max_results: 500 }
              );
            }}
          />
        </div>
      </div>
    </div>
  );
}

interface QuickPresetButtonProps {
  label: string;
  onClick: () => void;
}

function QuickPresetButton({ label, onClick }: QuickPresetButtonProps) {
  return (
    <button
      onClick={onClick}
      className="bg-gray-700 hover:bg-gray-600 text-gray-300 text-sm px-3 py-2 rounded transition-colors"
    >
      {label}
    </button>
  );
}
