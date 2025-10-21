/**
 * Risk Limit Gauges - Visual progress bars for risk limits
 */

import { AlertTriangle, CheckCircle } from 'lucide-react';

interface RiskLimit {
  name: string;
  current: number;
  limit: number;
  unit: string;
  status: 'safe' | 'warning' | 'danger';
}

export function RiskLimitGauges({ limits }: { limits: RiskLimit[] }) {
  const getColor = (status: string) => {
    switch (status) {
      case 'safe':
        return 'bg-green-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'danger':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getTextColor = (status: string) => {
    switch (status) {
      case 'safe':
        return 'text-green-400';
      case 'warning':
        return 'text-yellow-400';
      case 'danger':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Risk Limits</h3>
        <div className="text-sm text-gray-400">Real-time monitoring</div>
      </div>

      <div className="space-y-6">
        {limits.map((limit, index) => {
          const percentage = (Math.abs(limit.current) / Math.abs(limit.limit)) * 100;

          return (
            <div key={index}>
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center gap-2">
                  {limit.status === 'safe' ? (
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  ) : (
                    <AlertTriangle className={`w-4 h-4 ${getTextColor(limit.status)}`} />
                  )}
                  <span className="font-semibold">{limit.name}</span>
                </div>
                <div className="text-right">
                  <span className={`font-mono text-lg ${getTextColor(limit.status)}`}>
                    {limit.current}
                    {limit.unit}
                  </span>
                  <span className="text-gray-400 text-sm ml-2">
                    / {limit.limit}
                    {limit.unit}
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getColor(limit.status)} transition-all duration-300`}
                  style={{ width: `${Math.min(percentage, 100)}%` }}
                />
              </div>

              {/* Percentage Label */}
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>0%</span>
                <span className={getTextColor(limit.status)}>{percentage.toFixed(1)}% used</span>
                <span>100% {limit.status === 'danger' && '(KILL SWITCH)'}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
