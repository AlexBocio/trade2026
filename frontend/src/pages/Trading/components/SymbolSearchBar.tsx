/**
 * Symbol Search Bar Component - Search and display selected symbol info
 */

import { useState, useRef, useEffect } from 'react';
import { Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import type { SymbolInfo } from '../../../services/mock-data/trading-data';
import { mockSymbolDatabase } from '../../../services/mock-data/trading-data';
import { useTradingStore } from '../../../store/useTradingStore';

export function SymbolSearchBar() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SymbolInfo[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<SymbolInfo | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Search symbols as user types
  const handleSearch = (value: string) => {
    setQuery(value);
    if (value.length < 1) {
      setResults([]);
      setShowDropdown(false);
      return;
    }

    // Filter mock results
    const mockResults = mockSymbolDatabase
      .filter(
        (s) =>
          s.symbol.toLowerCase().includes(value.toLowerCase()) ||
          s.companyName.toLowerCase().includes(value.toLowerCase())
      )
      .slice(0, 10);

    setResults(mockResults);
    setShowDropdown(mockResults.length > 0);
  };

  const selectSymbol = (symbol: SymbolInfo) => {
    setSelectedSymbol(symbol);
    setQuery(symbol.symbol);
    setShowDropdown(false);

    // Update trading store
    useTradingStore.getState().setSymbol(symbol.symbol, symbol.price);
  };

  const handleQuickBuy = () => {
    if (selectedSymbol) {
      navigate(`/trading?symbol=${selectedSymbol.symbol}&action=buy`);
    }
  };

  const handleQuickSell = () => {
    if (selectedSymbol) {
      navigate(`/trading?symbol=${selectedSymbol.symbol}&action=sell`);
    }
  };

  return (
    <div className="bg-gray-800 border-b border-gray-700 p-4">
      <div className="flex items-center gap-6">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md" ref={dropdownRef}>
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search symbols..."
            className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-green-400"
          />

          {/* Dropdown Results */}
          {showDropdown && results.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-50 max-h-96 overflow-y-auto">
              {results.map((result) => (
                <div
                  key={result.symbol}
                  onClick={() => selectSymbol(result)}
                  className="px-4 py-3 hover:bg-gray-800 cursor-pointer border-b border-gray-800 last:border-b-0"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-semibold">{result.symbol}</div>
                      <div className="text-sm text-gray-400">{result.companyName}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-mono">${result.price.toFixed(2)}</div>
                      <div
                        className={`text-sm ${
                          result.changePct >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}
                      >
                        {result.changePct >= 0 ? '+' : ''}
                        {result.changePct.toFixed(2)}%
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Selected Symbol Info */}
        {selectedSymbol && (
          <div className="flex items-center gap-8">
            <div>
              <div className="text-2xl font-bold">{selectedSymbol.symbol}</div>
              <div className="text-sm text-gray-400">{selectedSymbol.companyName}</div>
            </div>

            <div>
              <div className="text-3xl font-mono font-bold text-white">
                ${selectedSymbol.price.toFixed(2)}
              </div>
              <div
                className={`text-sm font-mono ${
                  selectedSymbol.changePct >= 0 ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {selectedSymbol.changePct >= 0 ? '+' : ''}${selectedSymbol.change.toFixed(2)} (
                {selectedSymbol.changePct.toFixed(2)}%)
              </div>
            </div>

            <div className="text-sm">
              <div className="text-gray-400">Volume</div>
              <div className="font-mono">{(selectedSymbol.volume / 1000000).toFixed(2)}M</div>
            </div>

            <div className="text-sm">
              <div className="text-gray-400">Market Cap</div>
              <div className="font-mono">${(selectedSymbol.marketCap / 1000000).toFixed(0)}M</div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="flex gap-2 ml-auto">
          <button
            onClick={handleQuickBuy}
            disabled={!selectedSymbol}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-semibold transition"
          >
            Quick Buy
          </button>
          <button
            onClick={handleQuickSell}
            disabled={!selectedSymbol}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-semibold transition"
          >
            Quick Sell
          </button>
        </div>
      </div>
    </div>
  );
}
