/**
 * Scanner Preset Manager Component
 * Save, load, and delete scanner presets
 */

import React, { useState, useEffect } from 'react';
import { Save, FolderOpen, Trash2, X } from 'lucide-react';
import { scannerApi } from '../../api/scannerApi';
import type { ScannerConfig } from '../../types/scanner';

interface ScannerPresetManagerProps {
  config: ScannerConfig;
  onLoad: (config: ScannerConfig) => void;
}

export default function ScannerPresetManager({ config, onLoad }: ScannerPresetManagerProps) {
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showLoadModal, setShowLoadModal] = useState(false);
  const [presetName, setPresetName] = useState('');
  const [presets, setPresets] = useState<Array<{ name: string; description: string; created_at: string }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPresets = async () => {
    try {
      const response = await scannerApi.listPresets();
      setPresets(response.presets);
    } catch (err) {
      console.error('Failed to load presets:', err);
    }
  };

  useEffect(() => {
    loadPresets();
  }, []);

  const handleSave = async () => {
    if (!presetName.trim()) {
      setError('Please enter a preset name');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await scannerApi.savePreset(presetName, config);
      await loadPresets();
      setShowSaveModal(false);
      setPresetName('');
    } catch (err: any) {
      setError(err.message || 'Failed to save preset');
    } finally {
      setLoading(false);
    }
  };

  const handleLoad = async (name: string) => {
    setLoading(true);
    setError(null);

    try {
      const loadedConfig = await scannerApi.loadPreset(name, config.universe);
      onLoad(loadedConfig);
      setShowLoadModal(false);
    } catch (err: any) {
      setError(err.message || 'Failed to load preset');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (name: string) => {
    if (!confirm(`Delete preset "${name}"?`)) return;

    setLoading(true);
    try {
      await scannerApi.deletePreset(name);
      await loadPresets();
    } catch (err: any) {
      setError(err.message || 'Failed to delete preset');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 border-b border-gray-700 p-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-white font-semibold">Scanner Configuration</h3>
          <p className="text-sm text-gray-400">{config.name}</p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setShowSaveModal(true)}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
          >
            <Save className="w-4 h-4" />
            Save Preset
          </button>

          <button
            onClick={() => setShowLoadModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
          >
            <FolderOpen className="w-4 h-4" />
            Load Preset
          </button>
        </div>
      </div>

      {/* Save Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowSaveModal(false)}>
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 border border-gray-700" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white">Save Preset</h3>
              <button onClick={() => setShowSaveModal(false)} className="text-gray-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 mb-1 block">Preset Name</label>
                <input
                  type="text"
                  value={presetName}
                  onChange={(e) => setPresetName(e.target.value)}
                  placeholder="My Custom Scan"
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-500"
                  autoFocus
                />
              </div>

              {error && (
                <div className="bg-red-900/30 border border-red-700 rounded p-3 text-red-400 text-sm">
                  {error}
                </div>
              )}

              <div className="flex gap-2">
                <button
                  onClick={handleSave}
                  disabled={loading}
                  className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white py-2 rounded font-medium transition-colors"
                >
                  {loading ? 'Saving...' : 'Save'}
                </button>
                <button
                  onClick={() => setShowSaveModal(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-500 text-white py-2 rounded font-medium transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Load Modal */}
      {showLoadModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowLoadModal(false)}>
          <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 border border-gray-700 max-h-[80vh] overflow-hidden flex flex-col" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white">Load Preset</h3>
              <button onClick={() => setShowLoadModal(false)} className="text-gray-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            {error && (
              <div className="bg-red-900/30 border border-red-700 rounded p-3 text-red-400 text-sm mb-4">
                {error}
              </div>
            )}

            <div className="flex-1 overflow-y-auto space-y-2">
              {presets.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  No presets saved yet
                </div>
              ) : (
                presets.map((preset) => (
                  <div
                    key={preset.name}
                    className="bg-gray-750 rounded-lg p-4 hover:bg-gray-700 transition-colors border border-gray-600 flex items-center justify-between"
                  >
                    <div className="flex-1">
                      <h4 className="text-white font-medium">{preset.name}</h4>
                      <p className="text-sm text-gray-400">{preset.description || 'No description'}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        Created: {new Date(preset.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleLoad(preset.name)}
                        disabled={loading}
                        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded font-medium transition-colors"
                      >
                        Load
                      </button>
                      <button
                        onClick={() => handleDelete(preset.name)}
                        disabled={loading}
                        className="bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white p-2 rounded transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
