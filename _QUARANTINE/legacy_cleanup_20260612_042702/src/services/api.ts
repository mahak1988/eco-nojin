import { Analysis, Region, AnalysisRequest, AnalysisResponse } from '../types';

// نکته: در پروژه واقعی، این آدرس را از فایل .env بخوانید
// مثال: const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const API_BASE_URL = 'http://localhost:8000/api/v1';

export const api = {
  async getRegions(): Promise<Region[]> {
    const res = await fetch(`${API_BASE_URL}/regions`);
    if (!res.ok) throw new Error('خطا در دریافت لیست مناطق');
    const data = await res.json();
    return data.regions ?? data;
  },

  async getAnalyses(): Promise<Analysis[]> {
    const res = await fetch(`${API_BASE_URL}/analyses`);
    if (!res.ok) throw new Error('خطا در دریافت لیست تحلیل‌ها');
    const data = await res.json();
    return data.analyses ?? data;
  },

  async startAnalysis(payload: AnalysisRequest): Promise<AnalysisResponse> {
    const res = await fetch(`${API_BASE_URL}/analyze/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('خطا در شروع فرآیند تحلیل');
    return res.json();
  }
};