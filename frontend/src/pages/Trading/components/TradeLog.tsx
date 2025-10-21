/**
 * Trade Log Component - Activity log showing all trading actions
 */

import { useTradingStore } from '../../../store/useTradingStore';
import { format } from 'date-fns';
import { CheckCircle, AlertCircle, XCircle, Info } from 'lucide-react';

export function TradeLog() {
  const { tradeLog } = useTradingStore();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-400" />;
      case 'info':
        return <Info className="w-5 h-5 text-blue-400" />;
      default:
        return <Info className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusBgColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-green-900/20 border-green-700';
      case 'error':
        return 'bg-red-900/20 border-red-700';
      case 'warning':
        return 'bg-yellow-900/20 border-yellow-700';
      case 'info':
        return 'bg-blue-900/20 border-blue-700';
      default:
        return 'bg-gray-800 border-gray-700';
    }
  };

  return (
    <div className="space-y-2">
      {tradeLog.length === 0 ? (
        <div className="text-center text-gray-400 py-8">No trading activity yet</div>
      ) : (
        tradeLog.map((entry) => (
          <div
            key={entry.id}
            className={`p-4 rounded-lg border ${getStatusBgColor(entry.status)}`}
          >
            <div className="flex items-start gap-3">
              {getStatusIcon(entry.status)}
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-3">
                    <span className="font-semibold text-white">{entry.symbol}</span>
                    <span className="text-sm text-gray-400">{entry.action}</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {format(new Date(entry.timestamp), 'MMM dd, HH:mm:ss')}
                  </span>
                </div>
                <div className="text-sm text-gray-300">{entry.details}</div>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
