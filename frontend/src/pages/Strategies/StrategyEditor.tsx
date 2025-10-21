/**
 * Strategy Editor (Level 3) - Edit strategy configuration
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Save, Play, Trash2, Plus, X } from 'lucide-react';
import { useStrategyStore } from '../../store/useStrategyStore';

interface Condition {
  id: number;
  type: string;
  description: string;
  enabled: boolean;
}

interface Parameter {
  name: string;
  value: string;
  description: string;
}

export function StrategyEditor() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedStrategy, loadingStrategy, fetchStrategy, updateStrategy } = useStrategyStore();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');

  const [entryConditions, setEntryConditions] = useState<Condition[]>([
    { id: 1, type: 'Technical', description: 'RSI < 30 (Oversold)', enabled: true },
    { id: 2, type: 'Technical', description: 'MACD crosses above signal line', enabled: true },
    { id: 3, type: 'Volume', description: 'Volume > 20-day average', enabled: true },
  ]);

  const [exitConditions, setExitConditions] = useState<Condition[]>([
    { id: 1, type: 'Target', description: 'Take profit at +5%', enabled: true },
    { id: 2, type: 'Stop Loss', description: 'Stop loss at -2%', enabled: true },
    { id: 3, type: 'Technical', description: 'RSI > 70 (Overbought)', enabled: true },
  ]);

  const [parameters, setParameters] = useState<Parameter[]>([
    { name: 'Position Size', value: '10', description: 'Percentage of portfolio per trade' },
    { name: 'Max Positions', value: '5', description: 'Maximum concurrent positions' },
    { name: 'Stop Loss', value: '2', description: 'Maximum loss per trade (%)' },
    { name: 'Take Profit', value: '5', description: 'Target profit per trade (%)' },
    { name: 'RSI Period', value: '14', description: 'RSI calculation period' },
    { name: 'MACD Fast', value: '12', description: 'MACD fast EMA period' },
    { name: 'MACD Slow', value: '26', description: 'MACD slow EMA period' },
    { name: 'MACD Signal', value: '9', description: 'MACD signal line period' },
  ]);

  useEffect(() => {
    if (id) {
      fetchStrategy(id);
    }
  }, [id, fetchStrategy]);

  useEffect(() => {
    if (selectedStrategy) {
      setName(selectedStrategy.name);
      setDescription(selectedStrategy.description);
      setCategory(selectedStrategy.category || 'Momentum');
    }
  }, [selectedStrategy]);

  const handleSave = async () => {
    if (!selectedStrategy) return;

    try {
      await updateStrategy(selectedStrategy.id, {
        name,
        description,
        category,
        parameters: {
          positionSize: parameters.find((p) => p.name === 'Position Size')?.value || '10%',
          stopLoss: parameters.find((p) => p.name === 'Stop Loss')?.value || '2%',
          takeProfit: parameters.find((p) => p.name === 'Take Profit')?.value || '5%',
        },
      });
      navigate(`/strategies/${selectedStrategy.id}`);
    } catch (error) {
      console.error('Failed to save strategy:', error);
      alert('Failed to save strategy');
    }
  };

  const toggleCondition = (type: 'entry' | 'exit', id: number) => {
    if (type === 'entry') {
      setEntryConditions(
        entryConditions.map((c) => (c.id === id ? { ...c, enabled: !c.enabled } : c))
      );
    } else {
      setExitConditions(
        exitConditions.map((c) => (c.id === id ? { ...c, enabled: !c.enabled } : c))
      );
    }
  };

  const removeCondition = (type: 'entry' | 'exit', id: number) => {
    if (type === 'entry') {
      setEntryConditions(entryConditions.filter((c) => c.id !== id));
    } else {
      setExitConditions(exitConditions.filter((c) => c.id !== id));
    }
  };

  const updateParameter = (name: string, value: string) => {
    setParameters(parameters.map((p) => (p.name === name ? { ...p, value } : p)));
  };

  if (loadingStrategy) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-400">Loading strategy...</p>
        </div>
      </div>
    );
  }

  if (!selectedStrategy) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-400 mb-4">Strategy not found</p>
        <button onClick={() => navigate('/strategies')} className="btn-primary">
          Back to Strategies
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <button
            onClick={() => navigate(`/strategies/${selectedStrategy.id}`)}
            className="flex items-center gap-2 text-gray-400 hover:text-white mb-3 transition-colors"
          >
            <ArrowLeft size={18} />
            Back to Strategy Detail
          </button>
          <h1 className="text-3xl font-bold text-white">Edit Strategy</h1>
          <p className="text-gray-400 mt-1">Modify parameters and conditions</p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate(`/strategies/${selectedStrategy.id}`)}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded flex items-center gap-2 transition-colors"
          >
            <Save size={18} />
            Save Changes
          </button>
        </div>
      </div>

      {/* Basic Info */}
      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Basic Information</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Strategy Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="input-field w-full"
              placeholder="Enter strategy name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="input-field w-full"
              rows={3}
              placeholder="Enter strategy description"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="input-field w-full"
            >
              <option value="Momentum">Momentum</option>
              <option value="Mean Reversion">Mean Reversion</option>
              <option value="Trend Following">Trend Following</option>
              <option value="Scalping">Scalping</option>
              <option value="Swing Trading">Swing Trading</option>
              <option value="Machine Learning">Machine Learning</option>
            </select>
          </div>
        </div>
      </div>

      {/* Entry Conditions */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Entry Conditions</h2>
          <button className="px-3 py-1.5 bg-green-700 hover:bg-green-600 text-white text-sm rounded flex items-center gap-1 transition-colors">
            <Plus size={16} />
            Add Condition
          </button>
        </div>
        <div className="space-y-3">
          {entryConditions.map((condition) => (
            <div
              key={condition.id}
              className={`p-4 rounded border ${
                condition.enabled
                  ? 'bg-green-900/10 border-green-700'
                  : 'bg-gray-800 border-gray-700'
              }`}
            >
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked={condition.enabled}
                  onChange={() => toggleCondition('entry', condition.id)}
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 text-xs font-semibold bg-gray-700 text-gray-300 rounded">
                      {condition.type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-300">{condition.description}</p>
                </div>
                <button
                  onClick={() => removeCondition('entry', condition.id)}
                  className="p-1 hover:bg-red-900/30 text-red-400 rounded transition-colors"
                >
                  <X size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Exit Conditions */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Exit Conditions</h2>
          <button className="px-3 py-1.5 bg-red-700 hover:bg-red-600 text-white text-sm rounded flex items-center gap-1 transition-colors">
            <Plus size={16} />
            Add Condition
          </button>
        </div>
        <div className="space-y-3">
          {exitConditions.map((condition) => (
            <div
              key={condition.id}
              className={`p-4 rounded border ${
                condition.enabled
                  ? 'bg-red-900/10 border-red-700'
                  : 'bg-gray-800 border-gray-700'
              }`}
            >
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked={condition.enabled}
                  onChange={() => toggleCondition('exit', condition.id)}
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 text-xs font-semibold bg-gray-700 text-gray-300 rounded">
                      {condition.type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-300">{condition.description}</p>
                </div>
                <button
                  onClick={() => removeCondition('exit', condition.id)}
                  className="p-1 hover:bg-red-900/30 text-red-400 rounded transition-colors"
                >
                  <X size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Parameters */}
      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Parameters</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {parameters.map((param, index) => (
            <div key={index}>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                {param.name}
              </label>
              <input
                type="text"
                value={param.value}
                onChange={(e) => updateParameter(param.name, e.target.value)}
                className="input-field w-full"
                placeholder={param.description}
              />
              <p className="text-xs text-gray-500 mt-1">{param.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Validation Warning */}
      <div className="card bg-yellow-900/20 border-yellow-700">
        <h3 className="text-yellow-400 font-semibold mb-2">Validation</h3>
        <p className="text-sm text-gray-300">
          Please ensure all parameters are valid before saving. Invalid configurations may cause
          the strategy to fail during deployment.
        </p>
      </div>

      {/* Footer Actions */}
      <div className="flex items-center justify-between pb-8">
        <button
          onClick={() => {
            if (confirm('Delete this strategy? This action cannot be undone.')) {
              navigate('/strategies');
            }
          }}
          className="px-4 py-2 bg-red-900 hover:bg-red-800 text-white rounded flex items-center gap-2 transition-colors"
        >
          <Trash2 size={18} />
          Delete Strategy
        </button>
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate(`/strategies/${selectedStrategy.id}`)}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded flex items-center gap-2 transition-colors"
          >
            <Save size={18} />
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
