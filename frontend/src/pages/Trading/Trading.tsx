/**
 * Trading Page - Order entry, chart, and position management
 */

import { useEffect } from 'react';
import { SymbolSearchBar } from './components/SymbolSearchBar';
import { OrderTicket } from './components/OrderTicket';
import { TradingChart } from './components/TradingChart';
import { TradingTabs } from './components/TradingTabs';
import { useTradingStore } from '../../store/useTradingStore';

export function Trading() {
  const {
    selectedSymbol,
    currentPrice,
    chartData,
    loadPositions,
    loadOrders,
    loadFills,
    loadTradeLog,
  } = useTradingStore();

  useEffect(() => {
    // Load all trading data on mount
    loadPositions();
    loadOrders();
    loadFills();
    loadTradeLog();
  }, [loadPositions, loadOrders, loadFills, loadTradeLog]);

  return (
    <div className="flex flex-col h-full">
      {/* Top Bar - Symbol Search */}
      <SymbolSearchBar />

      {/* Main Trading Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Order Ticket */}
        <OrderTicket symbol={selectedSymbol || 'ABCD'} currentPrice={currentPrice} />

        {/* Main Panel - Chart */}
        <TradingChart symbol={selectedSymbol || 'ABCD'} data={chartData} />
      </div>

      {/* Bottom Panel - Tabs (Positions, Orders, Fills, Log) */}
      <TradingTabs />
    </div>
  );
}
