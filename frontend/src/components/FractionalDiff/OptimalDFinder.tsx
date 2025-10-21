/**
 * Optimal d Finder Component
 * Automatically find the minimum d that achieves stationarity
 */

import { useState } from 'react';
import { Loader, Info, TrendingUp } from 'lucide-react';
import Plot from 'react-plotly.js';
import { fractionalDiffApi, type OptimalDParams } from '../../api/fractionalDiffApi';

interface SearchResult {
  d: number;
  p_value: number;
  is_stationary: boolean;
  memory_score: number;
}

interface OptimalDResults {
  optimal_d: number;
  recommendation: string;
  search_results: SearchResult[];
  analysis: {
    min_stationary_d: number;
    max_memory_d: number;
    balanced_d: number;
  };
}

export function OptimalDFinder() {
  const [params, setParams] = useState<OptimalDParams>({
    ticker: 'SPY',
    d_min: 0.0,
    d_max: 1.0,
    step: 0.05,
    start_date: '2020-01-01',
  });

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<OptimalDResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFindOptimal = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await fractionalDiffApi.findOptimalD(params);
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'Backend not running! Start: python backend/fracdiff_service/app.py');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Configuration Panel */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-2xl font-semibold text-white mb-4">Find Optimal d Value</h2>

        <p className="text-gray-300 mb-6">
          Automatically find the minimum d that achieves stationarity (preserves maximum memory).
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Ticker Input */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Ticker Symbol</label>
            <input
              type="text"
              value={params.ticker}
              onChange={(e) => setParams({ ...params, ticker: e.target.value.toUpperCase() })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-blue-500"
              placeholder="SPY"
            />
          </div>

          {/* Start Date */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Start Date</label>
            <input
              type="date"
              value={params.start_date}
              onChange={(e) => setParams({ ...params, start_date: e.target.value })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Search Range */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Search Range</label>
            <div className="flex gap-2">
              <input
                type="number"
                value={params.d_min}
                onChange={(e) => setParams({ ...params, d_min: parseFloat(e.target.value) })}
                className="flex-1 px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-blue-500"
                min="0"
                max="1"
                step="0.05"
                placeholder="Min"
              />
              <span className="text-gray-400 self-center">to</span>
              <input
                type="number"
                value={params.d_max}
                onChange={(e) => setParams({ ...params, d_max: parseFloat(e.target.value) })}
                className="flex-1 px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-blue-500"
                min="0"
                max="1"
                step="0.05"
                placeholder="Max"
              />
            </div>
          </div>

          {/* Step Size */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Step Size</label>
            <input
              type="number"
              value={params.step}
              onChange={(e) => setParams({ ...params, step: parseFloat(e.target.value) })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-blue-500"
              min="0.01"
              max="0.2"
              step="0.01"
            />
            <p className="text-xs text-gray-500 mt-1">Smaller step = more precise, but slower</p>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-4 bg-red-900/30 border border-red-700 rounded-lg p-4">
            <div className="flex items-center gap-2 text-red-400">
              <Info className="w-5 h-5" />
              <span className="font-semibold">{error}</span>
            </div>
          </div>
        )}

        {/* Action Button */}
        <button
          onClick={handleFindOptimal}
          disabled={loading}
          className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Searching...
            </>
          ) : (
            <>
              <TrendingUp className="w-5 h-5" />
              Find Optimal d
            </>
          )}
        </button>
      </div>

      {/* Results Display */}
      {results && (
        <div className="space-y-6">
          {/* Recommendation Banner */}
          <div className="bg-green-900/20 border border-green-700 rounded-lg p-6">
            <h3 className="text-2xl font-bold text-green-400 mb-2">
              Optimal d = {results.optimal_d.toFixed(3)}
            </h3>
            <p className="text-gray-300 text-lg">{results.recommendation}</p>
          </div>

          {/* Analysis Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Minimum Stationary d</div>
              <div className="text-3xl font-bold text-blue-400">
                {results.analysis.min_stationary_d.toFixed(3)}
              </div>
              <p className="text-xs text-gray-500 mt-2">First d value that achieves stationarity</p>
            </div>

            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Maximum Memory d</div>
              <div className="text-3xl font-bold text-green-400">
                {results.analysis.max_memory_d.toFixed(3)}
              </div>
              <p className="text-xs text-gray-500 mt-2">Highest memory while staying stationary</p>
            </div>

            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Balanced d</div>
              <div className="text-3xl font-bold text-purple-400">
                {results.analysis.balanced_d.toFixed(3)}
              </div>
              <p className="text-xs text-gray-500 mt-2">Best trade-off between stability and memory</p>
            </div>
          </div>

          {/* Stationarity Test Results Chart */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h4 className="text-lg font-medium text-white mb-4">
              Stationarity Test Results Across d Values
            </h4>
            <Plot
              data={[
                {
                  x: results.search_results.map((r) => r.d),
                  y: results.search_results.map((r) => r.p_value),
                  type: 'scatter',
                  mode: 'lines+markers',
                  line: { color: '#60A5FA', width: 2 },
                  marker: {
                    size: 8,
                    color: results.search_results.map((r) => (r.is_stationary ? '#34D399' : '#F87171')),
                  },
                  name: 'ADF p-value',
                },
              ]}
              layout={{
                paper_bgcolor: '#1a1f2e',
                plot_bgcolor: '#1a1f2e',
                font: { color: '#e0e0e0', family: 'monospace' },
                xaxis: {
                  title: 'd Value',
                  gridcolor: '#2a3142',
                },
                yaxis: {
                  title: 'ADF p-value',
                  gridcolor: '#2a3142',
                },
                shapes: [
                  {
                    type: 'line',
                    x0: params.d_min,
                    x1: params.d_max,
                    y0: 0.05,
                    y1: 0.05,
                    line: {
                      color: '#EF4444',
                      dash: 'dash',
                      width: 2,
                    },
                  },
                ],
                annotations: [
                  {
                    x: (params.d_min! + params.d_max!) / 2,
                    y: 0.05,
                    text: 'Stationarity Threshold (p=0.05)',
                    showarrow: false,
                    yshift: 10,
                    font: { color: '#EF4444', size: 10 },
                  },
                ],
                margin: { t: 20, r: 20, b: 60, l: 60 },
                autosize: true,
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '400px' }}
            />
          </div>

          {/* Memory Retention Chart */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h4 className="text-lg font-medium text-white mb-4">Memory Retention vs d</h4>
            <Plot
              data={[
                {
                  x: results.search_results.map((r) => r.d),
                  y: results.search_results.map((r) => r.memory_score * 100),
                  type: 'scatter',
                  mode: 'lines+markers',
                  fill: 'tozeroy',
                  line: { color: '#34D399', width: 2 },
                  fillcolor: 'rgba(52, 211, 153, 0.2)',
                  marker: { size: 6 },
                  name: 'Memory Retention',
                },
              ]}
              layout={{
                paper_bgcolor: '#1a1f2e',
                plot_bgcolor: '#1a1f2e',
                font: { color: '#e0e0e0', family: 'monospace' },
                xaxis: {
                  title: 'd Value',
                  gridcolor: '#2a3142',
                },
                yaxis: {
                  title: 'Memory Retention (%)',
                  gridcolor: '#2a3142',
                  range: [0, 100],
                },
                margin: { t: 20, r: 20, b: 60, l: 60 },
                autosize: true,
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '400px' }}
            />
          </div>

          {/* Results Table */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h4 className="text-lg font-medium text-white mb-4">Detailed Results</h4>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-400 border-b border-dark-border">
                    <th className="pb-2">d Value</th>
                    <th className="pb-2 text-right">p-value</th>
                    <th className="pb-2 text-right">Status</th>
                    <th className="pb-2 text-right">Memory</th>
                  </tr>
                </thead>
                <tbody>
                  {results.search_results.map((result, index) => (
                    <tr key={index} className="border-b border-dark-border">
                      <td className="py-2 text-white font-mono">{result.d.toFixed(3)}</td>
                      <td className="py-2 text-right text-white font-mono">{result.p_value.toFixed(4)}</td>
                      <td className="py-2 text-right">
                        <span
                          className={`px-2 py-1 rounded text-xs font-semibold ${
                            result.is_stationary
                              ? 'bg-green-900/30 text-green-400'
                              : 'bg-red-900/30 text-red-400'
                          }`}
                        >
                          {result.is_stationary ? 'Stationary' : 'Non-Stationary'}
                        </span>
                      </td>
                      <td className="py-2 text-right text-white font-mono">
                        {(result.memory_score * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
