/**
 * Top navigation bar component with real-time updates
 */

import { useState, useEffect } from 'react';
import { Menu, Bell, Settings, User, Wifi, WifiOff } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { useTradingStore } from '../../store/useTradingStore';
import { formatCurrency, formatPercent, getColorClass } from '../../utils/helpers';

function getMarketStatus(time: Date): 'open' | 'closed' {
  const hour = time.getHours();
  const day = time.getDay();
  const minutes = time.getMinutes();

  // Weekend
  if (day === 0 || day === 6) return 'closed';

  // Market hours: 9:30 AM - 4:00 PM EST (Monday-Friday)
  if (hour < 9 || (hour === 9 && minutes < 30)) return 'closed';
  if (hour >= 16) return 'closed';

  return 'open';
}

export function TopBar() {
  const { toggleSidebar, isConnected, notifications, userName } = useAppStore();
  const { account } = useTradingStore();
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const marketStatus = getMarketStatus(currentTime);

  return (
    <header className="h-16 bg-dark-card border-b border-dark-border flex items-center justify-between px-6">
      {/* Left section */}
      <div className="flex items-center gap-6">
        <button
          onClick={toggleSidebar}
          className="p-2 hover:bg-dark-hover rounded-lg transition-colors"
          aria-label="Toggle sidebar"
        >
          <Menu size={20} />
        </button>

        {/* Market Status */}
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              marketStatus === 'open' ? 'bg-green-400 animate-pulse' : 'bg-red-400'
            }`}
          />
          <span className="text-sm font-medium">
            Market {marketStatus === 'open' ? 'Open' : 'Closed'}
          </span>
        </div>

        {/* Current Time */}
        <div className="text-sm text-gray-400 font-mono">
          {currentTime.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
          })}{' '}
          EST
        </div>

        {/* Account info */}
        {account && (
          <div className="flex items-center gap-6 text-sm">
            <div className="flex flex-col">
              <span className="text-gray-400">Portfolio Value</span>
              <span className="font-semibold text-white">
                {formatCurrency(account.portfolioValue)}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-gray-400">Day P&L</span>
              <span className={`font-semibold ${getColorClass(account.dayPnL)}`}>
                {formatCurrency(account.dayPnL)} ({formatPercent(account.dayPnLPercent)})
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-gray-400">Buying Power</span>
              <span className="font-semibold text-white">
                {formatCurrency(account.buyingPower)}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Right section */}
      <div className="flex items-center gap-4">
        {/* Connection Status */}
        <div className="flex items-center gap-2 text-sm">
          {isConnected ? (
            <>
              <Wifi className="w-4 h-4 text-green-400" />
              <span className="text-gray-400">Connected</span>
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4 text-red-400" />
              <span className="text-gray-400">Disconnected</span>
            </>
          )}
        </div>

        {/* Account type badge */}
        {account && (
          <div
            className={`px-3 py-1 rounded text-xs font-medium ${
              account.accountType === 'LIVE'
                ? 'bg-accent-green/20 text-accent-green'
                : 'bg-accent-yellow/20 text-accent-yellow'
            }`}
          >
            {account.accountType}
          </div>
        )}

        {/* Notifications */}
        <button
          className="p-2 hover:bg-dark-hover rounded-lg transition-colors relative"
          aria-label="Notifications"
        >
          <Bell size={20} />
          {notifications > 0 && (
            <span className="absolute top-1 right-1 w-5 h-5 bg-red-500 rounded-full text-xs flex items-center justify-center font-semibold">
              {notifications}
            </span>
          )}
        </button>

        {/* Settings */}
        <button
          className="p-2 hover:bg-dark-hover rounded-lg transition-colors"
          aria-label="Settings"
        >
          <Settings size={20} />
        </button>

        {/* User menu */}
        <button className="flex items-center gap-2 p-2 hover:bg-dark-hover rounded-lg transition-colors">
          <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
            <User className="w-5 h-5" />
          </div>
          <span className="text-sm font-medium">{userName}</span>
        </button>
      </div>
    </header>
  );
}
