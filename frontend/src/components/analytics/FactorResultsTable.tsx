/**
 * Factor Results Table - Display factor performance results
 */

import { CheckCircle, XCircle } from 'lucide-react';

interface FactorResult {
  name: string;
  annualReturn: number;
  sharpeRatio: number;
  pValue: number;
  tStat: number;
  significant: boolean;
}

export function FactorResultsTable({ factors }: { factors: FactorResult[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="text-left text-sm text-gray-400 border-b border-dark-border">
            <th className="pb-3 font-semibold">Factor</th>
            <th className="pb-3 font-semibold text-right">Annual Return</th>
            <th className="pb-3 font-semibold text-right">Sharpe Ratio</th>
            <th className="pb-3 font-semibold text-right">t-Statistic</th>
            <th className="pb-3 font-semibold text-right">p-value</th>
            <th className="pb-3 font-semibold text-center">Significant?</th>
          </tr>
        </thead>
        <tbody>
          {factors.map((factor, index) => (
            <tr key={index} className="border-b border-dark-border last:border-b-0">
              <td className="py-3 font-semibold text-white">{factor.name}</td>
              <td
                className={`py-3 text-right font-mono font-bold ${
                  factor.annualReturn > 0 ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {factor.annualReturn > 0 ? '+' : ''}
                {factor.annualReturn.toFixed(1)}%
              </td>
              <td className="py-3 text-right font-mono text-white">
                {factor.sharpeRatio.toFixed(2)}
              </td>
              <td className="py-3 text-right font-mono text-white">{factor.tStat.toFixed(2)}</td>
              <td
                className={`py-3 text-right font-mono ${
                  factor.pValue < 0.05 ? 'text-green-400 font-bold' : 'text-gray-400'
                }`}
              >
                {factor.pValue.toFixed(4)}
              </td>
              <td className="py-3 text-center">
                {factor.significant ? (
                  <div className="flex items-center justify-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span className="text-green-400 font-semibold">
                      {factor.pValue < 0.001 ? '✓✓✓' : factor.pValue < 0.01 ? '✓✓' : '✓'}
                    </span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-2">
                    <XCircle className="w-5 h-5 text-red-400" />
                    <span className="text-red-400">✗</span>
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="mt-4 text-sm text-gray-400">
        <strong>Significance levels:</strong> ✓✓✓ (p &lt; 0.001) = Very strong | ✓✓ (p &lt; 0.01)
        = Strong | ✓ (p &lt; 0.05) = Significant
      </div>
    </div>
  );
}
