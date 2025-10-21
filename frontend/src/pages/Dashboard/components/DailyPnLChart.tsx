/**
 * Daily P&L Chart - Bar chart showing daily profits/losses using Recharts
 */

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { format } from 'date-fns';

interface DailyPnLChartProps {
  data: Array<{ date: string; pnl: number }>;
}

export function DailyPnLChart({ data }: DailyPnLChartProps) {
  // Format data for chart
  const chartData = data.map((item) => ({
    ...item,
    date: format(new Date(item.date), 'MM/dd'),
  }));

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Daily P&L (Last 14 Days)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <XAxis
            dataKey="date"
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `$${value}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#f9fafb',
            }}
            formatter={(value: number) => [`$${value.toFixed(2)}`, 'P&L']}
            labelStyle={{ color: '#9ca3af' }}
          />
          <Bar dataKey="pnl" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.pnl >= 0 ? '#10b981' : '#ef4444'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
