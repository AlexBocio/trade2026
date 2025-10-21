/**
 * Train Model Tab - Train meta-labeling models
 */

import { useState } from 'react';
import { Loader, Info, Brain } from 'lucide-react';
import Plot from 'react-plotly.js';
import { metaLabelingApi, type TrainParams, type TrainResponse } from '../../api/metaLabelingApi';

const PRIMARY_STRATEGIES = [
  { id: 'momentum', name: 'Momentum Crossover' },
  { id: 'mean_reversion', name: 'Mean Reversion' },
  { id: 'breakout', name: 'Breakout' },
  { id: 'trend_following', name: 'Trend Following' },
];

const AVAILABLE_FEATURES = [
  'volatility_20d',
  'volume_ratio',
  'rsi_14',
  'macd_signal',
  'bollinger_position',
  'atr_14',
  'adx_14',
  'market_regime',
  'correlation_spy',
  'put_call_ratio',
];

const MODEL_TYPES = [
  { id: 'random_forest', name: 'Random Forest', description: 'Robust, handles non-linear relationships' },
  { id: 'xgboost', name: 'XGBoost', description: 'Best overall performance, gradient boosting' },
  { id: 'lightgbm', name: 'LightGBM', description: 'Fast training, good for large datasets' },
];

export function TrainModelTab() {
  const [primaryStrategy, setPrimaryStrategy] = useState('momentum');
  const [selectedFeatures, setSelectedFeatures] = useState<string[]>([
    'volatility_20d',
    'volume_ratio',
    'rsi_14',
    'macd_signal',
  ]);
  const [startDate, setStartDate] = useState('2020-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [modelType, setModelType] = useState<'random_forest' | 'xgboost' | 'lightgbm'>('xgboost');
  const [nEstimators, setNEstimators] = useState(100);
  const [maxDepth, setMaxDepth] = useState(10);
  const [cvFolds, setCvFolds] = useState(5);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TrainResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const toggleFeature = (feature: string) => {
    if (selectedFeatures.includes(feature)) {
      setSelectedFeatures(selectedFeatures.filter((f) => f !== feature));
    } else {
      setSelectedFeatures([...selectedFeatures, feature]);
    }
  };

  const handleTrain = async () => {
    if (selectedFeatures.length === 0) {
      setError('Please select at least one feature');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const params: TrainParams = {
        primary_strategy: primaryStrategy,
        features: selectedFeatures,
        start_date: startDate,
        end_date: endDate,
        model_type: modelType,
        n_estimators: nEstimators,
        max_depth: maxDepth,
        cv_folds: cvFolds,
      };

      const data = await metaLabelingApi.train(params);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Backend not running! Start: python backend/metalabeling_service/app.py');
    } finally {
      setLoading(false);
    }
  };

  // Generate feature importance chart
  const generateFeatureImportanceChart = () => {
    if (!result) return null;

    const features = Object.keys(result.feature_importance);
    const importance = Object.values(result.feature_importance);

    return (
      <Plot
        data={[
          {
            x: importance,
            y: features,
            type: 'bar',
            orientation: 'h',
            marker: { color: '#8B5CF6' },
          },
        ]}
        layout={{
          title: {
            text: 'Feature Importance',
            font: { color: '#fff', size: 18 },
          },
          paper_bgcolor: '#1a1f2e',
          plot_bgcolor: '#1a1f2e',
          font: { color: '#9CA3AF' },
          xaxis: {
            title: 'Importance',
            gridcolor: '#374151',
            color: '#9CA3AF',
          },
          yaxis: {
            gridcolor: '#374151',
            color: '#9CA3AF',
          },
          height: 400,
          margin: { l: 150, r: 20, t: 50, b: 50 },
        }}
        config={{ displayModeBar: false }}
        className="w-full"
      />
    );
  };

  // Generate confusion matrix heatmap
  const generateConfusionMatrix = () => {
    if (!result) return null;

    const cm = result.confusion_matrix;
    const labels = ['No Trade', 'Trade'];

    return (
      <Plot
        data={[
          {
            z: cm,
            x: labels,
            y: labels,
            type: 'heatmap',
            colorscale: 'Purples',
            text: cm.map(row => row.map(val => val.toString())),
            texttemplate: '%{text}',
            textfont: { size: 16, color: 'white' },
            showscale: false,
          },
        ]}
        layout={{
          title: {
            text: 'Confusion Matrix',
            font: { color: '#fff', size: 18 },
          },
          paper_bgcolor: '#1a1f2e',
          plot_bgcolor: '#1a1f2e',
          font: { color: '#9CA3AF' },
          xaxis: {
            title: 'Predicted',
            color: '#9CA3AF',
          },
          yaxis: {
            title: 'Actual',
            color: '#9CA3AF',
          },
          height: 400,
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
        <h2 className="text-2xl font-semibold text-white mb-4">Model Configuration</h2>

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

        {/* Feature Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Features ({selectedFeatures.length} selected)
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {AVAILABLE_FEATURES.map((feature) => (
              <button
                key={feature}
                onClick={() => toggleFeature(feature)}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition ${
                  selectedFeatures.includes(feature)
                    ? 'bg-purple-600 text-white'
                    : 'bg-dark-bg text-gray-400 hover:bg-dark-border'
                }`}
              >
                {feature}
              </button>
            ))}
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
        </div>

        {/* Model Type Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">Model Type</label>
          <div className="grid grid-cols-3 gap-4">
            {MODEL_TYPES.map((m) => (
              <button
                key={m.id}
                onClick={() => setModelType(m.id as any)}
                className={`p-4 rounded-lg border-2 transition text-left ${
                  modelType === m.id
                    ? 'border-purple-400 bg-purple-900/20'
                    : 'border-dark-border hover:border-dark-border-hover'
                }`}
              >
                <div className="font-semibold text-white mb-1">{m.name}</div>
                <div className="text-xs text-gray-400">{m.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Hyperparameters */}
        <div className="grid grid-cols-3 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              N Estimators: <span className="text-purple-400 font-mono">{nEstimators}</span>
            </label>
            <input
              type="range"
              min="50"
              max="500"
              step="50"
              value={nEstimators}
              onChange={(e) => setNEstimators(parseInt(e.target.value))}
              className="w-full h-2 bg-dark-bg rounded-lg appearance-none cursor-pointer"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Max Depth: <span className="text-purple-400 font-mono">{maxDepth}</span>
            </label>
            <input
              type="range"
              min="3"
              max="20"
              step="1"
              value={maxDepth}
              onChange={(e) => setMaxDepth(parseInt(e.target.value))}
              className="w-full h-2 bg-dark-bg rounded-lg appearance-none cursor-pointer"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              CV Folds: <span className="text-purple-400 font-mono">{cvFolds}</span>
            </label>
            <input
              type="range"
              min="3"
              max="10"
              step="1"
              value={cvFolds}
              onChange={(e) => setCvFolds(parseInt(e.target.value))}
              className="w-full h-2 bg-dark-bg rounded-lg appearance-none cursor-pointer"
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
          onClick={handleTrain}
          disabled={loading || selectedFeatures.length === 0}
          className="w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Training Model...
            </>
          ) : (
            <>
              <Brain className="w-5 h-5" />
              Train Meta-Labeling Model
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Model ID Badge */}
          <div className="bg-purple-900/20 border border-purple-700 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-400">Model ID</div>
                <div className="text-lg font-mono font-bold text-purple-400">{result.model_id}</div>
              </div>
              <div className="text-sm text-gray-400">
                Training: {result.training_samples} samples | Test: {result.test_samples} samples
              </div>
            </div>
          </div>

          {/* Metrics Cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Accuracy</div>
              <div className="text-3xl font-bold text-green-400">{(result.accuracy * 100).toFixed(1)}%</div>
            </div>
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Precision</div>
              <div className="text-3xl font-bold text-blue-400">{(result.precision * 100).toFixed(1)}%</div>
            </div>
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Recall</div>
              <div className="text-3xl font-bold text-yellow-400">{(result.recall * 100).toFixed(1)}%</div>
            </div>
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">F1 Score</div>
              <div className="text-3xl font-bold text-purple-400">{result.f1_score.toFixed(3)}</div>
            </div>
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">ROC AUC</div>
              <div className="text-3xl font-bold text-pink-400">{result.roc_auc.toFixed(3)}</div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              {generateFeatureImportanceChart()}
            </div>
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              {generateConfusionMatrix()}
            </div>
          </div>

          {/* Best Parameters */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Best Hyperparameters (from CV)</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(result.best_params).map(([key, value]) => (
                <div key={key} className="bg-dark-bg rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-1">{key}</div>
                  <div className="text-lg font-mono font-semibold text-white">{String(value)}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Next Steps */}
          <div className="bg-green-900/20 border border-green-700 rounded-lg p-4">
            <div className="text-sm text-green-400">
              ✅ Model trained successfully! Copy the Model ID above and use it in the "Backtest Comparison" or "Live Predictions" tabs.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
