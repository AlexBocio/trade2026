/**
 * Trading Store - Manages positions, orders, fills, and order submission
 */

import { create } from 'zustand';
import type { Position, Order, Fill, TradeLogEntry, Candle } from '../services/mock-data/trading-data';
import { mockPositions, mockOrders, mockFills, mockTradeLog, generateChartData } from '../services/mock-data/trading-data';

interface OrderRequest {
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  orderType: 'market' | 'limit' | 'stop';
  limitPrice?: number;
  stopPrice?: number;
  stopLoss?: number;
  profitTarget?: number;
  timeInForce: 'DAY' | 'GTC' | 'IOC';
}

interface TradingState {
  selectedSymbol: string | null;
  currentPrice: number;
  positions: Position[];
  orders: Order[];
  fills: Fill[];
  tradeLog: TradeLogEntry[];
  chartData: Candle[];
  isLoading: boolean;

  // Paper trading
  mode: 'paper' | 'live';
  paperBalance: number;
  liveBalance: number;
  paperPositions: Position[];
  paperOrders: Order[];

  // Actions
  setSymbol: (symbol: string, price: number) => void;
  setMode: (mode: 'paper' | 'live') => void;
  loadPositions: () => Promise<void>;
  loadOrders: () => Promise<void>;
  loadFills: () => Promise<void>;
  loadTradeLog: () => Promise<void>;
  loadChartData: (symbol: string, basePrice: number) => void;
  submitOrder: (order: OrderRequest) => Promise<void>;
  closePosition: (positionId: string) => Promise<void>;
  modifyPosition: (positionId: string, updates: Partial<Position>) => Promise<void>;
  cancelOrder: (orderId: string) => Promise<void>;
}

const delay = (ms: number = 500) => new Promise((resolve) => setTimeout(resolve, ms));

export const useTradingStore = create<TradingState>((set, get) => ({
  selectedSymbol: 'ABCD',
  currentPrice: 3.42,
  positions: [],
  orders: [],
  fills: [],
  tradeLog: [],
  chartData: [],
  isLoading: false,

  // Paper trading defaults
  mode: 'paper',
  paperBalance: 100000,
  liveBalance: 50000,
  paperPositions: [],
  paperOrders: [],

  setSymbol: (symbol, price) => {
    set({ selectedSymbol: symbol, currentPrice: price });
    get().loadChartData(symbol, price);
  },

  setMode: (mode) => {
    set({ mode });
    // Reload positions and orders when switching modes
    get().loadPositions();
    get().loadOrders();
  },

  loadPositions: async () => {
    set({ isLoading: true });
    await delay();
    const { mode, paperPositions } = get();
    set({
      positions: mode === 'paper' ? paperPositions : mockPositions,
      isLoading: false
    });
  },

  loadOrders: async () => {
    set({ isLoading: true });
    await delay();
    const { mode, paperOrders } = get();
    set({
      orders: mode === 'paper' ? paperOrders : mockOrders,
      isLoading: false
    });
  },

  loadFills: async () => {
    set({ isLoading: true });
    await delay();
    set({ fills: mockFills, isLoading: false });
  },

  loadTradeLog: async () => {
    set({ isLoading: true });
    await delay();
    set({ tradeLog: mockTradeLog, isLoading: false });
  },

  loadChartData: (symbol, basePrice) => {
    const data = generateChartData(symbol, basePrice);
    set({ chartData: data });
  },

  submitOrder: async (order) => {
    const { mode, currentPrice } = get();
    set({ isLoading: true });
    await delay(800);

    // Create new order
    const fillPrice = order.orderType === 'market' ? currentPrice : (order.limitPrice || currentPrice);
    const newOrder: Order = {
      id: `${mode}-ord-${Date.now()}`,
      symbol: order.symbol,
      side: order.side,
      quantity: order.quantity,
      orderType: order.orderType,
      limitPrice: order.limitPrice,
      stopPrice: order.stopPrice,
      status: mode === 'paper' ? 'filled' : 'pending',
      submittedAt: new Date().toISOString(),
      timeInForce: order.timeInForce,
      filledAt: mode === 'paper' ? new Date().toISOString() : undefined,
      filledPrice: mode === 'paper' ? fillPrice : undefined,
    };

    if (mode === 'paper') {
      // Paper trading - instant fill
      const orderCost = fillPrice * order.quantity;

      set((state) => {
        const updatedBalance = order.side === 'buy'
          ? state.paperBalance - orderCost
          : state.paperBalance + orderCost;

        // Update or create position
        const existingPosition = state.paperPositions.find(p => p.symbol === order.symbol);
        let updatedPositions: Position[];

        if (order.side === 'buy') {
          if (existingPosition) {
            updatedPositions = state.paperPositions.map(p =>
              p.symbol === order.symbol
                ? {
                    ...p,
                    quantity: p.quantity + order.quantity,
                    avgPrice: ((p.avgPrice * p.quantity) + (fillPrice * order.quantity)) / (p.quantity + order.quantity),
                  }
                : p
            );
          } else {
            updatedPositions = [
              ...state.paperPositions,
              {
                id: `paper-pos-${Date.now()}`,
                symbol: order.symbol,
                side: 'long',
                quantity: order.quantity,
                avgPrice: fillPrice,
                currentPrice: fillPrice,
                unrealizedPnL: 0,
                unrealizedPnLPct: 0,
                openedAt: new Date().toISOString(),
              },
            ];
          }
        } else {
          // Sell order - reduce or close position
          updatedPositions = state.paperPositions
            .map(p =>
              p.symbol === order.symbol
                ? { ...p, quantity: p.quantity - order.quantity }
                : p
            )
            .filter(p => p.quantity > 0);
        }

        return {
          paperBalance: updatedBalance,
          paperPositions: updatedPositions,
          paperOrders: [newOrder, ...state.paperOrders],
          positions: updatedPositions,
          orders: [newOrder, ...state.orders],
        };
      });
    } else {
      // Live trading - add to orders
      set((state) => ({
        orders: [newOrder, ...state.orders],
      }));
    }

    // Add to trade log
    const logEntry: TradeLogEntry = {
      id: `log-${Date.now()}`,
      timestamp: new Date().toISOString(),
      symbol: order.symbol,
      action: mode === 'paper' ? 'Paper Order Filled' : 'Order Submitted',
      details: `${order.side.toUpperCase()} ${order.quantity} @ $${fillPrice.toFixed(2)} (${order.orderType}) ${mode === 'paper' ? '[PAPER]' : ''}`,
      status: 'success',
    };

    set((state) => ({
      tradeLog: [logEntry, ...state.tradeLog],
      isLoading: false,
    }));

    console.log(`✅ ${mode === 'paper' ? 'Paper' : 'Live'} order submitted:`, newOrder);
  },

  closePosition: async (positionId) => {
    const position = get().positions.find((p) => p.id === positionId);
    if (!position) return;

    set({ isLoading: true });

    // Submit closing order
    await get().submitOrder({
      symbol: position.symbol,
      side: position.side === 'long' ? 'sell' : 'buy',
      quantity: position.quantity,
      orderType: 'market',
      timeInForce: 'DAY',
    });

    // Remove from positions
    set((state) => ({
      positions: state.positions.filter((p) => p.id !== positionId),
      isLoading: false,
    }));

    // Add to trade log
    const logEntry: TradeLogEntry = {
      id: `log-${Date.now()}`,
      timestamp: new Date().toISOString(),
      symbol: position.symbol,
      action: 'Position Closed',
      details: `Closed ${position.side.toUpperCase()} ${position.quantity} @ $${position.currentPrice.toFixed(2)} (P&L: ${position.unrealizedPnL >= 0 ? '+' : ''}$${position.unrealizedPnL.toFixed(2)})`,
      status: 'success',
    };

    set((state) => ({
      tradeLog: [logEntry, ...state.tradeLog],
    }));
  },

  modifyPosition: async (positionId, updates) => {
    set({ isLoading: true });
    await delay();

    set((state) => ({
      positions: state.positions.map((p) => (p.id === positionId ? { ...p, ...updates } : p)),
      isLoading: false,
    }));

    // Add to trade log
    const logEntry: TradeLogEntry = {
      id: `log-${Date.now()}`,
      timestamp: new Date().toISOString(),
      symbol: get().positions.find((p) => p.id === positionId)?.symbol || '',
      action: 'Position Modified',
      details: `Updated stop/target levels`,
      status: 'info',
    };

    set((state) => ({
      tradeLog: [logEntry, ...state.tradeLog],
    }));
  },

  cancelOrder: async (orderId) => {
    set({ isLoading: true });
    await delay();

    const order = get().orders.find((o) => o.id === orderId);
    if (!order) return;

    // Update order status
    set((state) => ({
      orders: state.orders.map((o) => (o.id === orderId ? { ...o, status: 'cancelled' as const } : o)),
      isLoading: false,
    }));

    // Add to trade log
    const logEntry: TradeLogEntry = {
      id: `log-${Date.now()}`,
      timestamp: new Date().toISOString(),
      symbol: order.symbol,
      action: 'Order Cancelled',
      details: `Cancelled ${order.side.toUpperCase()} ${order.quantity} @ $${order.limitPrice?.toFixed(2) || 'Market'}`,
      status: 'warning',
    };

    set((state) => ({
      tradeLog: [logEntry, ...state.tradeLog],
    }));
  },
}));
