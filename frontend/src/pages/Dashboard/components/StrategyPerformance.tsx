/**
 * Strategy Performance - Shows top 3 active strategies
 */

import { useNavigate } from 'react-router-dom';
import { Activity, TrendingUp } from 'lucide-react';
import { formatCurrency, formatPercent, getColorClass } from '../../../utils/helpers';

interface Strategy {
  id: string;
  name: string;
  status: 'live' | 'paper';
  trades: number;
  winRate: number;
  pnl: number;
  pnlPct: number;
}

interface StrategyPerformanceProps {
  strategies: Strategy[];
}

export function StrategyPerformance({ strategies }: StrategyPerformanceProps) {
  const navigate = useNavigate();

  const handleStrategyClick = (id: string) => {
    navigate(`/strategies/${id}`);
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Top Strategies</h3>
        <button
          onClick={() => navigate('/strategies')}
          className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
        >
          View All →
        </button>
      </div>
      <div className="space-y-3">
        {strategies.map((strategy) => (
          <div
            key={strategy.id}
            onClick={() => handleStrategyClick(strategy.id)}
            className="p-4 bg-gray-800/50 rounded-lg border border-gray-700 hover:border-gray-600 cursor-pointer transition-all"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-white">{strategy.name}</h4>
                  <span
                    className={`px-2 py-0.5 text-xs rounded ${
                      strategy.status === 'live'
                        ? 'bg-green-900/30 text-green-400'
                        : 'bg-yellow-900/30 text-yellow-400'
                    }`}
                  >
                    {strategy.status.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mt-1">
                  {strategy.trades} trades • {strategy.winRate.toFixed(1)}% win rate
                </p>
              </div>
              <div className="text-right">
                <p className={`text-lg font-bold ${getColorClass(strategy.pnl)}`}>
                  {formatCurrency(strategy.pnl)}
                </p>
                <p className={`text-sm ${getColorClass(strategy.pnl)}`}>
                  {formatPercent(strategy.pnlPct)}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <div className="flex items-center gap-1">
                <Activity size={12} />
                <span>{strategy.trades} trades</span>
              </div>
              <div className="flex items-center gap-1">
                <TrendingUp size={12} />
                <span>{strategy.winRate.toFixed(0)}% win rate</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
