/**
 * Active Positions Table - Shows current open positions
 */

import { useNavigate } from 'react-router-dom';
import { formatCurrency, formatPercent, getColorClass } from '../../../utils/helpers';

interface Position {
  symbol: string;
  entry: number;
  current: number;
  pnl: number;
  pnlPct: number;
  daysHeld: number;
}

interface ActivePositionsTableProps {
  positions: Position[];
}

export function ActivePositionsTable({ positions }: ActivePositionsTableProps) {
  const navigate = useNavigate();

  const handleRowClick = () => {
    navigate('/trading');
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Active Positions</h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-sm text-gray-400 border-b border-gray-700">
              <th className="pb-3 font-medium">Symbol</th>
              <th className="pb-3 font-medium">Entry</th>
              <th className="pb-3 font-medium">Current</th>
              <th className="pb-3 font-medium">P&L</th>
              <th className="pb-3 font-medium">P&L %</th>
              <th className="pb-3 font-medium">Days</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((position) => (
              <tr
                key={position.symbol}
                onClick={handleRowClick}
                className="border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer transition-colors"
              >
                <td className="py-3">
                  <span className="font-semibold text-white">{position.symbol}</span>
                </td>
                <td className="py-3 text-gray-300">${position.entry.toFixed(2)}</td>
                <td className="py-3 text-white">${position.current.toFixed(2)}</td>
                <td className={`py-3 font-semibold ${getColorClass(position.pnl)}`}>
                  {formatCurrency(position.pnl)}
                </td>
                <td className={`py-3 font-semibold ${getColorClass(position.pnl)}`}>
                  {formatPercent(position.pnlPct)}
                </td>
                <td className="py-3 text-gray-400">{position.daysHeld}d</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="mt-4 text-right">
          <button
            onClick={handleRowClick}
            className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            View All Positions →
          </button>
        </div>
      </div>
    </div>
  );
}
