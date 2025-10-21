/**
 * Catalyst Calendar Scanner Page
 * Find stocks with upcoming catalysts and good setups
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { alphaApi } from '../../api/alphaApi';
import CatalystSetupCard from '../../components/AlphaScanner/CatalystSetupCard';

interface ScanResult {
  scan_date: string;
  results: any[];
}

export default function CatalystCalendarScanner() {
  const navigate = useNavigate();
  const [universe, setUniverse] = useState('sp500');
  const [catalystTypes, setCatalystTypes] = useState<string[]>(['EARNINGS', 'FDA']);
  const [minDays, setMinDays] = useState(7);
  const [maxDays, setMaxDays] = useState(30);
  const [minSetupScore, setMinSetupScore] = useState(7.5);
  const [regimeFilter, setRegimeFilter] = useState<string>('');
  const [results, setResults] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const availableCatalystTypes = [
    { value: 'EARNINGS', label: '📊 Earnings' },
    { value: 'FDA', label: '💊 FDA Decision' },
    { value: 'PRODUCT_LAUNCH', label: '🚀 Product Launch' },
    { value: 'CONFERENCE', label: '🎤 Conference' },
    { value: 'MERGER', label: '🤝 Merger/Acquisition' },
    { value: 'DIVIDEND', label: '💰 Dividend' },
    { value: 'SPLIT', label: '✂️ Stock Split' },
  ];

  const toggleCatalystType = (type: string) => {
    if (catalystTypes.includes(type)) {
      setCatalystTypes(catalystTypes.filter((t) => t !== type));
    } else {
      setCatalystTypes([...catalystTypes, type]);
    }
  };

  const handleScan = async () => {
    if (catalystTypes.length === 0) {
      setError('Please select at least one catalyst type');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await alphaApi.catalyst.scan(
        universe,
        catalystTypes,
        minDays,
        maxDays,
        minSetupScore,
        regimeFilter || undefined
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
            <span>📅</span>
            <span>Catalyst Calendar Scanner</span>
          </h1>
          <p className="text-gray-400">
            Find stocks with upcoming catalysts and high-quality setups
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
                    <option value="biotech">Biotech (XBI)</option>
                  </select>
                </div>

                {/* Catalyst Types */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Catalyst Types</label>
                  <div className="space-y-2">
                    {availableCatalystTypes.map((type) => (
                      <label
                        key={type.value}
                        className="flex items-center space-x-2 cursor-pointer hover:bg-gray-700 p-2 rounded transition-colors"
                      >
                        <input
                          type="checkbox"
                          checked={catalystTypes.includes(type.value)}
                          onChange={() => toggleCatalystType(type.value)}
                          className="h-4 w-4 text-blue-600 rounded"
                        />
                        <span className="text-white text-sm">{type.label}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Date Range */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Days Ahead: {minDays} - {maxDays}
                  </label>
                  <div className="space-y-2">
                    <div>
                      <label className="text-xs text-gray-500">Min:</label>
                      <input
                        type="range"
                        min="1"
                        max="30"
                        value={minDays}
                        onChange={(e) => setMinDays(Number(e.target.value))}
                        className="w-full"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500">Max:</label>
                      <input
                        type="range"
                        min="7"
                        max="90"
                        value={maxDays}
                        onChange={(e) => setMaxDays(Number(e.target.value))}
                        className="w-full"
                      />
                    </div>
                  </div>
                </div>

                {/* Min Setup Score */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Min Setup Score: {minSetupScore.toFixed(1)}
                  </label>
                  <input
                    type="range"
                    min="5.0"
                    max="10.0"
                    step="0.5"
                    value={minSetupScore}
                    onChange={(e) => setMinSetupScore(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>5.0</span>
                    <span>10.0</span>
                  </div>
                </div>

                {/* Regime Filter */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Regime Filter (Optional)
                  </label>
                  <select
                    value={regimeFilter}
                    onChange={(e) => setRegimeFilter(e.target.value)}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                  >
                    <option value="">All Regimes</option>
                    <option value="BULLISH">Bullish Only</option>
                    <option value="BEARISH">Bearish Only</option>
                    <option value="NEUTRAL">Neutral Only</option>
                  </select>
                </div>

                {/* Scan Button */}
                <button
                  onClick={handleScan}
                  disabled={loading || catalystTypes.length === 0}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-colors"
                >
                  {loading ? '🔄 Scanning...' : '🔍 Find Catalyst Setups'}
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
                    Catalyst Trading
                  </span>
                </div>
                <p className="text-xs text-gray-300 leading-relaxed">
                  Catalysts create volatility and opportunity. The best setups combine:
                  <br />• High-quality technical setup
                  <br />• Favorable regime context
                  <br />• Historical pattern match
                  <br />• Proper positioning window (7-30 days before)
                </p>
              </div>
            </div>
          </div>

          {/* Right Panel: Results */}
          <div className="lg:col-span-3">
            {!results && !loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="text-6xl mb-4">📅</div>
                <h3 className="text-white font-semibold mb-2">
                  Configure settings and run scan
                </h3>
                <p className="text-gray-400 text-sm">
                  Find stocks with upcoming catalysts and high-quality technical setups
                </p>
              </div>
            )}

            {loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="animate-spin text-6xl mb-4">🔄</div>
                <h3 className="text-white font-semibold mb-2">
                  Scanning for catalyst setups...
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
                        Catalyst Setups Found: {results.results.length}
                      </h3>
                      <p className="text-sm text-gray-400">Scan date: {results.scan_date}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-400 mb-1">Settings</div>
                      <div className="text-sm text-white">
                        {minDays}-{maxDays} days | Score ≥ {minSetupScore.toFixed(1)}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Results */}
                {results.results.length === 0 ? (
                  <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                    <div className="text-gray-400">
                      No catalyst setups found with current settings. Try adjusting the parameters
                      or catalyst types.
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {results.results.map((setup, index) => (
                      <CatalystSetupCard key={`${setup.symbol}-${index}`} setup={setup} />
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
