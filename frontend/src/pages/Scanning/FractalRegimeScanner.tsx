/**
 * Fractal Regime Scanner Page
 * Find stocks with PERFECT alignment across ALL timeframes (5d, 20d, 60d, 252d)
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { alphaApi } from '../../api/alphaApi';
import FractalAlignmentCard from '../../components/AlphaScanner/FractalAlignmentCard';

interface ScanResult {
  target_regime: string;
  results: any[];
}

export default function FractalRegimeScanner() {
  const navigate = useNavigate();
  const [symbols, setSymbols] = useState('');
  const [targetRegime, setTargetRegime] = useState('BULLISH');
  const [minAlignment, setMinAlignment] = useState(8.0);
  const [results, setResults] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
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
      const data = await alphaApi.fractal.scan(symbolList, targetRegime, minAlignment);
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
            <span>🔄</span>
            <span>Fractal Regime Scanner</span>
          </h1>
          <p className="text-gray-400">
            Find stocks with PERFECT alignment across ALL timeframes (5d, 20d, 60d, 252d)
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Panel: Configuration */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 rounded-lg p-6 sticky top-6 border border-gray-700">
              <h3 className="text-white font-semibold mb-4">⚙️ Scan Settings</h3>

              <div className="space-y-4">
                {/* Symbols */}
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

                {/* Target Regime */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Target Regime</label>
                  <select
                    value={targetRegime}
                    onChange={(e) => setTargetRegime(e.target.value)}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                  >
                    <option value="BULLISH">Bullish (Up trends)</option>
                    <option value="BEARISH">Bearish (Down trends)</option>
                    <option value="ANY">Any (High alignment)</option>
                  </select>
                </div>

                {/* Min Alignment */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Min Alignment Score: {minAlignment.toFixed(1)}
                  </label>
                  <input
                    type="range"
                    min="5.0"
                    max="10.0"
                    step="0.5"
                    value={minAlignment}
                    onChange={(e) => setMinAlignment(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>5.0</span>
                    <span>10.0</span>
                  </div>
                </div>

                {/* Scan Button */}
                <button
                  onClick={handleScan}
                  disabled={loading || !symbols}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-colors"
                >
                  {loading ? '🔄 Scanning...' : '🔍 Scan Fractal Alignment'}
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
                  <span className="text-blue-400 font-semibold text-sm">
                    Fractal Coherence
                  </span>
                </div>
                <p className="text-xs text-gray-300">
                  When ALL timeframes (micro, swing, intermediate, long-term) show the SAME regime,
                  the trend has maximum strength. All traders aligned = powerful moves.
                </p>
              </div>

              {/* Quick Presets */}
              <div className="mt-4">
                <div className="text-sm font-semibold text-gray-400 mb-2">Quick Presets:</div>
                <div className="space-y-2">
                  <button
                    onClick={() => setSymbols('SPY, QQQ, IWM, DIA')}
                    className="w-full bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded text-sm transition-colors"
                  >
                    Major Indices
                  </button>
                  <button
                    onClick={() => setSymbols('AAPL, MSFT, GOOGL, NVDA, TSLA')}
                    className="w-full bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded text-sm transition-colors"
                  >
                    Mega Caps
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
                <div className="text-6xl mb-4">🔄</div>
                <h3 className="text-white font-semibold mb-2">
                  Enter symbols and scan for fractal alignment
                </h3>
                <p className="text-gray-400 text-sm">
                  Find stocks where all timeframes are in perfect harmony
                </p>
              </div>
            )}

            {loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="animate-spin text-6xl mb-4">🔄</div>
                <h3 className="text-white font-semibold mb-2">
                  Scanning for fractal alignment...
                </h3>
                <p className="text-gray-400 text-sm">Analyzing multi-timeframe regimes</p>
              </div>
            )}

            {results && !loading && (
              <div className="space-y-4">
                {/* Header */}
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white font-semibold text-lg mb-2">
                        Fractal Alignment Results: {results.results.length}
                      </h3>
                      <p className="text-sm text-gray-400">Target: {results.target_regime}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-400 mb-1">Min Alignment</div>
                      <div className="text-white font-bold text-lg">
                        {minAlignment.toFixed(1)}/10
                      </div>
                    </div>
                  </div>
                </div>

                {/* Results */}
                {results.results.length === 0 ? (
                  <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                    <div className="text-gray-400">
                      No fractal alignment found with current settings. Try different symbols or
                      lower the minimum alignment threshold.
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {results.results.map((stock) => (
                      <FractalAlignmentCard key={stock.symbol} stock={stock} />
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
