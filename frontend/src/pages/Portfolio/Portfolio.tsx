/**
 * Portfolio page - Track holdings, performance, and allocation
 */

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Target, Activity } from 'lucide-react';
import { usePortfolioStore } from '../../store/usePortfolioStore';
import { PortfolioSummaryCards } from '../../components/portfolio/PortfolioSummaryCards';
import { PortfolioEquityCurve } from '../../components/portfolio/PortfolioEquityCurve';
import { PnLByDayChart } from '../../components/portfolio/PnLByDayChart';
import { OpenPositionsTable } from '../../components/portfolio/OpenPositionsTable';
import { AssetAllocationChart } from '../../components/portfolio/AssetAllocationChart';
import { SectorExposureChart } from '../../components/portfolio/SectorExposureChart';
import { TopWinnersLosers } from '../../components/portfolio/TopWinnersLosers';

export function Portfolio() {
  const navigate = useNavigate();
  const { data, isLoading, error, loadPortfolio } = usePortfolioStore();

  useEffect(() => {
    loadPortfolio();
  }, [loadPortfolio]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-400">Loading portfolio...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-900/20 border-red-700">
        <h3 className="text-red-400 font-semibold mb-2">Error Loading Portfolio</h3>
        <p className="text-gray-300">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="card">
        <p className="text-gray-400">No portfolio data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Portfolio</h1>
        <p className="text-gray-400 mt-1">Track your holdings, performance, and allocation</p>
      </div>

      {/* Quick Access Cards */}
      <div className="grid grid-cols-2 gap-6">
        <div
          onClick={() => navigate('/portfolio/optimizer')}
          className="bg-dark-card border border-dark-border rounded-lg p-6 hover:border-green-400 cursor-pointer transition group"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center group-hover:scale-110 transition">
              <Target className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-white mb-1">Portfolio Optimizer</h3>
              <p className="text-sm text-gray-400">Mean-variance, risk parity, Black-Litterman, HRP</p>
            </div>
            <button className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-semibold transition">
              Launch
            </button>
          </div>
        </div>

        <div
          onClick={() => navigate('/portfolio/covariance-analysis')}
          className="bg-dark-card border border-dark-border rounded-lg p-6 hover:border-blue-400 cursor-pointer transition group"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-400 to-cyan-500 flex items-center justify-center group-hover:scale-110 transition">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-white mb-1">Covariance Cleaning</h3>
              <p className="text-sm text-gray-400">RMT denoising, detoning, detrending for stable matrices</p>
            </div>
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-semibold transition">
              Launch
            </button>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <PortfolioSummaryCards summary={data.summary} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Column (60%) */}
        <div className="col-span-2 space-y-6">
          <PortfolioEquityCurve data={data.equityCurve} />
          <PnLByDayChart data={data.pnlByDay} />
          <OpenPositionsTable positions={data.positions} />
        </div>

        {/* Right Column (40%) */}
        <div className="space-y-6">
          <AssetAllocationChart data={data.allocation} />
          <SectorExposureChart data={data.sectorExposure} />
          <TopWinnersLosers winners={data.topWinners} losers={data.topLosers} />
        </div>
      </div>
    </div>
  );
}
