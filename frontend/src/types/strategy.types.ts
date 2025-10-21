/**
 * Strategy-related TypeScript type definitions
 */

export type StrategyStatus = 'LIVE' | 'PAPER' | 'STOPPED' | 'ERROR';
export type StrategyType = 'MOMENTUM' | 'MEAN_REVERSION' | 'BREAKOUT' | 'ARBITRAGE' | 'CUSTOM';
export type BacktestStatus = 'RUNNING' | 'COMPLETED' | 'FAILED' | 'QUEUED';

export interface Strategy {
  id: string;
  name: string;
  description: string;
  type: StrategyType;
  status: StrategyStatus;
  parameters: StrategyParameters;
  performance: StrategyPerformance;
  createdAt: Date;
  updatedAt: Date;
  lastExecutedAt?: Date;
}

export interface StrategyParameters {
  symbols?: string[];
  timeframe: string;
  lookbackPeriod: number;
  entryThreshold: number;
  exitThreshold: number;
  stopLoss?: number;
  takeProfit?: number;
  maxPositionSize: number;
  maxPositions: number;
  riskPerTrade: number;
  [key: string]: string | number | string[] | number[] | boolean | undefined;
}

export interface StrategyPerformance {
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  winRate: number;
  totalPnL: number;
  avgWin: number;
  avgLoss: number;
  profitFactor: number;
  sharpeRatio: number;
  maxDrawdown: number;
  maxDrawdownPercent: number;
  returnPercent: number;
}

export interface Backtest {
  id: string;
  strategyId: string;
  strategyName: string;
  status: BacktestStatus;
  startDate: Date;
  endDate: Date;
  initialCapital: number;
  finalCapital: number;
  parameters: StrategyParameters;
  results?: BacktestResults;
  createdAt: Date;
  completedAt?: Date;
}

export interface BacktestResults {
  performance: StrategyPerformance;
  trades: BacktestTrade[];
  equityCurve: EquityPoint[];
  metrics: BacktestMetrics;
  monthlyReturns: MonthlyReturn[];
}

export interface BacktestTrade {
  id: string;
  symbol: string;
  entryDate: Date;
  exitDate: Date;
  entryPrice: number;
  exitPrice: number;
  quantity: number;
  side: 'LONG' | 'SHORT';
  pnl: number;
  pnlPercent: number;
  holdingPeriod: number; // in days
  commission: number;
}

export interface EquityPoint {
  date: Date;
  equity: number;
  drawdown: number;
  drawdownPercent: number;
}

export interface BacktestMetrics {
  totalReturn: number;
  annualizedReturn: number;
  volatility: number;
  sharpeRatio: number;
  sortinoRatio: number;
  calmarRatio: number;
  maxDrawdown: number;
  maxDrawdownPercent: number;
  winRate: number;
  profitFactor: number;
  avgWin: number;
  avgLoss: number;
  avgTrade: number;
  bestTrade: number;
  worstTrade: number;
  avgHoldingPeriod: number;
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  totalCommissions: number;
}

export interface MonthlyReturn {
  month: string;
  return: number;
  returnPercent: number;
}

export interface StrategyTemplate {
  id: string;
  name: string;
  description: string;
  type: StrategyType;
  defaultParameters: StrategyParameters;
  category: string;
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
}
