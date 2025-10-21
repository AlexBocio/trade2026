/**
 * Data Explorer (Level 1) - Database overview showing hot/warm/cold tiers
 */

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, Server, HardDrive, ArrowRight, Activity, Zap } from 'lucide-react';
import { useDatabaseStore } from '../../store/useDatabaseStore';

export function DataExplorer() {
  const navigate = useNavigate();
  const { overview, isLoading, loadOverview } = useDatabaseStore();

  useEffect(() => {
    loadOverview();
  }, [loadOverview]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-400">Loading database overview...</p>
        </div>
      </div>
    );
  }

  if (!overview) {
    return (
      <div className="card">
        <p className="text-gray-400">No data available</p>
      </div>
    );
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

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'hot':
        return <Zap className="text-red-400" size={24} />;
      case 'warm':
        return <Server className="text-yellow-400" size={24} />;
      case 'cold':
        return <HardDrive className="text-blue-400" size={24} />;
      default:
        return <Database className="text-gray-400" size={24} />;
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'hot':
        return 'border-red-700 hover:border-red-500';
      case 'warm':
        return 'border-yellow-700 hover:border-yellow-500';
      case 'cold':
        return 'border-blue-700 hover:border-blue-500';
      default:
        return 'border-gray-700 hover:border-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Database Explorer</h1>
        <p className="text-gray-400 mt-1">
          Multi-tier data storage: {formatSize(overview.totalSize)} total • {formatRows(overview.totalRows)} rows
        </p>
      </div>

      {/* Tier Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {overview.tiers.map((tier) => (
          <div
            key={tier.tier}
            onClick={() => navigate(`/database/${tier.tier}`)}
            className={`card cursor-pointer transition-all ${getTierColor(tier.tier)}`}
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                {getTierIcon(tier.tier)}
                <div>
                  <h3 className="text-lg font-semibold text-white">{tier.name}</h3>
                  <p className="text-sm text-gray-400">{tier.technology}</p>
                </div>
              </div>
              <ArrowRight className="text-gray-500" size={20} />
            </div>

            {/* Description */}
            <p className="text-sm text-gray-400 mb-4">{tier.description}</p>

            {/* Metrics */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <div className="text-xs text-gray-500">Size</div>
                <div className="text-lg font-semibold text-white">{formatSize(tier.sizeGB)}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Rows</div>
                <div className="text-lg font-semibold text-white">{formatRows(tier.rowCount)}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Retention</div>
                <div className="text-sm font-semibold text-white">{tier.retention}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Avg Query</div>
                <div className="text-sm font-semibold text-white">{tier.avgQueryTime}</div>
              </div>
            </div>

            {/* Tables */}
            <div className="pt-4 border-t border-gray-700">
              <div className="text-xs text-gray-500 mb-2">{tier.tables.length} Tables</div>
              <div className="space-y-1">
                {tier.tables.slice(0, 3).map((table) => (
                  <div key={table.name} className="flex items-center justify-between text-xs">
                    <span className="text-gray-400">{table.name}</span>
                    <span className="text-gray-500">{formatRows(table.rows)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Ingestion Rate */}
            {tier.ingestionRate > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-700 flex items-center gap-2">
                <Activity size={14} className="text-green-400" />
                <span className="text-xs text-gray-400">
                  {tier.ingestionRate.toLocaleString()} rows/sec
                </span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Quick Stats */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">System Overview</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <div className="text-sm text-gray-500 mb-1">Total Data</div>
            <div className="text-2xl font-bold text-white">{formatSize(overview.totalSize)}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">Total Rows</div>
            <div className="text-2xl font-bold text-white">{formatRows(overview.totalRows)}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">Ingestion Rate</div>
            <div className="text-2xl font-bold text-white">
              {overview.avgIngestionRate.toLocaleString()}
            </div>
            <div className="text-xs text-gray-500">rows/sec</div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">Data Tiers</div>
            <div className="text-2xl font-bold text-white">{overview.tiers.length}</div>
          </div>
        </div>
      </div>

      {/* Data Tiering Breakdown */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">Data Distribution</h2>
        <div className="space-y-4">
          {overview.tiers.map((tier) => {
            const percentage = (tier.sizeGB / overview.totalSize) * 100;
            return (
              <div key={tier.tier}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getTierIcon(tier.tier)}
                    <span className="text-sm font-medium text-white">{tier.name}</span>
                  </div>
                  <span className="text-sm text-gray-400">
                    {formatSize(tier.sizeGB)} ({percentage.toFixed(1)}%)
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      tier.tier === 'hot'
                        ? 'bg-red-500'
                        : tier.tier === 'warm'
                        ? 'bg-yellow-500'
                        : 'bg-blue-500'
                    }`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
