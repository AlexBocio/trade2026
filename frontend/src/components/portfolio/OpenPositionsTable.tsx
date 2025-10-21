/**
 * Open Positions Table - AG Grid table of all open positions
 */

import { AgGridReact } from 'ag-grid-react';
import { useMemo } from 'react';

interface Position {
  id: string;
  symbol: string;
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  value: number;
  pnl: number;
  pnlPct: number;
  sector: string;
}

export function OpenPositionsTable({ positions }: { positions: Position[] }) {
  const columnDefs: any[] = useMemo(
    () => [
      {
        field: 'symbol',
        headerName: 'Symbol',
        width: 120,
        cellClass: 'font-semibold',
      },
      {
        field: 'quantity',
        headerName: 'Quantity',
        width: 120,
        valueFormatter: (params) => params.value.toLocaleString(),
      },
      {
        field: 'entryPrice',
        headerName: 'Entry Price',
        width: 130,
        valueFormatter: (params) => `$${params.value.toFixed(2)}`,
      },
      {
        field: 'currentPrice',
        headerName: 'Current Price',
        width: 140,
        valueFormatter: (params) => `$${params.value.toFixed(2)}`,
      },
      {
        field: 'value',
        headerName: 'Market Value',
        width: 150,
        valueFormatter: (params) => `$${params.value.toLocaleString()}`,
      },
      {
        field: 'pnl',
        headerName: 'P&L',
        width: 130,
        valueFormatter: (params) => {
          const sign = params.value >= 0 ? '+' : '';
          return `${sign}$${params.value.toLocaleString()}`;
        },
        cellClass: (params) => (params.value >= 0 ? 'text-green-400' : 'text-red-400'),
      },
      {
        field: 'pnlPct',
        headerName: 'P&L %',
        width: 120,
        valueFormatter: (params) => {
          const sign = params.value >= 0 ? '+' : '';
          return `${sign}${params.value.toFixed(2)}%`;
        },
        cellClass: (params) => (params.value >= 0 ? 'text-green-400' : 'text-red-400'),
      },
      {
        field: 'sector',
        headerName: 'Sector',
        width: 140,
        cellClass: 'text-gray-400',
      },
    ],
    []
  );

  // Filter out cash position for this table
  const tradingPositions = positions.filter((p) => p.symbol !== 'MNOP' && p.quantity > 0);

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h3 className="text-lg font-semibold mb-4">Open Positions</h3>
      <div className="ag-theme-alpine-dark" style={{ height: 300, width: '100%' }}>
        <AgGridReact<Position>
          rowData={tradingPositions}
          columnDefs={columnDefs}
          defaultColDef={{
            sortable: true,
            filter: true,
            resizable: true,
          }}
          animateRows={true}
          rowSelection="single"
        />
      </div>
    </div>
  );
}
