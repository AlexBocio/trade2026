/**
 * Paper Trading Toggle - Switch between paper and live trading modes
 */

import { useTradingStore } from '../../store/useTradingStore';
import { TestTube, Zap } from 'lucide-react';

export function PaperTradingToggle() {
  const { mode, setMode, paperBalance, liveBalance } = useTradingStore();

  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-dark-card border border-dark-border rounded-lg">
      <div className="flex items-center gap-2">
        <button
          onClick={() => setMode('paper')}
          className={`px-3 py-1.5 rounded-lg font-semibold flex items-center gap-2 transition ${
            mode === 'paper'
              ? 'bg-blue-600 text-white'
              : 'bg-dark-border text-gray-400 hover:bg-gray-700'
          }`}
        >
          <TestTube className="w-4 h-4" />
          Paper
        </button>
        <button
          onClick={() => setMode('live')}
          className={`px-3 py-1.5 rounded-lg font-semibold flex items-center gap-2 transition ${
            mode === 'live'
              ? 'bg-green-600 text-white'
              : 'bg-dark-border text-gray-400 hover:bg-gray-700'
          }`}
        >
          <Zap className="w-4 h-4" />
          Live
        </button>
      </div>

      <div className="border-l border-dark-border pl-3">
        <div className="text-xs text-gray-400">Balance</div>
        <div className="font-mono font-bold text-white">
          ${mode === 'paper' ? paperBalance.toLocaleString() : liveBalance.toLocaleString()}
        </div>
      </div>

      {mode === 'paper' && (
        <div className="px-3 py-1 bg-blue-900/30 border border-blue-700 rounded text-xs font-semibold text-blue-300">
          PAPER MODE - NOT REAL MONEY
        </div>
      )}
    </div>
  );
}
