/**
 * Settings Page - User preferences and configuration
 */

import { useAppStore } from '../../store/useAppStore';
import { wsSimulator } from '../../services/WebSocketSimulator';

export function Settings() {
  const { theme, setTheme, userName, isConnected, setConnected } = useAppStore();

  const handleToggleConnection = () => {
    if (wsSimulator.getStatus()) {
      wsSimulator.stop();
      setConnected(false);
    } else {
      wsSimulator.start();
      setConnected(true);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Settings</h1>
        <p className="text-gray-400 mt-1">Manage your preferences and configuration</p>
      </div>

      {/* User Profile */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold mb-4">User Profile</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Name</label>
            <input
              type="text"
              value={userName}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white"
              readOnly
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">User ID</label>
            <input
              type="text"
              value="user-001"
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg font-mono text-gray-400"
              readOnly
            />
          </div>
        </div>
      </div>

      {/* Appearance */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold mb-4">Appearance</h2>
        <div className="flex items-center justify-between">
          <div>
            <div className="font-medium">Theme</div>
            <div className="text-sm text-gray-400">Choose your preferred color scheme</div>
          </div>
          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition font-medium"
          >
            {theme === 'dark' ? 'Dark Mode' : 'Light Mode'}
          </button>
        </div>
      </div>

      {/* Connection Settings */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold mb-4">Connection Settings</h2>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">Real-time Updates</div>
              <div className="text-sm text-gray-400">
                Status: {isConnected ? 'Connected' : 'Disconnected'}
              </div>
            </div>
            <button
              onClick={handleToggleConnection}
              className={`px-4 py-2 rounded-lg transition font-medium ${
                isConnected
                  ? 'bg-red-600 hover:bg-red-700'
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {isConnected ? 'Disconnect' : 'Connect'}
            </button>
          </div>

          <div className="pt-4 border-t border-gray-700">
            <label className="block text-sm text-gray-400 mb-2">Gateway URL</label>
            <input
              type="text"
              defaultValue="http://gateway:8080"
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg font-mono text-white"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">WebSocket URL</label>
            <input
              type="text"
              defaultValue="ws://gateway:8080/ws"
              className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg font-mono text-white"
            />
          </div>
        </div>
      </div>

      {/* Trading Preferences */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold mb-4">Trading Preferences</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">Order Confirmations</div>
              <div className="text-sm text-gray-400">Confirm before submitting orders</div>
            </div>
            <input type="checkbox" defaultChecked className="w-5 h-5 rounded" />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">Sound Notifications</div>
              <div className="text-sm text-gray-400">Play sound on order fills and alerts</div>
            </div>
            <input type="checkbox" defaultChecked className="w-5 h-5 rounded" />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">Auto-refresh Scanner</div>
              <div className="text-sm text-gray-400">Automatically refresh scanner results</div>
            </div>
            <input type="checkbox" defaultChecked className="w-5 h-5 rounded" />
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition">
          Save Settings
        </button>
      </div>
    </div>
  );
}
