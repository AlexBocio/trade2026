/**
 * Mock Trading Data - Positions, Orders, Fills, Symbols
 */

export interface Position {
  id: string;
  symbol: string;
  side: 'long' | 'short';
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  unrealizedPnL: number;
  unrealizedPnLPct: number;
  stopLoss: number;
  profitTarget: number;
  daysHeld: number;
  entryDate: string;
}

export interface Order {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  orderType: 'market' | 'limit' | 'stop';
  limitPrice?: number;
  stopPrice?: number;
  status: 'pending' | 'filled' | 'cancelled' | 'rejected';
  submittedAt: string;
  filledAt?: string;
  timeInForce: 'DAY' | 'GTC' | 'IOC';
}

export interface Fill {
  id: string;
  orderId: string;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  fillPrice: number;
  filledAt: string;
  commission: number;
}

export interface SymbolInfo {
  symbol: string;
  companyName: string;
  price: number;
  change: number;
  changePct: number;
  volume: number;
  avgVolume: number;
  marketCap: number;
  sector: string;
}

export interface TradeLogEntry {
  id: string;
  timestamp: string;
  symbol: string;
  action: string;
  details: string;
  status: 'success' | 'error' | 'warning' | 'info';
}

export interface Candle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// Mock Positions
export const mockPositions: Position[] = [
  {
    id: 'pos-001',
    symbol: 'NVAX',
    side: 'long',
    quantity: 500,
    entryPrice: 45.20,
    currentPrice: 49.10,
    unrealizedPnL: 29.3,
    unrealizedPnLPct: 8.6,
    stopLoss: 42.04,
    profitTarget: 54.24,
    daysHeld: 3,
    entryDate: '2025-10-04',
  },
  {
    id: 'pos-002',
    symbol: 'SAVA',
    side: 'long',
    quantity: 800,
    entryPrice: 12.80,
    currentPrice: 12.35,
    unrealizedPnL: -5.4,
    unrealizedPnLPct: -3.5,
    stopLoss: 11.90,
    profitTarget: 15.36,
    daysHeld: 1,
    entryDate: '2025-10-06',
  },
  {
    id: 'pos-003',
    symbol: 'MNMD',
    side: 'long',
    quantity: 1200,
    entryPrice: 8.45,
    currentPrice: 9.12,
    unrealizedPnL: 12.1,
    unrealizedPnLPct: 7.9,
    stopLoss: 7.85,
    profitTarget: 10.14,
    daysHeld: 5,
    entryDate: '2025-10-02',
  },
  {
    id: 'pos-004',
    symbol: 'OCGN',
    side: 'long',
    quantity: 600,
    entryPrice: 5.20,
    currentPrice: 5.45,
    unrealizedPnL: 2.3,
    unrealizedPnLPct: 4.8,
    stopLoss: 4.83,
    profitTarget: 6.24,
    daysHeld: 2,
    entryDate: '2025-10-05',
  },
];

// Mock Orders
export const mockOrders: Order[] = [
  {
    id: 'ord-001',
    symbol: 'ABCD',
    side: 'buy',
    quantity: 1000,
    orderType: 'limit',
    limitPrice: 3.45,
    status: 'pending',
    submittedAt: '2025-10-07T14:30:00Z',
    timeInForce: 'DAY',
  },
  {
    id: 'ord-002',
    symbol: 'EFGH',
    side: 'buy',
    quantity: 500,
    orderType: 'limit',
    limitPrice: 12.80,
    status: 'pending',
    submittedAt: '2025-10-07T13:15:00Z',
    timeInForce: 'GTC',
  },
  {
    id: 'ord-003',
    symbol: 'MNMD',
    side: 'sell',
    quantity: 1200,
    orderType: 'limit',
    limitPrice: 10.14,
    status: 'pending',
    submittedAt: '2025-10-07T12:00:00Z',
    timeInForce: 'GTC',
  },
  {
    id: 'ord-004',
    symbol: 'NVAX',
    side: 'sell',
    quantity: 500,
    orderType: 'stop',
    stopPrice: 42.04,
    status: 'pending',
    submittedAt: '2025-10-04T10:05:30Z',
    timeInForce: 'GTC',
  },
];

// Mock Fills
export const mockFills: Fill[] = [
  {
    id: 'fill-001',
    orderId: 'ord-101',
    symbol: 'NVAX',
    side: 'buy',
    quantity: 500,
    fillPrice: 45.18,
    filledAt: '2025-10-04T10:05:23Z',
    commission: 1.50,
  },
  {
    id: 'fill-002',
    orderId: 'ord-102',
    symbol: 'SAVA',
    side: 'buy',
    quantity: 800,
    fillPrice: 12.82,
    filledAt: '2025-10-06T09:30:15Z',
    commission: 2.00,
  },
  {
    id: 'fill-003',
    orderId: 'ord-103',
    symbol: 'MNMD',
    side: 'buy',
    quantity: 1200,
    fillPrice: 8.43,
    filledAt: '2025-10-02T14:22:08Z',
    commission: 2.50,
  },
  {
    id: 'fill-004',
    orderId: 'ord-104',
    symbol: 'OCGN',
    side: 'buy',
    quantity: 600,
    fillPrice: 5.22,
    filledAt: '2025-10-05T11:15:45Z',
    commission: 1.25,
  },
];

// Mock Symbol Database (for search)
export const mockSymbolDatabase: SymbolInfo[] = [
  {
    symbol: 'ABCD',
    companyName: 'ABCD Therapeutics Inc.',
    price: 3.42,
    change: 0.08,
    changePct: 2.39,
    volume: 1250000,
    avgVolume: 850000,
    marketCap: 937500,
    sector: 'Biotechnology',
  },
  {
    symbol: 'NVAX',
    companyName: 'Novavax Inc.',
    price: 49.10,
    change: 2.35,
    changePct: 5.03,
    volume: 8500000,
    avgVolume: 5200000,
    marketCap: 33750000,
    sector: 'Biotechnology',
  },
  {
    symbol: 'SAVA',
    companyName: 'Cassava Sciences Inc.',
    price: 12.35,
    change: -0.45,
    changePct: -3.52,
    volume: 2100000,
    avgVolume: 1800000,
    marketCap: 4350000,
    sector: 'Biotechnology',
  },
  {
    symbol: 'MNMD',
    companyName: 'Mind Medicine Inc.',
    price: 9.12,
    change: 0.67,
    changePct: 7.93,
    volume: 1850000,
    avgVolume: 1200000,
    marketCap: 3150000,
    sector: 'Biotechnology',
  },
  {
    symbol: 'OCGN',
    companyName: 'Ocugen Inc.',
    price: 5.45,
    change: 0.25,
    changePct: 4.81,
    volume: 3200000,
    avgVolume: 2500000,
    marketCap: 5100000,
    sector: 'Biotechnology',
  },
  {
    symbol: 'EFGH',
    companyName: 'EFGH Pharma Corp.',
    price: 12.75,
    change: -0.15,
    changePct: -1.16,
    volume: 950000,
    avgVolume: 750000,
    marketCap: 2400000,
    sector: 'Pharmaceuticals',
  },
  {
    symbol: 'IJKL',
    companyName: 'IJKL Biotech Ltd.',
    price: 6.80,
    change: 0.40,
    changePct: 6.25,
    volume: 1100000,
    avgVolume: 800000,
    marketCap: 2062500,
    sector: 'Biotechnology',
  },
  {
    symbol: 'MNOP',
    companyName: 'MNOP Genetics Inc.',
    price: 15.20,
    change: -0.80,
    changePct: -5.00,
    volume: 1650000,
    avgVolume: 1400000,
    marketCap: 6675000,
    sector: 'Biotechnology',
  },
];

// Mock Trade Log
export const mockTradeLog: TradeLogEntry[] = [
  {
    id: 'log-001',
    timestamp: '2025-10-07T14:30:15Z',
    symbol: 'ABCD',
    action: 'Order Submitted',
    details: 'BUY 1000 @ $3.45 (Limit)',
    status: 'success',
  },
  {
    id: 'log-002',
    timestamp: '2025-10-07T13:15:08Z',
    symbol: 'EFGH',
    action: 'Order Submitted',
    details: 'BUY 500 @ $12.80 (Limit)',
    status: 'success',
  },
  {
    id: 'log-003',
    timestamp: '2025-10-06T09:30:20Z',
    symbol: 'SAVA',
    action: 'Order Filled',
    details: 'BUY 800 @ $12.82 (Market)',
    status: 'success',
  },
  {
    id: 'log-004',
    timestamp: '2025-10-05T11:15:50Z',
    symbol: 'OCGN',
    action: 'Order Filled',
    details: 'BUY 600 @ $5.22 (Limit)',
    status: 'success',
  },
  {
    id: 'log-005',
    timestamp: '2025-10-04T10:05:30Z',
    symbol: 'NVAX',
    action: 'Order Filled',
    details: 'BUY 500 @ $45.18 (Limit)',
    status: 'success',
  },
];

// Generate chart data
export function generateChartData(symbol: string, basePrice: number, days: number = 90): Candle[] {
  const data: Candle[] = [];
  let price = basePrice;
  const now = new Date();

  for (let i = days; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);

    const open = price;
    const volatility = 0.03;
    const change = (Math.random() - 0.48) * price * volatility;
    const close = open + change;
    const high = Math.max(open, close) * (1 + Math.random() * 0.02);
    const low = Math.min(open, close) * (1 - Math.random() * 0.02);
    const volume = Math.floor(500000 + Math.random() * 2000000);

    data.push({
      time: date.toISOString().split('T')[0],
      open: Number(open.toFixed(2)),
      high: Number(high.toFixed(2)),
      low: Number(low.toFixed(2)),
      close: Number(close.toFixed(2)),
      volume,
    });

    price = close;
  }

  return data;
}
