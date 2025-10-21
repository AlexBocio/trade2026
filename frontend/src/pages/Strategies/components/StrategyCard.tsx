/**
 * Strategy Card Component - Displays strategy summary in grid
 */

import { useNavigate } from 'react-router-dom';
import { Play, Pause, Edit, TrendingUp, Award, DollarSign, BarChart3 } from 'lucide-react';
import type { StrategyExtended } from '../../../services/mock-data/strategy-data';
import { formatCurrency, formatPercent, getColorClass } from '../../../utils/helpers';
import { useStrategyStore } from '../../../store/useStrategyStore';

interface StrategyCardProps {
  strategy: StrategyExtended;
}

export function StrategyCard({ strategy }: StrategyCardProps) {
  const navigate = useNavigate();
  const { deployStrategy, retireStrategy } = useStrategyStore();

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

  const handleDeploy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`Deploy "${strategy.name}" to live trading?`)) {
      await deployStrategy(strategy.id);
    }
  };

  const handleRetire = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`Stop "${strategy.name}"?`)) {
      await retireStrategy(strategy.id);
    }
  };

  return (
    <div
      onClick={() => navigate(`/strategies/${strategy.id}`)}
      className="card hover:border-blue-600 cursor-pointer transition-all group"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-white truncate group-hover:text-blue-400 transition-colors">
            {strategy.name}
          </h3>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-sm text-gray-400">v{strategy.version}</span>
            <span className="text-xs text-gray-500">• {strategy.category}</span>
          </div>
        </div>
        <span
          className={`px-2 py-1 text-xs font-semibold rounded border ${getStatusColor(
            strategy.status
          )}`}
        >
          {strategy.status}
        </span>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-400 mb-4 line-clamp-2">{strategy.description}</p>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="flex items-center gap-2">
          <Award size={14} className="text-blue-400" />
          <div>
            <div className="text-xs text-gray-500">Win Rate</div>
            <div className="text-sm font-semibold text-white">
              {strategy.performance.winRate.toFixed(1)}%
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <TrendingUp size={14} className="text-purple-400" />
          <div>
            <div className="text-xs text-gray-500">Sharpe</div>
            <div className="text-sm font-semibold text-white">
              {strategy.performance.sharpeRatio.toFixed(2)}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <DollarSign size={14} className={getColorClass(strategy.performance.totalPnL)} />
          <div>
            <div className="text-xs text-gray-500">P&L</div>
            <div className={`text-sm font-semibold ${getColorClass(strategy.performance.totalPnL)}`}>
              {formatCurrency(strategy.performance.totalPnL)}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <BarChart3 size={14} className="text-yellow-400" />
          <div>
            <div className="text-xs text-gray-500">Trades</div>
            <div className="text-sm font-semibold text-white">{strategy.performance.totalTrades}</div>
          </div>
        </div>
      </div>

      {/* Footer - Action Buttons */}
      <div className="flex items-center gap-2 pt-4 border-t border-gray-700">
        <button
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/strategies/${strategy.id}`);
          }}
          className="flex-1 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded transition-colors"
        >
          View
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/strategies/${strategy.id}/edit`);
          }}
          className="p-1.5 bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors"
          title="Edit"
        >
          <Edit size={16} />
        </button>
        {strategy.status !== 'LIVE' ? (
          <button
            onClick={handleDeploy}
            className="p-1.5 bg-green-700 hover:bg-green-600 text-white rounded transition-colors"
            title="Deploy"
          >
            <Play size={16} />
          </button>
        ) : (
          <button
            onClick={handleRetire}
            className="p-1.5 bg-red-700 hover:bg-red-600 text-white rounded transition-colors"
            title="Stop"
          >
            <Pause size={16} />
          </button>
        )}
      </div>
    </div>
  );
}
