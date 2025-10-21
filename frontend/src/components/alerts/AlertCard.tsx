/**
 * Alert Card - Displays individual alert
 */

import {
  Bell,
  TrendingUp,
  TrendingDown,
  Activity,
  Newspaper,
  AlertCircle,
  Check,
  X,
  Mail,
  Smartphone,
  MessageSquare,
  Volume2,
  Play,
  Pause,
  Trash2,
} from 'lucide-react';
import type { Alert } from '../../services/mock-data/alerts-data';
import { useAlertsStore } from '../../store/useAlertsStore';
import { useNavigate } from 'react-router-dom';

interface AlertCardProps {
  alert: Alert;
}

export function AlertCard({ alert }: AlertCardProps) {
  const navigate = useNavigate();
  const { toggleAlert, deleteAlert, testAlert } = useAlertsStore();

  const getTypeIcon = () => {
    switch (alert.type) {
      case 'price':
        return alert.condition === 'above' ? TrendingUp : TrendingDown;
      case 'volume':
        return Activity;
      case 'indicator':
        return Activity;
      case 'news':
        return Newspaper;
      default:
        return Bell;
    }
  };

  const getStatusColor = () => {
    switch (alert.status) {
      case 'active':
        return 'bg-green-900/30 text-green-400 border-green-700';
      case 'triggered':
        return 'bg-blue-900/30 text-blue-400 border-blue-700';
      case 'expired':
        return 'bg-gray-900/30 text-gray-400 border-gray-700';
      case 'disabled':
        return 'bg-gray-900/30 text-gray-400 border-gray-700';
    }
  };

  const getTypeColor = () => {
    switch (alert.type) {
      case 'price':
        return 'text-blue-400';
      case 'volume':
        return 'text-purple-400';
      case 'indicator':
        return 'text-yellow-400';
      case 'news':
        return 'text-green-400';
      default:
        return 'text-gray-400';
    }
  };

  const TypeIcon = getTypeIcon();

  const handleToggle = async () => {
    await toggleAlert(alert.id);
  };

  const handleDelete = async () => {
    if (confirm(`Delete alert for ${alert.symbol}?`)) {
      await deleteAlert(alert.id);
    }
  };

  const handleTest = async () => {
    await testAlert(alert.id);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const isClose = () => {
    if (typeof alert.threshold !== 'number' || typeof alert.currentValue !== 'number') {
      return false;
    }
    const diff = Math.abs(alert.currentValue - alert.threshold);
    const percentage = (diff / alert.threshold) * 100;
    return percentage < 5; // Within 5%
  };

  return (
    <div
      onClick={() => navigate(`/alerts/${alert.id}`)}
      className={`bg-dark-card border rounded-lg p-4 transition cursor-pointer ${
        alert.status === 'active' && isClose()
          ? 'border-yellow-700 bg-yellow-900/10'
          : 'border-dark-border hover:border-dark-border-hover'
      }`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg bg-dark-bg ${getTypeColor()}`}>
            <TypeIcon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">{alert.symbol}</h3>
            <p className="text-sm text-gray-400 capitalize">
              {alert.type} • {alert.metric}
            </p>
          </div>
        </div>

        <div className={`px-2.5 py-1 rounded border text-xs font-medium capitalize ${getStatusColor()}`}>
          {alert.status}
        </div>
      </div>

      {/* Condition */}
      <div className="mb-3 p-3 bg-dark-bg rounded">
        <div className="text-sm text-gray-400 mb-1">Condition</div>
        <div className="text-white font-semibold">
          {alert.metric.toUpperCase()} {alert.condition}{' '}
          {typeof alert.threshold === 'number' ? alert.threshold.toLocaleString() : alert.threshold}
        </div>
        <div className="text-sm text-gray-400 mt-1">
          Current:{' '}
          <span className={isClose() ? 'text-yellow-400 font-semibold' : 'text-white'}>
            {typeof alert.currentValue === 'number'
              ? alert.currentValue.toLocaleString()
              : alert.currentValue || 'N/A'}
          </span>
          {isClose() && <span className="ml-2 text-yellow-400">(Close!)</span>}
        </div>
      </div>

      {/* Message */}
      {alert.message && (
        <div className="mb-3 text-sm text-gray-300">
          <AlertCircle className="w-4 h-4 inline mr-1" />
          {alert.message}
        </div>
      )}

      {/* Notification Methods */}
      <div className="flex gap-2 mb-3">
        {alert.notification.email && (
          <div className="flex items-center gap-1 px-2 py-1 bg-blue-900/20 text-blue-400 rounded text-xs">
            <Mail className="w-3 h-3" />
            Email
          </div>
        )}
        {alert.notification.push && (
          <div className="flex items-center gap-1 px-2 py-1 bg-green-900/20 text-green-400 rounded text-xs">
            <Smartphone className="w-3 h-3" />
            Push
          </div>
        )}
        {alert.notification.sms && (
          <div className="flex items-center gap-1 px-2 py-1 bg-purple-900/20 text-purple-400 rounded text-xs">
            <MessageSquare className="w-3 h-3" />
            SMS
          </div>
        )}
        {alert.notification.sound && (
          <div className="flex items-center gap-1 px-2 py-1 bg-yellow-900/20 text-yellow-400 rounded text-xs">
            <Volume2 className="w-3 h-3" />
            Sound
          </div>
        )}
      </div>

      {/* Metadata */}
      <div className="grid grid-cols-2 gap-3 mb-3 text-xs text-gray-400">
        <div>
          <div className="mb-1">Created</div>
          <div className="text-white">{formatDate(alert.createdAt)}</div>
        </div>
        {alert.triggeredAt && (
          <div>
            <div className="mb-1">Triggered</div>
            <div className="text-white">{formatDate(alert.triggeredAt)}</div>
          </div>
        )}
        {alert.expiresAt && !alert.triggeredAt && (
          <div>
            <div className="mb-1">Expires</div>
            <div className="text-white">{formatDate(alert.expiresAt)}</div>
          </div>
        )}
        <div>
          <div className="mb-1">Frequency</div>
          <div className="text-white capitalize">{alert.frequency}</div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-3 border-t border-dark-border">
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleToggle();
          }}
          className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded font-medium text-sm transition ${
            alert.status === 'disabled'
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-dark-border hover:bg-dark-border-hover text-gray-300'
          }`}
        >
          {alert.status === 'disabled' ? (
            <>
              <Play className="w-4 h-4" />
              Enable
            </>
          ) : (
            <>
              <Pause className="w-4 h-4" />
              Disable
            </>
          )}
        </button>

        <button
          onClick={(e) => {
            e.stopPropagation();
            handleTest();
          }}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded font-medium text-sm transition"
        >
          <Bell className="w-4 h-4" />
          Test
        </button>

        <button
          onClick={(e) => {
            e.stopPropagation();
            handleDelete();
          }}
          className="px-3 py-2 bg-red-900/30 hover:bg-red-900/50 text-red-400 rounded transition"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
