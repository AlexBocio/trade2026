/**
 * Event Badge Component
 * Badge for calendar events (earnings, FOMC, etc.)
 */

import React from 'react';

interface EventBadgeProps {
  label: string;
  active: boolean;
  color?: 'blue' | 'yellow' | 'red' | 'green';
}

const COLOR_CLASSES = {
  blue: 'bg-blue-900/30 border-blue-700 text-blue-400',
  yellow: 'bg-yellow-900/30 border-yellow-700 text-yellow-400',
  red: 'bg-red-900/30 border-red-700 text-red-400',
  green: 'bg-green-900/30 border-green-700 text-green-400',
};

export default function EventBadge({ label, active, color = 'blue' }: EventBadgeProps) {
  if (!active) return null;

  const colorClass = COLOR_CLASSES[color];

  return (
    <div className={`${colorClass} border rounded-lg px-3 py-2 text-sm font-medium flex items-center gap-2`}>
      <div className="w-2 h-2 rounded-full bg-current animate-pulse" />
      {label}
    </div>
  );
}
