/**
 * Export Menu Component
 * Dropdown menu for exporting heatmap in multiple formats
 */

import React, { useState } from 'react';
import { Download } from 'lucide-react';

interface ExportMenuProps {
  onExport: (format: 'png' | 'csv' | 'html' | 'json') => void;
}

export const ExportMenu: React.FC<ExportMenuProps> = ({ onExport }) => {
  const [showMenu, setShowMenu] = useState(false);

  const handleExport = (format: 'png' | 'csv' | 'html' | 'json') => {
    onExport(format);
    setShowMenu(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowMenu(!showMenu)}
        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
      >
        <Download className="w-4 h-4" />
        Export
      </button>

      {showMenu && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setShowMenu(false)}
          />

          {/* Menu */}
          <div className="absolute right-0 mt-2 w-56 bg-dark-card border border-dark-border rounded-lg shadow-xl z-20">
            <div className="p-2 space-y-1">
              <button
                onClick={() => handleExport('png')}
                className="w-full text-left px-4 py-2 hover:bg-dark-bg text-white text-sm rounded transition-colors flex items-center gap-3"
              >
                <span className="text-lg">📷</span>
                <div>
                  <div className="font-medium">PNG Image</div>
                  <div className="text-xs text-gray-400">High-quality screenshot</div>
                </div>
              </button>

              <button
                onClick={() => handleExport('html')}
                className="w-full text-left px-4 py-2 hover:bg-dark-bg text-white text-sm rounded transition-colors flex items-center gap-3"
              >
                <span className="text-lg">🌐</span>
                <div>
                  <div className="font-medium">Interactive HTML</div>
                  <div className="text-xs text-gray-400">Shareable webpage</div>
                </div>
              </button>

              <button
                onClick={() => handleExport('csv')}
                className="w-full text-left px-4 py-2 hover:bg-dark-bg text-white text-sm rounded transition-colors flex items-center gap-3"
              >
                <span className="text-lg">📊</span>
                <div>
                  <div className="font-medium">CSV Data</div>
                  <div className="text-xs text-gray-400">Import to Excel</div>
                </div>
              </button>

              <button
                onClick={() => handleExport('json')}
                className="w-full text-left px-4 py-2 hover:bg-dark-bg text-white text-sm rounded transition-colors flex items-center gap-3"
              >
                <span className="text-lg">🔧</span>
                <div>
                  <div className="font-medium">JSON (API)</div>
                  <div className="text-xs text-gray-400">Raw data format</div>
                </div>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
