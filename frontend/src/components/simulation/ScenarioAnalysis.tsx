/**
 * Scenario Analysis Component
 * Stress testing portfolios against historical crisis scenarios
 */

import { useState } from 'react';
import { Loader, Info, Plus, Trash2 } from 'lucide-react';
import Plot from 'react-plotly.js';
import { simulationApi, type ScenarioParams } from '../../api/simulationApi';

const PREDEFINED_SCENARIOS = [
  { id: '2008', name: '2008 Financial Crisis', description: 'Subprime mortgage collapse, banking crisis' },
  { id: '2020', name: '2020 COVID-19 Crash', description: 'Pandemic-induced market crash' },
  { id: 'dotcom', name: 'Dot-com Bubble (2000)', description: 'Tech stock collapse' },
  { id: '1987', name: 'Black Monday (1987)', description: 'Single-day market crash' },
  { id: 'custom', name: 'Custom Scenario', description: 'Define your own shocks' },
];

export function ScenarioAnalysis() {
  const [portfolio, setPortfolio] = useState<{ ticker: string; weight: number }[]>([
    { ticker: 'AAPL', weight: 0.25 },
    { ticker: 'MSFT', weight: 0.25 },
    { ticker: 'GOOGL', weight: 0.25 },
    { ticker: 'AMZN', weight: 0.25 },
  ]);

  const [selectedScenarios, setSelectedScenarios] = useState<string[]>(['2008', '2020']);
  const [customShocks, setCustomShocks] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const addPosition = () => {
    setPortfolio([...portfolio, { ticker: '', weight: 0 }]);
  };

  const removePosition = (index: number) => {
    setPortfolio(portfolio.filter((_, i) => i !== index));
  };

  const updatePosition = (index: number, field: 'ticker' | 'weight', value: string | number) => {
    const updated = [...portfolio];
    updated[index] = { ...updated[index], [field]: value };
    setPortfolio(updated);
  };

  const toggleScenario = (scenarioId: string) => {
    if (selectedScenarios.includes(scenarioId)) {
      setSelectedScenarios(selectedScenarios.filter((s) => s !== scenarioId));
    } else {
      setSelectedScenarios([...selectedScenarios, scenarioId]);
    }
  };

  const handleRun = async () => {
    if (selectedScenarios.length === 0) {
      setError('Please select at least one scenario');
      return;
    }

    const totalWeight = portfolio.reduce((sum, p) => sum + p.weight, 0);
    if (Math.abs(totalWeight - 1.0) > 0.01) {
      setError('Portfolio weights must sum to 1.0');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const params: ScenarioParams = {
        portfolio,
        scenarios: selectedScenarios as any,
        custom_shocks: selectedScenarios.includes('custom') ? customShocks : undefined,
      };

      const data = await simulationApi.runScenario(params);
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'Backend not running! Start: python backend/simulation_engine/app.py');
    } finally {
      setLoading(false);
    }
  };

  const totalWeight = portfolio.reduce((sum, p) => sum + p.weight, 0);

  return (
    <div className="space-y-6">
      {/* Portfolio Builder */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Portfolio Composition</h3>
          <button
            onClick={addPosition}
            className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-semibold transition"
          >
            <Plus className="w-4 h-4" />
            Add Position
          </button>
        </div>

        <div className="space-y-3 mb-4">
          {portfolio.map((position, index) => (
            <div key={index} className="flex items-center gap-3">
              <input
                type="text"
                value={position.ticker}
                onChange={(e) => updatePosition(index, 'ticker', e.target.value.toUpperCase())}
                className="flex-1 px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                placeholder="Ticker"
              />
              <input
                type="number"
                value={position.weight}
                onChange={(e) => updatePosition(index, 'weight', parseFloat(e.target.value) || 0)}
                className="w-32 px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                placeholder="Weight"
                step="0.01"
                min="0"
                max="1"
              />
              <button
                onClick={() => removePosition(index)}
                className="p-2 text-red-400 hover:bg-red-900/30 rounded-lg transition"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          ))}
        </div>

        <div className="text-sm">
          <span className="text-gray-400">Total Weight: </span>
          <span
            className={`font-mono font-bold ${
              Math.abs(totalWeight - 1.0) < 0.01 ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {totalWeight.toFixed(3)}
          </span>
          {Math.abs(totalWeight - 1.0) > 0.01 && (
            <span className="text-red-400 ml-2">(must equal 1.0)</span>
          )}
        </div>
      </div>

      {/* Scenario Selection */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Select Scenarios</h3>

        <div className="space-y-2 mb-4">
          {PREDEFINED_SCENARIOS.map((scenario) => (
            <label
              key={scenario.id}
              className="flex items-start gap-3 p-3 bg-dark-bg rounded-lg cursor-pointer hover:bg-dark-border transition"
            >
              <input
                type="checkbox"
                checked={selectedScenarios.includes(scenario.id)}
                onChange={() => toggleScenario(scenario.id)}
                className="mt-1"
              />
              <div className="flex-1">
                <div className="font-semibold text-white">{scenario.name}</div>
                <div className="text-xs text-gray-400">{scenario.description}</div>
              </div>
            </label>
          ))}
        </div>

        {/* Custom Scenario Shocks */}
        {selectedScenarios.includes('custom') && (
          <div className="mt-4 p-4 bg-dark-bg rounded-lg">
            <h4 className="text-sm font-semibold text-white mb-3">Custom Shocks (% change)</h4>
            <div className="space-y-2">
              {portfolio.map((position) => (
                <div key={position.ticker} className="flex items-center gap-3">
                  <span className="font-mono text-white w-20">{position.ticker}:</span>
                  <input
                    type="number"
                    value={customShocks[position.ticker] || 0}
                    onChange={(e) =>
                      setCustomShocks({ ...customShocks, [position.ticker]: parseFloat(e.target.value) || 0 })
                    }
                    className="flex-1 px-3 py-2 bg-dark-card border border-dark-border rounded-lg text-white"
                    placeholder="0"
                    step="0.1"
                  />
                  <span className="text-gray-400">%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error Banner */}
        {error && (
          <div className="mt-4 bg-red-900/30 border border-red-700 rounded-lg p-4">
            <div className="flex items-center gap-2 text-red-400">
              <Info className="w-5 h-5" />
              <span className="font-semibold">{error}</span>
            </div>
          </div>
        )}

        {/* Run Button */}
        <button
          onClick={handleRun}
          disabled={loading || selectedScenarios.length === 0}
          className="mt-4 w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Running Scenario Analysis...
            </>
          ) : (
            <>Run Scenario Analysis</>
          )}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Scenario Impact Table */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Scenario Impact</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-400 border-b border-dark-border">
                    <th className="pb-2">Scenario</th>
                    <th className="pb-2 text-right">Portfolio Return</th>
                    <th className="pb-2 text-right">VaR (95%)</th>
                    <th className="pb-2 text-right">CVaR</th>
                    <th className="pb-2 text-right">Max Drawdown</th>
                  </tr>
                </thead>
                <tbody>
                  {results.scenarios?.map((scenario: any) => (
                    <tr key={scenario.name} className="border-b border-dark-border">
                      <td className="py-2 text-white font-semibold">{scenario.name}</td>
                      <td className={`py-2 text-right font-mono ${scenario.return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {scenario.return >= 0 ? '+' : ''}
                        {scenario.return?.toFixed(2)}%
                      </td>
                      <td className="py-2 text-right font-mono text-red-400">
                        {scenario.var_95?.toFixed(2)}%
                      </td>
                      <td className="py-2 text-right font-mono text-red-400">
                        {scenario.cvar?.toFixed(2)}%
                      </td>
                      <td className="py-2 text-right font-mono text-red-400">
                        {scenario.max_drawdown?.toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Comparison Bar Chart */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Returns by Scenario</h3>
            {results.scenarios && (
              <Plot
                data={[
                  {
                    x: results.scenarios.map((s: any) => s.name),
                    y: results.scenarios.map((s: any) => s.return),
                    type: 'bar',
                    marker: {
                      color: results.scenarios.map((s: any) => (s.return >= 0 ? '#10b981' : '#ef4444')),
                    },
                  },
                ]}
                layout={{
                  paper_bgcolor: '#1a1f2e',
                  plot_bgcolor: '#1a1f2e',
                  font: { color: '#e0e0e0', family: 'monospace' },
                  xaxis: { title: 'Scenario', gridcolor: '#2a3142' },
                  yaxis: { title: 'Portfolio Return (%)', gridcolor: '#2a3142', zeroline: true },
                  margin: { t: 20, b: 100, l: 60, r: 20 },
                  autosize: true,
                  showlegend: false,
                }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%', height: '400px' }}
              />
            )}
          </div>

          {/* Stress Test Heatmap */}
          {results.heatmap && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Position-Level Impact</h3>
              <Plot
                data={[
                  {
                    z: results.heatmap.values,
                    x: results.heatmap.scenarios,
                    y: results.heatmap.tickers,
                    type: 'heatmap',
                    colorscale: 'RdYlGn',
                    showscale: true,
                    reversescale: false,
                  },
                ]}
                layout={{
                  paper_bgcolor: '#1a1f2e',
                  plot_bgcolor: '#1a1f2e',
                  font: { color: '#e0e0e0', family: 'monospace' },
                  xaxis: { title: 'Scenario', gridcolor: '#2a3142' },
                  yaxis: { title: 'Ticker', gridcolor: '#2a3142' },
                  margin: { t: 20, b: 100, l: 80, r: 20 },
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
