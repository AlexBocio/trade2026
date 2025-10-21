/**
 * Regime Strength Bar Component
 * Visual progress bar for regime strength (0-10)
 */

import React from 'react';

interface RegimeStrengthBarProps {
  strength: number;
  max?: number;
  animate?: boolean;
}

export default function RegimeStrengthBar({ strength, max = 10, animate = true }: RegimeStrengthBarProps) {
  const percentage = (strength / max) * 100;

  // Color based on strength
  const getColor = () => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-green-600';
    if (percentage >= 40) return 'bg-yellow-500';
    if (percentage >= 20) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <div className="w-full bg-gray-700 rounded-full h-2.5 overflow-hidden">
      <div
        className={`h-full ${getColor()} ${animate ? 'transition-all duration-500 ease-out' : ''}`}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}
