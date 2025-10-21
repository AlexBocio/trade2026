/**
 * Scanner Page - Small-cap stock scanner with real-time updates
 */

import { useEffect, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef, GridReadyEvent } from 'ag-grid-community';
import { useScannerStore } from '../../store/useScannerStore';
import { scannerFilters } from '../../services/mock-data/scanner-data';
import { MiniChart } from './components/MiniChart';
import { StockDetailsPanel } from './components/StockDetailsPanel';
import { formatCurrency } from '../../utils/helpers';
import { Search, TrendingUp, Settings, Activity } from 'lucide-react';

import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

export function Scanner() {
  const navigate = useNavigate();
  const gridRef = useRef<AgGridReact>(null);
  const {
    stocks,
    selectedStock,
    filters,
    isLoading,
    loadScanner,
    applyFilters,
    selectStock,
    updatePrices,
  } = useScannerStore();

  useEffect(() => {
    loadScanner();
  }, [loadScanner]);

  // Live updates every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      updatePrices();
    }, 5000);

    return () => clearInterval(interval);
  }, [updatePrices]);

  // Column definitions for AG Grid
  const columnDefs: ColDef[] = useMemo(
    () => [
      {
        field: 'symbol',
        headerName: 'Symbol',
        width: 100,
        cellRenderer: (params: any) => (
          <strong className="text-white">{params.value}</strong>
        ),
      },
      {
        field: 'price',
        headerName: 'Price',
        width: 100,
        valueFormatter: (params) => formatCurrency(params.value),
      },
      {
        field: 'change',
        headerName: 'Change %',
        width: 120,
        cellClass: (params) => (params.value > 0 ? 'text-profit' : 'text-loss'),
        valueFormatter: (params) =>
          `${params.value > 0 ? '+' : ''}${params.value.toFixed(1)}%`,
      },
      {
        field: 'volumeSurge',
        headerName: 'Vol Surge',
        width: 110,
        valueFormatter: (params) => `${params.value.toFixed(1)}x`,
      },
      {
        field: 'momentumScore',
        headerName: 'Momentum',
        width: 130,
        cellRenderer: (params: any) => (
          <span
            className={`px-2 py-1 rounded text-xs font-semibold ${
              params.value > 85
                ? 'bg-green-900 text-green-300'
                : params.value > 70
                ? 'bg-yellow-900 text-yellow-300'
                : 'bg-orange-900 text-orange-300'
            }`}
          >
            {params.value.toFixed(0)}
          </span>
        ),
      },
      {
        field: 'pattern',
        headerName: 'Pattern',
        width: 160,
      },
      {
        field: 'catalyst',
        headerName: 'Catalyst',
        width: 140,
        valueFormatter: (params) => params.value || '-',
      },
      {
        field: 'liquidity',
        headerName: 'Liquidity',
        width: 110,
        valueFormatter: (params) => `${(params.value / 1000).toFixed(0)}K`,
      },
    ],
    []
  );

  const defaultColDef: ColDef = useMemo(
    () => ({
      sortable: true,
      filter: true,
      resizable: true,
    }),
    []
  );

  // Filter stocks based on selected filters
  const filteredStocks = useMemo(() => {
    return stocks.filter((stock) => {
      // Market cap filter
      if (filters.marketCap !== 'All') {
        const [min, max] = filters.marketCap.split('-').map((v) => {
          const num = parseFloat(v.replace('M', ''));
          return num * 1000000;
        });
        if (stock.marketCap < min || stock.marketCap > max) return false;
      }

      // Price range filter
      if (filters.priceRange !== 'All') {
        const [min, max] = filters.priceRange.split('-').map(parseFloat);
        if (stock.price < min || stock.price > max) return false;
      }

      // Volume surge filter
      if (filters.volumeSurge !== 'All') {
        const minSurge = parseFloat(filters.volumeSurge.replace('>','').replace('x',''));
        if (stock.volumeSurge < minSurge) return false;
      }

      // Pattern filter
      if (filters.pattern !== 'All' && stock.pattern !== filters.pattern) {
        return false;
      }

      return true;
    });
  }, [stocks, filters]);

  const onGridReady = (params: GridReadyEvent) => {
    params.api.sizeColumnsToFit();
  };

  const onRowClicked = (event: any) => {
    selectStock(event.data.symbol);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-400">Loading scanner...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Small-Cap Scanner</h1>
        <p className="text-gray-400 mt-1">
          Real-time momentum scanner ({filteredStocks.length} stocks found)
        </p>
      </div>

      {/* Scanner Tools Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Advanced Screener Promotion Card */}
        <div className="card bg-gradient-to-r from-blue-900/30 to-purple-900/30 border-blue-500/50">
          <div className="flex flex-col h-full">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-blue-600 rounded-lg">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">
                  Stock Screener
                </h3>
                <p className="text-xs text-gray-300">
                  Multi-factor quantitative analysis
                </p>
              </div>
            </div>
            <button
              onClick={() => navigate('/scanner/stock-screener')}
              className="mt-auto px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition flex items-center justify-center gap-2"
            >
              <Search className="w-4 h-4" />
              Launch Screener
            </button>
          </div>
        </div>

        {/* Custom Scanner Builder Card */}
        <div className="card bg-gradient-to-r from-purple-900/30 to-pink-900/30 border-purple-500/50">
          <div className="flex flex-col h-full">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-purple-600 rounded-lg">
                <Settings className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">
                  Scanner Builder
                </h3>
                <p className="text-xs text-gray-300">
                  Build custom regime scanners
                </p>
              </div>
            </div>
            <button
              onClick={() => navigate('/scanner/custom-builder')}
              className="mt-auto px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition flex items-center justify-center gap-2"
            >
              <Settings className="w-4 h-4" />
              Build Scanner
            </button>
          </div>
        </div>

        {/* Regime Dashboard Card */}
        <div className="card bg-gradient-to-r from-green-900/30 to-teal-900/30 border-green-500/50">
          <div className="flex flex-col h-full">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-3 bg-green-600 rounded-lg">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">
                  Regime Dashboard
                </h3>
                <p className="text-xs text-gray-300">
                  Multi-layer regime analysis
                </p>
              </div>
            </div>
            <button
              onClick={() => navigate('/scanner/regime-dashboard')}
              className="mt-auto px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition flex items-center justify-center gap-2"
            >
              <Activity className="w-4 h-4" />
              View Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Market Cap Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Market Cap</label>
            <select
              value={filters.marketCap}
              onChange={(e) => applyFilters({ marketCap: e.target.value })}
              className="input-field w-full"
            >
              {scannerFilters.marketCap.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          {/* Price Range Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Price Range</label>
            <select
              value={filters.priceRange}
              onChange={(e) => applyFilters({ priceRange: e.target.value })}
              className="input-field w-full"
            >
              {scannerFilters.priceRange.map((option) => (
                <option key={option} value={option}>
                  ${option}
                </option>
              ))}
            </select>
          </div>

          {/* Volume Surge Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Volume Surge</label>
            <select
              value={filters.volumeSurge}
              onChange={(e) => applyFilters({ volumeSurge: e.target.value })}
              className="input-field w-full"
            >
              {scannerFilters.volumeSurge.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          {/* Pattern Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Pattern</label>
            <select
              value={filters.pattern}
              onChange={(e) => applyFilters({ pattern: e.target.value })}
              className="input-field w-full"
            >
              {scannerFilters.pattern.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* AG Grid Table */}
      <div className="card p-0 overflow-hidden">
        <div className="ag-theme-alpine-dark" style={{ height: 500, width: '100%' }}>
          <AgGridReact
            ref={gridRef}
            rowData={filteredStocks}
            columnDefs={columnDefs}
            defaultColDef={defaultColDef}
            onGridReady={onGridReady}
            onRowClicked={onRowClicked}
            rowSelection="single"
            animateRows={true}
            domLayout="normal"
          />
        </div>
      </div>

      {/* Bottom Panel - Shows when stock selected */}
      {selectedStock && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Mini Chart */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">
              {selectedStock.symbol} - 1-Hour Chart
            </h3>
            <MiniChart symbol={selectedStock.symbol} price={selectedStock.price} />
          </div>

          {/* Stock Details */}
          <div className="card">
            <StockDetailsPanel stock={selectedStock} />
          </div>
        </div>
      )}
    </div>
  );
}
