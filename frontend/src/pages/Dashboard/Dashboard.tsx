/**
 * Dashboard page - Main overview of trading platform
 */

import { useEffect } from 'react';
import { useDashboardStore } from '../../store/useDashboardStore';
import { PortfolioSummary } from './components/PortfolioSummary';
import { EquityCurveChart } from './components/EquityCurveChart';
import { DailyPnLChart } from './components/DailyPnLChart';
import { RecentSignalsTable } from './components/RecentSignalsTable';
import { ActivePositionsTable } from './components/ActivePositionsTable';
import { StrategyPerformance } from './components/StrategyPerformance';
import { RiskMetrics } from './components/RiskMetrics';

export function Dashboard() {
  const { data, isLoading, error, loadDashboard } = useDashboardStore();

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-900/20 border-red-700">
        <h3 className="text-red-400 font-semibold mb-2">Error Loading Dashboard</h3>
        <p className="text-gray-300">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="card">
        <p className="text-gray-400">No data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Portfolio Summary Cards */}
      <PortfolioSummary data={data.portfolio} />

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <EquityCurveChart data={data.equityCurve} />
        <DailyPnLChart data={data.dailyPnL} />
      </div>

      {/* Tables Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentSignalsTable signals={data.recentSignals} />
        <ActivePositionsTable positions={data.activePositions} />
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <StrategyPerformance strategies={data.strategies} />
        <RiskMetrics risk={data.risk} />
      </div>
    </div>
  );
}
