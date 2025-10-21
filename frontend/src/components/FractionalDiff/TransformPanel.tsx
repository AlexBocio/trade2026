/**
 * Transform Panel Component
 * Apply fractional differentiation with custom d value
 */

import { useState } from 'react';
import { Loader, Info } from 'lucide-react';
import Plot from 'react-plotly.js';
import { fractionalDiffApi, type TransformParams } from '../../api/fractionalDiffApi';

interface StationarityResult {
  is_stationary: boolean;
  p_value: number;
  statistic: number;
  critical_values: Record<string, number>;
}

interface TransformResults {
  dates: string[];
  original: number[];
  transformed: number[];
  stationarity_before: StationarityResult;
  stationarity_after: StationarityResult;
  memory_retained: number;
  d_used: number;
}

export function TransformPanel() {
  const [params, setParams] = useState<TransformParams>({
    ticker: 'SPY',
    d: 0.5,
    start_date: '2020-01-01',
    method: 'ffd',
  });

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<TransformResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTransform = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await fractionalDiffApi.transform(params);
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
        <h2 className="text-2xl font-semibold text-white mb-4">Transform Time Series</h2>

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
        </div>

        {/* d Value Slider */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Differentiation Order (d): <span className="text-blue-400 font-mono">{params.d.toFixed(2)}</span>
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={params.d}
            onChange={(e) => setParams({ ...params, d: parseFloat(e.target.value) })}
            className="w-full h-2 bg-dark-bg rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0.0 (Original)</span>
            <span>0.5 (Balanced)</span>
            <span>1.0 (Returns)</span>
          </div>
        </div>

        {/* Method Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">Method</label>
          <div className="flex gap-4">
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                value="ffd"
                checked={params.method === 'ffd'}
                onChange={(e) => setParams({ ...params, method: e.target.value as 'ffd' })}
                className="mr-2"
              />
              <span className="text-white">FFD (Fast, Memory Efficient)</span>
            </label>
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                value="standard"
                checked={params.method === 'standard'}
                onChange={(e) => setParams({ ...params, method: e.target.value as 'standard' })}
                className="mr-2"
              />
              <span className="text-white">Standard (Full Window)</span>
            </label>
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-300">
              <strong>Guide:</strong> d=0 keeps original series (non-stationary), d=1 gives returns (stationary, no memory).
              Try d=0.4-0.6 for stationarity with memory retention. Use FFD for large datasets.
            </div>
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
          onClick={handleTransform}
          disabled={loading}
          className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Transforming...
            </>
          ) : (
            <>Apply Fractional Differentiation</>
          )}
        </button>
      </div>

      {/* Results Display */}
      {results && (
        <div className="space-y-6">
          {/* Time Series Chart */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Original vs Transformed Series</h3>
            <Plot
              data={[
                {
                  x: results.dates,
                  y: results.original,
                  name: 'Original',
                  type: 'scatter',
                  mode: 'lines',
                  line: { color: '#60A5FA', width: 2 },
                },
                {
                  x: results.dates,
                  y: results.transformed,
                  name: `Transformed (d=${results.d_used.toFixed(2)})`,
                  type: 'scatter',
                  mode: 'lines',
                  line: { color: '#34D399', width: 2 },
                },
              ]}
              layout={{
                paper_bgcolor: '#1a1f2e',
                plot_bgcolor: '#1a1f2e',
                font: { color: '#e0e0e0', family: 'monospace' },
                xaxis: { title: 'Date', gridcolor: '#2a3142' },
                yaxis: { title: 'Value', gridcolor: '#2a3142' },
                legend: { x: 0, y: 1, bgcolor: 'rgba(0,0,0,0)' },
                margin: { t: 20, r: 20, b: 50, l: 60 },
                autosize: true,
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '400px' }}
            />
          </div>

          {/* Stationarity Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Before Card */}
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h4 className="text-lg font-medium text-white mb-3">Before (Original Series)</h4>
              <StationarityBadge result={results.stationarity_before} />
            </div>

            {/* After Card */}
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h4 className="text-lg font-medium text-white mb-3">
                After (d={results.d_used.toFixed(2)})
              </h4>
              <StationarityBadge result={results.stationarity_after} />
            </div>
          </div>

          {/* Memory Retention */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h4 className="text-lg font-medium text-white mb-4">Memory Retention</h4>
            <div className="flex items-center gap-4">
              <div className="flex-1 bg-dark-bg rounded-full h-6 overflow-hidden">
                <div
                  className="bg-green-500 h-6 rounded-full transition-all duration-500 flex items-center justify-center"
                  style={{ width: `${results.memory_retained * 100}%` }}
                >
                  <span className="text-xs font-bold text-white">
                    {(results.memory_retained * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
              <span className="text-2xl font-bold text-green-400 min-w-[80px] text-right">
                {(results.memory_retained * 100).toFixed(1)}%
              </span>
            </div>
            <p className="text-sm text-gray-400 mt-2">
              Percentage of original price information retained after transformation
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper Component - Stationarity Badge
interface StationarityBadgeProps {
  result: StationarityResult;
}

function StationarityBadge({ result }: StationarityBadgeProps) {
  const isStationary = result.is_stationary;

  return (
    <div className="space-y-3">
      <div
        className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold ${
          isStationary
            ? 'bg-green-900/30 text-green-400 border border-green-700'
            : 'bg-red-900/30 text-red-400 border border-red-700'
        }`}
      >
        {isStationary ? '✓ Stationary' : '✗ Non-Stationary'}
      </div>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-400">ADF p-value:</span>
          <span className="text-white font-mono">{result.p_value.toFixed(4)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Test statistic:</span>
          <span className="text-white font-mono">{result.statistic.toFixed(4)}</span>
        </div>
        {result.critical_values && (
          <div className="mt-3 pt-3 border-t border-dark-border">
            <div className="text-gray-400 mb-1">Critical Values:</div>
            {Object.entries(result.critical_values).map(([level, value]) => (
              <div key={level} className="flex justify-between text-xs">
                <span className="text-gray-500">{level}:</span>
                <span className="text-gray-400 font-mono">{value.toFixed(4)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
