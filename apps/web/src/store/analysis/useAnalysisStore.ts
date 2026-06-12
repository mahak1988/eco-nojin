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