/**
 * Trading Tabs Component - Bottom panel with positions, orders, fills, and trade log
 */

import { useState } from 'react';
import { PositionsTable } from './PositionsTable';
import { OrdersTable } from './OrdersTable';
import { FillsTable } from './FillsTable';
import { TradeLog } from './TradeLog';

export function TradingTabs() {
  const [activeTab, setActiveTab] = useState<'positions' | 'orders' | 'fills' | 'log'>(
    'positions'
  );

  return (
    <div className="bg-gray-800 border-t border-gray-700">
      {/* Tabs */}
      <div className="flex border-b border-gray-700">
        {[
          { id: 'positions', label: 'Positions' },
          { id: 'orders', label: 'Orders' },
          { id: 'fills', label: 'Fills' },
          { id: 'log', label: 'Trade Log' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-6 py-3 font-semibold transition ${
              activeTab === tab.id
                ? 'text-green-400 border-b-2 border-green-400'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-4">
        {activeTab === 'positions' && <PositionsTable />}
        {activeTab === 'orders' && <OrdersTable />}
        {activeTab === 'fills' && <FillsTable />}
        {activeTab === 'log' && <TradeLog />}
      </div>
    </div>
  );
}
