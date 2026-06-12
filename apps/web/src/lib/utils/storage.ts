// ============================================================================
// Type-Safe LocalStorage Wrapper
// ============================================================================

class StorageService {
  private prefix = 'econojin_';

  // Set item with optional expiration
  set<T>(key: string, value: T, expiresInSeconds?: number): void {
    try {
      const item = {
        value,
        expires: expiresInSeconds ? Date.now() + expiresInSeconds * 1000 : null,
      };
      localStorage.setItem(this.prefix + key, JSON.stringify(item));
    } catch (error) {
      console.error(`Error setting storage key ${key}:`, error);
    }
  }

  // Get item with expiration check
  get<T>(key: string): T | null {
    try {
      const itemStr = localStorage.getItem(this.prefix + key);
      if (!itemStr) return null;

      const item = JSON.parse(itemStr);
      
      // Check expiration
      if (item.expires && Date.now() > item.expires) {
        this.remove(key);
        return null;
      }

      return item.value as T;
    } catch (error) {
      console.error(`Error getting storage key ${key}:`, error);
      return null;
    }
  }

  // Remove item
  remove(key: string): void {
    try {
      localStorage.removeItem(this.prefix + key);
    } catch (error) {
      console.error(`Error removing storage key ${key}:`, error);
    }
  }

  // Clear all items with prefix
  clear(): void {
    try {
      const keysToRemove: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(this.prefix)) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach((key: any) => localStorage.removeItem(key));
    } catch (error) {
      console.error('Error clearing storage:', error);
    }
  }

  // Check if key exists and is not expired
  has(key: string): boolean {
    return this.get(key) !== null;
  }
}

export const storage = new StorageService();

// ============================================================================
// Auth Storage Keys
// ============================================================================

export const AUTH_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_PROFILE: 'user_profile',
  FARMER_ID: 'farmer_id',
} as const;

// ============================================================================
// Auth Storage Helpers
// ============================================================================

export const authStorage = {
  setTokens: (accessToken: string, refreshToken?: string, expiresIn?: number) => {
    storage.set(AUTH_KEYS.ACCESS_TOKEN, accessToken, expiresIn);
    if (refreshToken) {
      storage.set(AUTH_KEYS.REFRESH_TOKEN, refreshToken, 60 * 60 * 24 * 7); // 7 days
    }
  },

  getAccessToken: (): string | null => {
    return storage.get<string>(AUTH_KEYS.ACCESS_TOKEN);
  },

  getRefreshToken: (): string | null => {
    return storage.get<string>(AUTH_KEYS.REFRESH_TOKEN);
  },

  setUserProfile: (profile: any) => {
    storage.set(AUTH_KEYS.USER_PROFILE, profile);
  },

  getUserProfile: () => {
    return storage.get<any>(AUTH_KEYS.USER_PROFILE);
  },

  setFarmerId: (farmerId: string) => {
    storage.set(AUTH_KEYS.FARMER_ID, farmerId);
  },

  getFarmerId: (): string | null => {
    return storage.get<string>(AUTH_KEYS.FARMER_ID);
  },

  clearAll: () => {
    storage.remove(AUTH_KEYS.ACCESS_TOKEN);
    storage.remove(AUTH_KEYS.REFRESH_TOKEN);
    storage.remove(AUTH_KEYS.USER_PROFILE);
    storage.remove(AUTH_KEYS.FARMER_ID);
  },

  isAuthenticated: (): boolean => {
    return !!authStorage.getAccessToken();
  },
};