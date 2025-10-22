/**
 * Market Data Page
 * Real-time IBKR market data and FRED economic indicators
 */

import { useState, useEffect } from 'react';
import { RefreshCw, TrendingUp, DollarSign, Activity } from 'lucide-react';
import dataIngestionApi from '../../api/dataIngestionApi';
import type { IBKRTicker, FREDIndicator } from '../../api/dataIngestionApi';

export default function MarketData() {
  const [marketData, setMarketData] = useState<IBKRTicker[]>([]);
  const [economicIndicators, setEconomicIndicators] = useState<FREDIndicator[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [error, setError] = useState<string | null>(null);

  const fetchData = async (isRefresh: boolean = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError(null);

    try {
      const [market, indicators] = await Promise.all([
        dataIngestionApi.getIBKRMarketData(),
        dataIngestionApi.getFREDIndicators(),
      ]);

      setMarketData(market);
      setEconomicIndicators(indicators);
      setLastUpdate(new Date());
    } catch (err: any) {
      console.error('Failed to fetch market data:', err);
      setError(err.message || 'Failed to fetch market data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Auto-refresh every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetchData(true);
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  if (loading && marketData.length === 0) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mb-4"></div>
          <div className="text-white text-xl font-semibold mb-2">Loading Market Data</div>
          <div className="text-gray-400 text-sm">
            Fetching real-time IBKR tickers and FRED indicators...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-[1800px] mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
                <Activity className="w-8 h-8 text-green-400" />
                Live Market Data
              </h1>
              <p className="text-gray-400">
                Real-time IBKR market data & FRED economic indicators
              </p>
            </div>

            <div className="text-right">
              <div className="text-sm text-gray-400 mb-2">
                Last updated: {lastUpdate.toLocaleTimeString()}
              </div>
              <button
                onClick={() => fetchData(true)}
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
          </div>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* FRED Economic Indicators */}
          <div className="xl:col-span-1">
            <div className="bg-gray-800 border border-gray-700 rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-400" />
                FRED Economic Indicators
              </h2>

              {economicIndicators.length === 0 ? (
                <div className="text-gray-400 text-sm">No indicators available</div>
              ) : (
                <div className="space-y-3">
                  {economicIndicators
                    .sort((a, b) => a.series_id.localeCompare(b.series_id))
                    .map((indicator) => (
                      <div
                        key={indicator.series_id}
                        className="bg-gray-750 rounded-lg p-3 border border-gray-600"
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-mono text-blue-400">
                            {indicator.series_id}
                          </span>
                          <span className="text-xs text-gray-500">{indicator.units}</span>
                        </div>
                        <div className="text-lg font-bold text-white mb-1">
                          {indicator.value.toFixed(2)}
                        </div>
                        <div className="text-xs text-gray-400 truncate" title={indicator.title}>
                          {indicator.title}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          As of: {indicator.date}
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </div>
          </div>

          {/* IBKR Market Data */}
          <div className="xl:col-span-2">
            <div className="bg-gray-800 border border-gray-700 rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-green-400" />
                IBKR Live Market Data ({marketData.length} symbols)
              </h2>

              {marketData.length === 0 ? (
                <div className="text-gray-400 text-sm">No market data available</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-700">
                        <th className="text-left py-2 px-3 text-gray-400 font-semibold">Symbol</th>
                        <th className="text-right py-2 px-3 text-gray-400 font-semibold">Last</th>
                        <th className="text-right py-2 px-3 text-gray-400 font-semibold">Bid</th>
                        <th className="text-right py-2 px-3 text-gray-400 font-semibold">Ask</th>
                        <th className="text-right py-2 px-3 text-gray-400 font-semibold">Bid Size</th>
                        <th className="text-right py-2 px-3 text-gray-400 font-semibold">Ask Size</th>
                        <th className="text-right py-2 px-3 text-gray-400 font-semibold">Volume</th>
                      </tr>
                    </thead>
                    <tbody>
                      {marketData
                        .sort((a, b) => a.symbol.localeCompare(b.symbol))
                        .map((ticker) => (
                          <tr
                            key={ticker.symbol}
                            className="border-b border-gray-700/50 hover:bg-gray-750 transition-colors"
                          >
                            <td className="py-2 px-3 font-mono font-bold text-white">
                              {ticker.symbol}
                            </td>
                            <td className="py-2 px-3 text-right font-semibold text-green-400">
                              ${ticker.last.toFixed(2)}
                            </td>
                            <td className="py-2 px-3 text-right text-gray-300">
                              ${ticker.bid.toFixed(2)}
                            </td>
                            <td className="py-2 px-3 text-right text-gray-300">
                              ${ticker.ask.toFixed(2)}
                            </td>
                            <td className="py-2 px-3 text-right text-gray-400">
                              {ticker.bid_size?.toLocaleString() || '-'}
                            </td>
                            <td className="py-2 px-3 text-right text-gray-400">
                              {ticker.ask_size?.toLocaleString() || '-'}
                            </td>
                            <td className="py-2 px-3 text-right text-blue-400">
                              {ticker.volume?.toLocaleString() || '-'}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Info Footer */}
        <div className="mt-6 bg-gray-800 border border-gray-700 rounded-lg p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-400">
            <div>
              <strong className="text-gray-300">Data Source:</strong> IBKR Gateway (port 4002) + FRED
              API
            </div>
            <div>
              <strong className="text-gray-300">Storage:</strong> Valkey (cache) + QuestDB
              (time-series)
            </div>
            <div>
              <strong className="text-gray-300">Refresh:</strong> Auto-refresh every 10 seconds
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
