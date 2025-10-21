/**
 * Backtest List - View and manage all backtests
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, TrendingUp, TrendingDown, Clock, CheckCircle, XCircle, Activity, Zap, Beaker } from 'lucide-react';
import { mockBacktests } from '../../services/mock-data/backtest-data';
import type { Backtest } from '../../types/strategy.types';

export function BacktestList() {
  const navigate = useNavigate();
  const [backtests, setBacktests] = useState<Backtest[]>([]);
  const [filter, setFilter] = useState<'all' | 'COMPLETED' | 'RUNNING' | 'FAILED'>('all');

  useEffect(() => {
    // Load backtests from mock data
    setBacktests(mockBacktests);
  }, []);

  const filteredBacktests = backtests.filter((bt) => {
    if (filter === 'all') return true;
    return bt.status === filter;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'RUNNING':
        return <Activity className="w-5 h-5 text-blue-400 animate-pulse" />;
      case 'FAILED':
        return <XCircle className="w-5 h-5 text-red-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-green-900/30 text-green-400 border-green-700';
      case 'RUNNING':
        return 'bg-blue-900/30 text-blue-400 border-blue-700';
      case 'FAILED':
        return 'bg-red-900/30 text-red-400 border-red-700';
      default:
        return 'bg-gray-900/30 text-gray-400 border-gray-700';
    }
  };

  const calculateReturn = (bt: Backtest) => {
    if (!bt.finalCapital || !bt.initialCapital) return 0;
    return ((bt.finalCapital - bt.initialCapital) / bt.initialCapital) * 100;
  };

  const stats = {
    total: backtests.length,
    completed: backtests.filter((bt) => bt.status === 'COMPLETED').length,
    running: backtests.filter((bt) => bt.status === 'RUNNING').length,
    failed: backtests.filter((bt) => bt.status === 'FAILED').length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Backtests</h1>
          <p className="text-sm text-gray-400">View and analyze historical strategy performance</p>
        </div>
        <button
          onClick={() => navigate('/strategies')}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition"
        >
          <Play className="w-5 h-5" />
          Run New Backtest
        </button>
      </div>

      {/* Quick Access Cards */}
      <div className="grid grid-cols-2 gap-6">
        <div
          onClick={() => navigate('/backtesting/advanced')}
          className="bg-dark-card border border-dark-border rounded-lg p-6 hover:border-green-400 cursor-pointer transition group"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center group-hover:scale-110 transition">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-white mb-1">Advanced Backtest</h3>
              <p className="text-sm text-gray-400">Walk-forward, Monte Carlo, portfolio-level testing</p>
            </div>
            <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-semibold transition">
              Launch
            </button>
          </div>
        </div>

        <div
          onClick={() => navigate('/backtesting/simulations')}
          className="bg-dark-card border border-dark-border rounded-lg p-6 hover:border-blue-400 cursor-pointer transition group"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-400 to-cyan-500 flex items-center justify-center group-hover:scale-110 transition">
              <Beaker className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-white mb-1">Simulation Engine</h3>
              <p className="text-sm text-gray-400">Bootstrap, GARCH, scenario analysis, synthetic data</p>
            </div>
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-semibold transition">
              Launch
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Total Backtests</div>
          <div className="text-3xl font-bold text-white">{stats.total}</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-1">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <span className="text-sm text-gray-400">Completed</span>
          </div>
          <div className="text-3xl font-bold text-green-400">{stats.completed}</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-1">
            <Activity className="w-5 h-5 text-blue-400" />
            <span className="text-sm text-gray-400">Running</span>
          </div>
          <div className="text-3xl font-bold text-blue-400">{stats.running}</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-1">
            <XCircle className="w-5 h-5 text-red-400" />
            <span className="text-sm text-gray-400">Failed</span>
          </div>
          <div className="text-3xl font-bold text-red-400">{stats.failed}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 bg-dark-card border border-dark-border rounded-lg p-2">
        {(['all', 'COMPLETED', 'RUNNING', 'FAILED'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`flex-1 px-3 py-2 rounded font-medium text-sm capitalize transition ${
              filter === f
                ? 'bg-green-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-dark-border'
            }`}
          >
            {f === 'all' ? 'All' : f.toLowerCase()}
          </button>
        ))}
      </div>

      {/* Backtests List */}
      <div className="space-y-4">
        {filteredBacktests.length === 0 ? (
          <div className="bg-dark-card border border-dark-border rounded-lg p-12 text-center">
            <Activity className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">No backtests found</h3>
            <p className="text-gray-500 mb-6">Try adjusting your filters or run a new backtest</p>
            <button
              onClick={() => navigate('/strategies')}
              className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition"
            >
              Run New Backtest
            </button>
          </div>
        ) : (
          filteredBacktests.map((bt) => {
            const returnPct = calculateReturn(bt);
            const isPositive = returnPct >= 0;

            return (
              <div
                key={bt.id}
                className="bg-dark-card border border-dark-border rounded-lg p-6 hover:border-dark-border-hover transition cursor-pointer"
                onClick={() => {
                  if (bt.status === 'COMPLETED') {
                    navigate(`/backtesting/report/${bt.id}`);
                  }
                }}
              >
                <div className="flex items-start justify-between">
                  {/* Left Section */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-bold text-white">{bt.strategyName}</h3>
                      <div className={`flex items-center gap-1 px-2 py-1 rounded border text-xs ${getStatusColor(bt.status)}`}>
                        {getStatusIcon(bt.status)}
                        <span className="capitalize">{bt.status.toLowerCase()}</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Period:</span>
                        <div className="text-white font-semibold">
                          {bt.startDate.toLocaleDateString()} - {bt.endDate.toLocaleDateString()}
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-400">Initial Capital:</span>
                        <div className="text-white font-semibold">${bt.initialCapital.toLocaleString()}</div>
                      </div>
                      <div>
                        <span className="text-gray-400">Final Capital:</span>
                        <div className={`font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                          ${bt.finalCapital.toLocaleString()}
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-400">Return:</span>
                        <div className={`flex items-center gap-1 font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                          {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                          {isPositive ? '+' : ''}{returnPct.toFixed(2)}%
                        </div>
                      </div>
                    </div>

                    {/* Parameters */}
                    <div className="flex gap-2 mt-3">
                      <span className="px-2 py-1 bg-dark-bg rounded text-xs text-gray-400">
                        Timeframe: {bt.parameters.timeframe}
                      </span>
                      <span className="px-2 py-1 bg-dark-bg rounded text-xs text-gray-400">
                        Lookback: {bt.parameters.lookbackPeriod}
                      </span>
                      <span className="px-2 py-1 bg-dark-bg rounded text-xs text-gray-400">
                        Risk: {bt.parameters.riskPerTrade}%
                      </span>
                      <span className="px-2 py-1 bg-dark-bg rounded text-xs text-gray-400">
                        Max Positions: {bt.parameters.maxPositions}
                      </span>
                    </div>
                  </div>

                  {/* Right Section - Actions */}
                  <div className="flex flex-col gap-2 ml-6">
                    {bt.status === 'COMPLETED' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/backtesting/report/${bt.id}`);
                        }}
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-semibold transition whitespace-nowrap"
                      >
                        View Report
                      </button>
                    )}
                    {bt.status === 'RUNNING' && (
                      <button
                        disabled
                        className="px-4 py-2 bg-blue-900/30 text-blue-400 rounded-lg text-sm font-semibold cursor-not-allowed"
                      >
                        Running...
                      </button>
                    )}
                    {bt.status === 'FAILED' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          // Retry logic would go here
                        }}
                        className="px-4 py-2 bg-dark-border hover:bg-dark-border-hover rounded-lg text-sm font-semibold transition"
                      >
                        Retry
                      </button>
                    )}
                    <div className="text-xs text-gray-500 text-right">
                      Started: {bt.createdAt.toLocaleString()}
                    </div>
                    {bt.completedAt && (
                      <div className="text-xs text-gray-500 text-right">
                        Completed: {bt.completedAt.toLocaleString()}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
