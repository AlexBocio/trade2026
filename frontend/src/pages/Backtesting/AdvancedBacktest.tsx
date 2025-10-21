/**
 * Advanced Backtest - Walk-forward testing and robustness analysis
 */

import { useState } from 'react';
import { TrendingUp, Zap, Loader, ArrowLeft, Target } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const BACKTEST_API = 'http://localhost:5003/api/backtest';

type TabType = 'walk-forward' | 'robustness' | 'pbo';

const TABS = [
  { id: 'walk-forward', name: 'Walk-Forward Optimization', icon: '🔄' },
  { id: 'robustness', name: 'Robustness Testing', icon: '🛡️' },
  { id: 'pbo', name: 'PBO Analysis', icon: '📊' },
];

export function AdvancedBacktest() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('walk-forward');
  const [ticker, setTicker] = useState('AAPL');
  const [loading, setLoading] = useState(false);
  const [wfResult, setWfResult] = useState<any>(null);
  const [robustResult, setRobustResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleWalkForward = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${BACKTEST_API}/walk-forward`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker, train_period: 252, test_period: 63 })
      });

      if (!response.ok) {
        throw new Error('Backend not responding');
      }

      const data = await response.json();
      setWfResult(data);
    } catch (error) {
      console.error('Walk-forward error:', error);
      setError('Backend not running! Start: python backend/advanced_backtest/app.py');
    } finally {
      setLoading(false);
    }
  };

  const handleRobustness = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${BACKTEST_API}/robustness`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticker,
          params: { fast: 20, slow: 50 }
        })
      });

      if (!response.ok) {
        throw new Error('Backend not responding');
      }

      const data = await response.json();
      setRobustResult(data);
    } catch (error) {
      console.error('Robustness error:', error);
      setError('Backend not running! Start: python backend/advanced_backtest/app.py');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/backtesting')}
            className="p-2 hover:bg-dark-border rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white">Advanced Backtesting</h1>
            <p className="text-sm text-gray-400">
              Walk-forward analysis, robustness testing, and overfitting detection
            </p>
          </div>
        </div>
      </div>

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

      {/* Error Banner */}
      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-400">
            <span className="font-semibold">⚠️ {error}</span>
          </div>
        </div>
      )}

      {/* Tab Content */}
      {activeTab === 'walk-forward' && (
        <>
          {/* Controls */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Test Configuration</h2>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Ticker</label>
                <input
                  type="text"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                  placeholder="AAPL"
                />
              </div>
            </div>

            <button
              onClick={handleWalkForward}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Loading...
                </>
              ) : (
                <>
                  <TrendingUp className="w-5 h-5" />
                  Run Walk-Forward Test
                </>
              )}
            </button>
          </div>

          {/* Walk-Forward Results */}
          {wfResult && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Walk-Forward Results</h2>

              <div className="grid grid-cols-4 gap-4 mb-6">
                <MetricCard
                  label="Total Return"
                  value={`${wfResult.total_return?.toFixed(2) || '0.00'}%`}
                  color={wfResult.total_return >= 0 ? 'green' : 'red'}
                />
                <MetricCard
                  label="Sharpe Ratio"
                  value={wfResult.total_sharpe?.toFixed(2) || '0.00'}
                  color="blue"
                />
                <MetricCard
                  label="Win Rate"
                  value={`${wfResult.win_rate?.toFixed(1) || '0.0'}%`}
                  color="white"
                />
                <MetricCard
                  label="Param Stability"
                  value={wfResult.parameter_stability?.toFixed(2) || '0.00'}
                  color="purple"
                />
              </div>

              {/* Windows Table */}
              {wfResult.windows && wfResult.windows.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-gray-400 border-b border-dark-border">
                        <th className="pb-2">Period</th>
                        <th className="pb-2 text-right">Return</th>
                        <th className="pb-2 text-right">Sharpe</th>
                        <th className="pb-2">Optimal Params</th>
                      </tr>
                    </thead>
                    <tbody>
                      {wfResult.windows.map((w: any, i: number) => (
                        <tr key={i} className="border-b border-dark-border">
                          <td className="py-2 text-white">
                            {w.test_start} to {w.test_end}
                          </td>
                          <td
                            className={`py-2 text-right font-mono ${
                              w.test_return >= 0 ? 'text-green-400' : 'text-red-400'
                            }`}
                          >
                            {w.test_return >= 0 ? '+' : ''}
                            {w.test_return.toFixed(2)}%
                          </td>
                          <td className="py-2 text-right font-mono text-white">
                            {w.test_sharpe.toFixed(2)}
                          </td>
                          <td className="py-2 text-xs text-gray-400">
                            Fast: {w.optimal_params.fast}, Slow: {w.optimal_params.slow}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {activeTab === 'robustness' && (
        <>
          {/* Controls */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Robustness Configuration</h2>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Ticker</label>
                <input
                  type="text"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                  placeholder="AAPL"
                />
              </div>
            </div>

            <button
              onClick={handleRobustness}
              disabled={loading}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Loading...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Run Robustness Analysis
                </>
              )}
            </button>
          </div>

          {/* Robustness Results */}
          {robustResult && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Robustness Analysis</h2>

              <div className="grid grid-cols-3 gap-6">
                {/* Monte Carlo */}
                {robustResult.monte_carlo && (
                  <div className="bg-dark-bg rounded-lg p-4">
                    <h3 className="font-semibold text-white mb-3">Monte Carlo Test</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Baseline Sharpe:</span>
                        <span className="font-mono text-white">
                          {robustResult.monte_carlo.baseline_sharpe?.toFixed(2) || '0.00'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Random Sharpe:</span>
                        <span className="font-mono text-white">
                          {robustResult.monte_carlo.mean_random_sharpe?.toFixed(2) || '0.00'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">P-Value:</span>
                        <span className="font-mono text-white">
                          {robustResult.monte_carlo.p_value?.toFixed(3) || '0.000'}
                        </span>
                      </div>
                      <div
                        className={`px-3 py-1 rounded text-center font-semibold mt-3 ${
                          robustResult.monte_carlo.is_significant
                            ? 'bg-green-900/30 text-green-400 border border-green-700'
                            : 'bg-red-900/30 text-red-400 border border-red-700'
                        }`}
                      >
                        {robustResult.monte_carlo.is_significant ? '✓ Significant' : '✗ Not Significant'}
                      </div>
                    </div>
                  </div>
                )}

                {/* Complexity */}
                {robustResult.complexity && (
                  <div className="bg-dark-bg rounded-lg p-4">
                    <h3 className="font-semibold text-white mb-3">Strategy Complexity</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Parameters:</span>
                        <span className="font-mono text-white">
                          {robustResult.complexity.n_parameters || 0}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Complexity Score:</span>
                        <span className="font-mono text-white">
                          {robustResult.complexity.complexity_score?.toFixed(2) || '0.00'}
                        </span>
                      </div>
                      <div
                        className={`px-3 py-1 rounded text-center font-semibold mt-8 ${
                          robustResult.complexity.is_simple
                            ? 'bg-green-900/30 text-green-400 border border-green-700'
                            : 'bg-orange-900/30 text-orange-400 border border-orange-700'
                        }`}
                      >
                        {robustResult.complexity.is_simple ? '✓ Simple' : '⚠ Complex'}
                      </div>
                    </div>
                  </div>
                )}

                {/* Regime Stability */}
                {robustResult.regime_stability && (
                  <div className="bg-dark-bg rounded-lg p-4">
                    <h3 className="font-semibold text-white mb-3">Regime Stability</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Pre-Regime:</span>
                        <span className="font-mono text-white">
                          {robustResult.regime_stability.pre_regime_sharpe?.toFixed(2) || '0.00'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Post-Regime:</span>
                        <span className="font-mono text-white">
                          {robustResult.regime_stability.post_regime_sharpe?.toFixed(2) || '0.00'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Stability:</span>
                        <span className="font-mono text-white">
                          {robustResult.regime_stability.stability_score?.toFixed(2) || '0.00'}
                        </span>
                      </div>
                      <div
                        className={`px-3 py-1 rounded text-center font-semibold ${
                          robustResult.regime_stability.is_stable
                            ? 'bg-green-900/30 text-green-400 border border-green-700'
                            : 'bg-red-900/30 text-red-400 border border-red-700'
                        }`}
                      >
                        {robustResult.regime_stability.is_stable ? '✓ Stable' : '✗ Unstable'}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}

      {activeTab === 'pbo' && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">PBO Analysis</h2>
          <p className="text-gray-400 mb-6">
            Probability of Backtest Overfitting measures the likelihood that your best-performing strategy is
            due to luck and overfitting.
          </p>

          <button
            onClick={() => navigate('/backtesting/pbo-analysis')}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition flex items-center gap-2"
          >
            <Target className="w-5 h-5" />
            Go to Full PBO Analysis
          </button>

          <div className="mt-6 bg-blue-900/20 border border-blue-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-blue-400 mb-2">What is PBO?</h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li>
                • <strong>Tests multiple parameter combinations</strong> to see if best IS performer also
                performs well OOS
              </li>
              <li>
                • <strong>PBO &lt; 50%</strong> = Strategy appears robust (good IS → good OOS)
              </li>
              <li>
                • <strong>PBO &gt; 50%</strong> = High risk of overfitting (good IS → poor OOS)
              </li>
              <li>• Includes Deflated Sharpe Ratio, CPCV, and Stochastic Dominance tests</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ label, value, color }: any) {
  const colorClasses: any = {
    green: 'text-green-400',
    red: 'text-red-400',
    blue: 'text-blue-400',
    purple: 'text-purple-400',
    white: 'text-white',
  };

  return (
    <div className="bg-dark-bg rounded-lg p-4">
      <div className="text-sm text-gray-400 mb-1">{label}</div>
      <div className={`text-2xl font-bold ${colorClasses[color]}`}>{value}</div>
    </div>
  );
}
