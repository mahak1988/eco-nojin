// Econojin API Services
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiCall<T>(path: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...options?.headers },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  } catch (error) {
    console.error(`API call failed: ${path}`, error);
    throw error;
  }
}

// Health Service
export const healthService = {
  check: () => apiCall<any>("/api/v1/health"),
  modules: () => apiCall<any>("/api/v1/modules"),
};

// Dashboard Service
export const dashboardService = {
  getStats: () => apiCall<any>("/api/v1/dashboard/stats"),
  getActivity: () => apiCall<any>("/api/v1/dashboard/activity"),
};

// AI Service
export const aiService = {
  chat: (message: string, context?: unknown) =>
    apiCall<any>("/api/v1/ai/chat", { 
      method: "POST", 
      body: JSON.stringify({ message, context }) 
    }),
};

// Auth Service
export const authService = {
  login: (data: unknown) => apiCall<any>("/api/v1/auth/login", { method: "POST", body: JSON.stringify(data) }),
  register: (data: unknown) => apiCall<any>("/api/v1/auth/register", { method: "POST", body: JSON.stringify(data) }),
  getProfile: () => apiCall<any>("/api/v1/auth/profile"),
};

// Weather Service
export const weatherService = {
  getForecast: (location: string, days = 7) =>
    apiCall<any>(`/api/v1/weather/forecast?location=${encodeURIComponent(location)}&days=${days}`),
  getAlerts: (region: string) =>
    apiCall<any>(`/api/v1/weather/alerts?region=${encodeURIComponent(region)}`),
};

// GIS Service
export const gisService = {
  calculateArea: (coords: unknown) =>
    apiCall<any>("/api/v1/gis/calculate/area", { method: "POST", body: JSON.stringify({ coordinates: coords }) }),
  getNdvi: (region: string) =>
    apiCall<any>(`/api/v1/gis/ndvi?region=${encodeURIComponent(region)}`),
};

// Carbon Service
export const carbonService = {
  calculate: (data: unknown) =>
    apiCall<any>("/api/v1/carbon/calculate", { method: "POST", body: JSON.stringify(data) }),
};

// Drought Service
export const droughtService = {
  getIndex: (region: string) =>
    apiCall<any>(`/api/v1/drought/index?region=${encodeURIComponent(region)}`),
  getRegions: () => apiCall<any>("/api/v1/drought/regions"),
};

// Shop Service
export const shopService = {
  getProducts: () => apiCall<any>("/api/v1/shop"),
};

// Calendar Service
export const calendarService = {
  getEvents: () => apiCall<any>("/api/v1/calendar"),
};

// Library Service
export const libraryService = {
  getResources: () => apiCall<any>("/api/v1/library"),
};

// Education Service
export const educationService = {
  getCourses: () => apiCall<any>("/api/v1/education"),
};

// Community Service
export const communityService = {
  getPosts: () => apiCall<any>("/api/v1/community"),
};

// Analytics Service
export const analyticsService = {
  track: (event: string, properties?: unknown) =>
    apiCall<any>("/api/v1/analytics/track", { 
      method: "POST", 
      body: JSON.stringify({ event, properties, timestamp: new Date().toISOString() }) 
    }),
};
