/**
 * Notification Panel - Display recent alert notifications
 */

import { Bell, X, Clock, ExternalLink, CheckCircle } from 'lucide-react';

export interface Notification {
  id: string;
  alertId: string;
  alertName: string;
  symbol: string;
  message: string;
  details: string;
  timestamp: string;
  priority: 'low' | 'medium' | 'high';
  isRead: boolean;
}

interface NotificationPanelProps {
  notifications: Notification[];
  onDismiss: (id: string) => void;
  onSnooze: (id: string, minutes: number) => void;
  onViewStock: (symbol: string) => void;
}

export function NotificationPanel({
  notifications,
  onDismiss,
  onSnooze,
  onViewStock,
}: NotificationPanelProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'border-red-500 bg-red-900/20';
      case 'medium':
        return 'border-yellow-500 bg-yellow-900/20';
      case 'low':
        return 'border-blue-500 bg-blue-900/20';
      default:
        return 'border-gray-700 bg-dark-card';
    }
  };

  const getTimeAgo = (timestamp: string) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  if (notifications.length === 0) {
    return (
      <div className="bg-dark-card border border-dark-border rounded-lg p-8 text-center">
        <CheckCircle className="w-12 h-12 text-gray-600 mx-auto mb-3" />
        <p className="text-gray-400">No recent notifications</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`border rounded-lg p-4 ${getPriorityColor(
            notification.priority
          )}`}
        >
          <div className="flex items-start gap-3">
            <Bell
              className={`w-5 h-5 mt-0.5 ${
                notification.priority === 'high'
                  ? 'text-red-400'
                  : notification.priority === 'medium'
                  ? 'text-yellow-400'
                  : 'text-blue-400'
              }`}
            />

            <div className="flex-1">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <div className="font-semibold text-white">
                    {notification.symbol}
                  </div>
                  <div className="text-sm text-gray-400">
                    {notification.alertName}
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  {getTimeAgo(notification.timestamp)}
                </div>
              </div>

              <div className="text-white mb-2">{notification.message}</div>
              <div className="text-sm text-gray-400 mb-3">
                {notification.details}
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => onViewStock(notification.symbol)}
                  className="px-3 py-1.5 bg-green-600 hover:bg-green-700 rounded text-sm flex items-center gap-2 transition"
                >
                  <ExternalLink className="w-4 h-4" />
                  View Stock
                </button>
                <button
                  onClick={() => onSnooze(notification.id, 15)}
                  className="px-3 py-1.5 bg-dark-border hover:bg-dark-border-hover rounded text-sm flex items-center gap-2 transition"
                >
                  <Clock className="w-4 h-4" />
                  Snooze 15m
                </button>
                <button
                  onClick={() => onDismiss(notification.id)}
                  className="px-3 py-1.5 bg-dark-border hover:bg-dark-border-hover rounded text-sm flex items-center gap-2 transition"
                >
                  <X className="w-4 h-4" />
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
