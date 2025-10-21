/**
 * Mock API service - returns mock data for initial development
 */

import type { ScannerResult, Position, Account, PortfolioMetrics } from '../../types/trading.types';
import type { Strategy, Backtest, StrategyTemplate } from '../../types/strategy.types';
import type { DatabaseTable, TierMetrics } from '../../types/database.types';

import { mockStrategies, mockStrategyTemplates } from '../mock-data/strategy-data';
import { mockBacktests } from '../mock-data/backtest-data';
import {
  mockDatabaseTables,
  mockTierMetrics,
  mockPositions,
  mockAccount,
  mockPortfolioMetrics,
} from '../mock-data/database-data';

/**
 * Simulates network delay
 */
const delay = (ms: number = 300) => new Promise((resolve) => setTimeout(resolve, ms));

export class MockAPI {
  // Scanner endpoints (now handled by useScannerStore directly)
  async getScannerResults(): Promise<ScannerResult[]> {
    await delay();
    return []; // Scanner now uses its own store
  }

  // Strategy endpoints
  async getStrategies(): Promise<Strategy[]> {
    await delay();
    return mockStrategies;
  }

  async getStrategy(id: string): Promise<Strategy | null> {
    await delay();
    return mockStrategies.find((s) => s.id === id) || null;
  }

  async getStrategyTemplates(): Promise<StrategyTemplate[]> {
    await delay();
    return mockStrategyTemplates;
  }

  async createStrategy(strategy: Omit<Strategy, 'id' | 'createdAt' | 'updatedAt'>): Promise<Strategy> {
    await delay();
    const newStrategy: Strategy = {
      ...strategy,
      id: `strat-${Date.now()}`,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    return newStrategy;
  }

  async updateStrategy(id: string, updates: Partial<Strategy>): Promise<Strategy | null> {
    await delay();
    const strategy = mockStrategies.find((s) => s.id === id);
    if (!strategy) return null;
    return { ...strategy, ...updates, updatedAt: new Date() };
  }

  async deleteStrategy(id: string): Promise<boolean> {
    await delay();
    return mockStrategies.some((s) => s.id === id);
  }

  // Backtest endpoints
  async getBacktests(): Promise<Backtest[]> {
    await delay();
    return mockBacktests;
  }

  async getBacktest(id: string): Promise<Backtest | null> {
    await delay();
    return mockBacktests.find((b) => b.id === id) || null;
  }

  async createBacktest(backtest: Omit<Backtest, 'id' | 'createdAt'>): Promise<Backtest> {
    await delay();
    const newBacktest: Backtest = {
      ...backtest,
      id: `bt-${Date.now()}`,
      createdAt: new Date(),
    };
    return newBacktest;
  }

  // Position endpoints
  async getPositions(): Promise<Position[]> {
    await delay();
    return mockPositions;
  }

  async getPosition(id: string): Promise<Position | null> {
    await delay();
    return mockPositions.find((p) => p.id === id) || null;
  }

  // Account endpoints
  async getAccount(): Promise<Account> {
    await delay();
    return mockAccount;
  }

  async getPortfolioMetrics(): Promise<PortfolioMetrics> {
    await delay();
    return mockPortfolioMetrics;
  }

  // Database endpoints
  async getDatabaseTables(): Promise<DatabaseTable[]> {
    await delay();
    return mockDatabaseTables;
  }

  async getDatabaseTable(name: string): Promise<DatabaseTable | null> {
    await delay();
    return mockDatabaseTables.find((t) => t.name === name) || null;
  }

  async getTierMetrics(): Promise<TierMetrics[]> {
    await delay();
    return mockTierMetrics;
  }

  async queryDatabase(sql: string): Promise<unknown> {
    await delay();
    // Return empty result for now
    return {
      columns: ['id', 'symbol', 'price'],
      rows: [],
      rowCount: 0,
      executionTime: 45,
    };
  }
}

export default new MockAPI();
