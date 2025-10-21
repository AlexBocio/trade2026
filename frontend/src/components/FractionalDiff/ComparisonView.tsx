/**
 * Comparison View Component
 * Compare multiple d values side by side
 */

import { useState } from 'react';
import { Loader, Info, Plus, Trash2 } from 'lucide-react';
import Plot from 'react-plotly.js';
import { fractionalDiffApi, type CompareParams } from '../../api/fractionalDiffApi';

interface ComparisonResult {
  d: number;
  transformed_series: number[];
  stationarity: {
    is_stationary: boolean;
    p_value: number;
    statistic: number;
  };
  memory_retained: number;
  volatility: number;
  correlation_with_original: number;
}

interface ComparisonResults {
  ticker: string;
  dates: string[];
  original: number[];
  comparisons: ComparisonResult[];
}

export function ComparisonView() {
  const [ticker, setTicker] = useState('SPY');
  const [startDate, setStartDate] = useState('2020-01-01');
  const [dValues, setDValues] = useState<number[]>([0.0, 0.3, 0.5, 0.7, 1.0]);
  const [newDValue, setNewDValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ComparisonResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  const addDValue = () => {
    const d = parseFloat(newDValue);
    if (!isNaN(d) && d >= 0 && d <= 1 && !dValues.includes(d)) {
      setDValues([...dValues, d].sort((a, b) => a - b));
      setNewDValue('');
    }
  };

  const removeDValue = (d: number) => {
    setDValues(dValues.filter((v) => v !== d));
  };

  const handleCompare = async () => {
    if (dValues.length === 0) {
      setError('Please add at least one d value to compare');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await fractionalDiffApi.compare({
        ticker,
        d_values: dValues,
        start_date: startDate,
      });
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
        <h2 className="text-2xl font-semibold text-white mb-4">Compare d Values</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Ticker Input */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Ticker Symbol</label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-blue-500"
              placeholder="SPY"
            />
          </div>

          {/* Start Date */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* d Values Manager */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">d Values to Compare</label>

          {/* Current d Values */}
          <div className="flex flex-wrap gap-2 mb-3">
            {dValues.map((d) => (
              <div
                key={d}
                className="flex items-center gap-2 bg-blue-900/30 border border-blue-700 rounded-lg px-3 py-1"
              >
                <span className="text-blue-400 font-mono font-semibold">{d.toFixed(2)}</span>
                <button
                  onClick={() => removeDValue(d)}
                  className="text-blue-400 hover:text-red-400 transition"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>

          {/* Add New d Value */}
          <div className="flex gap-2">
            <input
              type="number"
              value={newDValue}
              onChange={(e) => setNewDValue(e.target.value)}
              className="flex-1 px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-blue-500"
              placeholder="Enter d value (0.0 - 1.0)"
              min="0"
              max="1"
              step="0.1"
              onKeyPress={(e) => e.key === 'Enter' && addDValue()}
            />
            <button
              onClick={addDValue}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Add multiple d values to compare their effects side by side
          </p>
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
          onClick={handleCompare}
          disabled={loading || dValues.length === 0}
          className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Comparing...
            </>
          ) : (
            <>Compare {dValues.length} d Values</>
          )}
        </button>
      </div>

      {/* Results Display */}
      {results && (
        <div className="space-y-6">
          {/* Time Series Comparison Chart */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-xl font-semibold text-white mb-4">
              Transformed Series Comparison
            </h3>
            <Plot
              data={[
                {
                  x: results.dates,
                  y: results.original,
                  name: 'Original',
                  type: 'scatter',
                  mode: 'lines',
                  line: { color: '#9CA3AF', width: 2 },
                },
                ...results.comparisons.map((comp, index) => ({
                  x: results.dates,
                  y: comp.transformed_series,
                  name: `d=${comp.d.toFixed(2)}`,
                  type: 'scatter' as const,
                  mode: 'lines' as const,
                  line: {
                    color: ['#60A5FA', '#34D399', '#F472B6', '#FBBF24', '#A78BFA'][index % 5],
                    width: 2,
                  },
                })),
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
              style={{ width: '100%', height: '500px' }}
            />
          </div>

          {/* Comparison Table */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Metrics Comparison</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-400 border-b border-dark-border">
                    <th className="pb-3">d Value</th>
                    <th className="pb-3 text-right">Status</th>
                    <th className="pb-3 text-right">p-value</th>
                    <th className="pb-3 text-right">Memory</th>
                    <th className="pb-3 text-right">Volatility</th>
                    <th className="pb-3 text-right">Correlation</th>
                  </tr>
                </thead>
                <tbody>
                  {results.comparisons.map((comp, index) => (
                    <tr key={index} className="border-b border-dark-border">
                      <td className="py-3">
                        <span className="text-white font-mono font-semibold">
                          {comp.d.toFixed(2)}
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        <span
                          className={`px-2 py-1 rounded text-xs font-semibold ${
                            comp.stationarity.is_stationary
                              ? 'bg-green-900/30 text-green-400 border border-green-700'
                              : 'bg-red-900/30 text-red-400 border border-red-700'
                          }`}
                        >
                          {comp.stationarity.is_stationary ? '✓ Stationary' : '✗ Non-Stationary'}
                        </span>
                      </td>
                      <td className="py-3 text-right text-white font-mono">
                        {comp.stationarity.p_value.toFixed(4)}
                      </td>
                      <td className="py-3 text-right">
                        <span className="text-green-400 font-mono font-semibold">
                          {(comp.memory_retained * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-3 text-right text-white font-mono">
                        {comp.volatility.toFixed(4)}
                      </td>
                      <td className="py-3 text-right text-white font-mono">
                        {comp.correlation_with_original.toFixed(4)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Metrics Bar Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Memory Retention Bar Chart */}
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h4 className="text-lg font-medium text-white mb-4">Memory Retention</h4>
              <Plot
                data={[
                  {
                    x: results.comparisons.map((c) => `d=${c.d.toFixed(2)}`),
                    y: results.comparisons.map((c) => c.memory_retained * 100),
                    type: 'bar',
                    marker: { color: '#34D399' },
                  },
                ]}
                layout={{
                  paper_bgcolor: '#1a1f2e',
                  plot_bgcolor: '#1a1f2e',
                  font: { color: '#e0e0e0', family: 'monospace' },
                  xaxis: { title: 'd Value', gridcolor: '#2a3142' },
                  yaxis: { title: 'Memory Retained (%)', gridcolor: '#2a3142', range: [0, 100] },
                  margin: { t: 20, r: 20, b: 60, l: 60 },
                  autosize: true,
                  showlegend: false,
                }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%', height: '300px' }}
              />
            </div>

            {/* p-value Bar Chart */}
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h4 className="text-lg font-medium text-white mb-4">Stationarity p-value</h4>
              <Plot
                data={[
                  {
                    x: results.comparisons.map((c) => `d=${c.d.toFixed(2)}`),
                    y: results.comparisons.map((c) => c.stationarity.p_value),
                    type: 'bar',
                    marker: {
                      color: results.comparisons.map((c) =>
                        c.stationarity.is_stationary ? '#34D399' : '#F87171'
                      ),
                    },
                  },
                ]}
                layout={{
                  paper_bgcolor: '#1a1f2e',
                  plot_bgcolor: '#1a1f2e',
                  font: { color: '#e0e0e0', family: 'monospace' },
                  xaxis: { title: 'd Value', gridcolor: '#2a3142' },
                  yaxis: { title: 'p-value', gridcolor: '#2a3142' },
                  shapes: [
                    {
                      type: 'line',
                      x0: -0.5,
                      x1: results.comparisons.length - 0.5,
                      y0: 0.05,
                      y1: 0.05,
                      line: { color: '#EF4444', dash: 'dash', width: 2 },
                    },
                  ],
                  margin: { t: 20, r: 20, b: 60, l: 60 },
                  autosize: true,
                  showlegend: false,
                }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%', height: '300px' }}
              />
            </div>
          </div>

          {/* Recommendation Box */}
          <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-6">
            <h4 className="text-lg font-semibold text-blue-400 mb-2">Recommendation</h4>
            <p className="text-gray-300">
              {getBestRecommendation(results.comparisons)}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper function to get best recommendation
function getBestRecommendation(comparisons: ComparisonResult[]): string {
  const stationary = comparisons.filter((c) => c.stationarity.is_stationary);

  if (stationary.length === 0) {
    return 'None of the tested d values achieve stationarity. Try increasing d values or check your data quality.';
  }

  // Find the stationary d with highest memory retention
  const best = stationary.reduce((prev, curr) =>
    curr.memory_retained > prev.memory_retained ? curr : prev
  );

  return `For optimal balance between stationarity and memory preservation, use d=${best.d.toFixed(
    3
  )} which retains ${(best.memory_retained * 100).toFixed(
    1
  )}% of memory while achieving stationarity (p-value: ${best.stationarity.p_value.toFixed(4)}).`;
}
