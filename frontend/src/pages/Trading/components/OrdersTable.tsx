/**
 * Orders Table Component - AG Grid table showing pending/active orders
 */

import { AgGridReact } from 'ag-grid-react';
import { useMemo } from 'react';
import { useTradingStore } from '../../../store/useTradingStore';
import { format } from 'date-fns';

import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

export function OrdersTable() {
  const { orders, cancelOrder } = useTradingStore();

  const handleCancel = (orderId: string) => {
    if (window.confirm('Are you sure you want to cancel this order?')) {
      cancelOrder(orderId);
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
        field: 'orderType',
        headerName: 'Type',
        width: 100,
        valueFormatter: (p: any) => p.value.toUpperCase(),
      },
      {
        field: 'limitPrice',
        headerName: 'Limit Price',
        width: 120,
        valueFormatter: (p: any) => (p.value ? `$${p.value.toFixed(2)}` : '-'),
      },
      {
        field: 'stopPrice',
        headerName: 'Stop Price',
        width: 120,
        valueFormatter: (p: any) => (p.value ? `$${p.value.toFixed(2)}` : '-'),
      },
      {
        field: 'status',
        headerName: 'Status',
        width: 100,
        cellRenderer: (params: any) => {
          const colors = {
            pending: 'text-yellow-400',
            filled: 'text-green-400',
            cancelled: 'text-gray-400',
            rejected: 'text-red-400',
          };
          return (
            <span className={colors[params.value as keyof typeof colors]}>
              {params.value.toUpperCase()}
            </span>
          );
        },
      },
      {
        field: 'timeInForce',
        headerName: 'TIF',
        width: 80,
      },
      {
        field: 'submittedAt',
        headerName: 'Submitted',
        width: 180,
        valueFormatter: (p: any) => format(new Date(p.value), 'MMM dd, HH:mm:ss'),
      },
      {
        headerName: 'Actions',
        width: 120,
        cellRenderer: (params: any) => (
          <div className="flex gap-2 py-1">
            {params.data.status === 'pending' && (
              <button
                onClick={() => handleCancel(params.data.id)}
                className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm transition"
              >
                Cancel
              </button>
            )}
          </div>
        ),
      },
    ],
    [cancelOrder]
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
        rowData={orders}
        columnDefs={columnDefs}
        defaultColDef={defaultColDef}
        rowHeight={50}
        domLayout="autoHeight"
      />
    </div>
  );
}
