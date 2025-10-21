/**
 * Meta-Labeling - Predict when primary strategy will be profitable
 */

import { useState } from 'react';
import { ArrowLeft, Brain } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { TrainModelTab } from '../../components/MetaLabeling/TrainModelTab';
import { BacktestComparisonTab } from '../../components/MetaLabeling/BacktestComparisonTab';
import { LivePredictionsTab } from '../../components/MetaLabeling/LivePredictionsTab';

type TabType = 'train' | 'backtest' | 'live';

const TABS = [
  {
    id: 'train',
    name: 'Train Model',
    description: 'Train meta-labeling model on primary strategy signals',
    icon: '🎓',
  },
  {
    id: 'backtest',
    name: 'Backtest Comparison',
    description: 'Compare primary strategy vs meta-labeled version',
    icon: '📊',
  },
  {
    id: 'live',
    name: 'Live Predictions',
    description: 'Real-time meta-labeling predictions',
    icon: '⚡',
  },
];

export function MetaLabeling() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('train');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'train':
        return <TrainModelTab />;
      case 'backtest':
        return <BacktestComparisonTab />;
      case 'live':
        return <LivePredictionsTab />;
      default:
        return <TrainModelTab />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/ai-lab')}
            className="p-2 hover:bg-dark-border rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <Brain className="w-6 h-6 text-purple-400" />
              <h1 className="text-2xl font-bold text-white">Meta-Labeling</h1>
            </div>
            <p className="text-sm text-gray-400">
              Use ML to predict when your primary strategy will be profitable (bet sizing)
            </p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-2">
        <div className="grid grid-cols-3 gap-2">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              className={`p-4 rounded-lg text-left transition ${
                activeTab === tab.id
                  ? 'bg-purple-600 text-white'
                  : 'bg-dark-bg text-gray-400 hover:bg-dark-border hover:text-white'
              }`}
            >
              <div className="text-2xl mb-2">{tab.icon}</div>
              <div className="font-semibold text-sm mb-1">{tab.name}</div>
              <div className="text-xs opacity-75">{tab.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="min-h-[600px]">{renderTabContent()}</div>

      {/* Info Footer */}
      <div className="bg-purple-900/20 border border-purple-700 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="text-purple-400 text-2xl">💡</div>
          <div>
            <div className="font-semibold text-white mb-1">About Meta-Labeling</div>
            <div className="text-sm text-gray-300 space-y-1">
              <p>
                <strong>The Problem:</strong> Your primary strategy generates signals, but not all signals are
                equally profitable. Some will win, some will lose.
              </p>
              <p>
                <strong>The Solution:</strong> Train a secondary ML model (meta-labeler) to predict WHICH signals
                will be profitable. Use it for bet sizing or filtering bad trades.
              </p>
              <p>
                <strong>How it Works:</strong> The meta-model learns from features like volatility, volume,
                market regime, technical indicators to predict signal quality.
              </p>
              <p>
                <strong>Result:</strong> Higher Sharpe ratio, better win rate, reduced drawdowns by avoiding
                low-quality trades.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
