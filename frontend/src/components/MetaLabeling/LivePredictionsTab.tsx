/**
 * Live Predictions Tab - Real-time meta-labeling predictions
 */

import { useState, useEffect } from 'react';
import { Loader, Info, Activity, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { metaLabelingApi, type PredictParams, type PredictResponse, type ModelInfo } from '../../api/metaLabelingApi';

export function LivePredictionsTab() {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModelId, setSelectedModelId] = useState('');
  const [features, setFeatures] = useState<Record<string, number>>({});
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingModels, setLoadingModels] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load available models on mount
  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setLoadingModels(true);
    try {
      const data = await metaLabelingApi.listModels();
      setModels(data);
      if (data.length > 0 && !selectedModelId) {
        setSelectedModelId(data[0].model_id);
        // Initialize features for the first model
        const initialFeatures: Record<string, number> = {};
        data[0].features.forEach(f => {
          initialFeatures[f] = 0;
        });
        setFeatures(initialFeatures);
      }
    } catch (err: any) {
      setError(err.message || 'Backend not running! Start: python backend/metalabeling_service/app.py');
    } finally {
      setLoadingModels(false);
    }
  };

  const handleModelChange = (modelId: string) => {
    setSelectedModelId(modelId);
    const model = models.find(m => m.model_id === modelId);
    if (model) {
      const newFeatures: Record<string, number> = {};
      model.features.forEach(f => {
        newFeatures[f] = features[f] || 0;
      });
      setFeatures(newFeatures);
    }
    setPrediction(null);
  };

  const handleFeatureChange = (feature: string, value: string) => {
    setFeatures({
      ...features,
      [feature]: parseFloat(value) || 0,
    });
  };

  const handlePredict = async () => {
    if (!selectedModelId) {
      setError('Please select a model');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const params: PredictParams = {
        model_id: selectedModelId,
        features,
      };

      const data = await metaLabelingApi.predict(params);
      setPrediction(data);
    } catch (err: any) {
      setError(err.message || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const selectedModel = models.find(m => m.model_id === selectedModelId);

  return (
    <div className="space-y-6">
      {/* Model Selection */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold text-white">Live Predictions</h2>
          <button
            onClick={loadModels}
            disabled={loadingModels}
            className="flex items-center gap-2 px-3 py-2 bg-dark-border hover:bg-dark-border-hover rounded-lg transition text-sm"
          >
            <RefreshCw className={`w-4 h-4 ${loadingModels ? 'animate-spin' : ''}`} />
            Refresh Models
          </button>
        </div>

        {models.length === 0 ? (
          <div className="bg-yellow-900/20 border border-yellow-700 rounded-lg p-4">
            <div className="text-sm text-yellow-400">
              No trained models found. Go to the "Train Model" tab to create a meta-labeling model first.
            </div>
          </div>
        ) : (
          <>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">Select Model</label>
              <select
                value={selectedModelId}
                onChange={(e) => handleModelChange(e.target.value)}
                className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-purple-500"
              >
                {models.map((m) => (
                  <option key={m.model_id} value={m.model_id}>
                    {m.model_id} - {m.primary_strategy} ({m.model_type}) - Acc: {(m.accuracy * 100).toFixed(1)}%
                  </option>
                ))}
              </select>
            </div>

            {selectedModel && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="bg-dark-bg rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-1">Strategy</div>
                  <div className="text-sm font-semibold text-white">{selectedModel.primary_strategy}</div>
                </div>
                <div className="bg-dark-bg rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-1">Model Type</div>
                  <div className="text-sm font-semibold text-white">{selectedModel.model_type}</div>
                </div>
                <div className="bg-dark-bg rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-1">Accuracy</div>
                  <div className="text-sm font-semibold text-green-400">{(selectedModel.accuracy * 100).toFixed(1)}%</div>
                </div>
                <div className="bg-dark-bg rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-1">F1 Score</div>
                  <div className="text-sm font-semibold text-blue-400">{selectedModel.f1_score.toFixed(3)}</div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Feature Input */}
      {selectedModel && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Current Market Features</h3>
          <p className="text-sm text-gray-400 mb-6">
            Enter current market conditions for the features below. The model will predict whether your primary strategy signal should be taken.
          </p>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            {selectedModel.features.map((feature) => (
              <div key={feature}>
                <label className="block text-sm font-medium text-gray-300 mb-2">{feature}</label>
                <input
                  type="number"
                  step="0.01"
                  value={features[feature] || 0}
                  onChange={(e) => handleFeatureChange(feature, e.target.value)}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white font-mono focus:outline-none focus:border-purple-500"
                  placeholder="0.00"
                />
              </div>
            ))}
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

          {/* Predict Button */}
          <button
            onClick={handlePredict}
            disabled={loading}
            className="w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Predicting...
              </>
            ) : (
              <>
                <Activity className="w-5 h-5" />
                Get Prediction
              </>
            )}
          </button>
        </div>
      )}

      {/* Prediction Result */}
      {prediction && (
        <div className="space-y-6">
          {/* Signal Badge */}
          <div
            className={`rounded-lg p-8 border-2 ${
              prediction.signal === 'TRADE'
                ? 'bg-green-900/30 border-green-500'
                : 'bg-red-900/30 border-red-500'
            }`}
          >
            <div className="flex items-center justify-center gap-4 mb-4">
              {prediction.signal === 'TRADE' ? (
                <CheckCircle className="w-16 h-16 text-green-400" />
              ) : (
                <XCircle className="w-16 h-16 text-red-400" />
              )}
              <div>
                <div className="text-sm text-gray-400 mb-1">Prediction</div>
                <div
                  className={`text-5xl font-bold ${
                    prediction.signal === 'TRADE' ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  {prediction.signal}
                </div>
              </div>
            </div>

            <div className="text-center text-gray-300">
              {prediction.signal === 'TRADE' ? (
                <>
                  ✅ The model predicts this signal will be <strong>profitable</strong>. Consider taking the trade.
                </>
              ) : (
                <>
                  ⛔ The model predicts this signal will <strong>not be profitable</strong>. Consider skipping this trade.
                </>
              )}
            </div>
          </div>

          {/* Confidence Metrics */}
          <div className="grid grid-cols-3 gap-6">
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Probability</div>
              <div className="text-4xl font-bold text-purple-400">{(prediction.probability * 100).toFixed(1)}%</div>
              <div className="text-xs text-gray-500 mt-2">Model confidence in prediction</div>
            </div>

            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Confidence Score</div>
              <div className="text-4xl font-bold text-blue-400">{(prediction.confidence * 100).toFixed(1)}%</div>
              <div className="text-xs text-gray-500 mt-2">Overall prediction confidence</div>
            </div>

            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <div className="text-sm text-gray-400 mb-1">Model ID</div>
              <div className="text-sm font-mono font-bold text-white mt-2">{prediction.model_id}</div>
              <div className="text-xs text-gray-500 mt-2">{prediction.features_used.length} features used</div>
            </div>
          </div>

          {/* Features Used */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Features Used in Prediction</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {prediction.features_used.map((feature) => (
                <div key={feature} className="bg-dark-bg rounded-lg p-3">
                  <div className="text-xs text-gray-400">{feature}</div>
                  <div className="text-lg font-mono font-semibold text-white">{features[feature]?.toFixed(4) || 'N/A'}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendation */}
          <div
            className={`rounded-lg p-4 border ${
              prediction.signal === 'TRADE'
                ? 'bg-green-900/20 border-green-700'
                : 'bg-red-900/20 border-red-700'
            }`}
          >
            <div className={`text-sm ${prediction.signal === 'TRADE' ? 'text-green-400' : 'text-red-400'}`}>
              <strong>Recommended Action:</strong>{' '}
              {prediction.signal === 'TRADE'
                ? `Take the trade with position size proportional to confidence (${(prediction.confidence * 100).toFixed(0)}%).`
                : `Skip this trade. Wait for a higher-quality signal from your primary strategy.`}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
