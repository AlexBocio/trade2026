/**
 * Pattern Library Component
 * Browsable list of historical winning patterns for Time Machine scanner
 */

import React from 'react';
import RegimeBadge from '../Regime/RegimeBadge';

interface Pattern {
  pattern_id: string;
  symbol: string;
  total_return: number;
  start_date: string;
  end_date: string;
  duration_days: number;
  pre_move_characteristics: {
    regime: string;
    catalyst?: string;
  };
}

interface PatternLibraryProps {
  patterns: Pattern[];
  selectedPattern: string | null;
  onSelect: (patternId: string) => void;
}

export default function PatternLibrary({
  patterns,
  selectedPattern,
  onSelect,
}: PatternLibraryProps) {
  if (patterns.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-white font-semibold mb-4">Pattern Library</h3>
        <div className="text-center py-8 text-gray-400 text-sm">
          No patterns available. Create your first pattern to get started.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h3 className="text-white font-semibold mb-4">📚 Pattern Library</h3>

      <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
        {patterns.map((pattern) => (
          <button
            key={pattern.pattern_id}
            onClick={() => onSelect(pattern.pattern_id)}
            className={`w-full text-left p-4 rounded-lg transition-all ${
              selectedPattern === pattern.pattern_id
                ? 'bg-blue-600 ring-2 ring-blue-400'
                : 'bg-gray-750 hover:bg-gray-700'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-semibold">{pattern.symbol}</span>
              <span className="text-green-400 font-bold">
                +{(pattern.total_return * 100).toFixed(0)}%
              </span>
            </div>

            <div className="text-xs text-gray-400 mb-2">
              {pattern.start_date} → {pattern.end_date}
            </div>

            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">{pattern.duration_days} days</span>
              <RegimeBadge regime={pattern.pre_move_characteristics.regime as any} />
            </div>

            {pattern.pre_move_characteristics.catalyst && (
              <div className="mt-2 text-xs text-blue-400">
                💡 {pattern.pre_move_characteristics.catalyst}
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
