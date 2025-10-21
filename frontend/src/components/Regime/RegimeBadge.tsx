/**
 * Regime Badge Component
 * Color-coded badge for displaying regime types
 */

import React from 'react';
import type { RegimeType } from '../../types/regime';

interface RegimeBadgeProps {
  regime: RegimeType | undefined;
  large?: boolean;
}

const REGIME_COLORS: Record<RegimeType, string> = {
  BULL_TRENDING: 'bg-green-600 text-white border-green-500',
  BEAR_TRENDING: 'bg-red-600 text-white border-red-500',
  MOMENTUM: 'bg-blue-600 text-white border-blue-500',
  MEAN_REVERTING: 'bg-purple-600 text-white border-purple-500',
  HIGH_VOLATILITY: 'bg-orange-600 text-white border-orange-500',
  LOW_VOLATILITY: 'bg-teal-600 text-white border-teal-500',
  RANGE_BOUND: 'bg-yellow-600 text-white border-yellow-500',
  CRISIS: 'bg-red-800 text-white border-red-700',
  EXPANSION: 'bg-green-500 text-white border-green-400',
  CONTRACTION: 'bg-red-500 text-white border-red-400',
  NEUTRAL: 'bg-gray-600 text-white border-gray-500',
};

const REGIME_LABELS: Record<RegimeType, string> = {
  BULL_TRENDING: 'Bull Trending',
  BEAR_TRENDING: 'Bear Trending',
  MOMENTUM: 'Momentum',
  MEAN_REVERTING: 'Mean Reverting',
  HIGH_VOLATILITY: 'High Volatility',
  LOW_VOLATILITY: 'Low Volatility',
  RANGE_BOUND: 'Range Bound',
  CRISIS: 'Crisis',
  EXPANSION: 'Expansion',
  CONTRACTION: 'Contraction',
  NEUTRAL: 'Neutral',
};

const REGIME_ICONS: Record<RegimeType, string> = {
  BULL_TRENDING: '📈',
  BEAR_TRENDING: '📉',
  MOMENTUM: '🚀',
  MEAN_REVERTING: '↔️',
  HIGH_VOLATILITY: '⚡',
  LOW_VOLATILITY: '😴',
  RANGE_BOUND: '📏',
  CRISIS: '🔥',
  EXPANSION: '💪',
  CONTRACTION: '📉',
  NEUTRAL: '➡️',
};

export default function RegimeBadge({ regime, large = false }: RegimeBadgeProps) {
  if (!regime) {
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded border bg-gray-700 text-gray-400 border-gray-600 ${large ? 'text-base' : 'text-xs'} font-semibold`}>
        Unknown
      </span>
    );
  }

  const colorClass = REGIME_COLORS[regime] || 'bg-gray-600 text-white border-gray-500';
  const label = REGIME_LABELS[regime] || regime;
  const icon = REGIME_ICONS[regime] || '';

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 rounded border ${colorClass} ${large ? 'text-base px-3 py-1.5' : 'text-xs'} font-semibold`}
    >
      {icon} {label}
    </span>
  );
}
