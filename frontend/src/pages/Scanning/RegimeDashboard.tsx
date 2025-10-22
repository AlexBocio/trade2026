/**
 * Regime Dashboard Page
 * Multi-layer regime visualization dashboard with auto-refresh
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, ArrowLeft, TrendingUp } from 'lucide-react';
import { regimeApi } from '../../api/regimeApi';
import dataIngestionApi from '../../api/dataIngestionApi';
import type { FREDIndicator } from '../../api/dataIngestionApi';
import TemporalContextCard from '../../components/Regime/TemporalContextCard';
import MacroRegimeCard from '../../components/Regime/MacroRegimeCard';
import CrossAssetMatrix from '../../components/Regime/CrossAssetMatrix';
import MarketRegimesCard from '../../components/Regime/MarketRegimesCard';
import SectorHeatmap from '../../components/Regime/SectorHeatmap';
import IndustryHeatmap from '../../components/Regime/IndustryHeatmap';
import type {
  TemporalContext,
  MacroRegime,
  MarketRegimes,
  SectorRegimeData,
  IndustryRegimeData,
} from '../../types/regime';

function LoadingScreen() {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mb-4"></div>
        <div className="text-white text-xl font-semibold mb-2">Loading Regime Data</div>
        <div className="text-gray-400 text-sm">
          Analyzing markets across multiple regime layers...
        </div>
      </div>
    </div>
  );
}

export default function RegimeDashboard() {
  const navigate = useNavigate();
  const [temporalContext, setTemporalContext] = useState<TemporalContext | null>(null);
  const [macroRegime, setMacroRegime] = useState<MacroRegime | null>(null);
  const [marketRegimes, setMarketRegimes] = useState<MarketRegimes | null>(null);
  const [sectorRegimes, setSectorRegimes] = useState<SectorRegimeData | null>(null);
  const [industryRegimes, setIndustryRegimes] = useState<IndustryRegimeData | null>(null);
  const [fredIndicators, setFredIndicators] = useState<FREDIndicator[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [error, setError] = useState<string | null>(null);

  // Fetch all regime data
  const fetchAllData = async (isRefresh: boolean = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError(null);

    try {
      // Fetch all data in parallel
      const [temporal, macro, sectors, industries, fredData] = await Promise.all([
        regimeApi.getTemporalContext(),
        regimeApi.getMacroRegime(),
        regimeApi.getSectorRegimes(),
        regimeApi.getIndustryRegimes(30),
        dataIngestionApi.getFREDIndicators(),
      ]);

      // Also fetch market regimes
      const marketSymbols = ['SPY', 'QQQ', 'IWM', 'DIA'];
      const marketData = await regimeApi.batchDetect(marketSymbols);

      setTemporalContext(temporal);
      setMacroRegime(macro);
      setMarketRegimes(marketData);
      setSectorRegimes(sectors);
      setIndustryRegimes(industries);
      setFredIndicators(fredData);
      setLastUpdate(new Date());
    } catch (err: any) {
      console.error('Failed to fetch regime data:', err);
      setError(err.message || 'Failed to fetch regime data. Make sure backend is running on port 5008.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchAllData();
  }, []);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchAllData(true);
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, []);

  // Show loading screen on initial load
  if (loading && !temporalContext) {
    return <LoadingScreen />;
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-[1800px] mx-auto">
        {/* Header */}
        <div className="mb-6">
          {/* Back Button */}
          <button
            onClick={() => navigate('/scanner')}
            className="mb-4 flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Scanner</span>
          </button>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                🌍 Global Regime Command Center
              </h1>
              <p className="text-gray-400">
                Multi-layer regime detection across all markets
              </p>
            </div>

            <div className="text-right">
              <div className="text-sm text-gray-400 mb-2">
                Last updated: {lastUpdate.toLocaleTimeString()}
              </div>
              <button
                onClick={() => fetchAllData(true)}
                disabled={refreshing}
                className={`bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm flex items-center gap-2 transition-colors ${
                  refreshing ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                {refreshing ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-6 bg-red-900/30 border border-red-700 rounded-lg p-4">
            <div className="flex items-center gap-2 text-red-400 font-semibold mb-2">
              ⚠️ Error Loading Data
            </div>
            <p className="text-sm text-red-300">{error}</p>
            <p className="text-sm text-red-400 mt-2">
              Make sure the regime backend is running:{' '}
              <code className="bg-red-950 px-2 py-1 rounded">
                python backend/regime_service/app.py
              </code>
            </p>
          </div>
        )}

        {/* Dashboard Grid */}
        <div className="space-y-6">
          {/* Row 1: Temporal + Macro */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TemporalContextCard data={temporalContext} />
            <MacroRegimeCard data={macroRegime} />
          </div>

          {/* FRED Economic Indicators - Real-Time */}
          {fredIndicators.length > 0 && (
            <div className="bg-gray-800 border border-gray-700 rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-400" />
                FRED Economic Indicators (Live)
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {fredIndicators
                  .sort((a, b) => a.series_id.localeCompare(b.series_id))
                  .map((indicator) => (
                    <div
                      key={indicator.series_id}
                      className="bg-gray-750 rounded-lg p-4 border border-gray-600"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-mono text-blue-400">
                          {indicator.series_id}
                        </span>
                        <span className="text-xs text-gray-500">{indicator.units}</span>
                      </div>
                      <div className="text-2xl font-bold text-white mb-2">
                        {indicator.value.toFixed(2)}
                      </div>
                      <div className="text-xs text-gray-400 truncate" title={indicator.title}>
                        {indicator.title}
                      </div>
                      <div className="text-xs text-gray-500 mt-2">
                        As of: {indicator.date}
                      </div>
                    </div>
                  ))}
              </div>
              <div className="mt-4 text-xs text-gray-400">
                <strong className="text-gray-300">Data Source:</strong> Federal Reserve Economic Data (FRED) via data-ingestion service
              </div>
            </div>
          )}

          {/* Row 2: Cross-Asset Matrix */}
          <CrossAssetMatrix equities={marketRegimes} />

          {/* Row 3: Market Regimes */}
          <MarketRegimesCard data={marketRegimes} />

          {/* Row 4: Sector Heatmap */}
          <SectorHeatmap data={sectorRegimes} />

          {/* Row 5: Industry Heatmap (Top 30) */}
          <IndustryHeatmap data={industryRegimes} />

          {/* Info Footer */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h3 className="text-white font-semibold mb-3">💡 Dashboard Features</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-400">
              <div>
                <strong className="text-gray-300">Auto-Refresh:</strong> Data refreshes every 5
                minutes automatically
              </div>
              <div>
                <strong className="text-gray-300">Real-Time Regimes:</strong> All regime
                detections based on latest market data
              </div>
              <div>
                <strong className="text-gray-300">Multi-Layer Analysis:</strong> Temporal, macro,
                market, sector, and industry coverage
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
