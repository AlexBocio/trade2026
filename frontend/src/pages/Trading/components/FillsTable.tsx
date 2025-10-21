/**
 * Fills Table Component - AG Grid table showing order execution fills
 */

import { AgGridReact } from 'ag-grid-react';
import { useMemo } from 'react';
import { useTradingStore } from '../../../store/useTradingStore';
import { format } from 'date-fns';

import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

export function FillsTable() {
  const { fills } = useTradingStore();

  const columnDefs = useMemo(
    () => [
      {
        field: 'orderId',
        headerName: 'Order ID',
        width: 120,
        cellRenderer: (params: any) => <span className="font-mono text-sm">{params.value}</span>,
      },
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
          <span className={params.value === 'buy' ? 'text-green-400' : 'text-red-400'}>
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
        field: 'fillPrice',
        headerName: 'Fill Price',
        width: 120,
        valueFormatter: (p: any) => `$${p.value.toFixed(2)}`,
      },
      {
        field: 'commission',
        headerName: 'Commission',
        width: 120,
        valueFormatter: (p: any) => `$${p.value.toFixed(2)}`,
      },
      {
        field: 'filledAt',
        headerName: 'Filled At',
        width: 180,
        valueFormatter: (p: any) => format(new Date(p.value), 'MMM dd, HH:mm:ss'),
      },
      {
        headerName: 'Total',
        width: 140,
        valueGetter: (p: any) => p.data.quantity * p.data.fillPrice,
        valueFormatter: (p: any) => `$${p.value.toFixed(2)}`,
        cellStyle: { fontWeight: 'bold' },
      },
    ],
    []
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
        rowData={fills}
        columnDefs={columnDefs}
        defaultColDef={defaultColDef}
        rowHeight={50}
        domLayout="autoHeight"
      />
    </div>
  );
}
