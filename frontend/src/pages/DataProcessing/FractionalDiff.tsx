/**
 * Fractional Differentiation Main Page
 * Transform non-stationary prices to stationary features while preserving memory
 */

import { useState } from 'react';
import { TrendingUp, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { TransformPanel } from '../../components/FractionalDiff/TransformPanel';
import { OptimalDFinder } from '../../components/FractionalDiff/OptimalDFinder';
import { ComparisonView } from '../../components/FractionalDiff/ComparisonView';
import { BatchProcessor } from '../../components/FractionalDiff/BatchProcessor';

type TabType = 'transform' | 'find-optimal-d' | 'compare-d-values' | 'batch-processing';

const TABS = [
  {
    id: 'transform',
    name: 'Transform Series',
    description: 'Apply fractional differentiation with custom d value',
    icon: '📊',
  },
  {
    id: 'find-optimal-d',
    name: 'Find Optimal d',
    description: 'Auto-discover the minimum d that achieves stationarity',
    icon: '🔍',
  },
  {
    id: 'compare-d-values',
    name: 'Compare d Values',
    description: 'Side-by-side comparison of multiple d values',
    icon: '⚖️',
  },
  {
    id: 'batch-processing',
    name: 'Batch Processing',
    description: 'Transform multiple tickers at once',
    icon: '⚡',
  },
];

export function FractionalDiff() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('transform');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'transform':
        return <TransformPanel />;
      case 'find-optimal-d':
        return <OptimalDFinder />;
      case 'compare-d-values':
        return <ComparisonView />;
      case 'batch-processing':
        return <BatchProcessor />;
      default:
        return <TransformPanel />;
    }
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
            <div className="flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-blue-400" />
              <h1 className="text-2xl font-bold text-white">Fractional Differentiation</h1>
            </div>
            <p className="text-sm text-gray-400">
              Transform non-stationary prices to stationary features while preserving memory
            </p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-2">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              className={`p-4 rounded-lg text-left transition ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
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
      <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="text-blue-400 text-2xl">💡</div>
          <div>
            <div className="font-semibold text-white mb-1">About Fractional Differentiation</div>
            <div className="text-sm text-gray-300 space-y-1">
              <p>
                <strong>The Problem:</strong> Financial time series (prices) are non-stationary, making them
                unsuitable for many ML models. Standard differencing (d=1) creates stationarity but destroys memory.
              </p>
              <p>
                <strong>The Solution:</strong> Fractional differentiation with 0 {'<'} d {'<'} 1 achieves stationarity
                while retaining memory. This gives you stationary features for ML without losing predictive information.
              </p>
              <p>
                <strong>Practical Use:</strong> Use d=0.4-0.6 for most financial time series. Test with the
                "Find Optimal d" tool to find the minimum d that achieves stationarity for your data.
              </p>
              <p>
                <strong>Method:</strong> FFD (Fixed-Window Fractional Differentiation) is memory-efficient and
                suitable for large datasets. Standard method uses full history but is more computationally expensive.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
