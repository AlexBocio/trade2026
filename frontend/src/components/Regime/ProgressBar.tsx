/**
 * Generic Progress Bar Component
 * Reusable progress bar with custom colors
 */

import React from 'react';

interface ProgressBarProps {
  value: number;
  max?: number;
  color?: string;
  showLabel?: boolean;
  animate?: boolean;
}

export default function ProgressBar({
  value,
  max = 100,
  color = 'bg-blue-500',
  showLabel = true,
  animate = true
}: ProgressBarProps) {
  const percentage = Math.min((value / max) * 100, 100);

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-700 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full ${color} ${animate ? 'transition-all duration-500' : ''}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-xs text-white font-semibold w-10 text-right">
          {percentage.toFixed(0)}%
        </span>
      )}
    </div>
  );
}
