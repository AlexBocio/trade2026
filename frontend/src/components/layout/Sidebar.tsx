/**
 * Sidebar navigation component
 */

import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  ScanSearch,
  TrendingUp,
  Lightbulb,
  FlaskConical,
  Wallet,
  Shield,
  BookOpen,
  Bell,
  List,
  Newspaper,
  LineChart,
  Brain,
  Database,
  FileText,
  Settings as SettingsIcon,
} from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { cn } from '../../utils/helpers';

const navigationItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Scanner', path: '/scanner', icon: ScanSearch },
  { name: 'Trading', path: '/trading', icon: TrendingUp },
  { name: 'Strategies', path: '/strategies', icon: Lightbulb },
  { name: 'Backtesting', path: '/backtesting', icon: FlaskConical },
  { name: 'Portfolio', path: '/portfolio', icon: Wallet },
  { name: 'Risk', path: '/risk', icon: Shield },
  { name: 'Journal', path: '/journal', icon: BookOpen },
  { name: 'Alerts', path: '/alerts', icon: Bell },
  { name: 'Watchlists', path: '/watchlists', icon: List },
  { name: 'News', path: '/news', icon: Newspaper },
  { name: 'Analytics', path: '/analytics', icon: LineChart },
  { name: 'AI Lab', path: '/ai-lab', icon: Brain },
  { name: 'Database', path: '/database', icon: Database },
  { name: 'Reports', path: '/reports', icon: FileText },
  { name: 'Settings', path: '/settings', icon: SettingsIcon },
];

export function Sidebar() {
  const { sidebarCollapsed } = useAppStore();

  return (
    <aside
      className={cn(
        'bg-dark-card border-r border-dark-border transition-all duration-300',
        sidebarCollapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-center border-b border-dark-border">
        <h1 className={cn('font-bold text-accent-blue', sidebarCollapsed ? 'text-xl' : 'text-2xl')}>
          {sidebarCollapsed ? 'T' : 'Trade2026'}
        </h1>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {navigationItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                'nav-link',
                isActive && 'active',
                sidebarCollapsed && 'justify-center px-0'
              )
            }
          >
            <item.icon size={20} />
            {!sidebarCollapsed && <span>{item.name}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
