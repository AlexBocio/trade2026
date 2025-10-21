/**
 * Backtest Comparison Tab - Compare primary strategy vs meta-labeled version
 */

import { useState } from 'react';
import { Loader, Info, TrendingUp, TrendingDown } from 'lucide-react';
import Plot from 'react-plotly.js';
import { metaLabelingApi, type BacktestParams, type BacktestResponse } from '../../api/metaLabelingApi';

const PRIMARY_STRATEGIES = [
  { id: 'momentum', name: 'Momentum Crossover' },
  { id: 'mean_reversion', name: 'Mean Reversion' },
  { id: 'breakout', name: 'Breakout' },
  { id: 'trend_following', name: 'Trend Following' },
];

export function BacktestComparisonTab() {
  const [modelId, setModelId] = useState('');
  const [primaryStrategy, setPrimaryStrategy] = useState('momentum');
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [initialCapital, setInitialCapital] = useState(100000);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleBacktest = async () => {
    if (!modelId.trim()) {
      setError('Please enter a Model ID from the Train tab');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const params: BacktestParams = {
        model_id: modelId.trim(),
        primary_strategy: primaryStrategy,
        start_date: startDate,
        end_date: endDate,
        initial_capital: initialCapital,
      };

      const data = await metaLabelingApi.backtest(params);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Backend not running! Start: python backend/metalabeling_service/app.py');
    } finally {
      setLoading(false);
    }
  };

  // Generate equity curves comparison
  const generateEquityCurves = () => {
    if (!result) return null;

    return (
      <Plot
        data={[
          {
            x: result.equity_curves.dates,
            y: result.equity_curves.primary_only,
            type: 'scatter',
            mode: 'lines',
            name: 'Primary Only',
            line: { color: '#EF4444', width: 2 },
          },
          {
            x: result.equity_curves.dates,
            y: result.equity_curves.with_meta_labeling,
            type: 'scatter',
            mode: 'lines',
            name: 'With Meta-Labeling',
            line: { color: '#10B981', width: 2 },
          },
        ]}
        layout={{
          title: {
            text: 'Equity Curve Comparison',
            font: { color: '#fff', size: 18 },
          },
          paper_bgcolor: '#1a1f2e',
          plot_bgcolor: '#1a1f2e',
          font: { color: '#9CA3AF' },
          xaxis: {
            title: 'Date',
            gridcolor: '#374151',
            color: '#9CA3AF',
          },
          yaxis: {
            title: 'Portfolio Value ($)',
            gridcolor: '#374151',
            color: '#9CA3AF',
          },
          legend: {
            font: { color: '#9CA3AF' },
          },
          height: 500,
        }}
        config={{ displayModeBar: false }}
        className="w-full"
      />
    );
  };

  return (
    <div className="space-y-6">
      {/* Configuration Panel */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-2xl font-semibold text-white mb-4">Backtest Configuration</h2>

        {/* Model ID Input */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Model ID (from Train tab)
          </label>
          <input
            type="text"
            value={modelId}
            onChange={(e) => setModelId(e.target.value)}
            className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white font-mono focus:outline-none focus:border-purple-500"
            placeholder="e.g., meta_model_1234567890"
          />
        </div>

        {/* Primary Strategy Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">Primary Strategy</label>
          <select
            value={primaryStrategy}
            onChange={(e) => setPrimaryStrategy(e.target.value)}
            className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-purple-500"
          >
            {PRIMARY_STRATEGIES.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        {/* Date Range and Capital */}
        <div className="grid grid-cols-3 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-purple-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-purple-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Initial Capital</label>
            <input
              type="number"
              value={initialCapital}
              onChange={(e) => setInitialCapital(parseInt(e.target.value))}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-purple-500"
            />
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
          onClick={handleBacktest}
          disabled={loading || !modelId.trim()}
          className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Running Backtest...
            </>
          ) : (
            <>Run Backtest Comparison</>
          )}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Performance Comparison Cards */}
          <div className="grid grid-cols-2 gap-6">
            {/* Primary Only */}
            <div className="bg-dark-card border border-red-700 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <TrendingDown className="w-5 h-5 text-red-400" />
                Primary Strategy Only
              </h3>
              <div className="space-y-3">
                <MetricRow
                  label="Total Return"
                  value={`${(result.primary_only.total_return * 100).toFixed(2)}%`}
                  color="red"
                />
                <MetricRow
                  label="Sharpe Ratio"
                  value={result.primary_only.sharpe_ratio.toFixed(3)}
                  color="red"
                />
                <MetricRow
                  label="Max Drawdown"
                  value={`${(result.primary_only.max_drawdown * 100).toFixed(2)}%`}
                  color="red"
                />
                <MetricRow
                  label="Win Rate"
                  value={`${(result.primary_only.win_rate * 100).toFixed(1)}%`}
                  color="red"
                />
                <MetricRow label="Num Trades" value={result.primary_only.num_trades} color="red" />
                <MetricRow
                  label="Avg Trade"
                  value={`${(result.primary_only.avg_trade_return * 100).toFixed(2)}%`}
                  color="red"
                />
              </div>
            </div>

            {/* With Meta-Labeling */}
            <div className="bg-dark-card border border-green-700 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-400" />
                With Meta-Labeling
              </h3>
              <div className="space-y-3">
                <MetricRow
                  label="Total Return"
                  value={`${(result.with_meta_labeling.total_return * 100).toFixed(2)}%`}
                  color="green"
                />
                <MetricRow
                  label="Sharpe Ratio"
                  value={result.with_meta_labeling.sharpe_ratio.toFixed(3)}
                  color="green"
                />
                <MetricRow
                  label="Max Drawdown"
                  value={`${(result.with_meta_labeling.max_drawdown * 100).toFixed(2)}%`}
                  color="green"
                />
                <MetricRow
                  label="Win Rate"
                  value={`${(result.with_meta_labeling.win_rate * 100).toFixed(1)}%`}
                  color="green"
                />
                <MetricRow label="Num Trades" value={result.with_meta_labeling.num_trades} color="green" />
                <MetricRow
                  label="Avg Trade"
                  value={`${(result.with_meta_labeling.avg_trade_return * 100).toFixed(2)}%`}
                  color="green"
                />
              </div>
            </div>
          </div>

          {/* Improvement Summary */}
          <div className="bg-purple-900/20 border border-purple-700 rounded-lg p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Improvement Summary</h3>
            <div className="grid grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-sm text-gray-400 mb-1">Return Improvement</div>
                <div className="text-3xl font-bold text-green-400">
                  +{(result.improvement.return_improvement * 100).toFixed(1)}%
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-400 mb-1">Sharpe Improvement</div>
                <div className="text-3xl font-bold text-blue-400">
                  +{(result.improvement.sharpe_improvement * 100).toFixed(1)}%
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-400 mb-1">Drawdown Reduction</div>
                <div className="text-3xl font-bold text-purple-400">
                  {(result.improvement.drawdown_improvement * 100).toFixed(1)}%
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-400 mb-1">Trades Filtered</div>
                <div className="text-3xl font-bold text-yellow-400">{result.improvement.trades_filtered}</div>
              </div>
            </div>
          </div>

          {/* Equity Curves */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            {generateEquityCurves()}
          </div>

          {/* Conclusion */}
          <div className="bg-green-900/20 border border-green-700 rounded-lg p-4">
            <div className="text-sm text-green-400">
              {result.improvement.return_improvement > 0 ? (
                <>
                  ✅ Meta-labeling improved performance! The model successfully filtered {result.improvement.trades_filtered} low-quality trades,
                  resulting in better returns and reduced drawdowns.
                </>
              ) : (
                <>
                  ⚠️ Meta-labeling did not improve performance in this period. Consider retraining with different features or adjusting the model.
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricRow({ label, value, color }: any) {
  const colorClasses: any = {
    red: 'text-red-400',
    green: 'text-green-400',
  };

  return (
    <div className="flex items-center justify-between p-2 bg-dark-bg rounded">
      <span className="text-sm text-gray-400">{label}</span>
      <span className={`font-mono font-semibold ${colorClasses[color]}`}>{value}</span>
    </div>
  );
}
