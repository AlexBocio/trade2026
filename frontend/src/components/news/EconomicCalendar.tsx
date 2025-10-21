/**
 * Economic Calendar - Display today's economic events
 */

import { Calendar } from 'lucide-react';

interface EconomicEvent {
  id: string;
  time: string;
  event: string;
  previous?: string;
  forecast?: string;
  actual?: string;
  impact: 'high' | 'medium' | 'low';
}

// Mock economic events for today
const mockEvents: EconomicEvent[] = [
  {
    id: '1',
    time: '10:00 AM',
    event: 'CPI Report (MoM)',
    previous: '+0.2%',
    forecast: '+0.3%',
    actual: undefined,
    impact: 'high',
  },
  {
    id: '2',
    time: '2:00 PM',
    event: 'Fed Minutes',
    previous: undefined,
    forecast: undefined,
    actual: undefined,
    impact: 'high',
  },
  {
    id: '3',
    time: '8:30 AM',
    event: 'Unemployment Claims',
    previous: '220K',
    forecast: '215K',
    actual: '218K',
    impact: 'medium',
  },
  {
    id: '4',
    time: '9:45 AM',
    event: 'PMI Manufacturing',
    previous: '52.3',
    forecast: '52.5',
    actual: undefined,
    impact: 'medium',
  },
  {
    id: '5',
    time: '11:00 AM',
    event: 'Consumer Sentiment',
    previous: '67.2',
    forecast: '68.0',
    actual: undefined,
    impact: 'low',
  },
];

export function EconomicCalendar() {
  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'text-red-400';
      case 'medium':
        return 'text-yellow-400';
      case 'low':
        return 'text-green-400';
      default:
        return 'text-gray-400';
    }
  };

  const getImpactBadge = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'bg-red-900/30 text-red-400 border-red-700';
      case 'medium':
        return 'bg-yellow-900/30 text-yellow-400 border-yellow-700';
      case 'low':
        return 'bg-green-900/30 text-green-400 border-green-700';
      default:
        return 'bg-gray-900/30 text-gray-400 border-gray-700';
    }
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <Calendar className="w-5 h-5 text-green-400" />
        <h3 className="text-lg font-semibold text-white">Economic Calendar</h3>
      </div>

      <div className="text-sm text-gray-400 mb-4">Today's Events</div>

      <div className="space-y-3 max-h-[600px] overflow-y-auto">
        {mockEvents.map((event) => (
          <div key={event.id} className="bg-dark-bg rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold text-white">{event.time}</div>
              <div
                className={`px-2 py-0.5 rounded border text-xs font-semibold uppercase ${getImpactBadge(
                  event.impact
                )}`}
              >
                {event.impact}
              </div>
            </div>

            <div className="text-sm mb-2 text-white">{event.event}</div>

            {event.forecast && (
              <div className="text-xs text-gray-400 space-y-1">
                <div className="flex justify-between">
                  <span>Forecast:</span>
                  <span className="text-blue-400 font-semibold">
                    {event.forecast}
                  </span>
                </div>
                {event.previous && (
                  <div className="flex justify-between">
                    <span>Previous:</span>
                    <span>{event.previous}</span>
                  </div>
                )}
              </div>
            )}

            {event.actual && (
              <div className="text-xs mt-2 pt-2 border-t border-dark-border">
                <div className="flex justify-between">
                  <span className="text-gray-400">Actual:</span>
                  <span className="text-green-400 font-semibold">
                    {event.actual}
                  </span>
                </div>
              </div>
            )}
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
