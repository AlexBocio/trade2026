/**
 * Historical VaR Chart - Value at Risk over time
 */

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface VaRPoint {
  date: string;
  var: number;
}

export function HistoricalVaRChart({ data }: { data: VaRPoint[] }) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
      <h3 className="text-lg font-semibold mb-4">Historical VaR (95%)</h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
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
          <Line type="monotone" dataKey="var" stroke="#ff4444" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
