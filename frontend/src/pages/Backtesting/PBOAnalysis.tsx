/**
 * PBO Analysis - Probability of Backtest Overfitting
 * Measure the likelihood that backtest results are due to luck and overfitting
 */

import { useState } from 'react';
import { ArrowLeft, Loader, Info } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Plot from 'react-plotly.js';
import { pboApi, type PBOResponse, type DeflatedSharpeResponse, type CombinatorialCVResponse, type StochasticDominanceResponse } from '../../api/pboApi';

type TabType = 'pbo' | 'deflated-sharpe' | 'cpcv-results' | 'stochastic-dominance';

const TABS = [
  { id: 'pbo', name: 'PBO Analysis', icon: '📊' },
  { id: 'deflated-sharpe', name: 'Deflated Sharpe', icon: '📉' },
  { id: 'cpcv-results', name: 'CPCV Results', icon: '🔄' },
  { id: 'stochastic-dominance', name: 'Stochastic Dominance', icon: '⚖️' },
];

export function PBOAnalysis() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('pbo');

  // Configuration state
  const [ticker, setTicker] = useState('SPY');
  const [strategy, setStrategy] = useState('momentum');
  const [fastPeriods, setFastPeriods] = useState('5, 10, 15, 20');
  const [slowPeriods, setSlowPeriods] = useState('20, 30, 40, 50');
  const [nSplits, setNSplits] = useState(10);
  const [embargoPct, setEmbargoPct] = useState(1);

  // Results state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pboResults, setPboResults] = useState<PBOResponse | null>(null);
  const [dsrResults, setDsrResults] = useState<DeflatedSharpeResponse | null>(null);
  const [cpcvResults, setCpcvResults] = useState<CombinatorialCVResponse | null>(null);
  const [sdResults, setSdResults] = useState<StochasticDominanceResponse | null>(null);

  const handleCalculatePBO = async () => {
    setLoading(true);
    setError(null);

    try {
      // Parse parameter grid
      const fastArray = fastPeriods.split(',').map(s => parseInt(s.trim()));
      const slowArray = slowPeriods.split(',').map(s => parseInt(s.trim()));

      const params = {
        ticker,
        strategy,
        param_grid: {
          fast_period: fastArray,
          slow_period: slowArray,
        },
        n_splits: nSplits,
        embargo_pct: embargoPct,
      };

      const data = await pboApi.calculatePBO(params);
      setPboResults(data);

      // Also calculate deflated sharpe automatically
      if (data.best_is_sharpe) {
        const dsrParams = {
          observed_sharpe: data.best_is_sharpe,
          n_trials: data.n_trials,
          n_observations: 252 * 5, // Assume 5 years of daily data
        };
        const dsrData = await pboApi.deflatedSharpe(dsrParams);
        setDsrResults(dsrData);
      }

      // Calculate CPCV for best IS parameters
      if (data.parameter_combinations && data.parameter_combinations.length > 0) {
        const bestParams = data.parameter_combinations.sort((a, b) => b.is_sharpe - a.is_sharpe)[0];
        const cpcvParams = {
          ticker,
          strategy,
          params: bestParams.params,
          n_splits: nSplits,
          embargo_pct: embargoPct,
        };
        const cpcvData = await pboApi.combinatorialCV(cpcvParams);
        setCpcvResults(cpcvData);
      }
    } catch (err: any) {
      setError(err.message || 'Backend not running! Start: python backend/pbo_service/app.py');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/backtesting')}
          className="p-2 hover:bg-dark-border rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5 text-gray-400" />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-white">Probability of Backtest Overfitting</h1>
          <p className="text-gray-400 mt-1">
            Measure the likelihood that your backtest results are due to luck and overfitting
          </p>
        </div>
      </div>

      {/* Educational Banner */}
      <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-blue-400 mb-2">Understanding PBO</h3>
        <p className="text-sm text-gray-300 mb-2">
          <strong>PBO (Probability of Backtest Overfitting)</strong> tells you how likely it is that
          your best-performing in-sample strategy will underperform out-of-sample.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-3">
          <div className="bg-green-900/30 border border-green-700 rounded p-3">
            <div className="text-green-400 font-bold">PBO &lt; 50%</div>
            <div className="text-xs text-gray-400">Strategy appears robust</div>
          </div>
          <div className="bg-yellow-900/30 border border-yellow-700 rounded p-3">
            <div className="text-yellow-400 font-bold">PBO ≈ 50%</div>
            <div className="text-xs text-gray-400">Uncertain - needs more validation</div>
          </div>
          <div className="bg-red-900/30 border border-red-700 rounded p-3">
            <div className="text-red-400 font-bold">PBO &gt; 50%</div>
            <div className="text-xs text-gray-400">High risk of overfitting</div>
          </div>
        </div>
      </div>

      {/* Configuration Card */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-2xl font-semibold text-white mb-4">Strategy Configuration</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Ticker Input */}
          <div>
            <label className="text-sm font-medium text-gray-300 mb-2 block">Ticker Symbol</label>
            <input
              type="text"
              className="w-full bg-dark-bg text-white border border-dark-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="SPY"
            />
          </div>

          {/* Strategy Selector */}
          <div>
            <label className="text-sm font-medium text-gray-300 mb-2 block">Primary Strategy</label>
            <select
              className="w-full bg-dark-bg text-white border border-dark-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
            >
              <option value="momentum">Momentum Crossover</option>
              <option value="mean_reversion">Mean Reversion</option>
              <option value="breakout">Breakout</option>
              <option value="trend_following">Trend Following</option>
            </select>
          </div>
        </div>

        {/* Parameter Grid */}
        <div className="mb-6">
          <label className="text-sm font-medium text-gray-300 mb-3 block">
            Parameter Grid (What to test)
          </label>
          <div className="bg-dark-bg rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Fast Period</label>
                <input
                  type="text"
                  className="w-full bg-gray-700 text-white border border-dark-border rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                  placeholder="5, 10, 15, 20"
                  value={fastPeriods}
                  onChange={(e) => setFastPeriods(e.target.value)}
                />
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Slow Period</label>
                <input
                  type="text"
                  className="w-full bg-gray-700 text-white border border-dark-border rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                  placeholder="20, 30, 40, 50"
                  value={slowPeriods}
                  onChange={(e) => setSlowPeriods(e.target.value)}
                />
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Total combinations: {fastPeriods.split(',').length} × {slowPeriods.split(',').length} ={' '}
              {fastPeriods.split(',').length * slowPeriods.split(',').length} strategies will be tested
            </p>
          </div>
        </div>

        {/* Advanced Settings */}
        <details className="mb-6">
          <summary className="text-sm font-medium text-gray-300 cursor-pointer mb-2">
            Advanced Settings
          </summary>
          <div className="bg-dark-bg rounded-lg p-4 space-y-3">
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Number of CV Splits</label>
              <input
                type="number"
                className="w-full bg-gray-700 text-white border border-dark-border rounded px-3 py-2 focus:outline-none focus:border-blue-500"
                value={nSplits}
                onChange={(e) => setNSplits(parseInt(e.target.value))}
                min={5}
                max={20}
              />
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Embargo Period (%)</label>
              <input
                type="number"
                className="w-full bg-gray-700 text-white border border-dark-border rounded px-3 py-2 focus:outline-none focus:border-blue-500"
                value={embargoPct}
                onChange={(e) => setEmbargoPct(parseFloat(e.target.value))}
                min={0}
                max={10}
                step={0.5}
              />
              <p className="text-xs text-gray-500 mt-1">
                Gap between train and test sets to prevent leakage
              </p>
            </div>
          </div>
        </details>

        {/* Error Banner */}
        {error && (
          <div className="mb-4 bg-red-900/30 border border-red-700 rounded-lg p-4">
            <div className="flex items-center gap-2 text-red-400">
              <Info className="w-5 h-5" />
              <span className="font-semibold">{error}</span>
            </div>
          </div>
        )}

        <button
          onClick={handleCalculatePBO}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Calculating PBO...
            </>
          ) : (
            'Calculate Probability of Overfitting'
          )}
        </button>
      </div>

      {/* Results */}
      {pboResults && (
        <>
          {/* Tab Navigation */}
          <div className="flex border-b border-dark-border">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                className={`px-6 py-3 font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
                onClick={() => setActiveTab(tab.id as TabType)}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {activeTab === 'pbo' && <PBOTab results={pboResults} />}
          {activeTab === 'deflated-sharpe' && <DeflatedSharpeTab results={dsrResults} />}
          {activeTab === 'cpcv-results' && <CPCVTab results={cpcvResults} />}
          {activeTab === 'stochastic-dominance' && <StochasticDominanceTab results={sdResults} />}
        </>
      )}
    </div>
  );
}

// PBO Tab Component
function PBOTab({ results }: { results: PBOResponse }) {
  const pbo = results.pbo;
  const pboPercentage = results.pbo_percentage;

  // Color based on PBO value
  const getColor = () => {
    if (pbo < 0.3) return { bg: 'bg-green-900/30', border: 'border-green-700', text: 'text-green-400' };
    if (pbo < 0.5) return { bg: 'bg-blue-900/30', border: 'border-blue-700', text: 'text-blue-400' };
    if (pbo < 0.7) return { bg: 'bg-yellow-900/30', border: 'border-yellow-700', text: 'text-yellow-400' };
    return { bg: 'bg-red-900/30', border: 'border-red-700', text: 'text-red-400' };
  };

  const colors = getColor();

  return (
    <div className="space-y-6 mt-6">
      {/* PBO Score Card */}
      <div className={`${colors.bg} border ${colors.border} rounded-lg p-8`}>
        <div className="text-center">
          <div className="text-sm text-gray-400 mb-2">Probability of Backtest Overfitting</div>
          <div className={`text-7xl font-bold ${colors.text} mb-4`}>{pboPercentage.toFixed(1)}%</div>
          <div className="text-xl text-gray-300 mb-6">{results.interpretation}</div>

          {/* Gauge Chart */}
          <div className="flex justify-center">
            <Plot
              data={[
                {
                  type: 'indicator',
                  mode: 'gauge+number',
                  value: pboPercentage,
                  gauge: {
                    axis: { range: [0, 100] },
                    bar: { color: pbo < 0.5 ? '#34D399' : '#EF4444' },
                    steps: [
                      { range: [0, 30], color: 'rgba(52, 211, 153, 0.2)' },
                      { range: [30, 50], color: 'rgba(96, 165, 250, 0.2)' },
                      { range: [50, 70], color: 'rgba(251, 191, 36, 0.2)' },
                      { range: [70, 100], color: 'rgba(239, 68, 68, 0.2)' },
                    ],
                    threshold: {
                      line: { color: 'white', width: 4 },
                      thickness: 0.75,
                      value: 50,
                    },
                  },
                },
              ]}
              layout={{
                paper_bgcolor: 'rgba(0,0,0,0)',
                font: { color: '#E5E7EB', size: 16 },
                margin: { t: 20, r: 20, b: 20, l: 20 },
                height: 250,
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%' }}
            />
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Rank Correlation</div>
          <div className="text-3xl font-bold text-white">{results.rank_correlation.toFixed(3)}</div>
          <div className="text-xs text-gray-500 mt-1">IS vs OOS performance correlation</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Trials Tested</div>
          <div className="text-3xl font-bold text-white">{results.n_trials}</div>
          <div className="text-xs text-gray-500 mt-1">Parameter combinations</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Best IS Sharpe</div>
          <div className="text-3xl font-bold text-white">{results.best_is_sharpe.toFixed(2)}</div>
          <div className="text-xs text-gray-500 mt-1">OOS: {results.best_is_oos_sharpe.toFixed(2)}</div>
        </div>
      </div>

      {/* Rank Plot: IS vs OOS */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-4">
          Rank Plot: In-Sample vs Out-of-Sample Performance
        </h3>
        <p className="text-sm text-gray-400 mb-4">
          If PBO is low, points should cluster around the diagonal (good IS → good OOS). If scattered, the
          strategy is overfit.
        </p>

        <Plot
          data={[
            {
              x: results.rank_plot_data.ranks_is,
              y: results.rank_plot_data.ranks_oos,
              mode: 'markers',
              type: 'scatter',
              marker: {
                size: 10,
                color: results.rank_plot_data.ranks_is,
                colorscale: 'Viridis',
                showscale: true,
                colorbar: { title: 'IS Rank' },
              },
              text: results.parameter_combinations.map(
                (p, i) =>
                  `Params: ${JSON.stringify(p.params)}<br>IS: ${p.is_sharpe.toFixed(2)}<br>OOS: ${p.oos_sharpe.toFixed(2)}`
              ),
              hovertemplate: '%{text}<extra></extra>',
            },
            {
              x: [0, results.n_trials],
              y: [0, results.n_trials],
              mode: 'lines',
              type: 'scatter',
              line: { color: '#EF4444', dash: 'dash', width: 2 },
              name: 'Perfect Correlation',
              showlegend: true,
            },
            {
              x: [results.rank_plot_data.ranks_is[results.rank_plot_data.best_is_idx]],
              y: [results.rank_plot_data.ranks_oos[results.rank_plot_data.best_is_idx]],
              mode: 'markers',
              type: 'scatter',
              marker: { size: 20, color: '#F59E0B', symbol: 'star' },
              name: 'Best IS Strategy',
              showlegend: true,
            },
          ]}
          layout={{
            paper_bgcolor: '#1a1f2e',
            plot_bgcolor: '#1a1f2e',
            font: { color: '#E5E7EB' },
            xaxis: {
              title: 'In-Sample Rank',
              gridcolor: '#374151',
              range: [0, results.n_trials + 1],
            },
            yaxis: {
              title: 'Out-of-Sample Rank',
              gridcolor: '#374151',
              range: [0, results.n_trials + 1],
            },
            legend: { bgcolor: '#1a1f2e', bordercolor: '#374151', borderwidth: 1 },
            margin: { t: 20, r: 20, b: 60, l: 60 },
          }}
          config={{ displayModeBar: true, displaylogo: false, responsive: true }}
          style={{ width: '100%', height: '500px' }}
        />
      </div>

      {/* Parameter Combinations Table */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-4">All Parameter Combinations</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-dark-bg">
              <tr>
                <th className="px-4 py-3 text-gray-300">Rank</th>
                <th className="px-4 py-3 text-gray-300">Parameters</th>
                <th className="px-4 py-3 text-gray-300">IS Sharpe</th>
                <th className="px-4 py-3 text-gray-300">OOS Sharpe</th>
                <th className="px-4 py-3 text-gray-300">Difference</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border">
              {results.parameter_combinations
                .sort((a, b) => b.is_sharpe - a.is_sharpe)
                .map((combo, idx) => (
                  <tr
                    key={idx}
                    className={`hover:bg-dark-bg ${idx === 0 ? 'bg-yellow-900/20' : ''}`}
                  >
                    <td className="px-4 py-3 text-white">{idx + 1}</td>
                    <td className="px-4 py-3 text-gray-300 font-mono text-xs">
                      {JSON.stringify(combo.params)}
                    </td>
                    <td className="px-4 py-3 text-blue-400 font-medium">{combo.is_sharpe.toFixed(3)}</td>
                    <td className="px-4 py-3 text-green-400 font-medium">{combo.oos_sharpe.toFixed(3)}</td>
                    <td
                      className={`px-4 py-3 font-medium ${
                        combo.oos_sharpe < combo.is_sharpe ? 'text-red-400' : 'text-green-400'
                      }`}
                    >
                      {(combo.oos_sharpe - combo.is_sharpe).toFixed(3)}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recommendation */}
      <div className={`${colors.bg} border ${colors.border} rounded-lg p-6`}>
        <h3 className="text-xl font-semibold text-white mb-3">Recommendation</h3>
        {pbo < 0.5 ? (
          <div className="text-gray-300 space-y-2">
            <p>
              ✅ <strong>Strategy appears robust.</strong> PBO is below 50%, indicating low probability of
              overfitting.
            </p>
            <p>
              ✅ The best in-sample strategy has OOS Sharpe of {results.best_is_oos_sharpe.toFixed(2)}, which
              is{' '}
              {results.best_is_oos_sharpe > results.median_oos_sharpe ? 'above' : 'below'} the median OOS
              Sharpe ({results.median_oos_sharpe.toFixed(2)}).
            </p>
            <p>⚠️ Still recommended to:</p>
            <ul className="list-disc list-inside ml-4">
              <li>Test on additional out-of-sample data</li>
              <li>Check robustness across different market regimes</li>
              <li>Monitor live performance closely</li>
            </ul>
          </div>
        ) : (
          <div className="text-gray-300 space-y-2">
            <p>
              ⚠️ <strong>High risk of overfitting.</strong> PBO is {pboPercentage.toFixed(1)}%, indicating
              the strategy may not generalize well.
            </p>
            <p>
              ❌ The best in-sample strategy has OOS Sharpe of {results.best_is_oos_sharpe.toFixed(2)}, which
              is{' '}
              {results.best_is_oos_sharpe > results.median_oos_sharpe ? 'above' : 'below'} the median OOS
              Sharpe ({results.median_oos_sharpe.toFixed(2)}).
            </p>
            <p>📋 Recommended actions:</p>
            <ul className="list-disc list-inside ml-4">
              <li>Simplify the strategy (fewer parameters)</li>
              <li>Use economic rationale, not just optimization</li>
              <li>Increase out-of-sample period</li>
              <li>Apply regularization or ensemble methods</li>
              <li>Consider abandoning this approach</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

// Deflated Sharpe Tab
function DeflatedSharpeTab({ results }: { results: DeflatedSharpeResponse | null }) {
  if (!results) {
    return (
      <div className="bg-dark-card border border-dark-border rounded-lg p-6 mt-6">
        <p className="text-gray-400">Run PBO analysis first to calculate Deflated Sharpe Ratio</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 mt-6">
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h3 className="text-2xl font-semibold text-white mb-4">Deflated Sharpe Ratio</h3>
        <p className="text-sm text-gray-400 mb-6">
          The Deflated Sharpe Ratio adjusts for the number of trials tested and multiple testing bias. It
          answers: "What is the true Sharpe Ratio after accounting for selection bias?"
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-dark-bg rounded-lg p-6 text-center">
            <div className="text-sm text-gray-400 mb-2">Deflated Sharpe</div>
            <div className="text-5xl font-bold text-blue-400">{results.deflated_sharpe.toFixed(3)}</div>
          </div>
          <div className="bg-dark-bg rounded-lg p-6 text-center">
            <div className="text-sm text-gray-400 mb-2">P-Value</div>
            <div className="text-5xl font-bold text-purple-400">{results.p_value.toFixed(4)}</div>
          </div>
          <div className="bg-dark-bg rounded-lg p-6 text-center">
            <div className="text-sm text-gray-400 mb-2">Trials Effect</div>
            <div className="text-5xl font-bold text-yellow-400">{results.trials_effect.toFixed(3)}</div>
          </div>
        </div>

        <div className="mt-6 bg-blue-900/20 border border-blue-700 rounded-lg p-4">
          <p className="text-sm text-gray-300">{results.interpretation}</p>
        </div>
      </div>
    </div>
  );
}

// CPCV Tab
function CPCVTab({ results }: { results: CombinatorialCVResponse | null }) {
  if (!results) {
    return (
      <div className="bg-dark-card border border-dark-border rounded-lg p-6 mt-6">
        <p className="text-gray-400">Run PBO analysis first to generate CPCV results</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 mt-6">
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h3 className="text-2xl font-semibold text-white mb-4">
          Combinatorial Purged Cross-Validation (CPCV)
        </h3>
        <p className="text-sm text-gray-400 mb-6">
          CPCV tests strategy robustness across multiple train/test splits while preventing data leakage
          through purging and embargo.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-dark-bg rounded-lg p-6 text-center">
            <div className="text-sm text-gray-400 mb-2">Mean Sharpe</div>
            <div className="text-5xl font-bold text-green-400">{results.mean_sharpe.toFixed(3)}</div>
          </div>
          <div className="bg-dark-bg rounded-lg p-6 text-center">
            <div className="text-sm text-gray-400 mb-2">Std Sharpe</div>
            <div className="text-5xl font-bold text-yellow-400">{results.std_sharpe.toFixed(3)}</div>
          </div>
          <div className="bg-dark-bg rounded-lg p-6 text-center">
            <div className="text-sm text-gray-400 mb-2">Consistency Score</div>
            <div className="text-5xl font-bold text-blue-400">{results.consistency_score.toFixed(1)}%</div>
          </div>
        </div>

        {/* Fold Results Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-dark-bg">
              <tr>
                <th className="px-4 py-3 text-gray-300">Fold</th>
                <th className="px-4 py-3 text-gray-300">Train Sharpe</th>
                <th className="px-4 py-3 text-gray-300">Test Sharpe</th>
                <th className="px-4 py-3 text-gray-300">Train Return</th>
                <th className="px-4 py-3 text-gray-300">Test Return</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border">
              {results.fold_results.map((fold) => (
                <tr key={fold.fold_id} className="hover:bg-dark-bg">
                  <td className="px-4 py-3 text-white">{fold.fold_id}</td>
                  <td className="px-4 py-3 text-blue-400 font-medium">{fold.train_sharpe.toFixed(3)}</td>
                  <td className="px-4 py-3 text-green-400 font-medium">{fold.test_sharpe.toFixed(3)}</td>
                  <td className="px-4 py-3 text-gray-300">{(fold.train_return * 100).toFixed(2)}%</td>
                  <td className="px-4 py-3 text-gray-300">{(fold.test_return * 100).toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// Stochastic Dominance Tab
function StochasticDominanceTab({ results }: { results: StochasticDominanceResponse | null }) {
  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6 mt-6">
      <h3 className="text-2xl font-semibold text-white mb-4">Stochastic Dominance Test</h3>
      <p className="text-sm text-gray-400 mb-6">
        Compare two strategies to determine if one stochastically dominates the other (consistently better
        returns distribution).
      </p>
      {!results ? (
        <div className="text-center py-8 text-gray-400">
          Feature available when comparing two strategies. Configure and run from the main PBO analysis.
        </div>
      ) : (
        <div>
          <div className="bg-dark-bg rounded-lg p-6 mb-4">
            <div className="text-center">
              <div className="text-sm text-gray-400 mb-2">Result</div>
              <div className="text-3xl font-bold text-white mb-2">
                {results.dominates ? `${results.dominant_strategy} Dominates` : 'No Dominance'}
              </div>
              <div className="text-sm text-gray-400">{results.interpretation}</div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-dark-bg rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">Test Statistic</div>
              <div className="text-2xl font-bold text-white">{results.test_statistic.toFixed(4)}</div>
            </div>
            <div className="bg-dark-bg rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">P-Value</div>
              <div className="text-2xl font-bold text-white">{results.p_value.toFixed(4)}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
