/**
 * Sector Exposure Chart - Horizontal bar chart showing sector allocation
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface SectorExposure {
  sector: string;
  value: number;
  pct: number;
}

export function SectorExposureChart({ data }: { data: SectorExposure[] }) {
  const COLORS: Record<string, string> = {
    Healthcare: '#00ff88',
    Technology: '#00ddff',
    Finance: '#ffc800',
    Cash: '#888888',
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
      <h3 className="text-lg font-semibold mb-4">Sector Exposure</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data} layout="vertical" margin={{ left: 80 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a3142" />
          <XAxis type="number" stroke="#888" />
          <YAxis dataKey="sector" type="category" stroke="#888" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1a1f2e',
              border: '1px solid #2a3142',
              borderRadius: '8px',
              color: '#e0e0e0',
            }}
            formatter={(value: number) => `$${value.toLocaleString()}`}
          />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.sector] || '#888888'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Sector Table */}
      <div className="mt-4 space-y-2">
        {data.map((item, index) => (
          <div key={index} className="flex justify-between items-center text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded" style={{ backgroundColor: COLORS[item.sector] }} />
              <span>{item.sector}</span>
            </div>
            <span className="font-mono text-gray-400">{item.pct.toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
