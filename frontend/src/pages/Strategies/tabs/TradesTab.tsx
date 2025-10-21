/**
 * Trades Tab - AG Grid with trade history
 */

import { useEffect, useMemo, useRef, useState } from 'react';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef, GridReadyEvent } from 'ag-grid-community';
import { X } from 'lucide-react';
import type { StrategyExtended, Trade } from '../../../services/mock-data/strategy-data';
import { useStrategyStore } from '../../../store/useStrategyStore';
import { formatCurrency } from '../../../utils/helpers';
import { format } from 'date-fns';

import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

interface TradesTabProps {
  strategy: StrategyExtended;
}

export function TradesTab({ strategy }: TradesTabProps) {
  const gridRef = useRef<AgGridReact>(null);
  const { strategyTrades, fetchStrategyTrades } = useStrategyStore();
  const [selectedTrade, setSelectedTrade] = useState<Trade | null>(null);
  const [sideFilter, setSideFilter] = useState<string>('all');

  useEffect(() => {
    fetchStrategyTrades(strategy.id);
  }, [strategy.id, fetchStrategyTrades]);

  const columnDefs: ColDef<Trade>[] = useMemo(
    () => [
      {
        headerName: 'Symbol',
        field: 'symbol',
        width: 100,
        cellClass: 'font-semibold',
      },
      {
        headerName: 'Side',
        field: 'side',
        width: 90,
        cellRenderer: (params: any) => {
          const side = params.value;
          return (
            <span
              className={`px-2 py-1 text-xs font-semibold rounded ${
                side === 'BUY' ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'
              }`}
            >
              {side}
            </span>
          );
        },
      },
      {
        headerName: 'Entry',
        field: 'entryPrice',
        width: 110,
        valueFormatter: (params) => formatCurrency(params.value),
      },
      {
        headerName: 'Exit',
        field: 'exitPrice',
        width: 110,
        valueFormatter: (params) => (params.value ? formatCurrency(params.value) : '-'),
      },
      {
        headerName: 'Quantity',
        field: 'quantity',
        width: 100,
      },
      {
        headerName: 'P&L',
        field: 'pnl',
        width: 120,
        cellClass: (params) => (params.value >= 0 ? 'text-profit' : 'text-loss'),
        valueFormatter: (params) => formatCurrency(params.value),
      },
      {
        headerName: 'P&L %',
        field: 'pnlPercent',
        width: 100,
        cellClass: (params) => (params.value >= 0 ? 'text-profit' : 'text-loss'),
        valueFormatter: (params) => `${params.value >= 0 ? '+' : ''}${params.value.toFixed(2)}%`,
      },
      {
        headerName: 'Entry Time',
        field: 'entryTime',
        width: 160,
        valueFormatter: (params) => format(new Date(params.value), 'MMM d, yyyy HH:mm'),
      },
      {
        headerName: 'Exit Time',
        field: 'exitTime',
        width: 160,
        valueFormatter: (params) =>
          params.value ? format(new Date(params.value), 'MMM d, yyyy HH:mm') : '-',
      },
      {
        headerName: 'Status',
        field: 'status',
        width: 100,
        cellRenderer: (params: any) => {
          const status = params.value;
          return (
            <span
              className={`px-2 py-1 text-xs font-semibold rounded ${
                status === 'CLOSED'
                  ? 'bg-gray-700 text-gray-300'
                  : 'bg-blue-900/30 text-blue-400'
              }`}
            >
              {status}
            </span>
          );
        },
      },
    ],
    []
  );

  const filteredTrades = useMemo(() => {
    if (sideFilter === 'all') return strategyTrades;
    return strategyTrades.filter((trade) => trade.side === sideFilter);
  }, [strategyTrades, sideFilter]);

  const defaultColDef: ColDef = useMemo(
    () => ({
      sortable: true,
      filter: true,
      resizable: true,
    }),
    []
  );

  const onGridReady = (params: GridReadyEvent) => {
    params.api.sizeColumnsToFit();
  };

  const onRowClicked = (event: any) => {
    setSelectedTrade(event.data);
  };

  return (
    <div className="space-y-4">
      {/* Filters Bar */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            {['all', 'BUY', 'SELL'].map((filter) => (
              <button
                key={filter}
                onClick={() => setSideFilter(filter)}
                className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                  sideFilter === filter
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {filter === 'all' ? 'All' : filter}
              </button>
            ))}
          </div>
          <div className="text-sm text-gray-400">
            {filteredTrades.length} trade{filteredTrades.length !== 1 ? 's' : ''}
          </div>
        </div>
      </div>

      {/* AG Grid */}
      <div className="card p-0 overflow-hidden">
        <div className="ag-theme-alpine-dark" style={{ height: 500, width: '100%' }}>
          <AgGridReact
            ref={gridRef}
            rowData={filteredTrades}
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

      {/* Trade Detail Modal */}
      {selectedTrade && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-dark-card border border-gray-700 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-dark-card border-b border-gray-700 p-6 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">Trade Details</h2>
              <button
                onClick={() => setSelectedTrade(null)}
                className="p-2 hover:bg-gray-700 rounded transition-colors"
              >
                <X size={20} className="text-gray-400" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Header Info */}
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-3xl font-bold text-white mb-2">{selectedTrade.symbol}</h3>
                  <div className="flex items-center gap-3">
                    <span
                      className={`px-3 py-1 text-sm font-semibold rounded ${
                        selectedTrade.side === 'BUY'
                          ? 'bg-green-900/30 text-green-400'
                          : 'bg-red-900/30 text-red-400'
                      }`}
                    >
                      {selectedTrade.side}
                    </span>
                    <span
                      className={`px-3 py-1 text-sm font-semibold rounded ${
                        selectedTrade.status === 'CLOSED'
                          ? 'bg-gray-700 text-gray-300'
                          : 'bg-blue-900/30 text-blue-400'
                      }`}
                    >
                      {selectedTrade.status}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500 mb-1">P&L</div>
                  <div
                    className={`text-3xl font-bold ${
                      selectedTrade.pnl >= 0 ? 'text-profit' : 'text-loss'
                    }`}
                  >
                    {formatCurrency(selectedTrade.pnl)}
                  </div>
                  <div
                    className={`text-sm ${selectedTrade.pnl >= 0 ? 'text-profit' : 'text-loss'}`}
                  >
                    {selectedTrade.pnlPercent >= 0 ? '+' : ''}
                    {selectedTrade.pnlPercent.toFixed(2)}%
                  </div>
                </div>
              </div>

              {/* Trade Details Grid */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <div className="text-sm text-gray-500 mb-1">Entry Price</div>
                  <div className="text-xl font-semibold text-white">
                    {formatCurrency(selectedTrade.entryPrice)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 mb-1">Exit Price</div>
                  <div className="text-xl font-semibold text-white">
                    {selectedTrade.exitPrice ? formatCurrency(selectedTrade.exitPrice) : '-'}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 mb-1">Quantity</div>
                  <div className="text-xl font-semibold text-white">{selectedTrade.quantity}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 mb-1">Total Value</div>
                  <div className="text-xl font-semibold text-white">
                    {formatCurrency(selectedTrade.entryPrice * selectedTrade.quantity)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 mb-1">Entry Time</div>
                  <div className="text-sm text-white">
                    {format(new Date(selectedTrade.entryTime), 'MMM d, yyyy HH:mm:ss')}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 mb-1">Exit Time</div>
                  <div className="text-sm text-white">
                    {selectedTrade.exitTime
                      ? format(new Date(selectedTrade.exitTime), 'MMM d, yyyy HH:mm:ss')
                      : '-'}
                  </div>
                </div>
              </div>

              {/* Additional Info */}
              {selectedTrade.notes && (
                <div>
                  <div className="text-sm text-gray-500 mb-2">Notes</div>
                  <div className="p-4 bg-gray-800 rounded text-sm text-gray-300">
                    {selectedTrade.notes}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
