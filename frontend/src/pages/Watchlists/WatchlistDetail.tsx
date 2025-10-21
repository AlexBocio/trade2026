/**
 * Watchlist Detail - Detailed view of a single watchlist
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Plus,
  Edit,
  TrendingUp,
  TrendingDown,
  Bell,
  Download,
  Trash2,
} from 'lucide-react';
import { useWatchlistsStore } from '../../store/useWatchlistsStore';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

export function WatchlistDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {
    watchlists,
    addStock,
    removeStock,
  } = useWatchlistsStore();

  const [showAddSymbol, setShowAddSymbol] = useState(false);
  const [newSymbol, setNewSymbol] = useState('');

  const watchlist = watchlists.find((w) => w.id === id);

  const handleAddSymbol = async () => {
    if (!newSymbol || !id) return;
    await addStock(id, newSymbol.toUpperCase());
    setNewSymbol('');
    setShowAddSymbol(false);
  };

  const handleRemoveSymbol = async (symbol: string) => {
    if (!id) return;
    if (confirm(`Remove ${symbol} from watchlist?`)) {
      await removeStock(id, symbol);
    }
  };

  const handleQuickTrade = (symbol: string) => {
    navigate(`/trading?symbol=${symbol}`);
  };

  if (!watchlist) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-400 mb-2">
            Watchlist not found
          </h2>
          <button
            onClick={() => navigate('/watchlists')}
            className="text-green-400 hover:text-green-300"
          >
            Back to Watchlists
          </button>
        </div>
      </div>
    );
  }

  const columnDefs = [
    {
      field: 'symbol',
      headerName: 'Symbol',
      width: 120,
      cellRenderer: (params: any) => (
        <strong className="font-mono">{params.value}</strong>
      ),
      pinned: 'left' as const,
    },
    {
      field: 'name',
      headerName: 'Name',
      width: 200,
    },
    {
      field: 'price',
      headerName: 'Price',
      width: 100,
      valueFormatter: (p: any) => `$${p.value.toFixed(2)}`,
    },
    {
      field: 'changePct',
      headerName: 'Change %',
      width: 120,
      cellStyle: (params: any) => {
        return params.value >= 0
          ? { color: '#10b981' }
          : { color: '#ef4444' };
      },
      valueFormatter: (p: any) =>
        `${p.value >= 0 ? '+' : ''}${p.value.toFixed(2)}%`,
    },
    {
      field: 'change',
      headerName: 'Change $',
      width: 100,
      cellStyle: (params: any) => {
        return params.value >= 0
          ? { color: '#10b981' }
          : { color: '#ef4444' };
      },
      valueFormatter: (p: any) =>
        `${p.value >= 0 ? '+' : ''}$${p.value.toFixed(2)}`,
    },
    {
      field: 'volume',
      headerName: 'Volume',
      width: 120,
      valueFormatter: (p: any) => {
        if (p.value >= 1000000) {
          return `${(p.value / 1000000).toFixed(2)}M`;
        }
        return `${(p.value / 1000).toFixed(0)}K`;
      },
    },
    {
      field: 'marketCap',
      headerName: 'Market Cap',
      width: 120,
      valueFormatter: (p: any) => {
        if (p.value >= 1000000000) {
          return `$${(p.value / 1000000000).toFixed(2)}B`;
        }
        return `$${(p.value / 1000000).toFixed(0)}M`;
      },
    },
    {
      field: 'sector',
      headerName: 'Sector',
      width: 150,
    },
    {
      field: 'notes',
      headerName: 'Notes',
      width: 200,
      valueFormatter: (p: any) => p.value || '-',
    },
    {
      headerName: 'Actions',
      width: 250,
      cellRenderer: (params: any) => (
        <div className="flex gap-2 py-2">
          <button
            onClick={() => handleQuickTrade(params.data.symbol)}
            className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm transition"
          >
            Trade
          </button>
          <button
            onClick={() => navigate(`/scanner?symbol=${params.data.symbol}`)}
            className="px-3 py-1 bg-dark-border hover:bg-dark-border-hover rounded text-sm transition"
          >
            View
          </button>
          <button
            onClick={() => handleRemoveSymbol(params.data.symbol)}
            className="px-3 py-1 bg-red-900/30 hover:bg-red-900/50 text-red-400 rounded text-sm transition"
          >
            Remove
          </button>
        </div>
      ),
    },
  ];

  const topGainer = watchlist.stocks.length > 0
    ? [...watchlist.stocks].sort((a, b) => b.changePct - a.changePct)[0]
    : null;
  const topLoser = watchlist.stocks.length > 0
    ? [...watchlist.stocks].sort((a, b) => a.changePct - b.changePct)[0]
    : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/watchlists')}
            className="p-2 hover:bg-dark-border rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white">{watchlist.name}</h1>
            {watchlist.description && (
              <p className="text-sm text-gray-400">{watchlist.description}</p>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setShowAddSymbol(!showAddSymbol)}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg flex items-center gap-2 transition"
          >
            <Plus className="w-4 h-4" />
            Add Stock
          </button>
          <button
            onClick={() => navigate(`/alerts/create?watchlist=${id}`)}
            className="px-4 py-2 bg-dark-border hover:bg-dark-border-hover rounded-lg flex items-center gap-2 transition"
          >
            <Bell className="w-4 h-4" />
            Create Alert
          </button>
          <button
            onClick={() => {
              /* Export CSV */
            }}
            className="px-4 py-2 bg-dark-border hover:bg-dark-border-hover rounded-lg flex items-center gap-2 transition"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      {/* Add Symbol Input */}
      {showAddSymbol && (
        <div className="bg-green-900/10 border border-green-700 rounded-lg p-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value)}
              placeholder="Enter symbol (e.g., NVAX)"
              className="flex-1 px-4 py-2 bg-dark-bg border border-dark-border rounded-lg uppercase text-white"
              onKeyPress={(e) => e.key === 'Enter' && handleAddSymbol()}
            />
            <button
              onClick={handleAddSymbol}
              className="px-6 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition"
            >
              Add
            </button>
            <button
              onClick={() => setShowAddSymbol(false)}
              className="px-6 py-2 bg-dark-border hover:bg-dark-border-hover rounded-lg transition"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Total Stocks</div>
          <div className="text-3xl font-bold text-white">
            {watchlist.stocks.length}
          </div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Avg Performance</div>
          <div
            className={`text-3xl font-bold ${
              (watchlist.avgChange || 0) >= 0
                ? 'text-green-400'
                : 'text-red-400'
            }`}
          >
            {(watchlist.avgChange || 0) >= 0 ? '+' : ''}
            {(watchlist.avgChange || 0).toFixed(1)}%
          </div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Best Performer</div>
          {topGainer ? (
            <>
              <div className="text-xl font-bold text-green-400">
                {topGainer.symbol}
              </div>
              <div className="text-sm text-green-400">
                +{topGainer.changePct.toFixed(1)}%
              </div>
            </>
          ) : (
            <div className="text-sm text-gray-500">-</div>
          )}
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Worst Performer</div>
          {topLoser ? (
            <>
              <div className="text-xl font-bold text-red-400">
                {topLoser.symbol}
              </div>
              <div className="text-sm text-red-400">
                {topLoser.changePct.toFixed(1)}%
              </div>
            </>
          ) : (
            <div className="text-sm text-gray-500">-</div>
          )}
        </div>
      </div>

      {/* Stocks Table */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Stocks</h2>

        {watchlist.stocks.length === 0 ? (
          <div className="text-center py-12">
            <TrendingUp className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">
              No stocks in this watchlist
            </h3>
            <p className="text-gray-500 mb-6">Add stocks to start tracking</p>
            <button
              onClick={() => setShowAddSymbol(true)}
              className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition"
            >
              Add Stock
            </button>
          </div>
        ) : (
          <div
            className="ag-theme-alpine-dark"
            style={{ height: 600, width: '100%' }}
          >
            <AgGridReact
              rowData={watchlist.stocks}
              columnDefs={columnDefs}
              defaultColDef={{
                sortable: true,
                filter: true,
                resizable: true,
              }}
              rowHeight={50}
              suppressCellFocus={true}
            />
          </div>
        )}
      </div>
    </div>
  );
}
