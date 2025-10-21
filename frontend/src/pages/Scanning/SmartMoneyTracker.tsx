/**
 * Smart Money Tracker Page
 * Track dark pool activity, unusual options flow, and insider buying
 */

import React, { useState } from 'react';
import { alphaApi } from '../../api/alphaApi';
import SmartMoneyComposite from '../../components/AlphaScanner/SmartMoneyComposite';

export default function SmartMoneyTracker() {
  const [symbols, setSymbols] = useState('');
  const [lookbackDays, setLookbackDays] = useState(5);
  const [minSignals, setMinSignals] = useState(2);
  const [results, setResults] = useState<any[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTrack = async () => {
    const symbolList = symbols
      .split(',')
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean);

    if (symbolList.length === 0) {
      setError('Please enter at least one symbol');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await alphaApi.smartMoney.track(symbolList, lookbackDays, minSignals);
      setResults(data);
    } catch (err) {
      console.error('Tracking failed:', err);
      setError('Tracking failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center space-x-3">
            <span>💰</span>
            <span>Smart Money Tracker</span>
          </h1>
          <p className="text-gray-400">
            Track dark pool activity, unusual options flow, and insider buying
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Panel: Configuration */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 rounded-lg p-6 sticky top-6 border border-gray-700">
              <h3 className="text-white font-semibold mb-4">⚙️ Track Settings</h3>

              <div className="space-y-4">
                {/* Symbols Input */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Stock Symbols (comma-separated)
                  </label>
                  <textarea
                    value={symbols}
                    onChange={(e) => setSymbols(e.target.value)}
                    placeholder="AAPL, MSFT, TSLA..."
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg h-24 text-sm border border-gray-600 focus:border-blue-500 focus:outline-none"
                  />
                </div>

                {/* Lookback Days */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Lookback Period: {lookbackDays} days
                  </label>
                  <input
                    type="range"
                    min="3"
                    max="30"
                    step="1"
                    value={lookbackDays}
                    onChange={(e) => setLookbackDays(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>3d</span>
                    <span>30d</span>
                  </div>
                </div>

                {/* Min Signals */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Min Signals Required: {minSignals}/3
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="3"
                    step="1"
                    value={minSignals}
                    onChange={(e) => setMinSignals(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Any</span>
                    <span>All</span>
                  </div>
                </div>

                {/* Track Button */}
                <button
                  onClick={handleTrack}
                  disabled={loading || !symbols}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-colors"
                >
                  {loading ? '🔄 Tracking...' : '🔍 Track Smart Money'}
                </button>

                {error && (
                  <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-3 text-sm text-red-400">
                    {error}
                  </div>
                )}
              </div>

              {/* Info Box */}
              <div className="mt-6 bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-xl">💡</span>
                  <span className="text-blue-400 font-semibold text-sm">What We Track</span>
                </div>
                <ul className="text-xs text-gray-300 space-y-1">
                  <li>🏦 Dark Pool: Institutional block trades</li>
                  <li>📊 Options: Unusual flow (large premiums)</li>
                  <li>👔 Insider: SEC Form 4 filings</li>
                </ul>
              </div>

              {/* Quick Presets */}
              <div className="mt-4">
                <div className="text-sm font-semibold text-gray-400 mb-2">Quick Presets:</div>
                <div className="space-y-2">
                  <button
                    onClick={() => setSymbols('AAPL, MSFT, GOOGL, NVDA, TSLA')}
                    className="w-full bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded text-sm transition-colors"
                  >
                    Mega Caps
                  </button>
                  <button
                    onClick={() => setSymbols('XBI, MRNA, BNTX, REGN')}
                    className="w-full bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded text-sm transition-colors"
                  >
                    Biotech
                  </button>
                  <button
                    onClick={() => setSymbols('AMD, INTC, MU, QCOM, AVGO')}
                    className="w-full bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded text-sm transition-colors"
                  >
                    Semiconductors
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel: Results */}
          <div className="lg:col-span-3">
            {!results && !loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="text-6xl mb-4">💰</div>
                <h3 className="text-white font-semibold mb-2">Enter symbols and track smart money</h3>
                <p className="text-gray-400 text-sm">
                  Monitor institutional activity across dark pools, options, and insider filings
                </p>
              </div>
            )}

            {loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="animate-spin text-6xl mb-4">🔄</div>
                <h3 className="text-white font-semibold mb-2">Tracking smart money...</h3>
                <p className="text-gray-400 text-sm">Analyzing institutional signals</p>
              </div>
            )}

            {results && !loading && (
              <div className="space-y-4">
                {/* Header */}
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white font-semibold text-lg mb-2">
                        Stocks Tracked: {results.length}
                      </h3>
                      <p className="text-sm text-gray-400">
                        Lookback: {lookbackDays} days | Min Signals: {minSignals}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-400 mb-1">Strong Signals</div>
                      <div className="text-green-400 font-bold text-2xl">
                        {results.filter((r) => r.signal_strength === 'STRONG').length}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Results */}
                {results.length === 0 ? (
                  <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                    <div className="text-gray-400">
                      No significant smart money signals found. Try different symbols or lower the
                      minimum signals threshold.
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {results.map((stock) => (
                      <SmartMoneyComposite key={stock.symbol} data={stock} />
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
