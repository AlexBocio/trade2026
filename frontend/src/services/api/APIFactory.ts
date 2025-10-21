/**
 * API Factory - switches between Mock and Real API based on environment
 */

import MockAPI from './MockAPI';
import RealAPI from './RealAPI';

export type APIMode = 'mock' | 'real';

class APIFactory {
  private mode: APIMode;

  constructor() {
    // Check environment variable to determine which API to use
    // Default to 'mock' for initial development
    const envMode = import.meta.env.VITE_API_MODE as APIMode | undefined;
    this.mode = envMode || 'mock';
  }

  /**
   * Get the current API mode
   */
  getMode(): APIMode {
    return this.mode;
  }

  /**
   * Set the API mode (useful for development/testing)
   */
  setMode(mode: APIMode): void {
    this.mode = mode;
    console.log(`API mode switched to: ${mode}`);
  }

  /**
   * Get the appropriate API instance based on current mode
   */
  getAPI() {
    if (this.mode === 'mock') {
      return MockAPI;
    }
    return RealAPI;
  }
}

// Export singleton instance
const apiFactory = new APIFactory();
export default apiFactory;

// Export the API instance for direct usage
export const api = apiFactory.getAPI();
