/**
 * Preset Manager Component
 * Modal for managing saved scan presets
 */

import React from 'react';
import { X, Play, Star } from 'lucide-react';

interface Preset {
  id: string;
  name: string;
  description: string;
  config: any;
  is_default?: boolean;
  created_at?: string;
}

interface PresetManagerProps {
  presets: Preset[];
  onLoad: (presetId: string) => void;
  onClose: () => void;
}

export const PresetManager: React.FC<PresetManagerProps> = ({
  presets,
  onLoad,
  onClose
}) => {
  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card rounded-lg p-6 max-w-2xl w-full mx-4 border border-dark-border"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Scan Presets</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-dark-border rounded"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Presets List */}
        {presets.length > 0 ? (
          <div className="space-y-3 max-h-96 overflow-y-auto mb-6">
            {presets.map((preset) => (
              <div
                key={preset.id}
                className="bg-dark-bg rounded-lg p-4 hover:bg-dark-border cursor-pointer transition-colors border border-dark-border group"
                onClick={() => {
                  onLoad(preset.id);
                  onClose();
                }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="text-white font-semibold">{preset.name}</div>
                      {preset.is_default && (
                        <div className="flex items-center gap-1 bg-blue-600 text-white text-xs px-2 py-0.5 rounded">
                          <Star className="w-3 h-3" />
                          Default
                        </div>
                      )}
                    </div>
                    <div className="text-sm text-gray-400">{preset.description}</div>
                    {preset.created_at && (
                      <div className="text-xs text-gray-500 mt-1">
                        Created: {new Date(preset.created_at).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                  <button className="opacity-0 group-hover:opacity-100 transition-opacity bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                    <Play className="w-4 h-4" />
                    Run
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-gray-500 text-lg mb-2">No presets saved yet</div>
            <div className="text-gray-400 text-sm">
              Configure a scan and click "Save as Preset" to create one
            </div>
          </div>
        )}

        {/* Close Button */}
        <button
          onClick={onClose}
          className="bg-gray-600 hover:bg-gray-500 text-white px-6 py-2 rounded-lg w-full transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  );
};
