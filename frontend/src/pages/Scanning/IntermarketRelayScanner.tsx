/**
 * Intermarket Relay Scanner Page
 * Detect regime changes in LEAD markets, predict follow-on in LAG markets
 * Auto-scans and refreshes every 15 minutes
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { alphaApi } from '../../api/alphaApi';
import RelayOpportunityCard from '../../components/AlphaScanner/RelayOpportunityCard';

interface ScanResult {
  scan_timestamp: string;
  opportunities: any[];
  total_pairs: number;
}

export default function IntermarketRelayScanner() {
  const navigate = useNavigate();
  const [results, setResults] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [minConfidence, setMinConfidence] = useState(0.6);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);

  const handleScan = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await alphaApi.intermarket.scanRelay();
      setResults(data);
      setLastRefresh(new Date());
    } catch (err) {
      console.error('Scan failed:', err);
      setError('Scan failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh every 15 minutes
  useEffect(() => {
    // Initial scan on mount
    handleScan();

    if (!autoRefreshEnabled) return;

    // Set up 15-minute auto-refresh
    const interval = setInterval(() => {
      handleScan();
    }, 15 * 60 * 1000); // 15 minutes in milliseconds

    return () => clearInterval(interval);
  }, [autoRefreshEnabled]);

  // Filter opportunities by confidence
  const filteredOpportunities = results?.opportunities.filter(
    (opp) => opp.confidence >= minConfidence
  ) || [];

  // Sort by urgency (days_until_flip ascending)
  const sortedOpportunities = [...filteredOpportunities].sort(
    (a, b) => a.days_until_flip - b.days_until_flip
  );

  // Count urgent opportunities (days_until_flip <= 1)
  const urgentCount = filteredOpportunities.filter((opp) => opp.days_until_flip <= 1).length;

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
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-3xl font-bold text-white flex items-center space-x-3">
              <span>🔗</span>
              <span>Intermarket Relay Scanner</span>
            </h1>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setAutoRefreshEnabled(!autoRefreshEnabled)}
                className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                  autoRefreshEnabled
                    ? 'bg-green-600 hover:bg-green-700 text-white'
                    : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                }`}
              >
                {autoRefreshEnabled ? '✓ Auto-Refresh ON' : '✗ Auto-Refresh OFF'}
              </button>
              <button
                onClick={handleScan}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-2 px-6 rounded-lg transition-colors"
              >
                {loading ? '🔄 Scanning...' : '🔄 Manual Refresh'}
              </button>
            </div>
          </div>
          <p className="text-gray-400">
            Lead markets move first, lag markets follow. Auto-refreshes every 15 minutes.
          </p>
          {lastRefresh && (
            <p className="text-gray-500 text-sm mt-1">
              Last refresh: {lastRefresh.toLocaleTimeString()}
            </p>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Panel: Filters & Stats */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 rounded-lg p-6 sticky top-6 border border-gray-700 space-y-6">
              {/* Stats */}
              <div>
                <h3 className="text-white font-semibold mb-4">📊 Statistics</h3>
                <div className="space-y-3">
                  <div className="bg-gray-750 rounded-lg p-3">
                    <div className="text-xs text-gray-400 mb-1">Total Opportunities</div>
                    <div className="text-white font-bold text-2xl">
                      {filteredOpportunities.length}
                    </div>
                  </div>
                  <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-3">
                    <div className="text-xs text-red-400 mb-1">🚨 Urgent (≤1 day)</div>
                    <div className="text-red-400 font-bold text-2xl animate-pulse">
                      {urgentCount}
                    </div>
                  </div>
                  <div className="bg-gray-750 rounded-lg p-3">
                    <div className="text-xs text-gray-400 mb-1">Total Pairs Tracked</div>
                    <div className="text-white font-bold text-xl">
                      {results?.total_pairs || 0}
                    </div>
                  </div>
                </div>
              </div>

              {/* Confidence Filter */}
              <div>
                <h3 className="text-white font-semibold mb-4">⚙️ Filters</h3>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Min Confidence: {(minConfidence * 100).toFixed(0)}%
                  </label>
                  <input
                    type="range"
                    min="0.5"
                    max="0.95"
                    step="0.05"
                    value={minConfidence}
                    onChange={(e) => setMinConfidence(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>50%</span>
                    <span>95%</span>
                  </div>
                </div>
              </div>

              {/* Info Box */}
              <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-xl">💡</span>
                  <span className="text-blue-400 font-semibold text-sm">
                    How It Works
                  </span>
                </div>
                <p className="text-xs text-gray-300 leading-relaxed">
                  We track historical lead-lag relationships between correlated markets. When a
                  LEAD market moves, the LAG market typically follows within 2-5 days. This
                  scanner identifies these setups in real-time.
                </p>
              </div>

              {/* Common Pairs */}
              <div className="bg-gray-750 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-400 mb-2">
                  💎 Common Pairs
                </h4>
                <div className="text-xs text-gray-300 space-y-1">
                  <div>• Crude Oil → Energy Stocks (XLE)</div>
                  <div>• Gold (GLD) → Gold Miners (GDX)</div>
                  <div>• USD → Export-Heavy Stocks</div>
                  <div>• VIX → Market Beta Stocks</div>
                  <div>• Treasury Yields → Banks (KRE)</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel: Results */}
          <div className="lg:col-span-3">
            {!results && !loading && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="text-6xl mb-4">🔗</div>
                <h3 className="text-white font-semibold mb-2">
                  Initializing intermarket relay scanner...
                </h3>
                <p className="text-gray-400 text-sm">
                  Scanning for lead-lag opportunities across correlated markets
                </p>
              </div>
            )}

            {loading && !results && (
              <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                <div className="animate-spin text-6xl mb-4">🔄</div>
                <h3 className="text-white font-semibold mb-2">
                  Scanning intermarket relationships...
                </h3>
                <p className="text-gray-400 text-sm">
                  Analyzing lead-lag correlations across markets
                </p>
              </div>
            )}

            {error && (
              <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-6 text-center">
                <div className="text-4xl mb-3">⚠️</div>
                <div className="text-red-400 font-semibold">{error}</div>
              </div>
            )}

            {results && !loading && (
              <div className="space-y-4">
                {/* Header */}
                <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white font-semibold text-lg mb-2">
                        Relay Opportunities: {sortedOpportunities.length}
                      </h3>
                      <p className="text-sm text-gray-400">
                        Scan time: {new Date(results.scan_timestamp).toLocaleString()}
                      </p>
                    </div>
                    {urgentCount > 0 && (
                      <div className="bg-red-900/20 border border-red-700/50 rounded-lg px-4 py-3">
                        <div className="text-xs text-red-400 mb-1">🚨 URGENT</div>
                        <div className="text-red-400 font-bold text-2xl animate-pulse">
                          {urgentCount}
                        </div>
                        <div className="text-xs text-red-400">Imminent Flips</div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Results */}
                {sortedOpportunities.length === 0 ? (
                  <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
                    <div className="text-gray-400">
                      No relay opportunities found with current filters. Try lowering the minimum
                      confidence threshold.
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {sortedOpportunities.map((opportunity, index) => (
                      <RelayOpportunityCard
                        key={`${opportunity.lead_market}-${opportunity.lag_market}-${index}`}
                        opportunity={opportunity}
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
