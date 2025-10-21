/**
 * Reusable Panel Components - Consistent layout with automatic overflow handling
 *
 * Usage:
 * - Panel: Main container with automatic overflow handling
 * - PanelHeader: Fixed header that doesn't scroll
 * - PanelContent: Scrollable content area
 * - PanelFooter: Fixed footer that doesn't scroll
 */

import { ReactNode } from 'react';
import { cn } from '../../utils/helpers';

interface PanelProps {
  children: ReactNode;
  className?: string;
}

/**
 * Main Panel Container
 * Automatically handles overflow with flex layout
 */
export function Panel({ children, className }: PanelProps) {
  return (
    <div className={cn('bg-gray-900 rounded-lg border border-gray-700 h-full flex flex-col overflow-hidden', className)}>
      {children}
    </div>
  );
}

/**
 * Panel Header
 * Fixed at top, doesn't scroll with content
 */
export function PanelHeader({ children, className }: PanelProps) {
  return (
    <div className={cn('p-4 border-b border-gray-700 flex-shrink-0', className)}>
      {children}
    </div>
  );
}

/**
 * Panel Content
 * Scrollable content area that grows to fill available space
 */
export function PanelContent({ children, className }: PanelProps) {
  return (
    <div className={cn('p-4 flex-1 overflow-auto', className)}>
      {children}
    </div>
  );
}

/**
 * Panel Footer
 * Fixed at bottom, doesn't scroll with content
 */
export function PanelFooter({ children, className }: PanelProps) {
  return (
    <div className={cn('p-4 border-t border-gray-700 flex-shrink-0', className)}>
      {children}
    </div>
  );
}

/**
 * Panel Section
 * Use for subsections within PanelContent
 */
export function PanelSection({ children, className }: PanelProps) {
  return (
    <div className={cn('mb-6 last:mb-0', className)}>
      {children}
    </div>
  );
}

/**
 * Panel Grid
 * Responsive grid layout for multiple panels
 *
 * @param cols - Number of columns (1, 2, 3, or 4)
 * @param minHeight - Minimum height for each panel (default: 600px)
 */
interface PanelGridProps {
  children: ReactNode;
  cols?: 1 | 2 | 3 | 4;
  minHeight?: string;
  className?: string;
}

export function PanelGrid({ children, cols = 2, minHeight = '600px', className }: PanelGridProps) {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 lg:grid-cols-2',
    3: 'grid-cols-1 lg:grid-cols-2 xl:grid-cols-3',
    4: 'grid-cols-1 lg:grid-cols-2 xl:grid-cols-4',
  };

  return (
    <div
      className={cn('grid gap-6', gridCols[cols], className)}
      style={{ gridAutoRows: `minmax(${minHeight}, auto)` }}
    >
      {children}
    </div>
  );
}
