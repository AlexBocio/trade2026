/**
 * Synthetic Data Generator Component
 * Uses GAN or VAE to generate realistic synthetic market data
 */

import { useState } from 'react';
import { Loader, Info, Download } from 'lucide-react';
import Plot from 'react-plotly.js';
import { simulationApi, type SyntheticParams } from '../../api/simulationApi';

const GENERATION_METHODS = [
  {
    id: 'gan',
    name: 'GAN (Generative Adversarial Network)',
    description: 'Deep learning model that learns to generate realistic price data',
  },
  {
    id: 'vae',
    name: 'VAE (Variational Autoencoder)',
    description: 'Probabilistic model that generates data from learned latent space',
  },
];

export function SyntheticDataGenerator() {
  const [params, setParams] = useState<SyntheticParams>({
    ticker: 'AAPL',
    method: 'gan',
    n_samples: 1000,
    validation_tests: true,
  });

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await simulationApi.generateSynthetic(params);
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'Backend not running! Start: python backend/simulation_engine/app.py');
    } finally {
      setLoading(false);
    }
  };

  const downloadSyntheticData = () => {
    if (!results?.synthetic_data) return;

    const csvContent = [
      ['date', 'price', 'return'].join(','),
      ...results.synthetic_data.map((row: any) => [row.date, row.price, row.return].join(',')),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `synthetic_${params.ticker}_${params.method}_${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Configuration Panel */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Configuration</h3>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Ticker (Training Data)</label>
            <input
              type="text"
              value={params.ticker}
              onChange={(e) => setParams({ ...params, ticker: e.target.value.toUpperCase() })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              placeholder="AAPL"
            />
            <p className="text-xs text-gray-500 mt-1">Historical data used to train the model</p>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Number of Samples</label>
            <input
              type="number"
              value={params.n_samples}
              onChange={(e) => setParams({ ...params, n_samples: parseInt(e.target.value) })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              min="100"
              max="10000"
              step="100"
            />
            <p className="text-xs text-gray-500 mt-1">How many synthetic data points to generate</p>
          </div>
        </div>

        {/* Method Selection */}
        <div className="mb-6">
          <label className="block text-sm text-gray-400 mb-3">Generation Method</label>
          <div className="space-y-2">
            {GENERATION_METHODS.map((method) => (
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

        {/* Validation Tests Toggle */}
        <div className="mb-6">
          <label className="flex items-start gap-3 p-3 bg-dark-bg rounded-lg cursor-pointer">
            <input
              type="checkbox"
              checked={params.validation_tests}
              onChange={(e) => setParams({ ...params, validation_tests: e.target.checked })}
              className="mt-1"
            />
            <div className="flex-1">
              <div className="font-semibold text-white">Run Validation Tests</div>
              <div className="text-xs text-gray-400">
                Statistical tests to verify synthetic data quality (KS test, autocorrelation, etc.)
              </div>
            </div>
          </label>
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

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Generating Data...
            </>
          ) : (
            <>Generate Synthetic Data</>
          )}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Download Button */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">Generated {results.n_samples} samples</h3>
                <p className="text-sm text-gray-400">Synthetic data ready for download</p>
              </div>
              <button
                onClick={downloadSyntheticData}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition"
              >
                <Download className="w-5 h-5" />
                Download CSV
              </button>
            </div>
          </div>

          {/* Real vs Synthetic Comparison */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Real vs Synthetic Comparison</h3>
            {results.comparison && (
              <Plot
                data={[
                  {
                    x: results.comparison.real_dates,
                    y: results.comparison.real_prices,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Real Data',
                    line: { color: '#3b82f6', width: 2 },
                  },
                  {
                    x: results.comparison.synthetic_dates,
                    y: results.comparison.synthetic_prices,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Synthetic Data',
                    line: { color: '#10b981', width: 2, dash: 'dot' },
                  },
                ]}
                layout={{
                  paper_bgcolor: '#1a1f2e',
                  plot_bgcolor: '#1a1f2e',
                  font: { color: '#e0e0e0', family: 'monospace' },
                  xaxis: { title: 'Time Step', gridcolor: '#2a3142' },
                  yaxis: { title: 'Price ($)', gridcolor: '#2a3142' },
                  margin: { t: 20, b: 50, l: 60, r: 20 },
                  autosize: true,
                  legend: { x: 0, y: 1 },
                }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%', height: '400px' }}
              />
            )}
          </div>

          {/* Distribution Comparison */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Return Distribution Comparison</h3>
            {results.distributions && (
              <Plot
                data={[
                  {
                    x: results.distributions.real_returns,
                    type: 'histogram',
                    name: 'Real Returns',
                    opacity: 0.7,
                    marker: { color: '#3b82f6' },
                    nbinsx: 50,
                  },
                  {
                    x: results.distributions.synthetic_returns,
                    type: 'histogram',
                    name: 'Synthetic Returns',
                    opacity: 0.7,
                    marker: { color: '#10b981' },
                    nbinsx: 50,
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
                  barmode: 'overlay',
                  legend: { x: 0, y: 1 },
                }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%', height: '400px' }}
              />
            )}
          </div>

          {/* Statistical Moments Comparison */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Statistical Moments</h3>
            <div className="grid grid-cols-4 gap-4">
              {['mean', 'std', 'skew', 'kurtosis'].map((moment) => (
                <div key={moment} className="bg-dark-bg rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-2 capitalize">{moment}</div>
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-400">Real:</span>
                      <span className="text-blue-400 font-mono">
                        {results.moments?.real[moment]?.toFixed(3) || 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-400">Synthetic:</span>
                      <span className="text-green-400 font-mono">
                        {results.moments?.synthetic[moment]?.toFixed(3) || 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Validation Tests */}
          {params.validation_tests && results.validation && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Validation Tests</h3>
              <div className="space-y-3">
                {Object.entries(results.validation).map(([test, result]: any) => (
                  <div key={test} className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
                    <div>
                      <div className="font-semibold text-white capitalize">{test.replace('_', ' ')}</div>
                      <div className="text-xs text-gray-400">
                        {result.statistic && `Statistic: ${result.statistic.toFixed(4)}`}
                        {result.p_value && ` | p-value: ${result.p_value.toFixed(4)}`}
                      </div>
                    </div>
                    <div
                      className={`px-3 py-1 rounded text-sm font-semibold ${
                        result.passed
                          ? 'bg-green-900/30 text-green-400 border border-green-700'
                          : 'bg-red-900/30 text-red-400 border border-red-700'
                      }`}
                    >
                      {result.passed ? '✓ Passed' : '✗ Failed'}
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-4 p-3 bg-blue-900/20 border border-blue-700 rounded-lg">
                <p className="text-sm text-gray-300">
                  <strong>Interpretation:</strong> Validation tests check if synthetic data has similar
                  statistical properties to real data. Passed tests indicate high-quality synthetic data.
                </p>
              </div>
            </div>
          )}

          {/* Autocorrelation Comparison */}
          {results.autocorrelation && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Autocorrelation Function</h3>
              <Plot
                data={[
                  {
                    x: results.autocorrelation.lags,
                    y: results.autocorrelation.real,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Real Data',
                    line: { color: '#3b82f6', width: 2 },
                  },
                  {
                    x: results.autocorrelation.lags,
                    y: results.autocorrelation.synthetic,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Synthetic Data',
                    line: { color: '#10b981', width: 2 },
                  },
                ]}
                layout={{
                  paper_bgcolor: '#1a1f2e',
                  plot_bgcolor: '#1a1f2e',
                  font: { color: '#e0e0e0', family: 'monospace' },
                  xaxis: { title: 'Lag', gridcolor: '#2a3142' },
                  yaxis: { title: 'Autocorrelation', gridcolor: '#2a3142', range: [-0.2, 1] },
                  margin: { t: 20, b: 50, l: 60, r: 20 },
                  autosize: true,
                  legend: { x: 0, y: 1 },
                }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%', height: '400px' }}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
