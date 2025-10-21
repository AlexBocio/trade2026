/**
 * Walk-Forward Comparison Component
 * Compares Anchored, Rolling, and Expanding window walk-forward methods
 */

import { useState } from 'react';
import { Loader, Info } from 'lucide-react';
import Plot from 'react-plotly.js';
import { simulationApi, type WalkForwardParams } from '../../api/simulationApi';

const STRATEGY_TYPES = [
  { id: 'momentum', name: 'Momentum Strategy', description: 'Buy winners, sell losers' },
  { id: 'mean-reversion', name: 'Mean Reversion', description: 'Buy oversold, sell overbought' },
  { id: 'custom', name: 'Custom Strategy', description: 'User-defined strategy' },
];

const WF_METHODS = [
  { id: 'anchored', name: 'Anchored', description: 'Fixed start date, expanding train set' },
  { id: 'rolling', name: 'Rolling', description: 'Fixed-size train window, rolls forward' },
  { id: 'expanding', name: 'Expanding', description: 'Start date fixed, train set grows' },
];

export function WalkForwardComparison() {
  const [params, setParams] = useState<WalkForwardParams>({
    ticker: 'AAPL',
    strategy_type: 'momentum',
    methods: ['rolling'],
    train_size: 252,
    test_size: 63,
    step: 21,
  });

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const toggleMethod = (methodId: string) => {
    if (params.methods.includes(methodId as any)) {
      setParams({ ...params, methods: params.methods.filter((m) => m !== methodId) as any });
    } else {
      setParams({ ...params, methods: [...params.methods, methodId] as any });
    }
  };

  const handleRun = async () => {
    if (params.methods.length === 0) {
      setError('Please select at least one walk-forward method');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await simulationApi.compareWalkForward(params);
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
            <label className="block text-sm text-gray-400 mb-2">Strategy Type</label>
            <select
              value={params.strategy_type}
              onChange={(e) => setParams({ ...params, strategy_type: e.target.value as any })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            >
              {STRATEGY_TYPES.map((strategy) => (
                <option key={strategy.id} value={strategy.id}>
                  {strategy.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Train Size (days)</label>
            <input
              type="number"
              value={params.train_size}
              onChange={(e) => setParams({ ...params, train_size: parseInt(e.target.value) })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              min="20"
              max="1000"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Test Size (days)</label>
            <input
              type="number"
              value={params.test_size}
              onChange={(e) => setParams({ ...params, test_size: parseInt(e.target.value) })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              min="5"
              max="252"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-sm text-gray-400 mb-2">Step Size (days)</label>
            <input
              type="number"
              value={params.step}
              onChange={(e) => setParams({ ...params, step: parseInt(e.target.value) })}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
              min="1"
              max="100"
            />
            <p className="text-xs text-gray-500 mt-1">How many days to step forward between tests</p>
          </div>
        </div>

        {/* Method Selection (Multiple) */}
        <div className="mb-6">
          <label className="block text-sm text-gray-400 mb-3">
            Walk-Forward Methods (select multiple to compare)
          </label>
          <div className="space-y-2">
            {WF_METHODS.map((method) => (
              <label
                key={method.id}
                className="flex items-start gap-3 p-3 bg-dark-bg rounded-lg cursor-pointer hover:bg-dark-border transition"
              >
                <input
                  type="checkbox"
                  checked={params.methods.includes(method.id as any)}
                  onChange={() => toggleMethod(method.id)}
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
          disabled={loading || params.methods.length === 0}
          className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Running Comparison...
            </>
          ) : (
            <>Run Walk-Forward Comparison</>
          )}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Performance Comparison Table */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Performance Comparison</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-400 border-b border-dark-border">
                    <th className="pb-2">Method</th>
                    <th className="pb-2 text-right">Total Return</th>
                    <th className="pb-2 text-right">Sharpe Ratio</th>
                    <th className="pb-2 text-right">Max Drawdown</th>
                    <th className="pb-2 text-right">Win Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {results.comparison?.map((method: any) => (
                    <tr key={method.name} className="border-b border-dark-border">
                      <td className="py-2 text-white font-semibold capitalize">{method.name}</td>
                      <td className={`py-2 text-right font-mono ${method.total_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {method.total_return >= 0 ? '+' : ''}
                        {method.total_return?.toFixed(2)}%
                      </td>
                      <td className="py-2 text-right font-mono text-white">
                        {method.sharpe_ratio?.toFixed(2)}
                      </td>
                      <td className="py-2 text-right font-mono text-red-400">
                        {method.max_drawdown?.toFixed(2)}%
                      </td>
                      <td className="py-2 text-right font-mono text-white">
                        {method.win_rate?.toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Winner Declaration */}
            {results.winner && (
              <div className="mt-4 p-3 bg-green-900/30 border border-green-700 rounded-lg">
                <div className="text-sm font-semibold text-green-400">
                  🏆 Best Method: {results.winner.name} (Sharpe: {results.winner.sharpe_ratio?.toFixed(2)})
                </div>
              </div>
            )}
          </div>

          {/* Cumulative Returns Chart */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Cumulative Returns</h3>
            {results.cumulative_returns && (
              <Plot
                data={results.cumulative_returns.map((method: any, index: number) => ({
                  x: method.dates,
                  y: method.returns,
                  type: 'scatter',
                  mode: 'lines',
                  name: method.name,
                  line: {
                    color: ['#3b82f6', '#10b981', '#f59e0b'][index % 3],
                    width: 2,
                  },
                }))}
                layout={{
                  paper_bgcolor: '#1a1f2e',
                  plot_bgcolor: '#1a1f2e',
                  font: { color: '#e0e0e0', family: 'monospace' },
                  xaxis: { title: 'Date', gridcolor: '#2a3142' },
                  yaxis: { title: 'Cumulative Return (%)', gridcolor: '#2a3142' },
                  margin: { t: 20, b: 50, l: 60, r: 20 },
                  autosize: true,
                  legend: { x: 0, y: 1 },
                }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%', height: '500px' }}
              />
            )}
          </div>

          {/* Parameter Stability Heatmap */}
          {results.parameter_stability && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Parameter Stability</h3>
              <p className="text-sm text-gray-400 mb-4">
                Shows how consistent optimal parameters are across different time periods
              </p>
              <Plot
                data={[
                  {
                    z: results.parameter_stability.heatmap,
                    x: results.parameter_stability.periods,
                    y: results.parameter_stability.params,
                    type: 'heatmap',
                    colorscale: 'Viridis',
                    showscale: true,
                  },
                ]}
                layout={{
                  paper_bgcolor: '#1a1f2e',
                  plot_bgcolor: '#1a1f2e',
                  font: { color: '#e0e0e0', family: 'monospace' },
                  xaxis: { title: 'Period', gridcolor: '#2a3142' },
                  yaxis: { title: 'Parameter', gridcolor: '#2a3142' },
                  margin: { t: 20, b: 50, l: 100, r: 20 },
                  autosize: true,
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
