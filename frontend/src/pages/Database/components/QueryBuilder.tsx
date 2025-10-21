/**
 * Query Builder Component - Visual + SQL query interface
 */

import { useState } from 'react';
import { Play, Download } from 'lucide-react';
import { AgGridReact } from 'ag-grid-react';
import type { DatabaseTable } from '../../../types/database.types';
import { useDatabaseStore } from '../../../store/useDatabaseStore';

import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

interface QueryBuilderProps {
  tier: string;
  table: DatabaseTable;
}

export function QueryBuilder({ tier, table }: QueryBuilderProps) {
  const { queryResults, isLoading, executeQuery } = useDatabaseStore();
  const [sql, setSQL] = useState(`SELECT * FROM ${table.name} LIMIT 100`);

  const handleExecute = () => {
    executeQuery(tier, sql);
  };

  const columnDefs = queryResults && queryResults.length > 0
    ? Object.keys(queryResults[0]).map((key) => ({
        field: key,
        headerName: key,
        sortable: true,
        filter: true,
        resizable: true,
      }))
    : [];

  return (
    <div className="space-y-4">
      {/* Table Schema */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-3">{table.name}</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-700">
                <th className="pb-2">Column</th>
                <th className="pb-2">Type</th>
                <th className="pb-2">Nullable</th>
              </tr>
            </thead>
            <tbody>
              {table.schema.columns.map((col) => (
                <tr key={col.name} className="border-b border-gray-800">
                  <td className="py-2 font-mono text-blue-400">{col.name}</td>
                  <td className="py-2 text-gray-300">{col.type}</td>
                  <td className="py-2 text-gray-400">{col.nullable ? 'Yes' : 'No'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 pt-4 border-t border-gray-700 text-xs text-gray-500">
          <div>Rows: {table.rowCount.toLocaleString()} • Size: {table.sizeGB.toFixed(2)} GB</div>
          <div>Compression: {table.compressionRatio.toFixed(1)}x • Retention: {table.retentionDays} days</div>
        </div>
      </div>

      {/* SQL Editor */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-white">SQL Query</h3>
          <button
            onClick={handleExecute}
            disabled={isLoading}
            className="px-4 py-2 bg-green-700 hover:bg-green-600 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded flex items-center gap-2 transition-colors"
          >
            <Play size={16} />
            {isLoading ? 'Executing...' : 'Execute'}
          </button>
        </div>
        <textarea
          value={sql}
          onChange={(e) => setSQL(e.target.value)}
          className="input-field w-full font-mono text-sm"
          rows={6}
          placeholder="Enter SQL query..."
        />
      </div>

      {/* Results */}
      {queryResults && (
        <div className="card p-0 overflow-hidden">
          <div className="p-4 border-b border-gray-700 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">Results</h3>
              <p className="text-sm text-gray-400">{queryResults.length} rows</p>
            </div>
            <button className="px-3 py-1.5 bg-blue-700 hover:bg-blue-600 text-white text-sm rounded flex items-center gap-2 transition-colors">
              <Download size={14} />
              Export CSV
            </button>
          </div>
          <div className="ag-theme-alpine-dark" style={{ height: 400, width: '100%' }}>
            <AgGridReact
              rowData={queryResults}
              columnDefs={columnDefs}
              defaultColDef={{
                sortable: true,
                filter: true,
                resizable: true,
              }}
              animateRows={true}
              domLayout="normal"
            />
          </div>
        </div>
      )}
    </div>
  );
}
