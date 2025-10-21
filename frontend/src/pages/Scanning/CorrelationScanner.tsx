/**
 * Correlation Breakdown Scanner Page
 * Find stocks that USED TO correlate with sector/market but suddenly DON'T
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { alphaApi } from '../../api/alphaApi';
import CorrelationBreakdownCard from '../../components/AlphaScanner/CorrelationBreakdownCard';

interface CorrelationScanResult {
  scan_date: string;
  results: any[];
}

export default function CorrelationScanner() {
  const navigate = useNavigate();
  const [universe, setUniverse] = useState('sp500');
  const [historicalWindow, setHistoricalWindow] = useState(60);
  const [recentWindow, setRecentWindow] = useState(10);
  const [minBreakdown, setMinBreakdown] = useState(0.4);
  const [direction, setDirection] = useState('BOTH');
  const [results, setResults] = useState<CorrelationScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await alphaApi.correlation.scan(
        universe,
        historicalWindow,
        recentWindow,
        minBreakdown,
        direction
      );
      setResults(data);
    } catch (err) {
      console.error('Scan failed:', err);
      setError('Scan failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        <button
          onClick={() => navigate('/scanner')}
          className="mb-4 flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Scanner</span>
        </button>

        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center space-x-3">
            <span>🔗</span>
            <span>Correlation Breakdown Scanner</span>
          </h1>
          <p className="text-gray-400">
            Find stocks that USED TO correlate with sector/market but suddenly DON'T
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Panel: Configuration */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 rounded-lg p-6 sticky top-6 border border-gray-700">
              <h3 className="text-white font-semibold mb-4">⚙️ Scan Settings</h3>

              <div className="space-y-4">
                {/* Universe */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Stock Universe</label>
                  <select
                    value={universe}
                    onChange={(e) => setUniverse(e.target.value)}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                  >
                    <option value="sp500">S&P 500</option>
                    <option value="sp400">S&P 400 MidCap</option>
                    <option value="nasdaq100">NASDAQ 100</option>
                  </select>
                </div>

                {/* Historical Window */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Historical Window: {historicalWindow} days
                  </label>
                  <input
                    type="range"
                    min="30"
                    max="252"
                    step="10"
                    value={historicalWindow}
                    onChange={(e) => setHistoricalWindow(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>30d</span>
                    <span>252d</span>
                  </div>
                </div>

                {/* Recent Window */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Recent Window: {recentWindow} days
                  </label>
                  <input
                    type="range"
                    min="5"
                    max="30"
                    step="5"
                    value={recentWindow}
                    onChange={(e) => setRecentWindow(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>5d</span>
                    <span>30d</span>
                  </div>
                </div>

                {/* Min Breakdown */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Min Breakdown: {minBreakdown.toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="0.20"
                    max="0.80"
                    step="0.05"
                    value={minBreakdown}
                    onChange={(e) => setMinBreakdown(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0.20</span>
                    <span>0.80</span>
                  </div>
                </div>

                {/* Direction */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Divergence Type</label>
                  <select
                    value={direction}
                    onChange={(e) => setDirection(e.target.value)}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                  >
                    <option value="BOTH">Both (Positive & Negative)</option>
                    <option value="POSITIVE">Positive (Stock UP, Sector flat/down)</option>
                    <option value="NEGATIVE">Negative (Stock DOWN, Sector up)</option>
                  </select>
                </div>

                {/* Scan Button */}
                <button
                  onClick={handleScan}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-colors"
                >
                  {loading ? '🔄 Scanning...' : '🔍 Scan for Breakdowns'}
                </button>

                {error && (
                  <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-3 text-sm text-red-400">
                    {error}
                  </div>
                )}
              </div>

              {/* Info Card */}
              <div className="mt-6 bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-blue-400 mb-2">💡 How it works</h4>
                <p className="text-xs text-gray-400">
                  This scanner identifies stocks whose correlation with their sector has broken
                  down - often a sign of divergence and opportunity.
                </p>
              </div>
            </div>
          </div>

          {/* Right Panel: Results */}
          <div className="lg:col-span-3">
            {!results && !loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="text-6xl mb-4">📊</div>
                <h3 className="text-white font-semibold mb-2">Configure settings and run scan</h3>
                <p className="text-gray-400 text-sm">
                  Find stocks whose correlation with their sector has broken down - often a sign
                  of divergence and opportunity
                </p>
              </div>
            )}

            {loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="animate-spin text-6xl mb-4">🔄</div>
                <h3 className="text-white font-semibold mb-2">Scanning for breakdowns...</h3>
                <p className="text-gray-400 text-sm">
                  Analyzing correlation patterns across {universe.toUpperCase()}
                </p>
              </div>
            )}

            {results && !loading && (
              <div className="space-y-4">
                {/* Header */}
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-white font-semibold text-lg">
                        Correlation Breakdowns Found: {results.results.length}
                      </h3>
                      <p className="text-sm text-gray-400 mt-1">Scan date: {results.scan_date}</p>
                    </div>

                    <div className="text-right">
                      <div className="text-xs text-gray-400 mb-1">Settings</div>
                      <div className="text-sm text-white">
                        {historicalWindow}d → {recentWindow}d | Δ ≥ {minBreakdown.toFixed(2)}
                      </div>
                    </div>
                  </div>

                  {/* Summary Stats */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-gray-750 rounded-lg p-3">
                      <div className="text-xs text-gray-400 mb-1">Positive Divergence</div>
                      <div className="text-green-400 font-bold text-lg">
                        {
                          results.results.filter((r) => r.divergence_direction === 'POSITIVE')
                            .length
                        }
                      </div>
                    </div>

                    <div className="bg-gray-750 rounded-lg p-3">
                      <div className="text-xs text-gray-400 mb-1">Negative Divergence</div>
                      <div className="text-red-400 font-bold text-lg">
                        {
                          results.results.filter((r) => r.divergence_direction === 'NEGATIVE')
                            .length
                        }
                      </div>
                    </div>

                    <div className="bg-gray-750 rounded-lg p-3">
                      <div className="text-xs text-gray-400 mb-1">Actionable</div>
                      <div className="text-blue-400 font-bold text-lg">
                        {results.results.filter((r) => r.actionable).length}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Results */}
                {results.results.length === 0 ? (
                  <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                    <div className="text-gray-400">
                      No correlation breakdowns found with current settings. Try adjusting the
                      parameters.
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {results.results.map((breakdown) => (
                      <CorrelationBreakdownCard key={breakdown.symbol} breakdown={breakdown} />
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
