/**
 * Strategy Detail (Level 2) - Main detail page with tabs
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit, Play, Pause, Trash2 } from 'lucide-react';
import { useStrategyStore } from '../../store/useStrategyStore';
import { OverviewTab } from './tabs/OverviewTab';
import { PerformanceTab } from './tabs/PerformanceTab';
import { TradesTab } from './tabs/TradesTab';
import { ConfigurationTab } from './tabs/ConfigurationTab';

type TabType = 'overview' | 'performance' | 'trades' | 'configuration';

export function StrategyDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const {
    selectedStrategy,
    loadingStrategy,
    fetchStrategy,
    deployStrategy,
    retireStrategy,
    deleteStrategy,
  } = useStrategyStore();

  useEffect(() => {
    if (id) {
      fetchStrategy(id);
    }
  }, [id, fetchStrategy]);

  const handleDeploy = async () => {
    if (selectedStrategy && confirm(`Deploy "${selectedStrategy.name}" to live trading?`)) {
      await deployStrategy(selectedStrategy.id);
      fetchStrategy(selectedStrategy.id);
    }
  };

  const handleRetire = async () => {
    if (selectedStrategy && confirm(`Stop "${selectedStrategy.name}"?`)) {
      await retireStrategy(selectedStrategy.id);
      fetchStrategy(selectedStrategy.id);
    }
  };

  const handleDelete = async () => {
    if (
      selectedStrategy &&
      confirm(`Delete "${selectedStrategy.name}"? This action cannot be undone.`)
    ) {
      await deleteStrategy(selectedStrategy.id);
      navigate('/strategies');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'LIVE':
        return 'bg-green-900/30 text-green-400 border-green-700';
      case 'PAPER':
        return 'bg-yellow-900/30 text-yellow-400 border-yellow-700';
      case 'STOPPED':
        return 'bg-gray-900/30 text-gray-400 border-gray-700';
      case 'ERROR':
        return 'bg-red-900/30 text-red-400 border-red-700';
      default:
        return 'bg-blue-900/30 text-blue-400 border-blue-700';
    }
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

  const tabs: { id: TabType; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'performance', label: 'Performance' },
    { id: 'trades', label: 'Trades' },
    { id: 'configuration', label: 'Configuration' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <button
            onClick={() => navigate('/strategies')}
            className="flex items-center gap-2 text-gray-400 hover:text-white mb-3 transition-colors"
          >
            <ArrowLeft size={18} />
            Back to Strategies
          </button>
          <div className="flex items-center gap-4">
            <h1 className="text-3xl font-bold text-white">{selectedStrategy.name}</h1>
            <span
              className={`px-3 py-1 text-sm font-semibold rounded border ${getStatusColor(
                selectedStrategy.status
              )}`}
            >
              {selectedStrategy.status}
            </span>
          </div>
          <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
            <span>v{selectedStrategy.version}</span>
            <span>•</span>
            <span>{selectedStrategy.category}</span>
            <span>•</span>
            <span>by {selectedStrategy.author}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate(`/strategies/${selectedStrategy.id}/edit`)}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded flex items-center gap-2 transition-colors"
          >
            <Edit size={18} />
            Edit
          </button>
          {selectedStrategy.status !== 'LIVE' ? (
            <button
              onClick={handleDeploy}
              className="px-4 py-2 bg-green-700 hover:bg-green-600 text-white rounded flex items-center gap-2 transition-colors"
            >
              <Play size={18} />
              Deploy
            </button>
          ) : (
            <button
              onClick={handleRetire}
              className="px-4 py-2 bg-red-700 hover:bg-red-600 text-white rounded flex items-center gap-2 transition-colors"
            >
              <Pause size={18} />
              Stop
            </button>
          )}
          <button
            onClick={handleDelete}
            className="px-4 py-2 bg-red-900 hover:bg-red-800 text-white rounded flex items-center gap-2 transition-colors"
          >
            <Trash2 size={18} />
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-700">
        <div className="flex gap-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-3 px-1 font-medium transition-colors relative ${
                activeTab === tab.id
                  ? 'text-blue-400'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              {tab.label}
              {activeTab === tab.id && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500"></div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'overview' && <OverviewTab strategy={selectedStrategy} />}
        {activeTab === 'performance' && <PerformanceTab strategy={selectedStrategy} />}
        {activeTab === 'trades' && <TradesTab strategy={selectedStrategy} />}
        {activeTab === 'configuration' && <ConfigurationTab strategy={selectedStrategy} />}
      </div>
    </div>
  );
}
