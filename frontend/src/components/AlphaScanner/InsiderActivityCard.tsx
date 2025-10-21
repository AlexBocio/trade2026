/**
 * Insider Activity Card Component
 * Display recent insider buying/selling activity (SEC Form 4)
 */

import React from 'react';

interface Transaction {
  insider: string;
  date: string;
  shares: number;
  price: number;
  value: number;
}

interface InsiderActivityData {
  num_insiders_buying: number;
  total_purchases: number;
  transactions: Transaction[];
  insider_score: number;
}

interface InsiderActivityCardProps {
  data: InsiderActivityData;
}

export default function InsiderActivityCard({ data }: InsiderActivityCardProps) {
  if (data.num_insiders_buying === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 text-center text-gray-500 border border-gray-700">
        No recent insider activity
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
        <span>👔</span>
        <span>Insider Activity</span>
      </h4>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <div className="text-xs text-gray-400 mb-1">Insiders Buying</div>
          <div className="text-green-400 font-bold text-lg">{data.num_insiders_buying}</div>
        </div>
        <div>
          <div className="text-xs text-gray-400 mb-1">Total Purchases</div>
          <div className="text-white font-bold text-lg">
            ${(data.total_purchases / 1000).toFixed(0)}K
          </div>
        </div>
      </div>

      {/* Transactions */}
      <div>
        <div className="text-xs font-semibold text-gray-400 mb-2">Recent Transactions:</div>
        <div className="space-y-2">
          {data.transactions.map((txn, i) => (
            <div key={i} className="bg-gray-750 rounded p-2 text-xs border border-gray-600">
              <div className="flex items-center justify-between mb-1">
                <span className="text-white font-semibold">{txn.insider}</span>
                <span className="text-green-400 font-semibold">
                  ${(txn.value / 1000).toFixed(0)}K
                </span>
              </div>
              <div className="text-gray-400">
                {txn.date}: {txn.shares.toLocaleString()} shares @ ${txn.price.toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
