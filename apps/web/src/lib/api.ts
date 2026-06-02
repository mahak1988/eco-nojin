import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";

export interface ApiError {
  type: string;
  title: string;
  status: number;
  detail?: string;
  instance?: string;
}

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      headers: { "Content-Type": "application/json" },
      timeout: 30000,
    });

    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem("econojin_token");
      if (token) config.headers.Authorization = `Bearer ${token}`;
      return config;
    });

    this.client.interceptors.response.use(
      (res) => res,
      (error) => {
        if (error.response?.status === 401 && typeof window !== "undefined") {
          localStorage.removeItem("econojin_token");
          localStorage.removeItem("econojin_user");
          if (!window.location.pathname.startsWith("/login")) {
            window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`;
          }
        }
        const apiError: ApiError = error.response?.data?.detail
          ? {
              type: "api_error",
              title: "خطای API",
              status: error.response.status,
              detail:
                typeof error.response.data.detail === "string"
                  ? error.response.data.detail
                  : JSON.stringify(error.response.data.detail),
            }
          : error.response?.data || {
              type: "network_error",
              title: "خطای شبکه",
              status: error.response?.status || 0,
              detail: error.message,
            };
        return Promise.reject(apiError);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res: AxiosResponse<T> = await this.client.get(url, config);
    return res.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const res: AxiosResponse<T> = await this.client.post(url, data, config);
    return res.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const res: AxiosResponse<T> = await this.client.put(url, data, config);
    return res.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res: AxiosResponse<T> = await this.client.delete(url, config);
    return res.data;
  }
}

export const api = new ApiClient(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");

// سرویس‌های ماژول‌ها
export const healthService = {
  check: () => api.get<{ status: string; version: string; modules?: string[] }>("/api/v1/health"),
  modules: () => api.get<{ modules: Array<{ id: string; name: string; status: string }> }>("/api/v1/modules"),
};

export const dashboardService = {
  stats: () =>
    api.get<{
      active_users: number;
      active_modules: number;
      monthly_growth_percent: number;
      api_status: string;
      modules_online: string[];
    }>("/api/v1/dashboard/stats"),
};

export const accountingService = {
  summary: () =>
    api.get<{
      total_income: number;
      total_expense: number;
      net_profit: number;
      currency: string;
    }>("/api/v1/accounting/summary"),
  transactions: (limit = 10) =>
    api.get<{ transactions: Array<{ id: number; type: string; amount: number; date: string }> }>(
      `/api/v1/accounting/transactions?limit=${limit}`
    ),
};

export const weatherService = {
  getForecast: (location: string, days: number = 7) => 
    api.get(`/api/v1/weather/forecast?location=${encodeURIComponent(location)}&days=${days}`),
  getAlerts: (region: string) => api.get(`/api/v1/weather/alerts?region=${encodeURIComponent(region)}`),
};

export const economicService = {
  simulateProfit: (data: any) => api.post("/api/v1/economic/simulate/profit", data),
  monteCarlo: (data: any, iterations?: number) => 
    api.post(`/api/v1/economic/simulate/montecarlo${iterations ? `?iterations=${iterations}` : ""}`, data),
  sensitivity: (base: any, param: string, rangePercent: number) =>
    api.post(`/api/v1/economic/sensitivity?param=${param}&range_percent=${rangePercent}`, base),
};

export const analysisService = {
  startStream: (query: string, region: string, crop?: string, area?: number) =>
    api.post("/api/v1/analyze/stream", { query, region, crop, area_ha: area }),
  getAnalyses: (limit: number = 20, region?: string) =>
    api.get(`/api/v1/analyses?limit=${limit}${region ? `&region=${encodeURIComponent(region)}` : ""}`),
};

export const gisService = {
  calculateArea: (coordinates: [number, number][]) =>
    api.post("/api/v1/gis/calculate/area", coordinates),
  getLayers: () => gisLayers.get(),
  getMapTiles: (z: number, x: number, y: number) =>
    api.get(`/api/v1/gis/map/tiles?z=${z}&x=${x}&y=${y}`),
};

export const ecominingService = {
  mine: (
    actionType: string,
    amount: number,
    location: string,
    carbon_kg = 0,
    water_saved_liters = 0
  ) =>
    api.post("/api/v1/ecomining/mine", null, {
      params: {
        action_type: actionType,
        amount,
        location,
        carbon_kg,
        water_saved_liters,
      },
    }),
  getBalance: () => api.get("/api/v1/ecomining/balance"),
};

// Calendar Service
export const calendarService = {
  list: (params?: Record<string, string | number>) =>
    api.get<{ items: Array<{ id: number; title: string; start_time: string; category: string }>; total: number }>(
      "/api/v1/calendar/",
      { params }
    ),
  get: (id: number) => api.get(`/api/v1/calendar/${id}`),
  create: (data: unknown) => api.post("/api/v1/calendar/", data),
  update: (id: number, data: unknown) => api.put(`/api/v1/calendar/${id}`, data),
  delete: (id: number) => api.delete(`/api/v1/calendar/${id}`),
  upcoming: (hours?: number) =>
    api.get(`/api/v1/calendar/upcoming${hours ? `?hours=${hours}` : ""}`),
};

export const authService = {
  login: (fid: string, phone: string, name?: string) =>
    api.post<{ access_token: string; farmer_id: string }>("/api/v1/auth/login", {
      fid,
      phone,
      name: name || "",
    }),
  requestOtp: (phone: string, fid?: string) =>
    api.post<{ sent: boolean; dev_code?: string }>("/api/v1/auth/otp/request", {
      phone,
      fid: fid || "",
    }),
  verifyOtp: (phone: string, code: string, fid: string, name?: string) =>
    api.post<{ access_token: string; farmer_id: string }>("/api/v1/auth/otp/verify", {
      phone,
      code,
      fid,
      name: name || "",
    }),
  profile: () => api.get("/api/v1/auth/profile"),
};

export const aiService = {
  chat: (message: string, locale: string, module: string) =>
    api.post<{ reply: string; suggestions: string[] }>("/api/v1/ai/chat", {
      message,
      locale,
      module,
    }),
};

export const simulationService = {
  rothc: (data: Record<string, number>) => api.post("/api/v1/simulation/rothc", data),
  aquacrop: (data: Record<string, number | string>) =>
    api.post("/api/v1/simulation/aquacrop", data),
  coupling: (modules: unknown[]) => api.post("/api/v1/simulation/coupling", { modules }),
};

export const gisLayers = {
  get: () =>
    api.get<{
      base: { url: string; attribution: string };
      default_center: [number, number];
      default_zoom: number;
    }>("/api/v1/gis/layers"),
};

export const farmerService = {
  list: (skip = 0, limit = 50) =>
    api.get<{ total: number; farmers: Array<{ id: number; name: string }> }>(
      `/api/v1/farmers/?skip=${skip}&limit=${limit}`
    ),
  create: (data: unknown) => api.post("/api/v1/farmers/", data),
};
