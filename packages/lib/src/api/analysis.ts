import axios from 'axios';
import type {
  Analysis,
  Region,
  AnalysisRequest,
  AnalysisResponse,
} from '../types/analysis';

// ایجاد instance محور axios
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Interceptor برای مدیریت خطاها
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.message || error.message || 'خطای ناشناخته';
    return Promise.reject(new Error(message));
  }
);

export const analysisApi = {
  /**
   * دریافت لیست مناطق
   */
  async getRegions(): Promise<Region[]> {
    const { data } = await apiClient.get<Region[] | { regions: Region[] }>('/regions');
    return Array.isArray(data) ? data : data.regions ?? [];
  },

  /**
   * دریافت لیست تحلیل‌ها
   */
  async getAnalyses(): Promise<Analysis[]> {
    const { data } = await apiClient.get<Analysis[] | { analyses: Analysis[] }>('/analyses');
    return Array.isArray(data) ? data : data.analyses ?? [];
  },

  /**
   * شروع تحلیل جدید
   */
  async startAnalysis(payload: AnalysisRequest): Promise<AnalysisResponse> {
    const { data } = await apiClient.post<AnalysisResponse>('/analyze/stream', payload);
    return data;
  },
};