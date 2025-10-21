/**
 * Alert Detail - View and manage a specific alert
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Edit,
  Trash2,
  Play,
  Pause,
  Bell,
  TrendingUp,
  CheckCircle,
  Clock,
  Mail,
  Smartphone,
  MessageSquare,
} from 'lucide-react';
import { useAlertsStore } from '../../store/useAlertsStore';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function AlertDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { alerts, toggleAlert, deleteAlert, testAlert } = useAlertsStore();

  const alert = alerts.find((a) => a.id === id);

  const handleToggle = async () => {
    if (!id) return;
    await toggleAlert(id);
  };

  const handleDelete = async () => {
    if (!id || !alert) return;
    if (confirm(`Delete alert "${alert.name}"?`)) {
      await deleteAlert(id);
      navigate('/alerts');
    }
  };

  const handleTest = async () => {
    if (!id) return;
    await testAlert(id);
  };

  if (!alert) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Bell className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-400 mb-2">
            Alert not found
          </h2>
          <button
            onClick={() => navigate('/alerts')}
            className="text-green-400 hover:text-green-300"
          >
            Back to Alerts
          </button>
        </div>
      </div>
    );
  }

  // Mock trigger history data
  const triggerHistory = [
    { date: '2025-10-01', count: 2 },
    { date: '2025-10-02', count: 3 },
    { date: '2025-10-03', count: 1 },
    { date: '2025-10-04', count: 4 },
    { date: '2025-10-05', count: 2 },
    { date: '2025-10-06', count: 3 },
    { date: '2025-10-07', count: 5 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/alerts')}
            className="p-2 hover:bg-dark-border rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white">{alert.name}</h1>
            <p className="text-sm text-gray-400">{alert.description}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleToggle}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 font-semibold transition ${
              alert.status === 'active'
                ? 'bg-yellow-900/30 text-yellow-400 hover:bg-yellow-900/50'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {alert.status === 'active' ? (
              <>
                <Pause className="w-4 h-4" />
                Pause
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Activate
              </>
            )}
          </button>

          <button
            onClick={() => navigate(`/alerts/${id}/edit`)}
            className="px-4 py-2 bg-dark-border hover:bg-dark-border-hover rounded-lg flex items-center gap-2 transition"
          >
            <Edit className="w-4 h-4" />
            Edit
          </button>

          <button
            onClick={handleDelete}
            className="px-4 py-2 bg-red-900/30 hover:bg-red-900/50 text-red-400 rounded-lg flex items-center gap-2 transition"
          >
            <Trash2 className="w-4 h-4" />
            Delete
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-2">
            <Bell className="w-5 h-5 text-green-400" />
            <span className="text-sm text-gray-400">Status</span>
          </div>
          <div className="text-2xl font-bold text-white capitalize">
            {alert.status}
          </div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-5 h-5 text-blue-400" />
            <span className="text-sm text-gray-400">Triggered</span>
          </div>
          <div className="text-2xl font-bold text-white">
            {alert.triggerCount}x
          </div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <span className="text-sm text-gray-400">Win Rate</span>
          </div>
          <div className={`text-2xl font-bold ${
            (alert.winRate || 0) >= 50 ? 'text-green-400' : 'text-red-400'
          }`}>
            {alert.winRate || 0}%
          </div>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-5 h-5 text-purple-400" />
            <span className="text-sm text-gray-400">Last Triggered</span>
          </div>
          <div className="text-sm text-white">
            {alert.lastTriggered
              ? new Date(alert.lastTriggered).toLocaleDateString()
              : 'Never'}
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="col-span-2 space-y-6">
          {/* Conditions */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4">
              Alert Conditions
            </h2>

            <div className="space-y-3">
              {alert.conditions && alert.conditions.length > 0 ? (
                alert.conditions.map((condition, index) => (
                  <div
                    key={index}
                    className="bg-dark-bg border border-dark-border rounded-lg p-4"
                  >
                    <div className="text-sm text-gray-400 mb-2">
                      Condition {index + 1}
                    </div>
                    <div className="text-white font-medium">
                      {condition.description || `${condition.type} ${condition.operator} ${condition.value}`}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-gray-400">No conditions defined</div>
              )}
            </div>

            {alert.conditions && alert.conditions.length > 1 && (
              <div className="mt-4 text-sm text-gray-400">
                <strong>Logic:</strong> ALL conditions must be true (AND logic)
              </div>
            )}
          </div>

          {/* Trigger History Chart */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4">
              Trigger History (Last 7 Days)
            </h2>

            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={triggerHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="date"
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af' }}
                  tickFormatter={(value) =>
                    new Date(value).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                    })
                  }
                />
                <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: '#9ca3af' }}
                />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={{ fill: '#10b981', r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Test Alert */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4">
              Test Alert
            </h2>
            <p className="text-gray-400 mb-4">
              Send a test notification to verify your alert is configured correctly
            </p>
            <button
              onClick={handleTest}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition"
            >
              Send Test Notification
            </button>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Watching */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Watching</h2>
            <div className="text-gray-300">
              {alert.watchlist ? (
                <span className="px-3 py-1.5 bg-green-900/30 text-green-400 rounded-lg inline-block">
                  Watchlist: {alert.watchlist}
                </span>
              ) : (
                <span className="px-3 py-1.5 bg-yellow-900/30 text-yellow-400 rounded-lg inline-block">
                  All small-cap stocks
                </span>
              )}
            </div>
          </div>

          {/* Delivery Methods */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4">
              Delivery Methods
            </h2>

            <div className="space-y-3">
              {alert.notification && alert.notification.email && (
                <div className="flex items-center gap-3 p-3 bg-blue-900/20 border border-blue-700 rounded-lg">
                  <Mail className="w-5 h-5 text-blue-400" />
                  <div>
                    <div className="font-semibold text-white">Email</div>
                    <div className="text-xs text-gray-400">
                      Send to your email
                    </div>
                  </div>
                </div>
              )}

              {alert.notification && alert.notification.push && (
                <div className="flex items-center gap-3 p-3 bg-green-900/20 border border-green-700 rounded-lg">
                  <Smartphone className="w-5 h-5 text-green-400" />
                  <div>
                    <div className="font-semibold text-white">Push</div>
                    <div className="text-xs text-gray-400">
                      In-app notification
                    </div>
                  </div>
                </div>
              )}

              {alert.notification && alert.notification.sms && (
                <div className="flex items-center gap-3 p-3 bg-purple-900/20 border border-purple-700 rounded-lg">
                  <MessageSquare className="w-5 h-5 text-purple-400" />
                  <div>
                    <div className="font-semibold text-white">SMS</div>
                    <div className="text-xs text-gray-400">Text message</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Alert Info */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4">
              Alert Info
            </h2>

            <div className="space-y-3 text-sm">
              <div>
                <div className="text-gray-400 mb-1">Created</div>
                <div className="text-white">
                  {new Date(alert.createdAt).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </div>
              </div>

              <div>
                <div className="text-gray-400 mb-1">Last Modified</div>
                <div className="text-white">
                  {alert.updatedAt
                    ? new Date(alert.updatedAt).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })
                    : 'Never'}
                </div>
              </div>

              <div>
                <div className="text-gray-400 mb-1">Alert ID</div>
                <div className="text-white font-mono text-xs">{alert.id}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
