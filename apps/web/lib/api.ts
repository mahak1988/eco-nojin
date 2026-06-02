import axios from 'axios';
import { simulateCarbonCalculation, generateMockPortfolio } from '@/lib/simulators/carbon_calculator';
import { SentinelSimulator } from '@/lib/simulators/sentinel2';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

// Response interceptor with graceful fallback
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.warn('API Error:', error.message);
    return Promise.reject(error);
  }
);

// Gaia API with simulator fallback
export const gaiaApi = {
  calculateCarbon: async (data: any) => {
    try {
      const response = await api.post('/gaia/calculate', data);
      return response;
    } catch {
      // Fallback to simulator
      const result = simulateCarbonCalculation(data);
      return { data: result, fromSimulator: true };
    }
  },
  
  getStats: async () => {
    try {
      return await api.get('/gaia/stats');
    } catch {
      return { 
        data: {
          total_activities: 156,
          total_carbon_kg: 203558.45,
          total_carbon_tons: 203.56,
          equivalent_trees: 9253,
          estimated_value_usd: 10177.92,
          by_activity: {
            tree_planting: { count: 85, carbon_kg: 154000 },
            soil_regeneration: { count: 32, carbon_kg: 28000 },
            agroforestry: { count: 24, carbon_kg: 15558 },
          },
          timestamp: new Date().toISOString(),
        },
        fromSimulator: true 
      };
    }
  },
  
  verifySatellite: async (data: any) => {
    try {
      return await api.post('/gaia/verify-satellite', data);
    } catch {
      // Fallback to Sentinel simulator
      const result = SentinelSimulator.verify(
        data.latitude,
        data.longitude,
        new Date(data.activity_date || Date.now()),
        data.activity_type
      );
      return { data: result, fromSimulator: true };
    }
  },
  
  getPortfolio: async (address: string) => {
    try {
      return await api.get(`/gaia/portfolio/${address}`);
    } catch {
      return { data: generateMockPortfolio(address), fromSimulator: true };
    }
  },
};

// Farmer API
export const farmerApi = {
  list: async (skip = 0, limit = 100) => {
    try {
      return await api.get(`/farmer/farmers/?skip=${skip}&limit=${limit}`);
    } catch {
      return { 
        data: {
          farmers: [
            { id: 1, name: 'Ali Rezaei', farm_location: 'Tehran, Iran', farm_size_hectares: 15.5 },
            { id: 2, name: 'Sara Mohammadi', farm_location: 'Isfahan, Iran', farm_size_hectares: 8.2 },
            { id: 3, name: 'Hassan Karimi', farm_location: 'Shiraz, Iran', farm_size_hectares: 22.0 },
          ],
          total: 3,
        },
        fromSimulator: true 
      };
    }
  },
};

export default api;
