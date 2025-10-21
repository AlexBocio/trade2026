/**
 * Recent Signals Table - Shows last 5 trading signals
 */

import { useNavigate } from 'react-router-dom';
import { ArrowUpCircle, ArrowDownCircle, Clock } from 'lucide-react';
import { formatDistance } from 'date-fns';

interface Signal {
  id: string;
  strategyId: string;
  symbol: string;
  strategy: string;
  action: 'buy' | 'sell';
  price: number;
  confidence: number;
  timestamp: string;
}

interface RecentSignalsTableProps {
  signals: Signal[];
}

export function RecentSignalsTable({ signals }: RecentSignalsTableProps) {
  const navigate = useNavigate();

  const handleRowClick = (strategyId: string) => {
    navigate(`/strategies/${strategyId}`);
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Recent Signals</h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-sm text-gray-400 border-b border-gray-700">
              <th className="pb-3 font-medium">Symbol</th>
              <th className="pb-3 font-medium">Strategy</th>
              <th className="pb-3 font-medium">Action</th>
              <th className="pb-3 font-medium">Price</th>
              <th className="pb-3 font-medium">Confidence</th>
              <th className="pb-3 font-medium">Time</th>
            </tr>
          </thead>
          <tbody>
            {signals.map((signal) => (
              <tr
                key={signal.id}
                onClick={() => handleRowClick(signal.strategyId)}
                className="border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer transition-colors"
              >
                <td className="py-3">
                  <span className="font-semibold text-white">{signal.symbol}</span>
                </td>
                <td className="py-3 text-sm text-gray-300">{signal.strategy}</td>
                <td className="py-3">
                  <div className="flex items-center gap-2">
                    {signal.action === 'buy' ? (
                      <>
                        <ArrowUpCircle size={16} className="text-green-400" />
                        <span className="text-green-400 font-medium">BUY</span>
                      </>
                    ) : (
                      <>
                        <ArrowDownCircle size={16} className="text-red-400" />
                        <span className="text-red-400 font-medium">SELL</span>
                      </>
                    )}
                  </div>
                </td>
                <td className="py-3 text-white">${signal.price.toFixed(2)}</td>
                <td className="py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${
                          signal.confidence > 85
                            ? 'bg-green-500'
                            : signal.confidence > 70
                            ? 'bg-yellow-500'
                            : 'bg-orange-500'
                        }`}
                        style={{ width: `${signal.confidence}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-400">{signal.confidence.toFixed(0)}%</span>
                  </div>
                </td>
                <td className="py-3 text-sm text-gray-400">
                  <div className="flex items-center gap-1">
                    <Clock size={14} />
                    {formatDistance(new Date(signal.timestamp), new Date(), { addSuffix: true })}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
