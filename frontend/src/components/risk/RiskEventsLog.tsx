/**
 * Risk Events Log - Timeline of risk events and alerts
 */

import { AlertTriangle, XCircle, CheckCircle } from 'lucide-react';

interface RiskEvent {
  timestamp: string;
  type: 'breach' | 'warning' | 'resolved';
  severity: 'low' | 'medium' | 'high';
  message: string;
  limit: string;
  value: string;
}

export function RiskEventsLog({ events }: { events: RiskEvent[] }) {
  const getIcon = (type: string) => {
    switch (type) {
      case 'breach':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'resolved':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      default:
        return null;
    }
  };

  const getBgColor = (type: string) => {
    switch (type) {
      case 'breach':
        return 'bg-red-900/20 border-red-700';
      case 'warning':
        return 'bg-yellow-900/20 border-yellow-700';
      case 'resolved':
        return 'bg-green-900/20 border-green-700';
      default:
        return 'bg-gray-800 border-gray-700';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h3 className="text-lg font-semibold mb-4">Risk Events Log</h3>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {events.map((event, index) => (
          <div key={index} className={`p-3 rounded border ${getBgColor(event.type)}`}>
            <div className="flex items-start gap-3">
              {getIcon(event.type)}
              <div className="flex-1">
                <div className="flex justify-between items-start mb-1">
                  <div className="font-semibold">{event.message}</div>
                  <div className="text-xs text-gray-400">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </div>
                </div>
                <div className="text-sm text-gray-400">
                  {event.limit}: {event.value}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
