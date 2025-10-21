/**
 * Bootstrap Simulation Component
 * Implements various bootstrap resampling methods for return distribution analysis
 */

import { useState } from 'react';
import { Loader, Info } from 'lucide-react';
import Plot from 'react-plotly.js';
import { simulationApi, type BootstrapParams } from '../../api/simulationApi';

const BOOTSTRAP_METHODS = [
  {
    id: 'standard',
    name: 'Standard Bootstrap',
    description: 'Random resampling with replacement from historical returns',
  },
  {
    id: 'block',
    name: 'Block Bootstrap',
    description: 'Preserves serial correlation by resampling blocks of consecutive returns',
  },
  {
    id: 'circular',
    name: 'Circular Block Bootstrap',
    description: 'Block bootstrap treating the data as circular to avoid edge effects',
  },
  {
    id: 'stationary',
    name: 'Stationary Bootstrap',
    description: 'Random block lengths to better capture time-varying dependencies',
  },
  {
    id: 'wild',
    name: 'Wild Bootstrap',
    description: 'Multiplies residuals by random weights to preserve heteroskedasticity',
  },
];

export function BootstrapSimulation() {
  const [params, setParams] = useState<BootstrapParams>({
    ticker: 'AAPL',
    method: 'standard',
    n_simulations: 1000,
    block_size: 20,
    start_date: '2020-01-01',
    end_date: '2024-12-31',
  });

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await simulationApi.runBootstrap(params);
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'Backend not running! Start: python backend/simulation_engine/app.py');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Configuration Panel */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Configuration</h3>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Ticker</label>
            <input
              type="text"
              value={params.ticker}
              onChange={(e) => setParams({ ...params, ticker: e.target.value.toUpperCase() })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              placeholder="AAPL"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Number of Simulations</label>
            <input
              type="number"
              value={params.n_simulations}
              onChange={(e) => setParams({ ...params, n_simulations: parseInt(e.target.value) })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              min="100"
              max="10000"
              step="100"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Start Date</label>
            <input
              type="date"
              value={params.start_date}
              onChange={(e) => setParams({ ...params, start_date: e.target.value })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">End Date</label>
            <input
              type="date"
              value={params.end_date}
              onChange={(e) => setParams({ ...params, end_date: e.target.value })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            />
          </div>
        </div>

        {/* Method Selection */}
        <div className="mb-6">
          <label className="block text-sm text-gray-400 mb-3">Bootstrap Method</label>
          <div className="space-y-2">
            {BOOTSTRAP_METHODS.map((method) => (
              <label
                key={method.id}
                className="flex items-start gap-3 p-3 bg-dark-bg rounded-lg cursor-pointer hover:bg-dark-border transition"
              >
                <input
                  type="radio"
                  name="method"
                  value={method.id}
                  checked={params.method === method.id}
                  onChange={(e) => setParams({ ...params, method: e.target.value as any })}
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="font-semibold text-white">{method.name}</div>
                  <div className="text-xs text-gray-400">{method.description}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Block Size (for block-based methods) */}
        {['block', 'circular', 'stationary'].includes(params.method) && (
          <div className="mb-6">
            <label className="block text-sm text-gray-400 mb-2">Block Size</label>
            <input
              type="number"
              value={params.block_size || 20}
              onChange={(e) => setParams({ ...params, block_size: parseInt(e.target.value) })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              min="5"
              max="100"
            />
            <p className="text-xs text-gray-500 mt-1">Number of consecutive days per block</p>
          </div>
        )}

        {/* Error Banner */}
        {error && (
          <div className="mb-4 bg-red-900/30 border border-red-700 rounded-lg p-4">
            <div className="flex items-center gap-2 text-red-400">
              <Info className="w-5 h-5" />
              <span className="font-semibold">{error}</span>
            </div>
          </div>
        )}

        {/* Run Button */}
        <button
          onClick={handleRun}
          disabled={loading}
          className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Running Bootstrap...
            </>
          ) : (
            <>Run Bootstrap Simulation</>
          )}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Distribution Histogram */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Return Distribution</h3>
            {results.histogram && (
              <Plot
                data={[
                  {
                    x: results.histogram.returns,
                    type: 'histogram',
                    nbinsx: 50,
                    marker: { color: '#3b82f6' },
                    name: 'Bootstrap',
                  },
                ]}
                layout={{
                  paper_bgcolor: '#1a1f2e',
                  plot_bgcolor: '#1a1f2e',
                  font: { color: '#e0e0e0', family: 'monospace' },
                  xaxis: { title: 'Return (%)', gridcolor: '#2a3142' },
                  yaxis: { title: 'Frequency', gridcolor: '#2a3142' },
                  margin: { t: 20, b: 50, l: 50, r: 20 },
                  autosize: true,
                  showlegend: false,
                }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%', height: '400px' }}
              />
            )}
          </div>

          {/* Statistical Summary */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Statistical Summary</h3>
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Mean Return</div>
                <div className="text-2xl font-bold text-white">
                  {results.statistics?.mean?.toFixed(3) || '0.000'}%
                </div>
              </div>
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Std Deviation</div>
                <div className="text-2xl font-bold text-white">
                  {results.statistics?.std?.toFixed(3) || '0.000'}%
                </div>
              </div>
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Skewness</div>
                <div className="text-2xl font-bold text-white">
                  {results.statistics?.skew?.toFixed(3) || '0.000'}
                </div>
              </div>
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Kurtosis</div>
                <div className="text-2xl font-bold text-white">
                  {results.statistics?.kurtosis?.toFixed(3) || '0.000'}
                </div>
              </div>
            </div>
          </div>

          {/* Confidence Intervals */}
          {results.confidence_intervals && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Confidence Intervals</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
                  <span className="text-gray-400">95% CI</span>
                  <span className="font-mono text-white">
                    [{results.confidence_intervals.ci_95?.lower?.toFixed(3)}%, {results.confidence_intervals.ci_95?.upper?.toFixed(3)}%]
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
                  <span className="text-gray-400">99% CI</span>
                  <span className="font-mono text-white">
                    [{results.confidence_intervals.ci_99?.lower?.toFixed(3)}%, {results.confidence_intervals.ci_99?.upper?.toFixed(3)}%]
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
