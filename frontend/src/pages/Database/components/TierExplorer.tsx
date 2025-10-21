/**
 * Tier Explorer Component - Displays tables for a specific tier (hot/warm/cold)
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Table as TableIcon, Database } from 'lucide-react';
import { useDatabaseStore } from '../../../store/useDatabaseStore';
import { mockDatabaseTables, mockDatabaseOverview } from '../../../services/mock-data/database-data';
import { QueryBuilder } from './QueryBuilder';

interface TierExplorerProps {
  tier: 'hot' | 'warm' | 'cold';
}

export function TierExplorer({ tier }: TierExplorerProps) {
  const navigate = useNavigate();
  const { loadTier } = useDatabaseStore();
  const [selectedTable, setSelectedTable] = useState<string | null>(null);

  useEffect(() => {
    loadTier(tier);
  }, [tier, loadTier]);

  const tierData = mockDatabaseOverview.tiers.find((t) => t.tier === tier);
  const tables = mockDatabaseTables.filter(
    (t) => t.tier.toLowerCase() === tier.toLowerCase()
  );

  if (!tierData) {
    return <div className="card">Tier not found</div>;
  }

  const formatSize = (sizeGB: number): string => {
    if (sizeGB >= 1000) return `${(sizeGB / 1000).toFixed(2)} TB`;
    return `${sizeGB.toFixed(2)} GB`;
  };

  const formatRows = (rows: number): string => {
    if (rows >= 1000000000) return `${(rows / 1000000000).toFixed(2)}B`;
    if (rows >= 1000000) return `${(rows / 1000000).toFixed(2)}M`;
    if (rows >= 1000) return `${(rows / 1000).toFixed(2)}K`;
    return rows.toString();
  };

  const getTierColor = () => {
    switch (tier) {
      case 'hot':
        return 'text-red-400';
      case 'warm':
        return 'text-yellow-400';
      case 'cold':
        return 'text-blue-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate('/database')}
          className="flex items-center gap-2 text-gray-400 hover:text-white mb-3 transition-colors"
        >
          <ArrowLeft size={18} />
          Back to Database Explorer
        </button>
        <h1 className={`text-2xl font-bold ${getTierColor()}`}>{tierData.name}</h1>
        <p className="text-gray-400 mt-1">{tierData.technology} • {tierData.description}</p>
      </div>

      {/* Tier Summary */}
      <div className="card">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
          <div>
            <div className="text-sm text-gray-500 mb-1">Total Size</div>
            <div className="text-2xl font-bold text-white">{formatSize(tierData.sizeGB)}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">Total Rows</div>
            <div className="text-2xl font-bold text-white">{formatRows(tierData.rowCount)}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">Retention</div>
            <div className="text-2xl font-bold text-white">{tierData.retention}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">Avg Query Time</div>
            <div className="text-2xl font-bold text-white">{tierData.avgQueryTime}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">Ingestion Rate</div>
            <div className="text-2xl font-bold text-white">
              {tierData.ingestionRate > 0 ? `${tierData.ingestionRate.toLocaleString()}/s` : 'Archive'}
            </div>
          </div>
        </div>
      </div>

      {/* Tables List & Query Builder */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sidebar - Tables List */}
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Database size={20} />
            Tables ({tables.length})
          </h2>
          <div className="space-y-2">
            {tables.map((table) => (
              <button
                key={table.name}
                onClick={() => setSelectedTable(table.name)}
                className={`w-full text-left p-3 rounded transition-colors ${
                  selectedTable === table.name
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <TableIcon size={16} />
                  <span className="font-semibold">{table.name}</span>
                </div>
                <div className="text-xs text-gray-400">
                  {formatRows(table.rowCount)} rows • {formatSize(table.sizeGB)}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Main Panel - Query Builder */}
        <div className="lg:col-span-2">
          {selectedTable ? (
            <QueryBuilder
              tier={tier}
              table={tables.find((t) => t.name === selectedTable)!}
            />
          ) : (
            <div className="card h-full flex items-center justify-center">
              <div className="text-center text-gray-400">
                <Database size={48} className="mx-auto mb-4 opacity-50" />
                <p>Select a table to view data and run queries</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
