/**
 * Configuration Tab - View strategy parameters and conditions
 */

import { useNavigate } from 'react-router-dom';
import { Edit, AlertTriangle, CheckCircle, TrendingUp, TrendingDown } from 'lucide-react';
import type { StrategyExtended } from '../../../services/mock-data/strategy-data';

interface ConfigurationTabProps {
  strategy: StrategyExtended;
}

export function ConfigurationTab({ strategy }: ConfigurationTabProps) {
  const navigate = useNavigate();

  // Mock configuration data
  const entryConditions = [
    { id: 1, type: 'Technical', description: 'RSI < 30 (Oversold)', enabled: true },
    { id: 2, type: 'Technical', description: 'MACD crosses above signal line', enabled: true },
    { id: 3, type: 'Volume', description: 'Volume > 20-day average', enabled: true },
    {
      id: 4,
      type: 'Price Action',
      description: 'Price breaks above resistance with confirmation',
      enabled: false,
    },
  ];

  const exitConditions = [
    { id: 1, type: 'Target', description: 'Take profit at +5%', enabled: true },
    { id: 2, type: 'Stop Loss', description: 'Stop loss at -2%', enabled: true },
    { id: 3, type: 'Technical', description: 'RSI > 70 (Overbought)', enabled: true },
    { id: 4, type: 'Time-based', description: 'Close position after 5 days', enabled: false },
  ];

  const parameters = [
    { name: 'Position Size', value: '10%', description: 'Percentage of portfolio per trade' },
    { name: 'Max Positions', value: '5', description: 'Maximum concurrent positions' },
    { name: 'Stop Loss', value: '2%', description: 'Maximum loss per trade' },
    { name: 'Take Profit', value: '5%', description: 'Target profit per trade' },
    { name: 'RSI Period', value: '14', description: 'RSI calculation period' },
    { name: 'MACD Fast', value: '12', description: 'MACD fast EMA period' },
    { name: 'MACD Slow', value: '26', description: 'MACD slow EMA period' },
    { name: 'MACD Signal', value: '9', description: 'MACD signal line period' },
  ];

  const riskLimits = [
    { name: 'Max Daily Loss', value: '$2,000', current: '$450', percentage: 22.5 },
    { name: 'Max Position Size', value: '$25,000', current: '$18,500', percentage: 74 },
    { name: 'Max Drawdown', value: '15%', current: '8.3%', percentage: 55.3 },
    { name: 'Position Limit', value: '5', current: '3', percentage: 60 },
  ];

  return (
    <div className="space-y-6">
      {/* Header with Edit Button */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">Strategy Configuration</h2>
        <button
          onClick={() => navigate(`/strategies/${strategy.id}/edit`)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded flex items-center gap-2 transition-colors"
        >
          <Edit size={18} />
          Edit Configuration
        </button>
      </div>

      {/* Entry Conditions */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="text-green-400" size={20} />
          <h3 className="text-lg font-semibold text-white">Entry Conditions</h3>
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
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 text-xs font-semibold bg-gray-700 text-gray-300 rounded">
                      {condition.type}
                    </span>
                    {condition.enabled ? (
                      <CheckCircle size={16} className="text-green-400" />
                    ) : (
                      <AlertTriangle size={16} className="text-gray-500" />
                    )}
                  </div>
                  <p className="text-sm text-gray-300">{condition.description}</p>
                </div>
                <span
                  className={`text-xs font-semibold ${
                    condition.enabled ? 'text-green-400' : 'text-gray-500'
                  }`}
                >
                  {condition.enabled ? 'ACTIVE' : 'DISABLED'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Exit Conditions */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <TrendingDown className="text-red-400" size={20} />
          <h3 className="text-lg font-semibold text-white">Exit Conditions</h3>
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
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 text-xs font-semibold bg-gray-700 text-gray-300 rounded">
                      {condition.type}
                    </span>
                    {condition.enabled ? (
                      <CheckCircle size={16} className="text-green-400" />
                    ) : (
                      <AlertTriangle size={16} className="text-gray-500" />
                    )}
                  </div>
                  <p className="text-sm text-gray-300">{condition.description}</p>
                </div>
                <span
                  className={`text-xs font-semibold ${
                    condition.enabled ? 'text-green-400' : 'text-gray-500'
                  }`}
                >
                  {condition.enabled ? 'ACTIVE' : 'DISABLED'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Parameters */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Parameters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {parameters.map((param, index) => (
            <div key={index} className="p-4 bg-gray-800 rounded">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-400">{param.name}</span>
                <span className="text-lg font-bold text-white">{param.value}</span>
              </div>
              <p className="text-xs text-gray-500">{param.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Limits */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Risk Limits</h3>
        <div className="space-y-4">
          {riskLimits.map((limit, index) => (
            <div key={index}>
              <div className="flex items-center justify-between mb-2">
                <div>
                  <div className="text-sm font-medium text-white">{limit.name}</div>
                  <div className="text-xs text-gray-500">
                    {limit.current} of {limit.value}
                  </div>
                </div>
                <span className="text-sm font-semibold text-gray-400">
                  {limit.percentage.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    limit.percentage >= 90
                      ? 'bg-red-500'
                      : limit.percentage >= 70
                      ? 'bg-yellow-500'
                      : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(limit.percentage, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
        <div className="mt-6 p-4 bg-blue-900/20 border border-blue-700 rounded">
          <p className="text-sm text-gray-300">
            <strong className="text-blue-400">Note:</strong> Risk limits are enforced in real-time.
            When a limit is reached, the strategy will automatically stop taking new positions.
          </p>
        </div>
      </div>
    </div>
  );
}
