/**
 * Earnings Calendar - Display upcoming earnings events
 */

import { TrendingUp, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface EarningsEvent {
  id: string;
  symbol: string;
  companyName: string;
  date: string;
  time: 'pre' | 'post';
  epsEstimate?: number;
  inWatchlist: boolean;
}

// Mock earnings events for the next 7 days
const mockEarnings: EarningsEvent[] = [
  {
    id: '1',
    symbol: 'NVAX',
    companyName: 'Novavax Inc',
    date: '2025-10-15',
    time: 'post',
    epsEstimate: 0.45,
    inWatchlist: true,
  },
  {
    id: '2',
    symbol: 'SAVA',
    companyName: 'Cassava Sciences',
    date: '2025-10-18',
    time: 'pre',
    epsEstimate: -0.12,
    inWatchlist: true,
  },
  {
    id: '3',
    symbol: 'ABCD',
    companyName: 'ABC Diagnostics',
    date: '2025-10-16',
    time: 'post',
    epsEstimate: 0.28,
    inWatchlist: false,
  },
  {
    id: '4',
    symbol: 'EFGH',
    companyName: 'EFG Holdings',
    date: '2025-10-19',
    time: 'pre',
    epsEstimate: 0.15,
    inWatchlist: true,
  },
  {
    id: '5',
    symbol: 'MNOP',
    companyName: 'MNO Pharma',
    date: '2025-10-20',
    time: 'post',
    epsEstimate: -0.05,
    inWatchlist: false,
  },
];

export function EarningsCalendar() {
  const navigate = useNavigate();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-5 h-5 text-green-400" />
        <h3 className="text-lg font-semibold text-white">Upcoming Earnings</h3>
      </div>

      <div className="text-sm text-gray-400 mb-4">Next 7 Days</div>

      <div className="space-y-3 max-h-[600px] overflow-y-auto">
        {mockEarnings.map((event) => (
          <div
            key={event.id}
            onClick={() => navigate(`/trading?symbol=${event.symbol}`)}
            className={`bg-dark-bg rounded-lg p-3 cursor-pointer hover:bg-dark-border transition ${
              event.inWatchlist ? 'border border-green-700' : ''
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="font-bold font-mono text-white">
                {event.symbol}
              </div>
              {event.inWatchlist && (
                <span className="flex items-center gap-1 text-xs bg-green-900/30 text-green-400 px-2 py-0.5 rounded border border-green-700">
                  <Star className="w-3 h-3 fill-current" />
                  Watchlist
                </span>
              )}
            </div>

            <div className="text-sm text-gray-400 mb-2">
              {event.companyName}
            </div>

            <div className="flex items-center justify-between text-xs">
              <div className="text-gray-500">
                {formatDate(event.date)} •{' '}
                {event.time === 'pre' ? 'Before Market' : 'After Market'}
              </div>

              {event.epsEstimate !== undefined && (
                <div
                  className={`font-semibold ${
                    event.epsEstimate >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  EPS: ${event.epsEstimate.toFixed(2)}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-dark-border text-center">
        <button className="text-sm text-green-400 hover:text-green-300 transition">
          View Full Calendar →
        </button>
      </div>
    </div>
  );
}
