/**
 * Mock data for Alerts & Notifications
 */

export interface Alert {
  id: string;
  symbol: string;
  type: 'price' | 'volume' | 'indicator' | 'news' | 'custom';
  condition: 'above' | 'below' | 'crosses' | 'equals' | 'contains';
  metric: string; // 'price', 'volume', 'RSI', 'MACD', etc.
  threshold: number | string;
  currentValue: number | string;
  status: 'active' | 'triggered' | 'expired' | 'disabled';
  createdAt: string;
  triggeredAt?: string;
  expiresAt?: string;
  frequency: 'once' | 'repeating';
  notification: {
    email: boolean;
    push: boolean;
    sms: boolean;
    sound: boolean;
  };
  message?: string;
}

export interface AlertHistory {
  id: string;
  alertId: string;
  symbol: string;
  type: string;
  message: string;
  triggeredAt: string;
  acknowledged: boolean;
}

export const mockAlerts: Alert[] = [
  {
    id: 'alert-001',
    symbol: 'NVAX',
    type: 'price',
    condition: 'above',
    metric: 'price',
    threshold: 50.0,
    currentValue: 49.10,
    status: 'active',
    createdAt: '2025-10-07T10:00:00Z',
    expiresAt: '2025-10-14T10:00:00Z',
    frequency: 'once',
    notification: {
      email: true,
      push: true,
      sms: false,
      sound: true,
    },
    message: 'NVAX has broken above $50',
  },
  {
    id: 'alert-002',
    symbol: 'SAVA',
    type: 'price',
    condition: 'below',
    metric: 'price',
    threshold: 12.0,
    currentValue: 12.35,
    status: 'active',
    createdAt: '2025-10-06T14:30:00Z',
    frequency: 'repeating',
    notification: {
      email: true,
      push: true,
      sms: false,
      sound: false,
    },
    message: 'SAVA has dropped below $12',
  },
  {
    id: 'alert-003',
    symbol: 'EFGH',
    type: 'indicator',
    condition: 'above',
    metric: 'RSI',
    threshold: 70,
    currentValue: 65.2,
    status: 'active',
    createdAt: '2025-10-05T09:15:00Z',
    frequency: 'once',
    notification: {
      email: false,
      push: true,
      sms: false,
      sound: true,
    },
    message: 'EFGH RSI is overbought (>70)',
  },
  {
    id: 'alert-004',
    symbol: 'MNOP',
    type: 'volume',
    condition: 'above',
    metric: 'volume',
    threshold: 1000000,
    currentValue: 850000,
    status: 'active',
    createdAt: '2025-10-04T11:20:00Z',
    frequency: 'repeating',
    notification: {
      email: true,
      push: true,
      sms: true,
      sound: true,
    },
    message: 'MNOP volume spike detected (>1M)',
  },
  {
    id: 'alert-005',
    symbol: 'QRST',
    type: 'price',
    condition: 'above',
    metric: 'price',
    threshold: 25.0,
    currentValue: 26.5,
    status: 'triggered',
    createdAt: '2025-10-01T08:00:00Z',
    triggeredAt: '2025-10-01T14:30:00Z',
    frequency: 'once',
    notification: {
      email: true,
      push: true,
      sms: false,
      sound: true,
    },
    message: 'QRST has broken above $25',
  },
  {
    id: 'alert-006',
    symbol: 'UVWX',
    type: 'indicator',
    condition: 'below',
    metric: 'RSI',
    threshold: 30,
    currentValue: 28.5,
    status: 'triggered',
    createdAt: '2025-09-28T10:00:00Z',
    triggeredAt: '2025-09-29T15:45:00Z',
    frequency: 'once',
    notification: {
      email: true,
      push: true,
      sms: false,
      sound: true,
    },
    message: 'UVWX RSI is oversold (<30)',
  },
  {
    id: 'alert-007',
    symbol: 'ABCD',
    type: 'news',
    condition: 'contains',
    metric: 'news',
    threshold: 'FDA approval',
    currentValue: '',
    status: 'active',
    createdAt: '2025-10-05T12:00:00Z',
    frequency: 'repeating',
    notification: {
      email: true,
      push: true,
      sms: true,
      sound: true,
    },
    message: 'FDA approval news detected for ABCD',
  },
  {
    id: 'alert-008',
    symbol: 'XYZ',
    type: 'price',
    condition: 'below',
    metric: 'price',
    threshold: 15.0,
    currentValue: 16.2,
    status: 'disabled',
    createdAt: '2025-09-25T09:00:00Z',
    frequency: 'once',
    notification: {
      email: false,
      push: false,
      sms: false,
      sound: false,
    },
    message: 'XYZ has dropped below $15',
  },
];

export const mockAlertHistory: AlertHistory[] = [
  {
    id: 'history-001',
    alertId: 'alert-005',
    symbol: 'QRST',
    type: 'Price Alert',
    message: 'QRST has broken above $25.00 (current: $26.50)',
    triggeredAt: '2025-10-01T14:30:00Z',
    acknowledged: true,
  },
  {
    id: 'history-002',
    alertId: 'alert-006',
    symbol: 'UVWX',
    type: 'Indicator Alert',
    message: 'UVWX RSI is oversold at 28.5 (<30)',
    triggeredAt: '2025-09-29T15:45:00Z',
    acknowledged: true,
  },
  {
    id: 'history-003',
    alertId: 'alert-004',
    symbol: 'MNOP',
    type: 'Volume Alert',
    message: 'MNOP volume spike: 1.2M shares (threshold: 1M)',
    triggeredAt: '2025-10-04T13:20:00Z',
    acknowledged: false,
  },
  {
    id: 'history-004',
    alertId: 'alert-007',
    symbol: 'ABCD',
    type: 'News Alert',
    message: 'FDA approval announcement for ABCD',
    triggeredAt: '2025-10-06T16:00:00Z',
    acknowledged: false,
  },
  {
    id: 'history-005',
    alertId: 'alert-001',
    symbol: 'NVAX',
    type: 'Price Alert',
    message: 'NVAX testing resistance at $49.50 (threshold: $50.00)',
    triggeredAt: '2025-10-07T11:15:00Z',
    acknowledged: false,
  },
];

export interface AlertStats {
  totalAlerts: number;
  activeAlerts: number;
  triggeredToday: number;
  pendingAcknowledgement: number;
  avgResponseTime: number; // minutes
  mostTriggeredType: string;
  successRate: number; // percentage
}

export const mockAlertStats: AlertStats = {
  totalAlerts: 45,
  activeAlerts: 12,
  triggeredToday: 3,
  pendingAcknowledgement: 2,
  avgResponseTime: 8.5,
  mostTriggeredType: 'Price',
  successRate: 73.2,
};
