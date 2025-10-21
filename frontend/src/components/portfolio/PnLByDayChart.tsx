/**
 * P&L by Day Chart - Daily profit/loss bar chart
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface DailyPnL {
  date: string;
  pnl: number;
}

export function PnLByDayChart({ data }: { data: DailyPnL[] }) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
      <h3 className="text-lg font-semibold mb-4">P&L by Day</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a3142" />
          <XAxis
            dataKey="date"
            stroke="#888"
            tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          />
          <YAxis stroke="#888" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1a1f2e',
              border: '1px solid #2a3142',
              borderRadius: '8px',
              color: '#e0e0e0',
            }}
            formatter={(value: number) => `$${value.toLocaleString()}`}
            labelFormatter={(label) =>
              new Date(label).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
            }
          />
          <Bar dataKey="pnl" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.pnl >= 0 ? '#00ff88' : '#ff4444'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
