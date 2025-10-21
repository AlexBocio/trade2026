/**
 * Alerts - Main alerts and notifications page
 */

import { useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Plus, TrendingUp, Activity, Clock, CheckCircle } from 'lucide-react';
import { useAlertsStore } from '../../store/useAlertsStore';
import { AlertCard } from '../../components/alerts/AlertCard';
import { NotificationPanel } from '../../components/alerts/NotificationPanel';

export function Alerts() {
  const navigate = useNavigate();
  const { alerts, history, stats, isLoading, filter, loadAlerts, loadHistory, setFilter, acknowledgeAlert, notifications, loadNotifications, dismissNotification, snoozeNotification } =
    useAlertsStore();

  useEffect(() => {
    loadAlerts();
    loadHistory();
    loadNotifications();

    // Poll for new notifications every 10 seconds
    const interval = setInterval(() => {
      loadNotifications();
    }, 10000);

    return () => clearInterval(interval);
  }, [loadAlerts, loadHistory, loadNotifications]);

  // Filter alerts
  const filteredAlerts = useMemo(() => {
    if (filter === 'all') return alerts;
    return alerts.filter((alert) => alert.status === filter);
  }, [alerts, filter]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading alerts...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Bell className="w-8 h-8 text-green-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">Alerts & Notifications</h1>
            <p className="text-sm text-gray-400">
              Monitor conditions 24/7 • {stats.activeAlerts} active alerts
            </p>
          </div>
        </div>

        <button
          onClick={() => navigate('/alerts/create')}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition"
        >
          <Plus className="w-5 h-5" />
          New Alert
        </button>
      </div>

      {/* Recent Notifications */}
      {notifications.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-white mb-4">Recent Notifications</h2>
          <NotificationPanel
            notifications={notifications}
            onDismiss={dismissNotification}
            onSnooze={snoozeNotification}
            onViewStock={(symbol) => navigate(`/trading?symbol=${symbol}`)}
          />
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-6 gap-4">
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="text-3xl font-bold text-white mb-1">{stats.totalAlerts}</div>
          <div className="text-sm text-gray-400">Total Alerts</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <Activity className="w-5 h-5 text-green-400" />
            <span className="text-3xl font-bold text-green-400">{stats.activeAlerts}</span>
          </div>
          <div className="text-sm text-gray-400">Active</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-5 h-5 text-blue-400" />
            <span className="text-3xl font-bold text-blue-400">{stats.triggeredToday}</span>
          </div>
          <div className="text-sm text-gray-400">Triggered Today</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <Bell className="w-5 h-5 text-yellow-400" />
            <span className="text-3xl font-bold text-yellow-400">{stats.pendingAcknowledgement}</span>
          </div>
          <div className="text-sm text-gray-400">Pending</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <Clock className="w-5 h-5 text-purple-400" />
            <span className="text-3xl font-bold text-purple-400">{stats.avgResponseTime}</span>
          </div>
          <div className="text-sm text-gray-400">Avg Response (min)</div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-1">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <span className="text-3xl font-bold text-green-400">{stats.successRate}%</span>
          </div>
          <div className="text-sm text-gray-400">Success Rate</div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Alerts List */}
        <div className="col-span-2 space-y-4">
          {/* Filter Tabs */}
          <div className="flex gap-2 bg-dark-card border border-dark-border rounded-lg p-2">
            {(['all', 'active', 'triggered', 'expired', 'disabled'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`flex-1 px-4 py-2 rounded font-medium text-sm capitalize transition ${
                  filter === f
                    ? 'bg-green-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-dark-border'
                }`}
              >
                {f}
              </button>
            ))}
          </div>

          {/* Alerts Grid */}
          {filteredAlerts.length === 0 ? (
            <div className="bg-dark-card border border-dark-border rounded-lg p-12 text-center">
              <Bell className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-400 mb-2">No alerts found</h3>
              <p className="text-gray-500 mb-6">
                {filter === 'all'
                  ? 'Create your first alert to get started'
                  : `No ${filter} alerts at the moment`}
              </p>
              <button className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition">
                Create Alert
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {filteredAlerts.map((alert) => (
                <AlertCard key={alert.id} alert={alert} />
              ))}
            </div>
          )}
        </div>

        {/* Alert History Sidebar */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Recent Activity</h2>

          {history.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-sm text-gray-400">No recent activity</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-[800px] overflow-y-auto">
              {history.map((item) => (
                <div
                  key={item.id}
                  className={`p-3 rounded border transition ${
                    item.acknowledged
                      ? 'bg-dark-bg border-dark-border'
                      : 'bg-yellow-900/10 border-yellow-700'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-semibold text-white">{item.symbol}</div>
                    <div className="text-xs text-gray-400">{formatDate(item.triggeredAt)}</div>
                  </div>

                  <div className="text-xs text-gray-400 mb-2">{item.type}</div>

                  <div className="text-sm text-gray-300 mb-3">{item.message}</div>

                  {!item.acknowledged && (
                    <button
                      onClick={() => acknowledgeAlert(item.id)}
                      className="w-full flex items-center justify-center gap-2 px-3 py-1.5 bg-green-600 hover:bg-green-700 rounded text-sm font-medium transition"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Acknowledge
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
