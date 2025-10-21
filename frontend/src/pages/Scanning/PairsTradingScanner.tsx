/**
 * Pairs Trading Scanner Page
 * Find cointegrated pairs with mean-reversion opportunities
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { alphaApi } from '../../api/alphaApi';
import PairCard from '../../components/AlphaScanner/PairCard';

interface ScanResult {
  scan_date: string;
  pairs: any[];
}

export default function PairsTradingScanner() {
  const navigate = useNavigate();
  const [universe, setUniverse] = useState('sp500');
  const [sector, setSector] = useState('');
  const [minCorrelation, setMinCorrelation] = useState(0.7);
  const [minZscore, setMinZscore] = useState(2.0);
  const [maxHalfLife, setMaxHalfLife] = useState(15);
  const [results, setResults] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sectors = [
    { value: '', label: 'All Sectors' },
    { value: 'Technology', label: 'Technology' },
    { value: 'Financials', label: 'Financials' },
    { value: 'Healthcare', label: 'Healthcare' },
    { value: 'Energy', label: 'Energy' },
    { value: 'Consumer', label: 'Consumer' },
    { value: 'Industrials', label: 'Industrials' },
    { value: 'Materials', label: 'Materials' },
    { value: 'Utilities', label: 'Utilities' },
  ];

  const handleScan = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await alphaApi.pairs.find(
        universe,
        sector || undefined,
        minCorrelation,
        minZscore,
        maxHalfLife
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
            <span>↔️</span>
            <span>Pairs Trading Scanner</span>
          </h1>
          <p className="text-gray-400">
            Find cointegrated pairs with mean-reversion opportunities. Trade spread convergence.
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
                    <option value="nasdaq100">NASDAQ 100</option>
                  </select>
                </div>

                {/* Sector Filter */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Sector (Optional)</label>
                  <select
                    value={sector}
                    onChange={(e) => setSector(e.target.value)}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                  >
                    {sectors.map((s) => (
                      <option key={s.value} value={s.value}>
                        {s.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Min Correlation */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Min Correlation: {minCorrelation.toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="0.5"
                    max="0.95"
                    step="0.05"
                    value={minCorrelation}
                    onChange={(e) => setMinCorrelation(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0.50</span>
                    <span>0.95</span>
                  </div>
                </div>

                {/* Min Z-Score */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Min Z-Score: {minZscore.toFixed(1)}σ
                  </label>
                  <input
                    type="range"
                    min="1.5"
                    max="4.0"
                    step="0.5"
                    value={minZscore}
                    onChange={(e) => setMinZscore(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>1.5σ</span>
                    <span>4.0σ</span>
                  </div>
                </div>

                {/* Max Half-Life */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Max Half-Life: {maxHalfLife} days
                  </label>
                  <input
                    type="range"
                    min="5"
                    max="30"
                    step="5"
                    value={maxHalfLife}
                    onChange={(e) => setMaxHalfLife(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>5d</span>
                    <span>30d</span>
                  </div>
                </div>

                {/* Scan Button */}
                <button
                  onClick={handleScan}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-colors"
                >
                  {loading ? '🔄 Scanning...' : '🔍 Find Pairs'}
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
                    Pairs Trading 101
                  </span>
                </div>
                <p className="text-xs text-gray-300 leading-relaxed">
                  <strong>Cointegration:</strong> Two stocks move together long-term but
                  occasionally diverge.
                  <br />
                  <br />
                  <strong>Strategy:</strong> When spread widens beyond 2σ, trade for mean
                  reversion.
                  <br />
                  <br />
                  <strong>Half-Life:</strong> Expected days for spread to revert to mean. Shorter
                  is better.
                </p>
              </div>

              {/* Example Pairs */}
              <div className="mt-4 bg-gray-750 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-400 mb-2">Classic Pairs</h4>
                <div className="text-xs text-gray-300 space-y-1">
                  <div>• PEP ↔ KO (Beverages)</div>
                  <div>• WMT ↔ TGT (Retail)</div>
                  <div>• BA ↔ GD (Aerospace)</div>
                  <div>• JPM ↔ BAC (Banks)</div>
                  <div>• XOM ↔ CVX (Energy)</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel: Results */}
          <div className="lg:col-span-3">
            {!results && !loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="text-6xl mb-4">↔️</div>
                <h3 className="text-white font-semibold mb-2">
                  Configure settings and run scan
                </h3>
                <p className="text-gray-400 text-sm">
                  Find cointegrated pairs with tradeable spread divergences
                </p>
              </div>
            )}

            {loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="animate-spin text-6xl mb-4">🔄</div>
                <h3 className="text-white font-semibold mb-2">Scanning for pairs...</h3>
                <p className="text-gray-400 text-sm">
                  Analyzing {universe.toUpperCase()} for cointegrated pairs
                </p>
              </div>
            )}

            {results && !loading && (
              <div className="space-y-4">
                {/* Header */}
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white font-semibold text-lg mb-2">
                        Pairs Found: {results.pairs.length}
                      </h3>
                      <p className="text-sm text-gray-400">Scan date: {results.scan_date}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-400 mb-1">Filters</div>
                      <div className="text-sm text-white">
                        Corr ≥ {minCorrelation.toFixed(2)} | Z ≥ {minZscore.toFixed(1)}σ | HL ≤ {maxHalfLife}d
                      </div>
                    </div>
                  </div>
                </div>

                {/* Results */}
                {results.pairs.length === 0 ? (
                  <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                    <div className="text-gray-400">
                      No pairs found with current settings. Try adjusting the correlation threshold
                      or z-score minimum.
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {results.pairs.map((pair, index) => (
                      <PairCard
                        key={`${pair.stock_a}-${pair.stock_b}-${index}`}
                        pair={pair}
                      />
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
