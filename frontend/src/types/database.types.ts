/**
 * Database-related TypeScript type definitions
 */

export type DataTier = 'HOT' | 'WARM' | 'COLD';
export type TableType = 'TICKS' | 'OHLCV' | 'ORDERS' | 'FILLS' | 'POSITIONS' | 'STRATEGIES' | 'BACKTESTS';

export interface DatabaseTable {
  name: string;
  type: TableType;
  tier: DataTier;
  rowCount: number;
  sizeGB: number;
  lastUpdated: Date;
  retentionDays: number;
  compressionRatio: number;
  schema: TableSchema;
}

export interface TableSchema {
  columns: ColumnDefinition[];
  primaryKey: string[];
  indexes: IndexDefinition[];
  partitionKey?: string;
}

export interface ColumnDefinition {
  name: string;
  type: string;
  nullable: boolean;
  defaultValue?: string | number | boolean;
  description?: string;
}

export interface IndexDefinition {
  name: string;
  columns: string[];
  unique: boolean;
  type: 'BTREE' | 'HASH' | 'GIN' | 'GIST';
}

export interface DataQuery {
  id: string;
  name: string;
  description?: string;
  sql: string;
  parameters?: QueryParameter[];
  createdAt: Date;
  createdBy: string;
  savedQuery?: boolean;
}

export interface QueryParameter {
  name: string;
  type: string;
  required: boolean;
  defaultValue?: string | number | boolean;
}

export interface QueryResult {
  columns: string[];
  rows: Record<string, unknown>[];
  rowCount: number;
  executionTime: number;
  queryId?: string;
}

export interface DataExplorerState {
  selectedTable?: DatabaseTable;
  currentQuery?: DataQuery;
  queryResults?: QueryResult;
  isLoading: boolean;
  error?: string;
}

export interface TierMetrics {
  tier: DataTier;
  totalSizeGB: number;
  tableCount: number;
  totalRows: number;
  avgCompressionRatio: number;
  readQPS: number;
  writeQPS: number;
  avgLatencyMs: number;
}

export interface DataMigrationJob {
  id: string;
  sourceTier: DataTier;
  targetTier: DataTier;
  tableName: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  progress: number;
  startedAt?: Date;
  completedAt?: Date;
  rowsMigrated: number;
  totalRows: number;
  error?: string;
}
