/**
 * Positions Table Component - AG Grid table showing open positions
 */

import { AgGridReact } from 'ag-grid-react';
import { useMemo } from 'react';
import { useTradingStore } from '../../../store/useTradingStore';

import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

export function PositionsTable() {
  const { positions, closePosition, modifyPosition } = useTradingStore();

  const handleClose = (positionId: string) => {
    if (window.confirm('Are you sure you want to close this position?')) {
      closePosition(positionId);
    }
  };

  const handleModify = (positionId: string) => {
    const newStop = prompt('Enter new stop loss:');
    const newTarget = prompt('Enter new profit target:');

    if (newStop && newTarget) {
      modifyPosition(positionId, {
        stopLoss: parseFloat(newStop),
        profitTarget: parseFloat(newTarget),
      });
    }
  };

  const columnDefs = useMemo(
    () => [
      {
        field: 'symbol',
        headerName: 'Symbol',
        width: 100,
        cellRenderer: (params: any) => <strong>{params.value}</strong>,
      },
      {
        field: 'side',
        headerName: 'Side',
        width: 80,
        cellRenderer: (params: any) => (
          <span className={params.value === 'long' ? 'text-green-400' : 'text-red-400'}>
            {params.value.toUpperCase()}
          </span>
        ),
      },
      {
        field: 'quantity',
        headerName: 'Qty',
        width: 100,
        valueFormatter: (p: any) => p.value.toLocaleString(),
      },
      {
        field: 'entryPrice',
        headerName: 'Entry',
        width: 100,
        valueFormatter: (p: any) => `$${p.value.toFixed(2)}`,
      },
      {
        field: 'currentPrice',
        headerName: 'Current',
        width: 100,
        valueFormatter: (p: any) => `$${p.value.toFixed(2)}`,
      },
      {
        field: 'unrealizedPnL',
        headerName: 'P&L',
        width: 120,
        cellClassRules: {
          'text-green-400': (params: any) => params.value > 0,
          'text-red-400': (params: any) => params.value < 0,
        },
        valueFormatter: (p: any) => `$${p.value.toFixed(2)}`,
      },
      {
        field: 'unrealizedPnLPct',
        headerName: 'P&L%',
        width: 100,
        cellClassRules: {
          'text-green-400': (params: any) => params.value > 0,
          'text-red-400': (params: any) => params.value < 0,
        },
        valueFormatter: (p: any) => `${p.value > 0 ? '+' : ''}${p.value.toFixed(2)}%`,
      },
      {
        field: 'stopLoss',
        headerName: 'Stop',
        width: 100,
        valueFormatter: (p: any) => `$${p.value.toFixed(2)}`,
      },
      {
        field: 'profitTarget',
        headerName: 'Target',
        width: 100,
        valueFormatter: (p: any) => `$${p.value.toFixed(2)}`,
      },
      {
        field: 'daysHeld',
        headerName: 'Days',
        width: 80,
      },
      {
        headerName: 'Actions',
        width: 220,
        cellRenderer: (params: any) => (
          <div className="flex gap-2 py-1">
            <button
              onClick={() => handleClose(params.data.id)}
              className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm transition"
            >
              Close
            </button>
            <button
              onClick={() => handleModify(params.data.id)}
              className="px-3 py-1 bg-gray-600 hover:bg-gray-700 rounded text-sm transition"
            >
              Modify
            </button>
          </div>
        ),
      },
    ],
    [closePosition, modifyPosition]
  );

  const defaultColDef = useMemo(
    () => ({
      sortable: true,
      filter: true,
      resizable: true,
    }),
    []
  );

  return (
    <div className="ag-theme-alpine-dark h-full">
      <AgGridReact
        rowData={positions}
        columnDefs={columnDefs}
        defaultColDef={defaultColDef}
        rowHeight={50}
        domLayout="autoHeight"
      />
    </div>
  );
}
