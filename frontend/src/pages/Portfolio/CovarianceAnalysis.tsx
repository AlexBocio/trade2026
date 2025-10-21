/**
 * Covariance Analysis - Clean covariance matrices using detoning, detrending, RMT
 */

import { useState } from 'react';
import { ArrowLeft, Loader, Info, Plus, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Plot from 'react-plotly.js';
import { covarianceApi, type CleanParams, type CleanResponse, type CompareResponse } from '../../api/covarianceApi';

export function CovarianceAnalysis() {
  const navigate = useNavigate();

  // Form state
  const [tickers, setTickers] = useState<string[]>(['SPY', 'TLT', 'GLD', 'VNQ', 'DBC']);
  const [newTicker, setNewTicker] = useState('');
  const [startDate, setStartDate] = useState('2020-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [detone, setDetone] = useState(true);
  const [detrend, setDetrend] = useState(true);
  const [denoiseMethod, setDenoiseMethod] = useState<'marchenko_pastur' | 'constant_residual' | 'target_shrinkage'>('marchenko_pastur');
  const [kdeBwidth, setKdeBwidth] = useState(0.01);
  const [alpha, setAlpha] = useState(0.0);

  // Results state
  const [cleanResults, setCleanResults] = useState<CleanResponse | null>(null);
  const [compareResults, setCompareResults] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addTicker = () => {
    const ticker = newTicker.toUpperCase().trim();
    if (ticker && !tickers.includes(ticker)) {
      setTickers([...tickers, ticker]);
      setNewTicker('');
    }
  };

  const removeTicker = (ticker: string) => {
    setTickers(tickers.filter((t) => t !== ticker));
  };

  const handleAnalyze = async () => {
    if (tickers.length < 3) {
      setError('Please add at least 3 tickers for covariance analysis');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const cleanParams: CleanParams = {
        tickers,
        start_date: startDate,
        end_date: endDate,
        detone,
        detrend,
        denoise_method: denoiseMethod,
        kde_bwidth: kdeBwidth,
        alpha,
      };

      // Get cleaned covariance
      const cleanData = await covarianceApi.clean(cleanParams);
      setCleanResults(cleanData);

      // Get portfolio comparison
      const compareData = await covarianceApi.compare({
        tickers,
        start_date: startDate,
        end_date: endDate,
      });
      setCompareResults(compareData);
    } catch (err: any) {
      setError(err.message || 'Backend not running! Start: python backend/covariance_service/app.py');
    } finally {
      setLoading(false);
    }
  };

  // Generate heatmap data
  const generateHeatmap = (matrix: number[][], tickers: string[], title: string) => {
    return {
      z: matrix,
      x: tickers,
      y: tickers,
      type: 'heatmap' as const,
      colorscale: 'RdBu',
      reversescale: true,
      text: matrix.map(row => row.map(val => val.toFixed(4))),
      texttemplate: '%{text}',
      textfont: { size: 10, color: 'white' },
      hoverongaps: false,
      colorbar: {
        title: 'Correlation',
        titleside: 'right',
        tickfont: { color: '#9CA3AF' },
        titlefont: { color: '#9CA3AF' },
      },
    };
  };

  // Generate eigenvalue spectrum chart
  const generateEigenvalueChart = () => {
    if (!cleanResults) return null;

    return (
      <Plot
        data={[
          {
            x: cleanResults.eigenvalues_original.map((_, i) => i + 1),
            y: cleanResults.eigenvalues_original,
            type: 'bar',
            name: 'Original',
            marker: { color: '#EF4444' },
          },
          {
            x: cleanResults.eigenvalues_cleaned.map((_, i) => i + 1),
            y: cleanResults.eigenvalues_cleaned,
            type: 'bar',
            name: 'Cleaned',
            marker: { color: '#10B981' },
          },
        ]}
        layout={{
          title: {
            text: 'Eigenvalue Spectrum Comparison',
            font: { color: '#fff', size: 18 },
          },
          paper_bgcolor: '#1a1f2e',
          plot_bgcolor: '#1a1f2e',
          font: { color: '#9CA3AF' },
          xaxis: {
            title: 'Eigenvalue Index',
            gridcolor: '#374151',
            color: '#9CA3AF',
          },
          yaxis: {
            title: 'Eigenvalue Magnitude',
            gridcolor: '#374151',
            color: '#9CA3AF',
          },
          legend: {
            font: { color: '#9CA3AF' },
          },
          barmode: 'group',
          height: 400,
        }}
        config={{ displayModeBar: false }}
        className="w-full"
      />
    );
  };

  // Generate portfolio weights comparison
  const generateWeightsChart = () => {
    if (!compareResults) return null;

    const tickers = compareResults.tickers;
    const originalWeights = tickers.map(t => compareResults.original_weights[t] * 100);
    const cleanedWeights = tickers.map(t => compareResults.cleaned_weights[t] * 100);

    return (
      <Plot
        data={[
          {
            x: tickers,
            y: originalWeights,
            type: 'bar',
            name: 'Original',
            marker: { color: '#EF4444' },
          },
          {
            x: tickers,
            y: cleanedWeights,
            type: 'bar',
            name: 'Cleaned',
            marker: { color: '#10B981' },
          },
        ]}
        layout={{
          title: {
            text: 'Portfolio Weights Comparison (%)',
            font: { color: '#fff', size: 18 },
          },
          paper_bgcolor: '#1a1f2e',
          plot_bgcolor: '#1a1f2e',
          font: { color: '#9CA3AF' },
          xaxis: {
            gridcolor: '#374151',
            color: '#9CA3AF',
          },
          yaxis: {
            title: 'Weight (%)',
            gridcolor: '#374151',
            color: '#9CA3AF',
          },
          legend: {
            font: { color: '#9CA3AF' },
          },
          barmode: 'group',
          height: 400,
        }}
        config={{ displayModeBar: false }}
        className="w-full"
      />
    );
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
            <h1 className="text-2xl font-bold text-white">Covariance Matrix Cleaning</h1>
            <p className="text-sm text-gray-400">
              Remove noise, market effects, and industry trends using RMT denoising
            </p>
          </div>
        </div>
      </div>

      {/* Configuration Panel */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Analysis Configuration</h2>

        {/* Tickers */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Asset Universe ({tickers.length} tickers)
          </label>
          <div className="flex flex-wrap gap-2 mb-3 max-h-32 overflow-y-auto">
            {tickers.map((ticker) => (
              <div
                key={ticker}
                className="flex items-center gap-2 bg-blue-900/30 border border-blue-700 rounded-lg px-3 py-1"
              >
                <span className="text-blue-400 font-mono font-semibold">{ticker}</span>
                <button
                  onClick={() => removeTicker(ticker)}
                  className="text-blue-400 hover:text-red-400 transition"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={newTicker}
              onChange={(e) => setNewTicker(e.target.value)}
              className="flex-1 px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-blue-500"
              placeholder="Add ticker (e.g., AAPL)"
              onKeyPress={(e) => e.key === 'Enter' && addTicker()}
            />
            <button
              onClick={addTicker}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add
            </button>
          </div>
        </div>

        {/* Date Range */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* Cleaning Options */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={detone}
                onChange={(e) => setDetone(e.target.checked)}
                className="w-5 h-5 rounded border-dark-border bg-dark-bg"
              />
              <div>
                <label className="text-sm font-medium text-white">Detone (Remove Market Component)</label>
                <p className="text-xs text-gray-400">Remove dominant market factor from covariance</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={detrend}
                onChange={(e) => setDetrend(e.target.checked)}
                className="w-5 h-5 rounded border-dark-border bg-dark-bg"
              />
              <div>
                <label className="text-sm font-medium text-white">Detrend (Remove Industry Trends)</label>
                <p className="text-xs text-gray-400">Remove industry/sector group effects</p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Denoising Method</label>
              <select
                value={denoiseMethod}
                onChange={(e) => setDenoiseMethod(e.target.value as any)}
                className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                <option value="marchenko_pastur">Marchenko-Pastur (RMT)</option>
                <option value="constant_residual">Constant Residual Eigenvalue</option>
                <option value="target_shrinkage">Target Shrinkage</option>
              </select>
            </div>

            {denoiseMethod === 'marchenko_pastur' && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  KDE Bandwidth: <span className="text-blue-400 font-mono">{kdeBwidth.toFixed(3)}</span>
                </label>
                <input
                  type="range"
                  min="0.001"
                  max="0.1"
                  step="0.001"
                  value={kdeBwidth}
                  onChange={(e) => setKdeBwidth(parseFloat(e.target.value))}
                  className="w-full h-2 bg-dark-bg rounded-lg appearance-none cursor-pointer"
                />
              </div>
            )}

            {denoiseMethod === 'target_shrinkage' && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Alpha (Shrinkage): <span className="text-blue-400 font-mono">{alpha.toFixed(2)}</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={alpha}
                  onChange={(e) => setAlpha(parseFloat(e.target.value))}
                  className="w-full h-2 bg-dark-bg rounded-lg appearance-none cursor-pointer"
                />
              </div>
            )}
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

        {/* Action Button */}
        <button
          onClick={handleAnalyze}
          disabled={loading || tickers.length < 3}
          className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>Clean & Analyze Covariance</>
          )}
        </button>
      </div>

      {/* Results */}
      {cleanResults && compareResults && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Condition Number</div>
              <div className="text-2xl font-bold text-red-400">
                {cleanResults.condition_number_original.toFixed(1)}
              </div>
              <div className="text-xs text-gray-500">Original</div>
            </div>

            <div className="bg-dark-card border border-green-700 rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Condition Number</div>
              <div className="text-2xl font-bold text-green-400">
                {cleanResults.condition_number_cleaned.toFixed(1)}
              </div>
              <div className="text-xs text-gray-500">Cleaned</div>
            </div>

            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Sharpe Ratio</div>
              <div className="text-2xl font-bold text-red-400">
                {compareResults.original_sharpe.toFixed(2)}
              </div>
              <div className="text-xs text-gray-500">Original</div>
            </div>

            <div className="bg-dark-card border border-green-700 rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Sharpe Ratio</div>
              <div className="text-2xl font-bold text-green-400">
                {compareResults.cleaned_sharpe.toFixed(2)}
              </div>
              <div className="text-xs text-gray-500">Cleaned</div>
            </div>
          </div>

          {/* Eigenvalue Spectrum */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Eigenvalue Spectrum</h3>
            <p className="text-sm text-gray-400 mb-4">
              RMT denoising removes eigenvalues below the Marchenko-Pastur threshold, retaining only signal.
            </p>
            {generateEigenvalueChart()}
          </div>

          {/* Portfolio Weights */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Portfolio Weights Impact</h3>
            <p className="text-sm text-gray-400 mb-4">
              How cleaning the covariance matrix changes optimal portfolio allocation.
            </p>
            {generateWeightsChart()}
          </div>

          {/* Covariance Heatmaps */}
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Original Covariance</h3>
              <Plot
                data={[generateHeatmap(cleanResults.original_cov, cleanResults.tickers, 'Original')]}
                layout={{
                  paper_bgcolor: '#1a1f2e',
                  plot_bgcolor: '#1a1f2e',
                  font: { color: '#9CA3AF' },
                  height: 500,
                  margin: { l: 80, r: 80, t: 40, b: 80 },
                }}
                config={{ displayModeBar: false }}
                className="w-full"
              />
            </div>

            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Cleaned Covariance</h3>
              <Plot
                data={[generateHeatmap(cleanResults.cleaned_cov, cleanResults.tickers, 'Cleaned')]}
                layout={{
                  paper_bgcolor: '#1a1f2e',
                  plot_bgcolor: '#1a1f2e',
                  font: { color: '#9CA3AF' },
                  height: 500,
                  margin: { l: 80, r: 80, t: 40, b: 80 },
                }}
                config={{ displayModeBar: false }}
                className="w-full"
              />
            </div>
          </div>

          {/* Metrics Table */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Portfolio Metrics Comparison</h3>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-400 border-b border-dark-border">
                  <th className="pb-3">Metric</th>
                  <th className="pb-3 text-right">Original</th>
                  <th className="pb-3 text-right">Cleaned</th>
                  <th className="pb-3 text-right">Improvement</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-dark-border">
                  <td className="py-3 text-gray-300">Sharpe Ratio</td>
                  <td className="py-3 text-right text-white font-mono">
                    {compareResults.original_sharpe.toFixed(3)}
                  </td>
                  <td className="py-3 text-right text-white font-mono">
                    {compareResults.cleaned_sharpe.toFixed(3)}
                  </td>
                  <td className="py-3 text-right">
                    <span className={`font-semibold ${
                      compareResults.cleaned_sharpe > compareResults.original_sharpe
                        ? 'text-green-400'
                        : 'text-red-400'
                    }`}>
                      {((compareResults.cleaned_sharpe - compareResults.original_sharpe) / Math.abs(compareResults.original_sharpe) * 100).toFixed(1)}%
                    </span>
                  </td>
                </tr>
                <tr className="border-b border-dark-border">
                  <td className="py-3 text-gray-300">Volatility</td>
                  <td className="py-3 text-right text-white font-mono">
                    {(compareResults.original_volatility * 100).toFixed(2)}%
                  </td>
                  <td className="py-3 text-right text-white font-mono">
                    {(compareResults.cleaned_volatility * 100).toFixed(2)}%
                  </td>
                  <td className="py-3 text-right">
                    <span className={`font-semibold ${
                      compareResults.cleaned_volatility < compareResults.original_volatility
                        ? 'text-green-400'
                        : 'text-red-400'
                    }`}>
                      {((compareResults.cleaned_volatility - compareResults.original_volatility) / compareResults.original_volatility * 100).toFixed(1)}%
                    </span>
                  </td>
                </tr>
                <tr className="border-b border-dark-border">
                  <td className="py-3 text-gray-300">Diversification Ratio</td>
                  <td className="py-3 text-right text-white font-mono">
                    {compareResults.diversification_ratio_original.toFixed(3)}
                  </td>
                  <td className="py-3 text-right text-white font-mono">
                    {compareResults.diversification_ratio_cleaned.toFixed(3)}
                  </td>
                  <td className="py-3 text-right">
                    <span className={`font-semibold ${
                      compareResults.diversification_ratio_cleaned > compareResults.diversification_ratio_original
                        ? 'text-green-400'
                        : 'text-red-400'
                    }`}>
                      {((compareResults.diversification_ratio_cleaned - compareResults.diversification_ratio_original) / compareResults.diversification_ratio_original * 100).toFixed(1)}%
                    </span>
                  </td>
                </tr>
                <tr>
                  <td className="py-3 text-gray-300">Condition Number</td>
                  <td className="py-3 text-right text-white font-mono">
                    {cleanResults.condition_number_original.toFixed(1)}
                  </td>
                  <td className="py-3 text-right text-white font-mono">
                    {cleanResults.condition_number_cleaned.toFixed(1)}
                  </td>
                  <td className="py-3 text-right">
                    <span className={`font-semibold ${
                      cleanResults.condition_number_cleaned < cleanResults.condition_number_original
                        ? 'text-green-400'
                        : 'text-red-400'
                    }`}>
                      {((cleanResults.condition_number_cleaned - cleanResults.condition_number_original) / cleanResults.condition_number_original * 100).toFixed(1)}%
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Processing Summary */}
          <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
            <div className="text-sm text-gray-300">
              <strong className="text-white">Cleaning Applied:</strong>
              <ul className="list-disc list-inside mt-2 space-y-1">
                {cleanResults.detoning_applied && <li>Detoning: Market component removed</li>}
                {cleanResults.detrending_applied && <li>Detrending: Industry trends removed</li>}
                {cleanResults.denoising_applied && <li>Denoising: RMT filtering applied ({denoiseMethod})</li>}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Info Footer */}
      <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="text-blue-400 text-2xl">💡</div>
          <div>
            <div className="font-semibold text-white mb-1">About Covariance Cleaning</div>
            <div className="text-sm text-gray-300 space-y-1">
              <p>
                <strong>The Problem:</strong> Sample covariance matrices are noisy, especially with limited data. This leads to unstable portfolio optimization and poor out-of-sample performance.
              </p>
              <p>
                <strong>The Solution:</strong> Use Random Matrix Theory (RMT) to identify and remove noise eigenvalues, detone market effects, and detrend industry correlations.
              </p>
              <p>
                <strong>Key Metrics:</strong> Lower condition number = more stable matrix. Higher Sharpe ratio = better risk-adjusted returns. Higher diversification ratio = more efficient diversification.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
