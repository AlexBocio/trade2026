/**
 * Regime Badge Component
 * Reusable badge for displaying regime states
 */

interface RegimeBadgeProps {
  regime: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function RegimeBadge({ regime, size = 'md' }: RegimeBadgeProps) {
  const getRegimeStyles = (regime: string) => {
    const normalized = regime.toUpperCase();

    switch (normalized) {
      case 'BULLISH':
      case 'UP':
      case 'BULL':
        return {
          bg: 'bg-green-600',
          text: 'text-white',
          label: 'BULLISH',
        };
      case 'BEARISH':
      case 'DOWN':
      case 'BEAR':
        return {
          bg: 'bg-red-600',
          text: 'text-white',
          label: 'BEARISH',
        };
      case 'NEUTRAL':
      case 'SIDEWAYS':
      case 'RANGING':
        return {
          bg: 'bg-yellow-600',
          text: 'text-white',
          label: 'NEUTRAL',
        };
      case 'VOLATILE':
      case 'HIGH_VOLATILITY':
        return {
          bg: 'bg-orange-600',
          text: 'text-white',
          label: 'VOLATILE',
        };
      case 'TRANSITIONING':
      case 'TRANSITION':
        return {
          bg: 'bg-purple-600',
          text: 'text-white',
          label: 'TRANSITION',
        };
      default:
        return {
          bg: 'bg-gray-600',
          text: 'text-white',
          label: regime,
        };
    }
  };

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base',
  };

  const styles = getRegimeStyles(regime);

  return (
    <span
      className={`${styles.bg} ${styles.text} ${sizeClasses[size]} rounded font-semibold inline-block`}
    >
      {styles.label}
    </span>
  );
}
