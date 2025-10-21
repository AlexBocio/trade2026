/**
 * Main layout component - combines Sidebar and TopBar
 */

import { useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { useStrategyStore } from '../../store/useStrategyStore';

export function Layout() {
  const { fetchStrategies } = useStrategyStore();

  // Fetch initial data when layout mounts
  useEffect(() => {
    fetchStrategies();
  }, [fetchStrategies]);

  return (
    <div className="h-screen flex overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <TopBar />

        {/* Page content */}
        <main className="flex-1 overflow-auto bg-dark-bg p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
