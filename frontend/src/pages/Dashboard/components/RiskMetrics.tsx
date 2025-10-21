/**
 * Risk Metrics - Shows risk management indicators
 */

import { Shield, AlertTriangle, Activity, TrendingDown } from 'lucide-react';

interface RiskMetricsProps {
  risk: {
    positionLimitUsage: number;
    dailyLossLimit: number;
    dailyLossMax: number;
    portfolioHeat: number;
    maxDrawdown: number;
  };
}

export function RiskMetrics({ risk }: RiskMetricsProps) {
  const metrics = [
    {
      label: 'Position Limit Usage',
      value: risk.positionLimitUsage,
      max: 100,
      unit: '%',
      icon: Shield,
      color: risk.positionLimitUsage > 80 ? 'text-red-400' : 'text-blue-400',
      barColor: risk.positionLimitUsage > 80 ? 'bg-red-500' : 'bg-blue-500',
    },
    {
      label: 'Daily Loss Limit',
      value: Math.abs(risk.dailyLossLimit),
      max: Math.abs(risk.dailyLossMax),
      unit: '%',
      icon: AlertTriangle,
      color:
        Math.abs(risk.dailyLossLimit) > Math.abs(risk.dailyLossMax) * 0.8
          ? 'text-red-400'
          : 'text-yellow-400',
      barColor:
        Math.abs(risk.dailyLossLimit) > Math.abs(risk.dailyLossMax) * 0.8
          ? 'bg-red-500'
          : 'bg-yellow-500',
      displayValue: `${risk.dailyLossLimit.toFixed(2)}% / ${risk.dailyLossMax.toFixed(1)}%`,
    },
    {
      label: 'Portfolio Heat',
      value: risk.portfolioHeat,
      max: 100,
      unit: '%',
      icon: Activity,
      color: risk.portfolioHeat > 70 ? 'text-orange-400' : 'text-purple-400',
      barColor: risk.portfolioHeat > 70 ? 'bg-orange-500' : 'bg-purple-500',
    },
    {
      label: 'Max Drawdown',
      value: Math.abs(risk.maxDrawdown),
      max: 20,
      unit: '%',
      icon: TrendingDown,
      color: 'text-red-400',
      barColor: 'bg-red-500',
      displayValue: `${risk.maxDrawdown.toFixed(1)}%`,
    },
  ];

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Risk Metrics</h3>
      <div className="space-y-4">
        {metrics.map((metric, index) => (
          <div key={index}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <metric.icon className={metric.color} size={16} />
                <span className="text-sm text-gray-300">{metric.label}</span>
              </div>
              <span className={`text-sm font-semibold ${metric.color}`}>
                {metric.displayValue ||
                  `${metric.value.toFixed(metric.value % 1 === 0 ? 0 : 1)}${metric.unit}`}
              </span>
            </div>
            <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full ${metric.barColor} transition-all duration-300`}
                style={{ width: `${Math.min((metric.value / metric.max) * 100, 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4 pt-4 border-t border-gray-700">
        <p className="text-xs text-gray-500">
          All risk limits are within acceptable ranges. Portfolio is properly hedged.
        </p>
      </div>
    </div>
  );
}
