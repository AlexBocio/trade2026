/**
 * Alert Builder - Create new alert
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, X } from 'lucide-react';
import { useAlertsStore } from '../../store/useAlertsStore';
import { useWatchlistsStore } from '../../store/useWatchlistsStore';

interface AlertCondition {
  id: string;
  type: 'price' | 'volume' | 'change' | 'rsi' | 'strategy' | 'catalyst';
  operator: '>' | '<' | '>=' | '<=' | '=' | 'crosses_above' | 'crosses_below';
  value: number | string;
  description: string;
}

export function AlertBuilder() {
  const navigate = useNavigate();
  const { createAlert } = useAlertsStore();
  const { watchlists } = useWatchlistsStore();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [watchlistId, setWatchlistId] = useState<string | null>(null);
  const [conditions, setConditions] = useState<AlertCondition[]>([]);
  const [deliveryMethods, setDeliveryMethods] = useState<string[]>(['push']);

  const addCondition = () => {
    setConditions([
      ...conditions,
      {
        id: `cond-${Date.now()}`,
        type: 'price',
        operator: '>',
        value: 0,
        description: '',
      },
    ]);
  };

  const removeCondition = (id: string) => {
    setConditions(conditions.filter((c) => c.id !== id));
  };

  const updateCondition = (id: string, updates: Partial<AlertCondition>) => {
    setConditions(
      conditions.map((c) => (c.id === id ? { ...c, ...updates } : c))
    );
  };

  const generateConditionDescription = (condition: AlertCondition): string => {
    const typeLabels: any = {
      price: 'Price',
      volume: 'Volume',
      change: '% Change',
      rsi: 'RSI',
      strategy: 'Strategy Signal',
      catalyst: 'Catalyst',
    };

    const operatorLabels: any = {
      '>': 'greater than',
      '<': 'less than',
      '>=': 'greater than or equal to',
      '<=': 'less than or equal to',
      '=': 'equal to',
      crosses_above: 'crosses above',
      crosses_below: 'crosses below',
    };

    return `Alert when ${typeLabels[condition.type]} is ${
      operatorLabels[condition.operator]
    } ${condition.value}`;
  };

  const handleSubmit = async () => {
    if (!name || conditions.length === 0) {
      alert('Please provide a name and at least one condition');
      return;
    }

    await createAlert({
      name,
      description,
      watchlistId,
      conditions,
      deliveryMethods,
    });

    navigate('/alerts');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/alerts')}
            className="p-2 hover:bg-dark-border rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white">Create New Alert</h1>
            <p className="text-sm text-gray-400">
              Set up conditions to monitor your trading opportunities
            </p>
          </div>
        </div>
      </div>

      {/* Basic Info */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-lg font-semibold text-white mb-4">
          Basic Information
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Alert Name *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Volume Spike Alert"
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Description
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g., Notify when volume exceeds 300% of average"
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Watch</label>
            <select
              value={watchlistId || ''}
              onChange={(e) => setWatchlistId(e.target.value || null)}
              className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
            >
              <option value="">All small-cap stocks</option>
              {watchlists.map((wl) => (
                <option key={wl.id} value={wl.id}>
                  {wl.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Conditions */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Conditions *</h2>
          <button
            onClick={addCondition}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg flex items-center gap-2 transition"
          >
            <Plus className="w-4 h-4" />
            Add Condition
          </button>
        </div>

        {conditions.length === 0 && (
          <p className="text-gray-400 text-center py-8">
            Add at least one condition to trigger this alert
          </p>
        )}

        <div className="space-y-4">
          {conditions.map((condition, index) => (
            <div key={condition.id} className="bg-dark-bg rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="text-sm text-gray-400">
                  Condition {index + 1}
                </div>
                <button
                  onClick={() => removeCondition(condition.id)}
                  className="text-red-400 hover:text-red-300 transition"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="grid grid-cols-3 gap-3">
                {/* Type */}
                <div>
                  <label className="block text-xs text-gray-400 mb-2">
                    Type
                  </label>
                  <select
                    value={condition.type}
                    onChange={(e) =>
                      updateCondition(condition.id, {
                        type: e.target.value as any,
                      })
                    }
                    className="w-full px-3 py-2 bg-dark-card border border-dark-border rounded text-white text-sm"
                  >
                    <option value="price">Price</option>
                    <option value="volume">Volume</option>
                    <option value="change">% Change</option>
                    <option value="rsi">RSI</option>
                    <option value="strategy">Strategy Signal</option>
                    <option value="catalyst">Catalyst</option>
                  </select>
                </div>

                {/* Operator */}
                <div>
                  <label className="block text-xs text-gray-400 mb-2">
                    Operator
                  </label>
                  <select
                    value={condition.operator}
                    onChange={(e) =>
                      updateCondition(condition.id, {
                        operator: e.target.value as any,
                      })
                    }
                    className="w-full px-3 py-2 bg-dark-card border border-dark-border rounded text-white text-sm"
                  >
                    <option value=">">Greater than</option>
                    <option value="<">Less than</option>
                    <option value=">=">Greater or equal</option>
                    <option value="<=">Less or equal</option>
                    <option value="=">Equal to</option>
                    <option value="crosses_above">Crosses above</option>
                    <option value="crosses_below">Crosses below</option>
                  </select>
                </div>

                {/* Value */}
                <div>
                  <label className="block text-xs text-gray-400 mb-2">
                    Value
                  </label>
                  <input
                    type="number"
                    value={condition.value}
                    onChange={(e) =>
                      updateCondition(condition.id, {
                        value: Number(e.target.value),
                      })
                    }
                    className="w-full px-3 py-2 bg-dark-card border border-dark-border rounded text-white text-sm"
                  />
                </div>
              </div>

              {/* Generated Description */}
              <div className="mt-3 text-sm text-gray-400">
                {generateConditionDescription(condition)}
              </div>
            </div>
          ))}
        </div>

        {conditions.length > 1 && (
          <div className="mt-4 text-sm text-gray-400">
            <strong>Logic:</strong> ALL conditions must be true (AND logic)
          </div>
        )}
      </div>

      {/* Delivery Methods */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-lg font-semibold text-white mb-4">
          Delivery Methods
        </h2>

        <div className="space-y-3">
          {[
            {
              id: 'push',
              label: 'Push Notification',
              description: 'In-app notification',
            },
            {
              id: 'email',
              label: 'Email',
              description: 'Send to your email',
            },
            {
              id: 'sms',
              label: 'SMS',
              description: 'Text message (charges apply)',
            },
          ].map((method) => (
            <label
              key={method.id}
              className="flex items-center gap-3 p-3 bg-dark-bg rounded-lg cursor-pointer hover:bg-dark-border transition"
            >
              <input
                type="checkbox"
                checked={deliveryMethods.includes(method.id)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setDeliveryMethods([...deliveryMethods, method.id]);
                  } else {
                    setDeliveryMethods(
                      deliveryMethods.filter((m) => m !== method.id)
                    );
                  }
                }}
                className="w-4 h-4"
              />
              <div>
                <div className="font-semibold text-white">{method.label}</div>
                <div className="text-sm text-gray-400">{method.description}</div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={handleSubmit}
          className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition"
        >
          Create Alert
        </button>
        <button
          onClick={() => navigate('/alerts')}
          className="px-6 py-3 bg-dark-border hover:bg-dark-border-hover rounded-lg font-semibold transition"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
