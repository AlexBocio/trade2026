/**
 * Advanced Monte Carlo Simulation Component
 * Implements GARCH, Copula, Jump-Diffusion, and Regime-Switching models
 */

import { useState } from 'react';
import { Loader, Info } from 'lucide-react';
import Plot from 'react-plotly.js';
import { simulationApi, type MonteCarloParams } from '../../api/simulationApi';

const MONTE_CARLO_METHODS = [
  {
    id: 'garch',
    name: 'GARCH Model',
    description: 'Generalized Autoregressive Conditional Heteroskedasticity for volatility clustering',
  },
  {
    id: 'copula',
    name: 'Copula-based',
    description: 'Models dependence structure between multiple assets',
  },
  {
    id: 'jump-diffusion',
    name: 'Jump-Diffusion',
    description: 'Captures sudden price jumps in addition to continuous diffusion',
  },
  {
    id: 'regime-switching',
    name: 'Regime-Switching',
    description: 'Different market regimes (bull/bear) with state transitions',
  },
];

export function MonteCarloAdvanced() {
  const [params, setParams] = useState<MonteCarloParams>({
    ticker: 'AAPL',
    method: 'garch',
    n_simulations: 1000,
    horizon: 252, // 1 year trading days
  });

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await simulationApi.runMonteCarlo(params);
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

          <div className="col-span-2">
            <label className="block text-sm text-gray-400 mb-2">Forecast Horizon (days)</label>
            <input
              type="number"
              value={params.horizon}
              onChange={(e) => setParams({ ...params, horizon: parseInt(e.target.value) })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              min="1"
              max="1000"
            />
            <p className="text-xs text-gray-500 mt-1">252 days = 1 year, 21 days = 1 month</p>
          </div>
        </div>

        {/* Method Selection */}
        <div className="mb-6">
          <label className="block text-sm text-gray-400 mb-3">Simulation Method</label>
          <div className="space-y-2">
            {MONTE_CARLO_METHODS.map((method) => (
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
              Running Monte Carlo...
            </>
          ) : (
            <>Run Monte Carlo Simulation</>
          )}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Fan Chart (Percentile Bands) */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Price Path Forecast (Fan Chart)</h3>
            {results.fan_chart && (
              <Plot
                data={[
                  // Historical
                  {
                    x: results.fan_chart.dates?.slice(0, -params.horizon),
                    y: results.fan_chart.historical,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Historical',
                    line: { color: '#9ca3af', width: 2 },
                  },
                  // Forecast median
                  {
                    x: results.fan_chart.dates?.slice(-params.horizon),
                    y: results.fan_chart.median,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Median',
                    line: { color: '#3b82f6', width: 2 },
                  },
                  // 95% band
                  {
                    x: results.fan_chart.dates?.slice(-params.horizon),
                    y: results.fan_chart.p95,
                    type: 'scatter',
                    mode: 'lines',
                    name: '95th percentile',
                    line: { color: '#3b82f6', width: 0 },
                    showlegend: false,
                  },
                  {
                    x: results.fan_chart.dates?.slice(-params.horizon),
                    y: results.fan_chart.p5,
                    type: 'scatter',
                    mode: 'lines',
                    name: '5th-95th percentile',
                    fill: 'tonexty',
                    fillcolor: 'rgba(59, 130, 246, 0.2)',
                    line: { color: '#3b82f6', width: 0 },
                  },
                  // 75% band
                  {
                    x: results.fan_chart.dates?.slice(-params.horizon),
                    y: results.fan_chart.p75,
                    type: 'scatter',
                    mode: 'lines',
                    name: '75th percentile',
                    line: { color: '#3b82f6', width: 0 },
                    showlegend: false,
                  },
                  {
                    x: results.fan_chart.dates?.slice(-params.horizon),
                    y: results.fan_chart.p25,
                    type: 'scatter',
                    mode: 'lines',
                    name: '25th-75th percentile',
                    fill: 'tonexty',
                    fillcolor: 'rgba(59, 130, 246, 0.4)',
                    line: { color: '#3b82f6', width: 0 },
                  },
                ]}
                layout={{
                  paper_bgcolor: '#1a1f2e',
                  plot_bgcolor: '#1a1f2e',
                  font: { color: '#e0e0e0', family: 'monospace' },
                  xaxis: { title: 'Date', gridcolor: '#2a3142' },
                  yaxis: { title: 'Price ($)', gridcolor: '#2a3142' },
                  margin: { t: 20, b: 50, l: 60, r: 20 },
                  autosize: true,
                  legend: { x: 0, y: 1 },
                }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%', height: '500px' }}
              />
            )}
          </div>

          {/* Terminal Value Distribution */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Terminal Value Distribution</h3>
            {results.terminal_distribution && (
              <Plot
                data={[
                  {
                    x: results.terminal_distribution.values,
                    type: 'histogram',
                    nbinsx: 50,
                    marker: { color: '#10b981' },
                    name: 'Terminal Values',
                  },
                ]}
                layout={{
                  paper_bgcolor: '#1a1f2e',
                  plot_bgcolor: '#1a1f2e',
                  font: { color: '#e0e0e0', family: 'monospace' },
                  xaxis: { title: 'Price ($)', gridcolor: '#2a3142' },
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

          {/* Model Statistics */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Model Diagnostics</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Expected Return</div>
                <div className="text-2xl font-bold text-white">
                  {results.model_stats?.expected_return?.toFixed(2) || '0.00'}%
                </div>
              </div>
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Volatility</div>
                <div className="text-2xl font-bold text-white">
                  {results.model_stats?.volatility?.toFixed(2) || '0.00'}%
                </div>
              </div>
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">VaR (95%)</div>
                <div className="text-2xl font-bold text-red-400">
                  {results.model_stats?.var_95?.toFixed(2) || '0.00'}%
                </div>
              </div>
            </div>

            {/* Model Parameters */}
            {results.model_parameters && (
              <div className="mt-4 p-3 bg-blue-900/20 border border-blue-700 rounded-lg">
                <div className="text-sm font-semibold text-white mb-2">Model Parameters:</div>
                <div className="text-xs text-gray-300 space-y-1 font-mono">
                  {Object.entries(results.model_parameters).map(([key, value]: any) => (
                    <div key={key}>
                      {key}: {value?.toFixed(4) || 'N/A'}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
