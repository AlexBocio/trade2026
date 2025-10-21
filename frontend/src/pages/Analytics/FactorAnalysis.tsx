/**
 * Factor Analysis - Barra Factor Model Risk Decomposition
 */

import { useState } from 'react';
import { BarChart3, Loader, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const FACTOR_API = 'http://localhost:5004/api/factors';

export function FactorAnalysis() {
  const navigate = useNavigate();
  const [tickers, setTickers] = useState(['AAPL', 'MSFT', 'GOOGL', 'AMZN']);
  const [weights, setWeights] = useState({ AAPL: 0.25, MSFT: 0.25, GOOGL: 0.25, AMZN: 0.25 });
  const [loading, setLoading] = useState(false);
  const [barraResult, setBarraResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${FACTOR_API}/barra`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tickers, weights })
      });

      if (!response.ok) {
        throw new Error('Backend not responding');
      }

      const data = await response.json();
      setBarraResult(data);
    } catch (error) {
      console.error('Factor analysis error:', error);
      setError('Backend not running! Start: python backend/factor_models/app.py');
    } finally {
      setLoading(false);
    }
  };

  const updateWeight = (ticker: string, value: string) => {
    const newWeight = parseFloat(value) || 0;
    setWeights({ ...weights, [ticker]: newWeight });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/analytics')}
            className="p-2 hover:bg-dark-border rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white">Factor Analysis</h1>
            <p className="text-sm text-gray-400">
              Barra factor model risk decomposition and exposures
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

      {/* Controls */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Portfolio Setup</h2>

        <div className="mb-4">
          <label className="block text-sm text-gray-400 mb-2">Tickers (comma-separated)</label>
          <input
            type="text"
            value={tickers.join(', ')}
            onChange={(e) => setTickers(e.target.value.split(',').map((t) => t.trim()))}
            className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            placeholder="AAPL, MSFT, GOOGL, AMZN"
          />
        </div>

        <div className="mb-6">
          <label className="block text-sm text-gray-400 mb-3">Weights (must sum to 1.0)</label>
          <div className="grid grid-cols-4 gap-4">
            {tickers.map((ticker) => (
              <div key={ticker} className="flex items-center gap-2">
                <span className="font-mono font-bold text-white w-16">{ticker}:</span>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={weights[ticker] || 0}
                  onChange={(e) => updateWeight(ticker, e.target.value)}
                  className="flex-1 px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                />
              </div>
            ))}
          </div>
          <div className="mt-2 text-sm text-gray-400">
            Total: {Object.values(weights).reduce((sum, w) => sum + w, 0).toFixed(2)}
          </div>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <BarChart3 className="w-5 h-5" />
              Run Factor Analysis
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {barraResult && (
        <div className="space-y-6">
          {/* Risk Decomposition */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Risk Decomposition</h2>

            <div className="grid grid-cols-3 gap-4">
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Total Risk</div>
                <div className="text-2xl font-bold text-white">
                  {barraResult.risk_decomposition?.total_risk?.toFixed(2) || '0.00'}%
                </div>
                <div className="text-xs text-gray-500 mt-1">Portfolio volatility</div>
              </div>
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Factor Risk</div>
                <div className="text-2xl font-bold text-blue-400">
                  {barraResult.risk_decomposition?.factor_risk?.toFixed(2) || '0.00'}%
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {barraResult.risk_decomposition?.factor_risk &&
                  barraResult.risk_decomposition?.total_risk
                    ? `${(
                        (barraResult.risk_decomposition.factor_risk /
                          barraResult.risk_decomposition.total_risk) *
                        100
                      ).toFixed(1)}% of total`
                    : 'Systematic risk'}
                </div>
              </div>
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Specific Risk</div>
                <div className="text-2xl font-bold text-purple-400">
                  {barraResult.risk_decomposition?.specific_risk?.toFixed(2) || '0.00'}%
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {barraResult.risk_decomposition?.specific_risk &&
                  barraResult.risk_decomposition?.total_risk
                    ? `${(
                        (barraResult.risk_decomposition.specific_risk /
                          barraResult.risk_decomposition.total_risk) *
                        100
                      ).toFixed(1)}% of total`
                    : 'Idiosyncratic risk'}
                </div>
              </div>
            </div>

            <div className="mt-4 p-3 bg-blue-900/20 border border-blue-700 rounded-lg">
              <p className="text-sm text-gray-300">
                <strong>Interpretation:</strong> Factor risk represents systematic exposure to market
                factors (momentum, value, size, etc.). Specific risk is stock-specific and can be
                diversified away.
              </p>
            </div>
          </div>

          {/* Factor Tilts/Exposures */}
          {barraResult.factor_tilts && Object.keys(barraResult.factor_tilts).length > 0 && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Factor Exposures</h2>

              <div className="space-y-3">
                {Object.entries(barraResult.factor_tilts).map(([factor, exposure]: any) => (
                  <div key={factor} className="flex items-center justify-between">
                    <span className="font-semibold text-white capitalize w-32">{factor}</span>
                    <div className="flex items-center gap-4 flex-1 ml-4">
                      <div className="flex-1 bg-dark-bg rounded-full h-6 overflow-hidden relative">
                        {/* Zero line */}
                        <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-600" />
                        {/* Exposure bar */}
                        <div
                          className={`h-full ${exposure >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                          style={{
                            width: `${Math.min(Math.abs(exposure) * 50, 50)}%`,
                            marginLeft: exposure < 0 ? `${50 - Math.min(Math.abs(exposure) * 50, 50)}%` : '50%',
                          }}
                        />
                      </div>
                      <span className="font-mono font-bold w-20 text-right text-white">
                        {exposure.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-4 p-3 bg-blue-900/20 border border-blue-700 rounded-lg">
                <p className="text-sm text-gray-300">
                  <strong>Interpretation:</strong> Positive values indicate overweight exposure to the
                  factor, negative values indicate underweight. Zero indicates neutral exposure.
                </p>
              </div>
            </div>
          )}

          {/* Factor Contributions */}
          {barraResult.factor_contributions && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Factor Risk Contributions</h2>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-400 border-b border-dark-border">
                      <th className="pb-2">Factor</th>
                      <th className="pb-2 text-right">Exposure</th>
                      <th className="pb-2 text-right">Risk Contribution (%)</th>
                      <th className="pb-2 text-right">% of Factor Risk</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(barraResult.factor_contributions).map(([factor, contrib]: any) => (
                      <tr key={factor} className="border-b border-dark-border">
                        <td className="py-2 text-white capitalize">{factor}</td>
                        <td className="py-2 text-right font-mono text-white">
                          {barraResult.factor_tilts[factor]?.toFixed(2) || '0.00'}
                        </td>
                        <td className="py-2 text-right font-mono text-white">
                          {contrib.toFixed(2)}%
                        </td>
                        <td className="py-2 text-right font-mono text-gray-400">
                          {barraResult.risk_decomposition?.factor_risk
                            ? ((contrib / barraResult.risk_decomposition.factor_risk) * 100).toFixed(1)
                            : '0.0'}
                          %
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
