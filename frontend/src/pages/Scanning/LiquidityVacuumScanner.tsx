/**
 * Liquidity Vacuum Scanner Page
 * Find stocks in tight consolidation BEFORE catalysts - "coiled springs"
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { alphaApi } from '../../api/alphaApi';
import VacuumCard from '../../components/AlphaScanner/VacuumCard';

interface ScanResult {
  scan_date: string;
  results: any[];
}

export default function LiquidityVacuumScanner() {
  const navigate = useNavigate();
  const [universe, setUniverse] = useState('sp500');
  const [lookbackDays, setLookbackDays] = useState(20);
  const [minVacuumScore, setMinVacuumScore] = useState(7.0);
  const [requireCatalyst, setRequireCatalyst] = useState(true);
  const [results, setResults] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await alphaApi.liquidityVacuum.scan(
        universe,
        lookbackDays,
        minVacuumScore,
        requireCatalyst
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
            <span>🌀</span>
            <span>Liquidity Vacuum Scanner</span>
          </h1>
          <p className="text-gray-400">
            Find stocks in tight consolidation BEFORE catalysts - "coiled springs"
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
                    <option value="sp600">S&P 600 SmallCap</option>
                    <option value="biotech">Biotech (XBI holdings)</option>
                  </select>
                </div>

                {/* Lookback Days */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Lookback Period: {lookbackDays} days
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="60"
                    step="5"
                    value={lookbackDays}
                    onChange={(e) => setLookbackDays(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>10d</span>
                    <span>60d</span>
                  </div>
                </div>

                {/* Min Vacuum Score */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Min Vacuum Score: {minVacuumScore.toFixed(1)}
                  </label>
                  <input
                    type="range"
                    min="5.0"
                    max="10.0"
                    step="0.5"
                    value={minVacuumScore}
                    onChange={(e) => setMinVacuumScore(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>5.0</span>
                    <span>10.0</span>
                  </div>
                </div>

                {/* Require Catalyst */}
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={requireCatalyst}
                    onChange={(e) => setRequireCatalyst(e.target.checked)}
                    className="h-4 w-4 text-blue-600 rounded"
                  />
                  <label className="text-sm text-gray-300">
                    Require upcoming catalyst (earnings, FDA, etc.)
                  </label>
                </div>

                {/* Scan Button */}
                <button
                  onClick={handleScan}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-colors"
                >
                  {loading ? '🔄 Scanning...' : '🔍 Find Vacuums'}
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
                    What is a Liquidity Vacuum?
                  </span>
                </div>
                <p className="text-xs text-gray-300 leading-relaxed">
                  A stock in tight consolidation with:
                  <br />• Shrinking volume
                  <br />• Narrowing price range
                  <br />• Widening bid-ask spread
                  <br />• Often before a catalyst
                  <br />
                  <br />= "Coiled spring" ready to explode
                </p>
              </div>
            </div>
          </div>

          {/* Right Panel: Results */}
          <div className="lg:col-span-3">
            {!results && !loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="text-6xl mb-4">🌀</div>
                <h3 className="text-white font-semibold mb-2">Configure settings and run scan</h3>
                <p className="text-gray-400 text-sm">
                  Find stocks experiencing liquidity contraction - often a precursor to explosive
                  moves
                </p>
              </div>
            )}

            {loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="animate-spin text-6xl mb-4">🔄</div>
                <h3 className="text-white font-semibold mb-2">Scanning for liquidity vacuums...</h3>
                <p className="text-gray-400 text-sm">Analyzing {universe.toUpperCase()}</p>
              </div>
            )}

            {results && !loading && (
              <div className="space-y-4">
                {/* Header */}
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white font-semibold text-lg mb-2">
                        Liquidity Vacuums Found: {results.results.length}
                      </h3>
                      <p className="text-sm text-gray-400">Scan date: {results.scan_date}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-400 mb-1">Settings</div>
                      <div className="text-sm text-white">
                        {lookbackDays}d lookback | Score ≥ {minVacuumScore.toFixed(1)}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Results */}
                {results.results.length === 0 ? (
                  <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                    <div className="text-gray-400">
                      No liquidity vacuums found with current settings. Try adjusting the
                      parameters.
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {results.results.map((vacuum) => (
                      <VacuumCard key={vacuum.symbol} vacuum={vacuum} />
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
