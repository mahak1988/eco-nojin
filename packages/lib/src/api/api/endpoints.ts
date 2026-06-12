// ============================================================================
// API Endpoints - With /api/v1 prefix
// ============================================================================

export const ENDPOINTS = {
  AUTH: {
    BASE: "/auth",
    OTP_REQUEST: "/auth/otp/request",
    OTP_VERIFY: "/auth/otp/verify",
    LOGIN: "/auth/login",
    PROFILE: "/auth/profile",
    LINK_WALLET: "/auth/profile/wallet",
  },
  FARMERS: {
    BASE: "/farmers",
    LIST: "/farmers",
    CREATE: "/farmers",
    DETAIL: (id: number) => `/farmers/${id}`,
    UPDATE: (id: number) => `/farmers/${id}`,
    DELETE: (id: number) => `/farmers/${id}`,
  },
  ECOCOIN: {
    BASE: "/ecocoin",
    TOKENS: "/ecocoin/tokens",
    STATS: "/ecocoin/stats",
    WALLETS: {
      BY_ID: (id: number) => `/ecocoin/wallets/${id}`,
      ME: "/ecocoin/wallets/me",
    },
    TRANSFER: "/ecocoin/transfer",
    STAKE: "/ecocoin/stake",
  },
  SOIL_WATER: {
    BASE: "/soil-water",
    STATS: "/soil-water/stats",
    COMPREHENSIVE: "/soil-water/comprehensive-analysis",
    PROJECTS: {
      LIST: "/soil-water/projects",
      CREATE: "/soil-water/projects",
      DETAIL: (id: number) => `/soil-water/projects/${id}`,
      UPDATE: (id: number) => `/soil-water/projects/${id}`,
      DELETE: (id: number) => `/soil-water/projects/${id}`,
    },
    REPORTS: {
      LIST: "/soil-water/reports",
      CREATE: "/soil-water/reports",
      DETAIL: (id: number) => `/soil-water/reports/${id}`,
      DELETE: (id: number) => `/soil-water/reports/${id}`,
    },
    LDN: "/soil-water/ldn",
    NDVI: "/soil-water/ndvi",
    NDWI: "/soil-water/ndwi",
    RUSLE: "/soil-water/rusle",
    WATER_BALANCE: "/soil-water/water-balance",
    IRRIGATION: "/soil-water/irrigation",
    DROUGHT: "/soil-water/drought-classification",
    CARBON: "/soil-water/carbon-sequestration",
  },
  ECOMINING: { BASE: "/ecomining" },
  WEATHER: { BASE: "/weather" },
  GIS: { BASE: "/gis" },
  AI: { BASE: "/ai" },
  ACADEMY: { BASE: "/academy" },
  STORE: { BASE: "/store" },
  DASHBOARD: { BASE: "/dashboard" },
} as const;

export function buildUrl(endpoint: string, params?: Record<string, any>): string {
  let url = endpoint;
  if (params) {
    const queryString = new URLSearchParams(
      Object.entries(params)
        .filter(([_, value]) => value !== undefined && value !== null)
        .reduce((acc, [key, value]) => {
          acc[key] = String(value);
          return acc;
        }, {} as Record<string, string>)
    ).toString();
    if (queryString) url += `?${queryString}`;
  }
  return url;
}
