/**
 * Scanner API Service
 * Connects to Custom Scanner backend on Port 5008
 */

import type { ScannerConfig, ScanResponse } from '../types/scanner';

const SCANNER_API_BASE = 'http://localhost:5008';

export const scannerApi = {
  /**
   * Run custom scanner scan with user configuration
   */
  runCustomScan: async (config: ScannerConfig): Promise<ScanResponse> => {
    const response = await fetch(`${SCANNER_API_BASE}/api/scanner/custom`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    if (!response.ok) {
      throw new Error(`Custom scan failed: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Save a scanner preset
   */
  savePreset: async (name: string, config: ScannerConfig): Promise<{ success: boolean; preset_id: string }> => {
    const response = await fetch(`${SCANNER_API_BASE}/api/scanner/preset/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, config }),
    });
    if (!response.ok) {
      throw new Error(`Failed to save preset: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Load a scanner preset
   */
  loadPreset: async (name: string, universe: string): Promise<ScannerConfig> => {
    const response = await fetch(`${SCANNER_API_BASE}/api/scanner/preset/${name}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ universe }),
    });
    if (!response.ok) {
      throw new Error(`Failed to load preset: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * List all available presets
   */
  listPresets: async (): Promise<{ presets: Array<{ name: string; description: string; created_at: string }> }> => {
    const response = await fetch(`${SCANNER_API_BASE}/api/scanner/preset/list`);
    if (!response.ok) {
      throw new Error(`Failed to list presets: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Delete a preset
   */
  deletePreset: async (name: string): Promise<{ success: boolean }> => {
    const response = await fetch(`${SCANNER_API_BASE}/api/scanner/preset/${name}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`Failed to delete preset: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get available universes
   */
  getUniverses: async (): Promise<{ universes: string[] }> => {
    const response = await fetch(`${SCANNER_API_BASE}/api/scanner/universes`);
    if (!response.ok) {
      throw new Error(`Failed to fetch universes: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await fetch(`${SCANNER_API_BASE}/health`);
    if (!response.ok) {
      throw new Error('Scanner service is not available');
    }
    return response.json();
  },
};
