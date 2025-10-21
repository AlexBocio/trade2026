/**
 * WebSocket Simulator - Simulates real-time market data updates
 */

import { useTradingStore } from '../store/useTradingStore';
import { useScannerStore } from '../store/useScannerStore';

class WebSocketSimulator {
  private intervals: NodeJS.Timeout[] = [];
  private isRunning = false;

  start() {
    if (this.isRunning) {
      console.log('⚠️  WebSocket simulator already running');
      return;
    }

    console.log('🚀 Starting WebSocket simulation...');
    this.isRunning = true;

    // Simulate price updates every 2 seconds
    this.intervals.push(
      setInterval(() => {
        this.simulatePriceUpdates();
      }, 2000)
    );

    // Simulate account updates every 5 seconds
    this.intervals.push(
      setInterval(() => {
        this.simulateAccountUpdates();
      }, 5000)
    );

    // Simulate scanner updates every 15 seconds
    this.intervals.push(
      setInterval(() => {
        this.simulateScannerUpdates();
      }, 15000)
    );

    console.log('✅ WebSocket simulation started');
  }

  stop() {
    if (!this.isRunning) {
      return;
    }

    console.log('🛑 Stopping WebSocket simulation...');
    this.intervals.forEach(clearInterval);
    this.intervals = [];
    this.isRunning = false;
    console.log('✅ WebSocket simulation stopped');
  }

  private simulatePriceUpdates() {
    const tradingStore = useTradingStore.getState();

    if (!tradingStore.positions || tradingStore.positions.length === 0) {
      return;
    }

    // Simulate small price changes for positions
    tradingStore.positions.forEach((position) => {
      const change = (Math.random() - 0.5) * 0.02; // ±2% change
      const newPrice = position.currentPrice * (1 + change);

      // Update position price
      // Note: You'd need to add this method to the trading store
      // tradingStore.updatePositionPrice(position.symbol, newPrice);
    });
  }

  private simulateAccountUpdates() {
    const tradingStore = useTradingStore.getState();

    if (!tradingStore.account) {
      return;
    }

    // Simulate slight account value changes
    const change = (Math.random() - 0.48) * 100; // Slight bias upward
    const newPortfolioValue = tradingStore.account.portfolioValue + change;
    const newDayPnL = tradingStore.account.dayPnL + change;

    // Update account
    // Note: You'd need to add this method to the trading store
    // tradingStore.updateAccount({
    //   ...tradingStore.account,
    //   portfolioValue: newPortfolioValue,
    //   dayPnL: newDayPnL,
    //   dayPnLPercent: (newDayPnL / tradingStore.account.portfolioValue) * 100,
    // });
  }

  private simulateScannerUpdates() {
    const scannerStore = useScannerStore.getState();

    // Shuffle scanner results slightly
    if (scannerStore.results && scannerStore.results.length > 0) {
      // Add small random price changes to scanner results
      const updated = scannerStore.results.map((result) => ({
        ...result,
        price: result.price * (1 + (Math.random() - 0.5) * 0.01),
        changePercent: result.changePercent + (Math.random() - 0.5) * 0.5,
      }));

      // Note: You'd need to add this method to the scanner store
      // scannerStore.updateResults(updated);
    }
  }

  getStatus(): boolean {
    return this.isRunning;
  }
}

export const wsSimulator = new WebSocketSimulator();

// Auto-start in development mode
if (import.meta.env.DEV) {
  // Start after a short delay to ensure stores are initialized
  setTimeout(() => {
    wsSimulator.start();
  }, 1000);
}
