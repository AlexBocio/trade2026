/**
 * Filter Controls Component
 * Filters and exclusions (sectors, symbols, market cap, price)
 */

import React, { useState } from 'react';
import type { Filters } from '../../types/scanner';

interface FilterControlsProps {
  filters: Filters;
  onChange: (filters: Filters) => void;
}

const SECTORS = [
  'Technology', 'Healthcare', 'Financials', 'Consumer Discretionary',
  'Communication Services', 'Industrials', 'Consumer Staples', 'Energy',
  'Utilities', 'Real Estate', 'Materials',
];

export default function FilterControls({ filters, onChange }: FilterControlsProps) {
  const [blacklistInput, setBlacklistInput] = useState('');

  const toggleSector = (sector: string) => {
    const isExcluded = filters.sectors.exclude.includes(sector);
    onChange({
      ...filters,
      sectors: {
        exclude: isExcluded
          ? filters.sectors.exclude.filter((s) => s !== sector)
          : [...filters.sectors.exclude, sector],
      },
    });
  };

  const addToBlacklist = () => {
    if (blacklistInput.trim()) {
      const symbols = blacklistInput
        .toUpperCase()
        .split(',')
        .map((s) => s.trim())
        .filter((s) => s && !filters.symbols.blacklist.includes(s));

      onChange({
        ...filters,
        symbols: {
          blacklist: [...filters.symbols.blacklist, ...symbols],
        },
      });
      setBlacklistInput('');
    }
  };

  const removeFromBlacklist = (symbol: string) => {
    onChange({
      ...filters,
      symbols: {
        blacklist: filters.symbols.blacklist.filter((s) => s !== symbol),
      },
    });
  };

  return (
    <div className="p-4 space-y-6">
      {/* Sector Exclusions */}
      <div className="bg-gray-750 rounded-lg p-4">
        <h3 className="text-white font-semibold mb-3">🏭 Sector Exclusions</h3>
        <p className="text-sm text-gray-400 mb-4">
          Select sectors to exclude from scan results
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {SECTORS.map((sector) => {
            const isExcluded = filters.sectors.exclude.includes(sector);
            return (
              <button
                key={sector}
                onClick={() => toggleSector(sector)}
                className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                  isExcluded
                    ? 'bg-red-900/30 text-red-400 border border-red-700'
                    : 'bg-gray-700 text-gray-300 border border-gray-600 hover:bg-gray-600'
                }`}
              >
                {isExcluded && '✕ '}
                {sector}
              </button>
            );
          })}
        </div>
      </div>

      {/* Symbol Blacklist */}
      <div className="bg-gray-750 rounded-lg p-4">
        <h3 className="text-white font-semibold mb-3">🚫 Symbol Blacklist</h3>
        <p className="text-sm text-gray-400 mb-4">
          Exclude specific symbols (comma-separated)
        </p>
        <div className="flex gap-2 mb-3">
          <input
            type="text"
            value={blacklistInput}
            onChange={(e) => setBlacklistInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addToBlacklist()}
            placeholder="AAPL, TSLA, MSFT..."
            className="flex-1 bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={addToBlacklist}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-medium transition-colors"
          >
            Add
          </button>
        </div>
        {filters.symbols.blacklist.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {filters.symbols.blacklist.map((symbol) => (
              <div
                key={symbol}
                className="bg-red-900/30 text-red-400 border border-red-700 px-3 py-1 rounded flex items-center gap-2"
              >
                <span className="font-mono font-semibold">{symbol}</span>
                <button
                  onClick={() => removeFromBlacklist(symbol)}
                  className="text-red-500 hover:text-red-300"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Market Cap Range */}
      <div className="bg-gray-750 rounded-lg p-4">
        <h3 className="text-white font-semibold mb-3">💰 Market Cap Range</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Min (Millions)</label>
            <input
              type="number"
              value={filters.market_cap.min / 1000000}
              onChange={(e) =>
                onChange({
                  ...filters,
                  market_cap: { ...filters.market_cap, min: Number(e.target.value) * 1000000 },
                })
              }
              step={100}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Max (Millions)</label>
            <input
              type="number"
              value={filters.market_cap.max / 1000000}
              onChange={(e) =>
                onChange({
                  ...filters,
                  market_cap: { ...filters.market_cap, max: Number(e.target.value) * 1000000 },
                })
              }
              step={1000}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>
        <QuickFilter
          label="Quick filters:"
          options={[
            { label: 'Micro (<$300M)', min: 0, max: 300000000 },
            { label: 'Small ($300M-$2B)', min: 300000000, max: 2000000000 },
            { label: 'Mid ($2B-$10B)', min: 2000000000, max: 10000000000 },
            { label: 'Large (>$10B)', min: 10000000000, max: 10000000000000 },
          ]}
          onSelect={(min, max) =>
            onChange({ ...filters, market_cap: { min, max } })
          }
        />
      </div>

      {/* Price Range */}
      <div className="bg-gray-750 rounded-lg p-4">
        <h3 className="text-white font-semibold mb-3">💵 Price Range</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Min Price ($)</label>
            <input
              type="number"
              value={filters.price.min}
              onChange={(e) =>
                onChange({
                  ...filters,
                  price: { ...filters.price, min: Number(e.target.value) },
                })
              }
              step={1}
              min={0}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Max Price ($)</label>
            <input
              type="number"
              value={filters.price.max}
              onChange={(e) =>
                onChange({
                  ...filters,
                  price: { ...filters.price, max: Number(e.target.value) },
                })
              }
              step={10}
              className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Minimum Composite Score */}
      <div className="bg-gray-750 rounded-lg p-4">
        <h3 className="text-white font-semibold mb-3">⭐ Minimum Composite Score</h3>
        <input
          type="range"
          value={filters.composite_score.min}
          onChange={(e) =>
            onChange({
              ...filters,
              composite_score: { min: Number(e.target.value) },
            })
          }
          min={0}
          max={100}
          step={5}
          className="w-full"
        />
        <div className="flex justify-between text-sm mt-2">
          <span className="text-gray-400">0 (show all)</span>
          <span className="text-white font-semibold">{filters.composite_score.min}</span>
          <span className="text-gray-400">100 (best only)</span>
        </div>
      </div>
    </div>
  );
}

interface QuickFilterProps {
  label: string;
  options: Array<{ label: string; min: number; max: number }>;
  onSelect: (min: number, max: number) => void;
}

function QuickFilter({ label, options, onSelect }: QuickFilterProps) {
  return (
    <div className="mt-3">
      <span className="text-xs text-gray-500 mr-2">{label}</span>
      <div className="flex flex-wrap gap-2 mt-1">
        {options.map((opt) => (
          <button
            key={opt.label}
            onClick={() => onSelect(opt.min, opt.max)}
            className="text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 px-2 py-1 rounded transition-colors"
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}
