/**
 * Scan Results Component
 * Comprehensive results display with multiple views (list, heatmap, table)
 */

import React, { useState } from 'react';
import StockResultCard from './StockResultCard';
import ResultsTable from './ResultsTable';
import { exportToCSV, getTopRegime } from '../../utils/formatters';
import type { ScanResponse } from '../../types/scanner';

interface ScanResultsProps {
  results: ScanResponse | null;
}

interface StatCardProps {
  label: string;
  value: string;
  icon: string;
  color?: string;
}

function StatCard({ label, value, icon, color = 'blue' }: StatCardProps) {
  const colors = {
    blue: 'from-blue-900/30 to-blue-800/20 border-blue-700',
    green: 'from-green-900/30 to-green-800/20 border-green-700',
    yellow: 'from-yellow-900/30 to-yellow-800/20 border-yellow-700',
    purple: 'from-purple-900/30 to-purple-800/20 border-purple-700',
  };

  return (
    <div
      className={`bg-gradient-to-br ${colors[color as keyof typeof colors] || colors.blue} border rounded-lg p-4`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
        <span className="text-xs text-gray-400 uppercase tracking-wider">{label}</span>
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
    </div>
  );
}

export default function ScanResults({ results }: ScanResultsProps) {
  const [view, setView] = useState<'list' | 'table'>('list');
  const [sortBy, setSortBy] = useState('rank');
  const [filterScore, setFilterScore] = useState(0);

  if (!results || !results.results || results.results.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
        <div className="text-6xl mb-4">📭</div>
        <div className="text-white font-semibold text-xl mb-2">No results found</div>
        <div className="text-gray-400 text-sm">
          Try adjusting your criteria or expanding the universe
        </div>
      </div>
    );
  }

  // Filter and sort results
  const filteredResults = results.results
    .filter((r) => (r.composite_score || 0) >= filterScore)
    .sort((a, b) => {
      if (sortBy === 'rank') return (a.rank || 0) - (b.rank || 0);
      if (sortBy === 'score') return (b.composite_score || 0) - (a.composite_score || 0);
      if (sortBy === 'momentum')
        return (
          (b.criteria_scores?.momentum_20d || 0) - (a.criteria_scores?.momentum_20d || 0)
        );
      if (sortBy === 'alignment')
        return (b.alignment_score || 0) - (a.alignment_score || 0);
      return 0;
    });

  // Calculate summary stats
  const avgScore =
    filteredResults.reduce((sum, r) => sum + (r.composite_score || 0), 0) /
    (filteredResults.length || 1);

  const avgAlignment =
    filteredResults.reduce((sum, r) => sum + (r.alignment_score || 0), 0) /
    (filteredResults.length || 1);

  // Get top regime from results
  const regimeCounts: Record<string, number> = {};
  filteredResults.forEach((r) => {
    const regime =
      r.regime_hierarchy?.stock?.regime || r.primary_regime || r.regime || 'NEUTRAL';
    regimeCounts[regime] = (regimeCounts[regime] || 0) + 1;
  });
  const topRegime = getTopRegime(regimeCounts);

  const handleExport = () => {
    exportToCSV(filteredResults, `scan-results-${results.metadata?.config_name || 'export'}.csv`);
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 space-y-3 sm:space-y-0">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center space-x-2">
              <span>📊</span>
              <span>Scan Results</span>
            </h2>
            <p className="text-sm text-gray-400 mt-1">
              {filteredResults.length} stocks found
              {results.metadata?.universe_size && ` (from ${results.metadata.universe_size.toLocaleString()} scanned)`}
            </p>
          </div>

          {/* View Toggle */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setView('list')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                view === 'list'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              📋 List
            </button>
            <button
              onClick={() => setView('table')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                view === 'table'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              📊 Table
            </button>
          </div>
        </div>

        {/* Filters & Sort */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-3 sm:space-y-0 sm:space-x-4">
          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <label className="text-sm text-gray-400 whitespace-nowrap">Min Score:</label>
            <input
              type="range"
              min="0"
              max="10"
              step="0.5"
              value={filterScore}
              onChange={(e) => setFilterScore(Number(e.target.value))}
              className="flex-1 sm:w-32"
            />
            <span className="text-white text-sm font-semibold w-8">{filterScore.toFixed(1)}</span>
          </div>

          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <label className="text-sm text-gray-400">Sort:</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="flex-1 sm:flex-none bg-gray-700 text-white px-3 py-2 rounded-lg text-sm border border-gray-600 focus:border-blue-500 focus:outline-none"
            >
              <option value="rank">Rank</option>
              <option value="score">Score</option>
              <option value="momentum">Momentum</option>
              <option value="alignment">Alignment</option>
            </select>
          </div>

          {/* Export */}
          <button
            onClick={handleExport}
            className="sm:ml-auto w-full sm:w-auto bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center justify-center space-x-2"
          >
            <span>📥</span>
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Avg Alignment"
          value={avgAlignment.toFixed(1)}
          icon="🎯"
          color="green"
        />
        <StatCard label="Top Regime" value={topRegime.split('_')[0]} icon="📈" color="blue" />
        <StatCard label="Avg Score" value={avgScore.toFixed(1)} icon="⭐" color="yellow" />
        <StatCard
          label="Pass Rate"
          value={`${((filteredResults.length / (results.metadata?.universe_size || filteredResults.length)) * 100).toFixed(0)}%`}
          icon="✅"
          color="purple"
        />
      </div>

      {/* Results Display */}
      {view === 'list' && (
        <div className="space-y-3">
          {filteredResults.map((stock, index) => (
            <StockResultCard key={stock.symbol || stock.ticker} stock={stock} index={index} />
          ))}
        </div>
      )}

      {view === 'table' && <ResultsTable results={filteredResults} />}

      {/* Footer Info */}
      {results.metadata && (
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between text-sm space-y-2 sm:space-y-0">
            <div className="text-gray-400">
              Config: <span className="text-white">{results.metadata.config_name}</span>
            </div>
            <div className="text-gray-400">
              Scanned: {new Date(results.metadata.scan_timestamp).toLocaleString()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
