/**
 * Portfolio Optimizer - Advanced portfolio optimization with multiple algorithms
 */

import { useState } from 'react';
import { TrendingUp, Loader, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Plot from 'react-plotly.js';
import { portfolioApi } from '../../api/portfolioApi';
import type { HERCResponse, HERCvsHRPResponse } from '../../api/portfolioApi';
import { HERCResults } from '../../components/Portfolio/HERCResults';
import { HERCvsHRP } from '../../components/Portfolio/HERCvsHRP';

const OPTIMIZER_API = 'http://localhost:5001/api';

export function PortfolioOptimizer() {
  const navigate = useNavigate();
  const [tickers, setTickers] = useState(['AAPL', 'MSFT', 'GOOGL', 'AMZN']);
  const [method, setMethod] = useState('mean_variance');
  const [useCleanedCov, setUseCleanedCov] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [frontier, setFrontier] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // HERC-specific state
  const [hercRiskMeasure, setHercRiskMeasure] = useState<'volatility' | 'cvar'>('volatility');
  const [compareWithHRP, setCompareWithHRP] = useState(false);
  const [hercResults, setHercResults] = useState<HERCResponse | null>(null);
  const [comparisonResults, setComparisonResults] = useState<HERCvsHRPResponse | null>(null);

  const optimizationMethods = [
    { id: 'mean_variance', name: 'Mean-Variance (Markowitz)', description: 'Maximize Sharpe ratio' },
    { id: 'risk_parity', name: 'Risk Parity', description: 'Equal risk contribution' },
    { id: 'hrp', name: 'Hierarchical Risk Parity', description: 'Cluster-based allocation' },
    { id: 'herc', name: 'Hierarchical Equal Risk Contribution (HERC)', description: 'Equal risk contribution with clusters' },
    { id: 'min_variance', name: 'Minimum Variance', description: 'Lowest risk portfolio' },
    { id: 'max_diversification', name: 'Maximum Diversification', description: 'Maximize diversification ratio' },
  ];

  const handleOptimize = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setHercResults(null);
    setComparisonResults(null);

    try {
      // Handle HERC separately
      if (method === 'herc') {
        const hercData = await portfolioApi.herc({
          tickers,
          risk_measure: hercRiskMeasure,
        });
        setHercResults(hercData);

        // If comparison requested, fetch HRP comparison
        if (compareWithHRP) {
          const compData = await portfolioApi.hercVsHrp({ tickers });
          setComparisonResults(compData);
        }
      } else {
        // Existing optimization methods
        let endpoint = '';
        let body: any = {
          tickers,
          use_cleaned_cov: useCleanedCov
        };

        switch (method) {
          case 'mean_variance':
            endpoint = '/optimize/mean-variance';
            break;
          case 'risk_parity':
            endpoint = '/optimize/risk-parity';
            break;
          case 'hrp':
            endpoint = '/optimize/hrp';
            break;
          default:
            endpoint = '/optimize/mean-variance';
        }

        const response = await fetch(`${OPTIMIZER_API}${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });

        if (!response.ok) {
          throw new Error('Backend not responding');
        }

        const data = await response.json();
        setResult(data);

        // Also fetch efficient frontier
        if (method === 'mean_variance') {
          fetchEfficientFrontier();
        }
      }

    } catch (err) {
      console.error('Optimization error:', err);
      setError('Backend not running! Start: python backend/portfolio_optimizer/app.py');
    } finally {
      setLoading(false);
    }
  };

  const fetchEfficientFrontier = async () => {
    try {
      const response = await fetch(`${OPTIMIZER_API}/optimize/efficient-frontier`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tickers, n_points: 50 })
      });

      if (response.ok) {
        const data = await response.json();
        setFrontier(data.frontier);
      }
    } catch (error) {
      console.error('Frontier error:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/portfolio')}
            className="p-2 hover:bg-dark-border rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white">Advanced Portfolio Optimization</h1>
            <p className="text-sm text-gray-400">
              Optimize your portfolio using state-of-the-art algorithms
            </p>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-400">
            <span className="font-semibold">⚠️ {error}</span>
          </div>
        </div>
      )}

      {/* Method Selection */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Select Optimization Method</h2>

        <div className="grid grid-cols-2 gap-4 mb-6">
          {optimizationMethods.map((m) => (
            <button
              key={m.id}
              onClick={() => setMethod(m.id)}
              className={`p-4 rounded-lg border-2 transition text-left ${
                method === m.id
                  ? 'border-green-400 bg-green-900/20'
                  : 'border-dark-border hover:border-dark-border-hover'
              }`}
            >
              <div className="font-semibold text-white mb-1">{m.name}</div>
              <div className="text-sm text-gray-400">{m.description}</div>
            </button>
          ))}
        </div>

        {/* Ticker Input */}
        <div className="mb-4">
          <label className="block text-sm text-gray-400 mb-2">
            Assets (comma-separated tickers)
          </label>
          <input
            type="text"
            value={tickers.join(', ')}
            onChange={(e) => setTickers(e.target.value.split(',').map(t => t.trim()))}
            className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            placeholder="AAPL, MSFT, GOOGL, AMZN"
          />
        </div>

        {/* Covariance Cleaning Toggle */}
        {method !== 'herc' && (
          <div className="mb-6 p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={useCleanedCov}
                onChange={(e) => setUseCleanedCov(e.target.checked)}
                className="w-5 h-5 rounded border-dark-border bg-dark-bg cursor-pointer"
              />
              <div className="flex-1">
                <label className="text-sm font-semibold text-white cursor-pointer" onClick={() => setUseCleanedCov(!useCleanedCov)}>
                  Use Cleaned Covariance Matrix
                </label>
                <p className="text-xs text-gray-400 mt-1">
                  Apply RMT denoising, detoning, and detrending for more stable optimization results.
                </p>
              </div>
              <button
                onClick={() => navigate('/portfolio/covariance-analysis')}
                className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs font-medium transition whitespace-nowrap"
              >
                Configure →
              </button>
            </div>
          </div>
        )}

        {/* HERC-specific options */}
        {method === 'herc' && (
          <div className="mb-6 space-y-4 p-4 bg-purple-900/20 border border-purple-700 rounded-lg">
            <div>
              <label className="text-sm font-medium text-white mb-2 block">
                Risk Measure
              </label>
              <select
                className="w-full bg-dark-bg text-white border border-dark-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
                value={hercRiskMeasure}
                onChange={(e) => setHercRiskMeasure(e.target.value as 'volatility' | 'cvar')}
              >
                <option value="volatility">Volatility</option>
                <option value="cvar">CVaR (Tail Risk)</option>
              </select>
              <p className="text-xs text-gray-400 mt-1">
                {hercRiskMeasure === 'volatility'
                  ? 'Equalizes volatility contribution across clusters'
                  : 'Equalizes tail risk contribution (better for downside protection)'}
              </p>
            </div>

            <div>
              <label className="flex items-center space-x-2 text-white cursor-pointer">
                <input
                  type="checkbox"
                  className="w-4 h-4 text-blue-600 bg-dark-bg border-dark-border rounded"
                  checked={compareWithHRP}
                  onChange={(e) => setCompareWithHRP(e.target.checked)}
                />
                <span>Compare with HRP</span>
              </label>
              <p className="text-xs text-gray-400 ml-6 mt-1">
                Show side-by-side comparison of HERC vs HRP
              </p>
            </div>
          </div>
        )}

        <button
          onClick={handleOptimize}
          disabled={loading}
          className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Optimizing...
            </>
          ) : (
            <>
              <TrendingUp className="w-5 h-5" />
              Optimize Portfolio
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="grid grid-cols-2 gap-6">
          {/* Optimal Weights */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Optimal Allocation</h2>

            <div className="space-y-3">
              {Object.entries(result.weights).map(([ticker, weight]: any) => (
                <div key={ticker} className="flex items-center justify-between">
                  <span className="font-mono font-bold text-white">{ticker}</span>
                  <div className="flex items-center gap-4 flex-1 ml-4">
                    <div className="flex-1 bg-dark-bg rounded-full h-4 overflow-hidden">
                      <div
                        className="bg-green-500 h-full"
                        style={{ width: `${weight * 100}%` }}
                      />
                    </div>
                    <span className="font-mono font-bold w-16 text-right text-white">
                      {(weight * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Portfolio Metrics</h2>

            <div className="space-y-4">
              <MetricRow
                label="Expected Return"
                value={`${(result.expected_return * 100).toFixed(2)}%`}
                color="green"
              />
              <MetricRow
                label="Volatility"
                value={`${(result.volatility * 100).toFixed(2)}%`}
                color="orange"
              />
              <MetricRow
                label="Sharpe Ratio"
                value={result.sharpe_ratio.toFixed(3)}
                color="blue"
              />
              <MetricRow
                label="Method"
                value={result.method.replace('_', ' ').toUpperCase()}
                color="purple"
              />
            </div>
          </div>
        </div>
      )}

      {/* Efficient Frontier Chart */}
      {frontier && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Efficient Frontier</h2>
          <Plot
            data={[{
              x: frontier.map((p: any) => p.volatility),
              y: frontier.map((p: any) => p.return),
              type: 'scatter',
              mode: 'lines+markers',
              marker: {
                color: frontier.map((p: any) => p.sharpe),
                colorscale: 'Viridis',
                showscale: true,
                colorbar: { title: 'Sharpe Ratio' }
              },
              line: { color: '#3b82f6' },
            }]}
            layout={{
              paper_bgcolor: '#1a1f2e',
              plot_bgcolor: '#1a1f2e',
              font: { color: '#e0e0e0', family: 'monospace' },
              xaxis: { title: 'Volatility (Risk)', gridcolor: '#2a3142' },
              yaxis: { title: 'Expected Return', gridcolor: '#2a3142' },
              margin: { t: 20, b: 40, l: 50, r: 20 },
              autosize: true,
            }}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: '100%', height: '500px' }}
          />
        </div>
      )}

      {/* HERC Results */}
      {hercResults && (
        <HERCResults
          weights={hercResults.weights}
          riskContributions={hercResults.risk_contributions}
          portfolioMetrics={hercResults.portfolio_metrics}
          clusters={hercResults.clusters}
          dendrogram={hercResults.dendrogram}
        />
      )}

      {/* HERC vs HRP Comparison */}
      {comparisonResults && (
        <div className="mt-6">
          <h2 className="text-2xl font-bold text-white mb-4">HERC vs HRP Comparison</h2>
          <HERCvsHRP
            tickers={comparisonResults.tickers}
            hercWeights={comparisonResults.herc.weights}
            hrpWeights={comparisonResults.hrp.weights}
            hercRC={comparisonResults.herc.risk_contributions}
            hrpRC={comparisonResults.hrp.risk_contributions}
            comparison={comparisonResults.comparison}
          />
        </div>
      )}
    </div>
  );
}

function MetricRow({ label, value, color }: any) {
  const colorClasses: any = {
    green: 'text-green-400',
    orange: 'text-orange-400',
    blue: 'text-blue-400',
    purple: 'text-purple-400',
  };

  return (
    <div className="flex items-center justify-between p-3 bg-dark-bg rounded">
      <span className="text-gray-400">{label}</span>
      <span className={`font-bold text-lg ${colorClasses[color]}`}>{value}</span>
    </div>
  );
}
