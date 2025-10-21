/**
 * Portfolio Summary - 4 metric cards
 */

import { TrendingUp, DollarSign, Target, Award } from 'lucide-react';
import { formatCurrency, formatPercent, getColorClass } from '../../../utils/helpers';

interface PortfolioSummaryProps {
  data: {
    accountValue: number;
    todayPnL: number;
    todayPnLPct: number;
    openPositions: number;
    maxPositions: number;
    winRate: number;
    sharpeRatio: number;
  };
}

export function PortfolioSummary({ data }: PortfolioSummaryProps) {
  const cards = [
    {
      title: 'Account Value',
      value: formatCurrency(data.accountValue),
      icon: DollarSign,
      iconColor: 'text-blue-400',
      bgColor: 'bg-blue-900/20',
    },
    {
      title: "Today's P&L",
      value: formatCurrency(data.todayPnL),
      subtitle: formatPercent(data.todayPnLPct),
      icon: TrendingUp,
      iconColor: getColorClass(data.todayPnL),
      bgColor: data.todayPnL > 0 ? 'bg-green-900/20' : 'bg-red-900/20',
      valueColor: getColorClass(data.todayPnL),
    },
    {
      title: 'Open Positions',
      value: `${data.openPositions} / ${data.maxPositions}`,
      subtitle: `${((data.openPositions / data.maxPositions) * 100).toFixed(0)}% utilized`,
      icon: Target,
      iconColor: 'text-purple-400',
      bgColor: 'bg-purple-900/20',
    },
    {
      title: 'Win Rate',
      value: `${data.winRate.toFixed(1)}%`,
      subtitle: `Sharpe: ${data.sharpeRatio.toFixed(2)}`,
      icon: Award,
      iconColor: 'text-yellow-400',
      bgColor: 'bg-yellow-900/20',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => (
        <div key={index} className="card">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm text-gray-400 mb-1">{card.title}</p>
              <h3 className={`text-2xl font-bold ${card.valueColor || 'text-white'}`}>
                {card.value}
              </h3>
              {card.subtitle && (
                <p className="text-sm text-gray-500 mt-1">{card.subtitle}</p>
              )}
            </div>
            <div className={`p-3 rounded-lg ${card.bgColor}`}>
              <card.icon className={card.iconColor} size={24} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
