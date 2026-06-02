import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface AnalysisEvent {
  event_type: string;
  message: string;
  data?: any;
  timestamp: number;
}

export interface AppState {
  // UI State
  sidebarOpen: boolean;
  theme: "light" | "dark";
  currentModule: string | null;
  
  // Analysis State
  activeSession: string | null;
  analysisEvents: AnalysisEvent[];
  isAnalyzing: boolean;
  lastResult: any | null;
  
  // User State
  user: { fid?: string; name?: string; phone?: string; email?: string; role?: string } | null;
  token: string | null;
  
  // Actions
  toggleSidebar: () => void;
  setTheme: (theme: "light" | "dark") => void;
  setCurrentModule: (module: string | null) => void;
  
  setSession: (sessionId: string) => void;
  addEvent: (event: AnalysisEvent) => void;
  setAnalyzing: (status: boolean) => void;
  setResult: (result: any) => void;
  clearAnalysis: () => void;
  
  login: (token: string, user?: any) => void;
  logout: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial State
      sidebarOpen: true,
      theme: "dark",
      currentModule: null,
      activeSession: null,
      analysisEvents: [],
      isAnalyzing: false,
      lastResult: null,
      user: null,
      token: null,
      
      // UI Actions
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setTheme: (theme) => set({ theme }),
      setCurrentModule: (module) => set({ currentModule: module }),
      
      // Analysis Actions
      setSession: (sessionId) => set({ activeSession: sessionId }),
      addEvent: (event) => set((state) => ({ 
        analysisEvents: [...state.analysisEvents.slice(-49), event] // Keep last 50
      })),
      setAnalyzing: (status) => set({ isAnalyzing: status }),
      setResult: (result) => set({ lastResult: result }),
      clearAnalysis: () => set({ activeSession: null, analysisEvents: [], lastResult: null, isAnalyzing: false }),
      
      // Auth Actions
      login: (token, user) => set({ token, user }),
      logout: () => set({ token: null, user: null }),
    }),
    { name: "econojin-store", partialize: (state) => ({ theme, token, user }) }
  )
);
