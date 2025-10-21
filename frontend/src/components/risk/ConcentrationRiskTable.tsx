/**
 * Concentration Risk Table - Shows position concentration and risk scores
 */

import { AlertCircle } from 'lucide-react';

interface ConcentrationRisk {
  symbol: string;
  value: number;
  portfolioPct: number;
  sector: string;
  riskScore: number; // 0-100
}

export function ConcentrationRiskTable({ positions }: { positions: ConcentrationRisk[] }) {
  const getRiskColor = (score: number) => {
    if (score < 30) return 'text-green-400';
    if (score < 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  const highConcentrationCount = positions.filter((p) => p.portfolioPct > 10).length;

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Concentration Risk</h3>
        {highConcentrationCount > 0 && (
          <div className="flex items-center gap-2 text-sm text-yellow-400">
            <AlertCircle className="w-4 h-4" />
            <span>{highConcentrationCount} positions over 10%</span>
          </div>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-sm text-gray-400 border-b border-gray-700">
              <th className="pb-3">Symbol</th>
              <th className="pb-3 text-right">Value</th>
              <th className="pb-3 text-right">% of Portfolio</th>
              <th className="pb-3">Sector</th>
              <th className="pb-3 text-right">Risk Score</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((position, index) => (
              <tr key={index} className="border-b border-gray-700 last:border-b-0">
                <td className="py-3">
                  <div className="font-semibold">{position.symbol}</div>
                </td>
                <td className="py-3 text-right font-mono">${position.value.toLocaleString()}</td>
                <td className="py-3 text-right">
                  <span
                    className={`font-mono font-semibold ${
                      position.portfolioPct > 10
                        ? 'text-red-400'
                        : position.portfolioPct > 5
                          ? 'text-yellow-400'
                          : 'text-green-400'
                    }`}
                  >
                    {position.portfolioPct.toFixed(1)}%
                  </span>
                </td>
                <td className="py-3 text-sm text-gray-400">{position.sector}</td>
                <td className="py-3 text-right">
                  <span className={`font-mono font-semibold ${getRiskColor(position.riskScore)}`}>
                    {position.riskScore}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
