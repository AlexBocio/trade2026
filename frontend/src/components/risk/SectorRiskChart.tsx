/**
 * Sector Risk Chart - Sector exposure with risk limits
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';

interface SectorRisk {
  sector: string;
  exposure: number;
  limit: number;
  status: 'safe' | 'warning' | 'danger';
}

export function SectorRiskChart({ data }: { data: SectorRisk[] }) {
  const getColor = (status: string) => {
    switch (status) {
      case 'safe':
        return '#00ff88';
      case 'warning':
        return '#ffc800';
      case 'danger':
        return '#ff4444';
      default:
        return '#888888';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
      <h3 className="text-lg font-semibold mb-4">Sector Exposure Risk</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a3142" />
          <XAxis dataKey="sector" stroke="#888" />
          <YAxis stroke="#888" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1a1f2e',
              border: '1px solid #2a3142',
              borderRadius: '8px',
              color: '#e0e0e0',
            }}
            formatter={(value: number) => `${value.toFixed(1)}%`}
          />
          <Bar dataKey="exposure" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.status)} />
            ))}
          </Bar>
          {/* Reference line for typical limit */}
          <ReferenceLine y={70} stroke="#ff4444" strokeDasharray="3 3" label="Limit" />
        </BarChart>
      </ResponsiveContainer>

      {/* Status Summary */}
      <div className="mt-4 space-y-2">
        {data.map((item, index) => (
          <div key={index} className="flex justify-between items-center text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded" style={{ backgroundColor: getColor(item.status) }} />
              <span>{item.sector}</span>
            </div>
            <span className="font-mono text-gray-400">
              {item.exposure.toFixed(1)}% / {item.limit.toFixed(0)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
