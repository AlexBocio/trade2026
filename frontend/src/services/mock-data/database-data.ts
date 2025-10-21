/**
 * Mock database data - tables, tiers, and sample records
 */

import type { DatabaseTable, TierMetrics } from '../../types/database.types';
import type { Position, Order, Account, PortfolioMetrics } from '../../types/trading.types';

export const mockDatabaseTables: DatabaseTable[] = [
  {
    name: 'ticks',
    type: 'TICKS',
    tier: 'HOT',
    rowCount: 45823456,
    sizeGB: 234.5,
    lastUpdated: new Date('2025-10-08T08:30:00Z'),
    retentionDays: 7,
    compressionRatio: 4.2,
    schema: {
      columns: [
        { name: 'timestamp', type: 'TIMESTAMP', nullable: false, description: 'Tick timestamp' },
        { name: 'symbol', type: 'VARCHAR(10)', nullable: false, description: 'Stock symbol' },
        { name: 'price', type: 'DECIMAL(10,2)', nullable: false, description: 'Trade price' },
        { name: 'size', type: 'INTEGER', nullable: false, description: 'Trade size' },
        { name: 'bid', type: 'DECIMAL(10,2)', nullable: false, description: 'Bid price' },
        { name: 'ask', type: 'DECIMAL(10,2)', nullable: false, description: 'Ask price' },
        { name: 'bid_size', type: 'INTEGER', nullable: false, description: 'Bid size' },
        { name: 'ask_size', type: 'INTEGER', nullable: false, description: 'Ask size' },
      ],
      primaryKey: ['timestamp', 'symbol'],
      indexes: [
        { name: 'idx_ticks_symbol_timestamp', columns: ['symbol', 'timestamp'], unique: false, type: 'BTREE' },
        { name: 'idx_ticks_timestamp', columns: ['timestamp'], unique: false, type: 'BTREE' },
      ],
      partitionKey: 'timestamp',
    },
  },
  {
    name: 'ohlcv_1m',
    type: 'OHLCV',
    tier: 'HOT',
    rowCount: 8923456,
    sizeGB: 45.2,
    lastUpdated: new Date('2025-10-08T08:30:00Z'),
    retentionDays: 30,
    compressionRatio: 5.8,
    schema: {
      columns: [
        { name: 'timestamp', type: 'TIMESTAMP', nullable: false, description: 'Bar timestamp' },
        { name: 'symbol', type: 'VARCHAR(10)', nullable: false, description: 'Stock symbol' },
        { name: 'open', type: 'DECIMAL(10,2)', nullable: false, description: 'Open price' },
        { name: 'high', type: 'DECIMAL(10,2)', nullable: false, description: 'High price' },
        { name: 'low', type: 'DECIMAL(10,2)', nullable: false, description: 'Low price' },
        { name: 'close', type: 'DECIMAL(10,2)', nullable: false, description: 'Close price' },
        { name: 'volume', type: 'BIGINT', nullable: false, description: 'Volume' },
      ],
      primaryKey: ['timestamp', 'symbol'],
      indexes: [
        { name: 'idx_ohlcv_symbol_timestamp', columns: ['symbol', 'timestamp'], unique: false, type: 'BTREE' },
      ],
      partitionKey: 'timestamp',
    },
  },
  {
    name: 'ohlcv_1h',
    type: 'OHLCV',
    tier: 'WARM',
    rowCount: 3456789,
    sizeGB: 18.9,
    lastUpdated: new Date('2025-10-08T08:00:00Z'),
    retentionDays: 365,
    compressionRatio: 6.2,
    schema: {
      columns: [
        { name: 'timestamp', type: 'TIMESTAMP', nullable: false, description: 'Bar timestamp' },
        { name: 'symbol', type: 'VARCHAR(10)', nullable: false, description: 'Stock symbol' },
        { name: 'open', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'high', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'low', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'close', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'volume', type: 'BIGINT', nullable: false },
      ],
      primaryKey: ['timestamp', 'symbol'],
      indexes: [
        { name: 'idx_ohlcv_1h_symbol', columns: ['symbol'], unique: false, type: 'BTREE' },
      ],
      partitionKey: 'timestamp',
    },
  },
  {
    name: 'ohlcv_1d',
    type: 'OHLCV',
    tier: 'COLD',
    rowCount: 1234567,
    sizeGB: 6.8,
    lastUpdated: new Date('2025-10-08T00:00:00Z'),
    retentionDays: 7300,
    compressionRatio: 8.5,
    schema: {
      columns: [
        { name: 'timestamp', type: 'DATE', nullable: false, description: 'Bar date' },
        { name: 'symbol', type: 'VARCHAR(10)', nullable: false, description: 'Stock symbol' },
        { name: 'open', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'high', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'low', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'close', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'volume', type: 'BIGINT', nullable: false },
        { name: 'adj_close', type: 'DECIMAL(10,2)', nullable: true, description: 'Adjusted close price' },
      ],
      primaryKey: ['timestamp', 'symbol'],
      indexes: [
        { name: 'idx_ohlcv_1d_symbol', columns: ['symbol'], unique: false, type: 'BTREE' },
      ],
    },
  },
  {
    name: 'orders',
    type: 'ORDERS',
    tier: 'HOT',
    rowCount: 234567,
    sizeGB: 12.3,
    lastUpdated: new Date('2025-10-08T08:30:15Z'),
    retentionDays: 90,
    compressionRatio: 3.2,
    schema: {
      columns: [
        { name: 'id', type: 'UUID', nullable: false, description: 'Order ID' },
        { name: 'symbol', type: 'VARCHAR(10)', nullable: false },
        { name: 'side', type: 'VARCHAR(10)', nullable: false, description: 'BUY or SELL' },
        { name: 'type', type: 'VARCHAR(20)', nullable: false, description: 'Order type' },
        { name: 'quantity', type: 'INTEGER', nullable: false },
        { name: 'price', type: 'DECIMAL(10,2)', nullable: true },
        { name: 'stop_price', type: 'DECIMAL(10,2)', nullable: true },
        { name: 'status', type: 'VARCHAR(20)', nullable: false },
        { name: 'time_in_force', type: 'VARCHAR(10)', nullable: false },
        { name: 'filled_quantity', type: 'INTEGER', nullable: false, defaultValue: 0 },
        { name: 'avg_fill_price', type: 'DECIMAL(10,2)', nullable: true },
        { name: 'created_at', type: 'TIMESTAMP', nullable: false },
        { name: 'updated_at', type: 'TIMESTAMP', nullable: false },
      ],
      primaryKey: ['id'],
      indexes: [
        { name: 'idx_orders_symbol', columns: ['symbol'], unique: false, type: 'BTREE' },
        { name: 'idx_orders_status', columns: ['status'], unique: false, type: 'BTREE' },
        { name: 'idx_orders_created', columns: ['created_at'], unique: false, type: 'BTREE' },
      ],
    },
  },
  {
    name: 'fills',
    type: 'FILLS',
    tier: 'HOT',
    rowCount: 456789,
    sizeGB: 23.4,
    lastUpdated: new Date('2025-10-08T08:30:20Z'),
    retentionDays: 90,
    compressionRatio: 3.5,
    schema: {
      columns: [
        { name: 'id', type: 'UUID', nullable: false },
        { name: 'order_id', type: 'UUID', nullable: false },
        { name: 'symbol', type: 'VARCHAR(10)', nullable: false },
        { name: 'side', type: 'VARCHAR(10)', nullable: false },
        { name: 'quantity', type: 'INTEGER', nullable: false },
        { name: 'price', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'commission', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'timestamp', type: 'TIMESTAMP', nullable: false },
      ],
      primaryKey: ['id'],
      indexes: [
        { name: 'idx_fills_order_id', columns: ['order_id'], unique: false, type: 'BTREE' },
        { name: 'idx_fills_symbol', columns: ['symbol'], unique: false, type: 'BTREE' },
      ],
    },
  },
  {
    name: 'positions',
    type: 'POSITIONS',
    tier: 'HOT',
    rowCount: 1234,
    sizeGB: 0.05,
    lastUpdated: new Date('2025-10-08T08:30:25Z'),
    retentionDays: 365,
    compressionRatio: 2.1,
    schema: {
      columns: [
        { name: 'id', type: 'UUID', nullable: false },
        { name: 'symbol', type: 'VARCHAR(10)', nullable: false },
        { name: 'side', type: 'VARCHAR(10)', nullable: false },
        { name: 'quantity', type: 'INTEGER', nullable: false },
        { name: 'avg_entry_price', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'current_price', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'unrealized_pnl', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'unrealized_pnl_percent', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'market_value', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'cost_basis', type: 'DECIMAL(10,2)', nullable: false },
        { name: 'opened_at', type: 'TIMESTAMP', nullable: false },
      ],
      primaryKey: ['id'],
      indexes: [
        { name: 'idx_positions_symbol', columns: ['symbol'], unique: true, type: 'BTREE' },
      ],
    },
  },
  {
    name: 'strategies',
    type: 'STRATEGIES',
    tier: 'WARM',
    rowCount: 89,
    sizeGB: 0.002,
    lastUpdated: new Date('2025-10-08T07:00:00Z'),
    retentionDays: 365,
    compressionRatio: 1.5,
    schema: {
      columns: [
        { name: 'id', type: 'UUID', nullable: false },
        { name: 'name', type: 'VARCHAR(100)', nullable: false },
        { name: 'description', type: 'TEXT', nullable: true },
        { name: 'type', type: 'VARCHAR(50)', nullable: false },
        { name: 'status', type: 'VARCHAR(20)', nullable: false },
        { name: 'parameters', type: 'JSONB', nullable: false },
        { name: 'performance', type: 'JSONB', nullable: false },
        { name: 'created_at', type: 'TIMESTAMP', nullable: false },
        { name: 'updated_at', type: 'TIMESTAMP', nullable: false },
      ],
      primaryKey: ['id'],
      indexes: [
        { name: 'idx_strategies_status', columns: ['status'], unique: false, type: 'BTREE' },
        { name: 'idx_strategies_type', columns: ['type'], unique: false, type: 'BTREE' },
      ],
    },
  },
  {
    name: 'backtests',
    type: 'BACKTESTS',
    tier: 'WARM',
    rowCount: 456,
    sizeGB: 8.9,
    lastUpdated: new Date('2025-10-08T08:00:00Z'),
    retentionDays: 365,
    compressionRatio: 4.8,
    schema: {
      columns: [
        { name: 'id', type: 'UUID', nullable: false },
        { name: 'strategy_id', type: 'UUID', nullable: false },
        { name: 'status', type: 'VARCHAR(20)', nullable: false },
        { name: 'start_date', type: 'DATE', nullable: false },
        { name: 'end_date', type: 'DATE', nullable: false },
        { name: 'initial_capital', type: 'DECIMAL(15,2)', nullable: false },
        { name: 'final_capital', type: 'DECIMAL(15,2)', nullable: false },
        { name: 'parameters', type: 'JSONB', nullable: false },
        { name: 'results', type: 'JSONB', nullable: true },
        { name: 'created_at', type: 'TIMESTAMP', nullable: false },
        { name: 'completed_at', type: 'TIMESTAMP', nullable: true },
      ],
      primaryKey: ['id'],
      indexes: [
        { name: 'idx_backtests_strategy_id', columns: ['strategy_id'], unique: false, type: 'BTREE' },
        { name: 'idx_backtests_status', columns: ['status'], unique: false, type: 'BTREE' },
      ],
    },
  },
];

export interface TierOverview {
  name: string;
  tier: 'hot' | 'warm' | 'cold';
  technology: string;
  description: string;
  sizeGB: number;
  rowCount: number;
  retention: string;
  tables: Array<{ name: string; rows: number; sizeGB: number }>;
  avgQueryTime: string;
  ingestionRate: number;
}

export interface DatabaseOverview {
  tiers: TierOverview[];
  totalSize: number;
  totalRows: number;
  avgIngestionRate: number;
}

export const mockDatabaseOverview: DatabaseOverview = {
  tiers: [
    {
      name: 'Hot Data',
      tier: 'hot',
      technology: 'QuestDB',
      description: 'Real-time data, sub-millisecond queries',
      sizeGB: 315.5,
      rowCount: 125000000,
      retention: '72 hours',
      tables: [
        { name: 'ticks', rows: 85000000, sizeGB: 234.5 },
        { name: 'ohlcv_1m', rows: 25000000, sizeGB: 45.2 },
        { name: 'order_book_snapshots', rows: 15000000, sizeGB: 35.8 },
      ],
      avgQueryTime: '2.3ms',
      ingestionRate: 15000,
    },
    {
      name: 'Warm Data',
      tier: 'warm',
      technology: 'ClickHouse',
      description: 'Recent data, fast analytical queries',
      sizeGB: 380.7,
      rowCount: 890000000,
      retention: '90 days',
      tables: [
        { name: 'ticks', rows: 520000000, sizeGB: 220.4 },
        { name: 'ohlcv_1m', rows: 180000000, sizeGB: 85.3 },
        { name: 'orders', rows: 120000000, sizeGB: 45.8 },
        { name: 'fills', rows: 70000000, sizeGB: 29.2 },
      ],
      avgQueryTime: '45ms',
      ingestionRate: 5000,
    },
    {
      name: 'Cold Data',
      tier: 'cold',
      technology: 'Delta Lake (S3)',
      description: 'Historical data, archived',
      sizeGB: 2500.0,
      rowCount: 5200000000,
      retention: 'Forever',
      tables: [
        { name: 'ticks_historical', rows: 3800000000, sizeGB: 1800.0 },
        { name: 'ohlcv_daily', rows: 850000000, sizeGB: 420.0 },
        { name: 'trades_historical', rows: 550000000, sizeGB: 280.0 },
      ],
      avgQueryTime: '5.2s',
      ingestionRate: 0,
    },
  ],
  totalSize: 3196.2,
  totalRows: 6215000000,
  avgIngestionRate: 20000,
};

export const mockTierMetrics: TierMetrics[] = [
  {
    tier: 'HOT',
    totalSizeGB: 315.5,
    tableCount: 5,
    totalRows: 55510000,
    avgCompressionRatio: 3.8,
    readQPS: 8234,
    writeQPS: 1245,
    avgLatencyMs: 2.3,
  },
  {
    tier: 'WARM',
    totalSizeGB: 27.9,
    tableCount: 3,
    totalRows: 3456890,
    avgCompressionRatio: 5.5,
    readQPS: 456,
    writeQPS: 23,
    avgLatencyMs: 12.7,
  },
  {
    tier: 'COLD',
    totalSizeGB: 6.8,
    tableCount: 1,
    totalRows: 1234567,
    avgCompressionRatio: 8.5,
    readQPS: 12,
    writeQPS: 1,
    avgLatencyMs: 145.2,
  },
];

export const mockPositions: Position[] = [
  {
    id: 'pos-001',
    symbol: 'AAPL',
    side: 'LONG',
    quantity: 150,
    avgEntryPrice: 182.50,
    currentPrice: 185.42,
    unrealizedPnL: 438.00,
    unrealizedPnLPercent: 1.60,
    marketValue: 27813.00,
    costBasis: 27375.00,
    openedAt: new Date('2025-10-05T09:30:00Z'),
  },
  {
    id: 'pos-002',
    symbol: 'NVDA',
    side: 'LONG',
    quantity: 75,
    avgEntryPrice: 487.20,
    currentPrice: 495.22,
    unrealizedPnL: 601.50,
    unrealizedPnLPercent: 1.65,
    marketValue: 37141.50,
    costBasis: 36540.00,
    openedAt: new Date('2025-10-06T10:15:00Z'),
  },
  {
    id: 'pos-003',
    symbol: 'META',
    side: 'LONG',
    quantity: 100,
    avgEntryPrice: 308.90,
    currentPrice: 312.45,
    unrealizedPnL: 355.00,
    unrealizedPnLPercent: 1.15,
    marketValue: 31245.00,
    costBasis: 30890.00,
    openedAt: new Date('2025-10-07T11:20:00Z'),
  },
  {
    id: 'pos-004',
    symbol: 'AMD',
    side: 'LONG',
    quantity: 200,
    avgEntryPrice: 120.34,
    currentPrice: 118.56,
    unrealizedPnL: -356.00,
    unrealizedPnLPercent: -1.48,
    marketValue: 23712.00,
    costBasis: 24068.00,
    openedAt: new Date('2025-10-07T14:45:00Z'),
  },
  {
    id: 'pos-005',
    symbol: 'GOOGL',
    side: 'LONG',
    quantity: 120,
    avgEntryPrice: 138.20,
    currentPrice: 139.47,
    unrealizedPnL: 152.40,
    unrealizedPnLPercent: 0.92,
    marketValue: 16736.40,
    costBasis: 16584.00,
    openedAt: new Date('2025-10-08T09:00:00Z'),
  },
];

export const mockAccount: Account = {
  accountId: 'ACC-LIVE-001',
  accountType: 'LIVE',
  equity: 287456.78,
  cash: 150000.00,
  buyingPower: 300000.00,
  portfolioValue: 287456.78,
  dayPnL: 2345.67,
  dayPnLPercent: 0.82,
  totalPnL: 87456.78,
  totalPnLPercent: 43.73,
};

export const mockPortfolioMetrics: PortfolioMetrics = {
  totalValue: 287456.78,
  cash: 150000.00,
  positionsValue: 137456.78,
  dayPnL: 2345.67,
  dayPnLPercent: 0.82,
  totalReturn: 87456.78,
  totalReturnPercent: 43.73,
  winRate: 58.32,
  sharpeRatio: 2.45,
  maxDrawdown: -12456.34,
};

/**
 * Sample query results for table views
 */
export function generateMockTicksData(limit: number = 100): any[] {
  const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'AMD'];
  const exchanges = ['NYSE', 'NASDAQ', 'BATS', 'IEX'];
  const sides = ['buy', 'sell'];

  const data = [];
  const now = Date.now();

  for (let i = 0; i < limit; i++) {
    const symbol = symbols[Math.floor(Math.random() * symbols.length)];
    const basePrice = 100 + Math.random() * 400;
    const price = basePrice + (Math.random() - 0.5) * 5;

    data.push({
      symbol,
      timestamp: new Date(now - i * 1000).toISOString(),
      price: price.toFixed(2),
      size: Math.floor(Math.random() * 1000) + 1,
      bid: (price - 0.01 - Math.random() * 0.05).toFixed(2),
      ask: (price + 0.01 + Math.random() * 0.05).toFixed(2),
      bid_size: Math.floor(Math.random() * 500) + 1,
      ask_size: Math.floor(Math.random() * 500) + 1,
      exchange: exchanges[Math.floor(Math.random() * exchanges.length)],
      side: sides[Math.floor(Math.random() * sides.length)],
    });
  }

  return data;
}

export function generateMockOHLCVData(limit: number = 100): any[] {
  const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'];
  const data = [];
  const now = Date.now();

  for (let i = 0; i < limit; i++) {
    const symbol = symbols[Math.floor(Math.random() * symbols.length)];
    const basePrice = 100 + Math.random() * 400;
    const open = basePrice;
    const close = basePrice + (Math.random() - 0.5) * 10;
    const high = Math.max(open, close) + Math.random() * 3;
    const low = Math.min(open, close) - Math.random() * 3;

    data.push({
      symbol,
      timestamp: new Date(now - i * 60000).toISOString(),
      open: open.toFixed(2),
      high: high.toFixed(2),
      low: low.toFixed(2),
      close: close.toFixed(2),
      volume: Math.floor(Math.random() * 10000000) + 100000,
    });
  }

  return data;
}
