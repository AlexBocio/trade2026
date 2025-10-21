/**
 * Asset Allocation Chart - Pie chart showing portfolio allocation
 */

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface AllocationData {
  name: string;
  value: number;
  color: string;
}

export function AssetAllocationChart({ data }: { data: AllocationData[] }) {
  const COLORS = ['#00ff88', '#00ddff', '#ffc800', '#ff4444', '#8844ff'];

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
      <h3 className="text-lg font-semibold mb-4">Asset Allocation</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#1a1f2e',
              border: '1px solid #2a3142',
              borderRadius: '8px',
              color: '#e0e0e0',
            }}
            formatter={(value: number) => `$${value.toLocaleString()}`}
          />
          <Legend verticalAlign="bottom" height={36} wrapperStyle={{ color: '#e0e0e0' }} />
        </PieChart>
      </ResponsiveContainer>

      {/* Allocation Table */}
      <div className="mt-4 space-y-2">
        {data.map((item, index) => (
          <div key={index} className="flex justify-between items-center text-sm">
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <span>{item.name}</span>
            </div>
            <span className="font-mono">${item.value.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
