/**
 * Sentiment Divergence Scanner Page
 * Find stocks where sentiment DISAGREES with price action
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { alphaApi } from '../../api/alphaApi';
import DivergenceCard from '../../components/AlphaScanner/DivergenceCard';

interface ScanResult {
  scan_date: string;
  divergence_type: string;
  results: any[];
}

export default function SentimentDivergenceScanner() {
  const navigate = useNavigate();
  const [universe, setUniverse] = useState('sp500');
  const [divergenceType, setDivergenceType] = useState('BOTH');
  const [minDivergenceScore, setMinDivergenceScore] = useState(7.0);
  const [minMagnitude, setMinMagnitude] = useState(0.4);
  const [results, setResults] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await alphaApi.sentiment.scan(
        universe,
        divergenceType,
        minDivergenceScore,
        minMagnitude
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
            <span>💭</span>
            <span>Sentiment Divergence Scanner</span>
          </h1>
          <p className="text-gray-400">
            Find stocks where sentiment DISAGREES with price action
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

                {/* Divergence Type */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Divergence Type</label>
                  <select
                    value={divergenceType}
                    onChange={(e) => setDivergenceType(e.target.value)}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                  >
                    <option value="BOTH">Both (Bullish & Bearish)</option>
                    <option value="BULLISH">Bullish (Bad news, price UP)</option>
                    <option value="BEARISH">Bearish (Good news, price DOWN)</option>
                  </select>
                </div>

                {/* Min Divergence Score */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Min Divergence Score: {minDivergenceScore.toFixed(1)}
                  </label>
                  <input
                    type="range"
                    min="5.0"
                    max="10.0"
                    step="0.5"
                    value={minDivergenceScore}
                    onChange={(e) => setMinDivergenceScore(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>5.0</span>
                    <span>10.0</span>
                  </div>
                </div>

                {/* Min Magnitude */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Min Magnitude: {minMagnitude.toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="0.20"
                    max="0.80"
                    step="0.05"
                    value={minMagnitude}
                    onChange={(e) => setMinMagnitude(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0.20</span>
                    <span>0.80</span>
                  </div>
                </div>

                {/* Scan Button */}
                <button
                  onClick={handleScan}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-colors"
                >
                  {loading ? '🔄 Scanning...' : '🔍 Find Divergences'}
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
                    What is Sentiment Divergence?
                  </span>
                </div>
                <div className="text-xs text-gray-300 space-y-2">
                  <p>
                    <strong className="text-green-400">Bullish:</strong> Very negative news but
                    price rising = "Climbing wall of worry"
                  </p>
                  <p>
                    <strong className="text-red-400">Bearish:</strong> Very positive news but price
                    falling = "Distribution into hype"
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel: Results */}
          <div className="lg:col-span-3">
            {!results && !loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="text-6xl mb-4">💭</div>
                <h3 className="text-white font-semibold mb-2">
                  Configure settings and run scan
                </h3>
                <p className="text-gray-400 text-sm">
                  Find stocks where sentiment and price are telling different stories
                </p>
              </div>
            )}

            {loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="animate-spin text-6xl mb-4">🔄</div>
                <h3 className="text-white font-semibold mb-2">
                  Scanning for sentiment divergences...
                </h3>
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
                        Divergences Found: {results.results.length}
                      </h3>
                      <p className="text-sm text-gray-400">
                        Scan date: {results.scan_date} | Type: {results.divergence_type}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-400 mb-1">Settings</div>
                      <div className="text-sm text-white">
                        Score ≥ {minDivergenceScore.toFixed(1)} | Magnitude ≥{' '}
                        {minMagnitude.toFixed(2)}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Results */}
                {results.results.length === 0 ? (
                  <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                    <div className="text-gray-400">
                      No sentiment divergences found with current settings. Try adjusting the
                      parameters.
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {results.results.map((divergence) => (
                      <DivergenceCard key={divergence.symbol} divergence={divergence} />
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
