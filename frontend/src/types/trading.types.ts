/**
 * Trading-related TypeScript type definitions
 */

export type OrderSide = 'BUY' | 'SELL';
export type OrderType = 'MARKET' | 'LIMIT' | 'STOP' | 'STOP_LIMIT';
export type OrderStatus = 'PENDING' | 'FILLED' | 'PARTIALLY_FILLED' | 'CANCELLED' | 'REJECTED';
export type PositionSide = 'LONG' | 'SHORT';
export type TimeInForce = 'DAY' | 'GTC' | 'IOC' | 'FOK';

export interface Stock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  sector: string;
}

export interface ScannerResult extends Stock {
  momentumScore: number;
  rsi: number;
  macdSignal: 'BUY' | 'SELL' | 'NEUTRAL';
  volumeRatio: number;
  avgVolume: number;
  fiftyTwoWeekHigh: number;
  fiftyTwoWeekLow: number;
}

export interface Order {
  id: string;
  symbol: string;
  side: OrderSide;
  type: OrderType;
  quantity: number;
  price?: number;
  stopPrice?: number;
  status: OrderStatus;
  timeInForce: TimeInForce;
  filledQuantity: number;
  avgFillPrice?: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Position {
  id: string;
  symbol: string;
  side: PositionSide;
  quantity: number;
  avgEntryPrice: number;
  currentPrice: number;
  unrealizedPnL: number;
  unrealizedPnLPercent: number;
  marketValue: number;
  costBasis: number;
  openedAt: Date;
}

export interface Fill {
  id: string;
  orderId: string;
  symbol: string;
  side: OrderSide;
  quantity: number;
  price: number;
  commission: number;
  timestamp: Date;
}

export interface OHLCV {
  timestamp: Date;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Tick {
  timestamp: Date;
  symbol: string;
  price: number;
  size: number;
  bid: number;
  ask: number;
  bidSize: number;
  askSize: number;
}

export interface Account {
  accountId: string;
  accountType: 'LIVE' | 'PAPER';
  equity: number;
  cash: number;
  buyingPower: number;
  portfolioValue: number;
  dayPnL: number;
  dayPnLPercent: number;
  totalPnL: number;
  totalPnLPercent: number;
}

export interface PortfolioMetrics {
  totalValue: number;
  cash: number;
  positionsValue: number;
  dayPnL: number;
  dayPnLPercent: number;
  totalReturn: number;
  totalReturnPercent: number;
  winRate: number;
  sharpeRatio: number;
  maxDrawdown: number;
}
