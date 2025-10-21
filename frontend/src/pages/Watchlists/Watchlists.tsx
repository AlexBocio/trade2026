/**
 * Watchlists - Main watchlists page
 */

import { useEffect } from 'react';
import { List, Plus, TrendingUp, TrendingDown, Trash2, Edit, Star } from 'lucide-react';
import { useWatchlistsStore } from '../../store/useWatchlistsStore';

export function Watchlists() {
  const {
    watchlists,
    selectedWatchlist,
    stats,
    isLoading,
    loadWatchlists,
    selectWatchlist,
    deleteWatchlist,
    removeStock,
  } = useWatchlistsStore();

  useEffect(() => {
    loadWatchlists();
  }, [loadWatchlists]);

  const currentWatchlist = watchlists.find((w) => w.id === selectedWatchlist);

  const formatMarketCap = (marketCap: number) => {
    if (marketCap >= 1e9) {
      return `$${(marketCap / 1e9).toFixed(2)}B`;
    }
    return `$${(marketCap / 1e6).toFixed(0)}M`;
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1e6) {
      return `${(volume / 1e6).toFixed(2)}M`;
    }
    return `${(volume / 1e3).toFixed(0)}K`;
  };

  const handleDeleteWatchlist = async (id: string) => {
    const watchlist = watchlists.find((w) => w.id === id);
    if (!watchlist) return;

    if (confirm(`Delete watchlist "${watchlist.name}"?`)) {
      await deleteWatchlist(id);
    }
  };

  const handleRemoveStock = async (symbol: string) => {
    if (!currentWatchlist) return;

    if (confirm(`Remove ${symbol} from watchlist?`)) {
      await removeStock(currentWatchlist.id, symbol);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading watchlists...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <List className="w-8 h-8 text-green-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">Watchlists</h1>
            <p className="text-sm text-gray-400">
              Track stocks and build opportunity pipeline • {stats.totalStocks} stocks tracked
            </p>
          </div>
        </div>

        <button className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition">
          <Plus className="w-5 h-5" />
          New Watchlist
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-5 gap-4">
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-3xl font-bold text-white mb-1">{stats.totalWatchlists}</div>
          <div className="text-sm text-gray-400">Watchlists</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-3xl font-bold text-white mb-1">{stats.totalStocks}</div>
          <div className="text-sm text-gray-400">Total Stocks</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className={`text-3xl font-bold mb-1 ${stats.avgGain >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {stats.avgGain >= 0 ? '+' : ''}
            {stats.avgGain}%
          </div>
          <div className="text-sm text-gray-400">Avg Change</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-5 h-5 text-green-400" />
            <span className="text-2xl font-bold text-green-400">
              {stats.topGainer.symbol} +{stats.topGainer.changePct}%
            </span>
          </div>
          <div className="text-sm text-gray-400">Top Gainer</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <TrendingDown className="w-5 h-5 text-red-400" />
            <span className="text-2xl font-bold text-red-400">
              {stats.topLoser.symbol} {stats.topLoser.changePct}%
            </span>
          </div>
          <div className="text-sm text-gray-400">Top Loser</div>
        </div>
      </div>

      {/* Watchlist Tabs */}
      <div className="flex gap-2 bg-dark-card border border-dark-border rounded-lg p-2 overflow-x-auto">
        {watchlists.map((watchlist) => (
          <button
            key={watchlist.id}
            onClick={() => selectWatchlist(watchlist.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded font-medium text-sm whitespace-nowrap transition ${
              selectedWatchlist === watchlist.id
                ? 'bg-green-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-dark-border'
            }`}
          >
            {watchlist.isDefault && <Star className="w-4 h-4 fill-current" />}
            <span>{watchlist.name}</span>
            <span className="text-xs opacity-70">({watchlist.stocks.length})</span>
          </button>
        ))}
      </div>

      {/* Watchlist Content */}
      {currentWatchlist ? (
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          {/* Watchlist Header */}
          <div className="flex items-start justify-between mb-6">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl font-bold text-white">{currentWatchlist.name}</h2>
                {currentWatchlist.isDefault && (
                  <span className="px-2 py-1 bg-blue-900/30 text-blue-400 rounded text-xs font-medium">
                    Default
                  </span>
                )}
              </div>
              <p className="text-gray-400">{currentWatchlist.description}</p>
            </div>

            <div className="flex gap-2">
              <button className="px-3 py-2 bg-dark-border hover:bg-dark-border-hover rounded transition">
                <Edit className="w-4 h-4" />
              </button>
              {!currentWatchlist.isDefault && (
                <button
                  onClick={() => handleDeleteWatchlist(currentWatchlist.id)}
                  className="px-3 py-2 bg-red-900/30 hover:bg-red-900/50 text-red-400 rounded transition"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {/* Stocks Table */}
          {currentWatchlist.stocks.length === 0 ? (
            <div className="text-center py-12">
              <List className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-400 mb-2">No stocks in this watchlist</h3>
              <p className="text-gray-500 mb-6">Add stocks to start tracking</p>
              <button className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition">
                Add Stock
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-sm text-gray-400 border-b border-dark-border">
                    <th className="pb-3 font-medium">Symbol</th>
                    <th className="pb-3 font-medium">Name</th>
                    <th className="pb-3 font-medium text-right">Price</th>
                    <th className="pb-3 font-medium text-right">Change</th>
                    <th className="pb-3 font-medium text-right">Volume</th>
                    <th className="pb-3 font-medium text-right">Market Cap</th>
                    <th className="pb-3 font-medium">Sector</th>
                    <th className="pb-3 font-medium">Notes</th>
                    <th className="pb-3 font-medium"></th>
                  </tr>
                </thead>
                <tbody>
                  {currentWatchlist.stocks.map((stock) => (
                    <tr
                      key={stock.symbol}
                      className="border-b border-dark-border hover:bg-dark-bg transition"
                    >
                      <td className="py-4">
                        <div className="font-bold text-white">{stock.symbol}</div>
                      </td>
                      <td className="py-4 text-gray-300">{stock.name}</td>
                      <td className="py-4 text-right font-semibold text-white">
                        ${stock.price.toFixed(2)}
                      </td>
                      <td className="py-4 text-right">
                        <div
                          className={`flex items-center justify-end gap-1 ${
                            stock.changePct >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}
                        >
                          {stock.changePct >= 0 ? (
                            <TrendingUp className="w-4 h-4" />
                          ) : (
                            <TrendingDown className="w-4 h-4" />
                          )}
                          <span className="font-semibold">
                            {stock.changePct >= 0 ? '+' : ''}
                            {stock.changePct}%
                          </span>
                        </div>
                        <div className="text-sm text-gray-400">
                          {stock.change >= 0 ? '+' : ''}
                          {stock.change.toFixed(2)}
                        </div>
                      </td>
                      <td className="py-4 text-right text-gray-300">{formatVolume(stock.volume)}</td>
                      <td className="py-4 text-right text-gray-300">{formatMarketCap(stock.marketCap)}</td>
                      <td className="py-4">
                        <span className="px-2 py-1 bg-dark-bg rounded text-xs text-gray-300">
                          {stock.sector}
                        </span>
                      </td>
                      <td className="py-4 text-sm text-gray-400 max-w-xs truncate">
                        {stock.notes || '-'}
                      </td>
                      <td className="py-4">
                        <button
                          onClick={() => handleRemoveStock(stock.symbol)}
                          className="p-2 hover:bg-red-900/30 text-red-400 rounded transition"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-dark-card border border-dark-border rounded-lg p-12 text-center">
          <List className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-400 mb-2">No watchlist selected</h3>
          <p className="text-gray-500 mb-6">Create a watchlist to get started</p>
          <button className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition">
            Create Watchlist
          </button>
        </div>
      )}
    </div>
  );
}
