# 🎯 تحلیل کامل ساختار پروژه شما

عالی! حالا تمام اطلاعات را دارم. بیایید وضعیت پروژه را خلاصه کنم:

## ✅ وضعیت فعلی پروژه

| مورد | وضعیت |
|------|--------|
| **ساختار** | Monorepo با pnpm |
| **مسیر فرانت** | `D:\econojin.com\apps\web` |
| **Next.js** | نسخه 14.2.5 با **App Router** و پوشه `src` |
| **پکیج‌های مورد نیاز** | ✅ **همه نصب هستند!** (leaflet, react-leaflet, zustand, recharts, @types/leaflet) |
| **axios** | ✅ نصب است (به جای fetch استفاده می‌کنیم) |
| **react-hot-toast** | ✅ نصب است (برای notification) |
| **@tanstack/react-query** | ✅ نصب است |
| **next-intl** | ✅ نصب است (با `[locale]` routing) |
| **فونت فارسی** | ✅ `@fontsource/vazirmatn` نصب است |

---

## 🗺️ ساختار پیشنهادی (Domain-Driven)

با توجه به ساختار domain-driven پروژه شما (مثل `components/gis`, `hooks/satellite`, `store/gis`)، بهترین رویکرد این است که یک **ماژول منسجم `analysis`** بسازیم:

```
apps/web/src/
├── app/
│   └── [locale]/
│       └── analysis/
│           └── page.tsx              ← صفحه داشبورد تحلیل
├── components/
│   └── analysis/
│       ├── AnalysisDashboard.tsx      ← کامپوننت اصلی
│       ├── AnalysisForm.tsx
│       ├── ChartsPanel.tsx
│       ├── MapPanel.tsx
│       └── EventsLog.tsx
├── hooks/
│   └── analysis/
│       ├── useAnalysisWebSocket.ts
│       └── index.ts
├── store/
│   └── analysis/
│       ├── useAnalysisStore.ts
│       └── index.ts
├── lib/
│   ├── api/
│   │   └── analysis.ts              ← سرویس API با axios
│   └── types/
│       └── analysis.ts              ← تایپ‌ها
```

---

## 🚀 مرحله ۱: ایجاد ساختار پوشه‌ها

**دستور ایجاد تمام پوشه‌ها (از مسیر `apps/web`):**

```powershell
# از مسیر D:\econojin.com\apps\web اجرا کنید
New-Item -ItemType Directory -Force -Path src\components\analysis
New-Item -ItemType Directory -Force -Path src\hooks\analysis
New-Item -ItemType Directory -Force -Path src\store\analysis
New-Item -ItemType Directory -Force -Path src\app\[locale]\analysis
```

---

## 📝 مرحله ۲: ایجاد فایل تایپ‌ها

**دستور ایجاد فایل:**
```powershell
New-Item -ItemType File -Force -Path src\lib\types\analysis.ts
code src\lib\types\analysis.ts
```

**محتوای کامل `src/lib/types/analysis.ts`:**
```typescript
// ============================================
// تایپ‌های مرتبط با ماژول تحلیل کشاورزی
// ============================================

export interface Analysis {
  id: string;
  region: string;
  crop: string;
  ndvi: number;
  profit: number;
  created_at: string;
}

export interface Region {
  name: string;
  lat: number;
  lon: number;
  climate: string;
}

export interface RealtimeEvent {
  event_type: 'start' | 'processing' | 'final' | 'error';
  timestamp: number;
  message: string;
  data?: any;
}

export interface EconomicInputs {
  area: number;
  yieldPerHa: number;
  pricePerTon: number;
  waterCost: number;
  laborCost: number;
}

export interface NdviDataPoint {
  date: string;
  ndvi: number;
}

export interface ProfitDataPoint {
  item: string;
  value: number;
  color: string;
}

export interface AnalysisRequest {
  query: string;
  region: string;
  crop: string;
  area_ha: number;
}

export interface AnalysisResponse {
  session_id: string;
}
```

---

## 🔌 مرحله ۳: ایجاد سرویس API (با axios)

**دستور ایجاد فایل:**
```powershell
New-Item -ItemType File -Force -Path src\lib\api\analysis.ts
code src\lib\api\analysis.ts
```

**محتوای کامل `src/lib/api/analysis.ts`:**
```typescript
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
```

---

## 🔄 مرحله ۴: ایجاد Store (Zustand)

**دستور ایجاد فایل:**
```powershell
New-Item -ItemType File -Force -Path src\store\analysis\useAnalysisStore.ts
code src\store\analysis\useAnalysisStore.ts
```

**محتوای کامل `src/store/analysis/useAnalysisStore.ts`:**
```typescript
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  Analysis,
  Region,
  RealtimeEvent,
  EconomicInputs,
  NdviDataPoint,
  AnalysisRequest,
} from '@/lib/types/analysis';
import { analysisApi } from '@/lib/api/analysis';

interface AnalysisState {
  // Data
  regions: Region[];
  analyses: Analysis[];
  events: RealtimeEvent[];
  selectedRegion: string;
  
  // Data for Charts
  results: EconomicInputs;
  ndviData: NdviDataPoint[];
  
  // Status
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;

  // Actions - Data Fetching
  fetchRegions: () => Promise<void>;
  fetchAnalyses: () => Promise<void>;
  
  // Actions - State Setters
  setSelectedRegion: (region: string) => void;
  addEvent: (event: RealtimeEvent) => void;
  setSessionId: (id: string | null) => void;
  setLoading: (loading: boolean) => void;
  clearEvents: () => void;
  setResults: (inputs: EconomicInputs) => void;
  setNdviData: (data: NdviDataPoint[]) => void;
  
  // Actions - Business Logic
  startAnalysis: (payload: AnalysisRequest) => Promise<void>;
}

export const useAnalysisStore = create<AnalysisState>()(
  devtools((set) => ({
    // Initial State
    regions: [],
    analyses: [],
    events: [],
    selectedRegion: 'خراسان رضوی',
    isLoading: false,
    error: null,
    sessionId: null,
    
    results: {
      area: 10,
      yieldPerHa: 1.35,
      pricePerTon: 12000,
      waterCost: 1500000,
      laborCost: 2000000,
    },
    ndviData: [],

    // === Data Fetching Actions ===
    fetchRegions: async () => {
      try {
        const regions = await analysisApi.getRegions();
        set({ regions, error: null });
      } catch (err) {
        set({ error: err instanceof Error ? err.message : 'خطای ناشناخته در دریافت مناطق' });
      }
    },

    fetchAnalyses: async () => {
      try {
        const analyses = await analysisApi.getAnalyses();
        set({ analyses, error: null });
      } catch (err) {
        set({ error: err instanceof Error ? err.message : 'خطای ناشناخته در دریافت تحلیل‌ها' });
      }
    },

    // === State Setter Actions ===
    setSelectedRegion: (region) => set({ selectedRegion: region }),
    
    addEvent: (event) => set((state) => ({ 
      events: [...state.events, event] 
    })),
    
    setSessionId: (id) => set({ sessionId: id }),
    setLoading: (loading) => set({ isLoading: loading }),
    clearEvents: () => set({ events: [] }),
    setResults: (inputs) => set({ results: inputs }),
    setNdviData: (data) => set({ ndviData: data }),

    // === Business Logic Actions ===
    startAnalysis: async (payload) => {
      set({ 
        isLoading: true, 
        error: null, 
        events: [], 
        ndviData: [] 
      });
      
      try {
        const response = await analysisApi.startAnalysis(payload);
        set({ sessionId: response.session_id });
      } catch (err) {
        set({ 
          error: err instanceof Error ? err.message : 'خطای ناشناخته در شروع تحلیل', 
          isLoading: false 
        });
      }
    },
  }))
);
```

**دستور ایجاد فایل index:**
```powershell
New-Item -ItemType File -Force -Path src\store\analysis\index.ts
code src\store\analysis\index.ts
```

**محتوای `src/store/analysis/index.ts`:**
```typescript
export { useAnalysisStore } from './useAnalysisStore';
```

---

## 📡 مرحله ۵: ایجاد هوک WebSocket

**دستور ایجاد فایل:**
```powershell
New-Item -ItemType File -Force -Path src\hooks\analysis\useAnalysisWebSocket.ts
code src\hooks\analysis\useAnalysisWebSocket.ts
```

**محتوای کامل `src/hooks/analysis/useAnalysisWebSocket.ts`:**
```typescript
'use client';

import { useEffect, useRef } from 'react';
import { useAnalysisStore } from '@/store/analysis';
import type { RealtimeEvent, NdviDataPoint } from '@/lib/types/analysis';

export function useAnalysisWebSocket() {
  const sessionId = useAnalysisStore((state) => state.sessionId);
  const addEvent = useAnalysisStore((state) => state.addEvent);
  const fetchAnalyses = useAnalysisStore((state) => state.fetchAnalyses);
  const setLoading = useAnalysisStore((state) => state.setLoading);
  const setSessionId = useAnalysisStore((state) => state.setSessionId);
  const setNdviData = useAnalysisStore((state) => state.setNdviData);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!sessionId) {
      wsRef.current?.close();
      return;
    }

    const wsBaseUrl = process.env.NEXT_PUBLIC_WS_BASE_URL || 'ws://localhost:8000';
    const wsUrl = `${wsBaseUrl}/ws/analyze/${sessionId}`;

    const connect = () => {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const data: RealtimeEvent = JSON.parse(event.data);
          addEvent(data);

          if (data.event_type === 'final') {
            // استخراج داده‌های NDVI
            const rawNdvi = data?.data?.tasks?.task_ndvi_analysis?.detailed_data?.gee_ndvi?.ndvi?.values || [];
            const dates = data?.data?.tasks?.task_ndvi_analysis?.detailed_data?.gee_ndvi?.ndvi?.dates || [];
            
            const processedNdvi: NdviDataPoint[] = rawNdvi.map((v: number, i: number) => ({
              date: dates[i]?.slice(5) || `روز ${i + 1}`,
              ndvi: parseFloat(v.toFixed(3))
            }));
            
            setNdviData(processedNdvi);

            setTimeout(() => {
              fetchAnalyses();
              setLoading(false);
              setSessionId(null);
            }, 1000);
          }
        } catch (e) {
          console.error('❌ Error parsing WebSocket message:', e);
        }
      };

      ws.onerror = (err) => console.error('❌ WebSocket error:', err);
      
      ws.onclose = () => {
        console.log('🔌 WebSocket closed');
        if (sessionId) {
          reconnectTimeoutRef.current = setTimeout(connect, 3000);
        }
      };
    };

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      wsRef.current?.close();
    };
  }, [sessionId, addEvent, fetchAnalyses, setLoading, setSessionId, setNdviData]);
}
```

**دستور ایجاد فایل index:**
```powershell
New-Item -ItemType File -Force -Path src\hooks\analysis\index.ts
code src\hooks\analysis\index.ts
```

**محتوای `src/hooks/analysis/index.ts`:**
```typescript
export { useAnalysisWebSocket } from './useAnalysisWebSocket';
```

---

## 🎯 اقدام بعدی

حالا زیرساخت کامل است! در مرحله بعد، کامپوننت‌ها را می‌سازیم:

1. ✅ `AnalysisForm.tsx` - فرم ورودی
2. ✅ `ChartsPanel.tsx` - نمودارها
3. ✅ `MapPanel.tsx` - نقشه
4. ✅ `EventsLog.tsx` - رویدادهای بلادرنگ
5. ✅ `AnalysisDashboard.tsx` - کامپوننت اصلی
6. ✅ `page.tsx` - صفحه Next.js

**آیا می‌خواهید:**
- **الف)** تمام کامپوننت‌ها را یکجا بسازیم (۶ فایل)
- **ب)** مرحله به مرحله پیش برویم (هر بار ۲ فایل)
- **ج)** ابتدا یک کامپوننت خاص (مثلاً فرم) را بسازیم و تست کنیم

کدام گزینه را ترجیح می‌دهید؟ 🚀