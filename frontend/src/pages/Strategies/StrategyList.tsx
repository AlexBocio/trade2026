/**
 * Strategy List (Level 1) - Grid of all strategies with filters
 */

import { useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search } from 'lucide-react';
import { useStrategyStore } from '../../store/useStrategyStore';
import { StrategyCard } from './components/StrategyCard';

export function StrategyList() {
  const navigate = useNavigate();
  const {
    strategies,
    loadingStrategies,
    statusFilter,
    searchQuery,
    fetchStrategies,
    setStatusFilter,
    setSearchQuery,
  } = useStrategyStore();

  useEffect(() => {
    fetchStrategies();
  }, [fetchStrategies]);

  // Filter strategies
  const filteredStrategies = useMemo(() => {
    return strategies.filter((strategy) => {
      // Status filter
      if (statusFilter !== 'all' && strategy.status !== statusFilter.toUpperCase()) {
        return false;
      }

      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          strategy.name.toLowerCase().includes(query) ||
          strategy.description.toLowerCase().includes(query) ||
          strategy.category?.toLowerCase().includes(query)
        );
      }

      return true;
    });
  }, [strategies, statusFilter, searchQuery]);

  if (loadingStrategies) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-400">Loading strategies...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Strategies</h1>
          <p className="text-gray-400 mt-1">
            Manage your trading strategies ({filteredStrategies.length} total)
          </p>
        </div>
        <button
          onClick={() => navigate('/strategies/new')}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          Create New Strategy
        </button>
      </div>

      {/* Filters Bar */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search strategies..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field pl-10 w-full"
            />
          </div>

          {/* Status Filter */}
          <div className="flex gap-2">
            {['all', 'live', 'paper', 'stopped'].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                  statusFilter === status
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Strategy Grid */}
      {filteredStrategies.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-400 mb-4">No strategies found</p>
          <button onClick={() => navigate('/strategies/new')} className="btn-primary">
            Create Your First Strategy
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredStrategies.map((strategy) => (
            <StrategyCard key={strategy.id} strategy={strategy} />
          ))}
        </div>
      )}
    </div>
  );
}
