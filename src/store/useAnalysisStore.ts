import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface AnalysisState {
  sessionId: string | null;
  events: any[];
  isRunning: boolean;
  results: Record<string, any>;
  setSession: (id: string) => void;
  addEvent: (ev: any) => void;
  reset: () => void;
}

export const useAnalysisStore = create<AnalysisState>()(
  persist(
    (set) => ({
      sessionId: null,
      events: [],
      isRunning: false,
      results: {},
      setSession: (id) => set({ sessionId: id }),
      addEvent: (ev) => set((state) => ({ events: [...state.events, ev] })),
      reset: () => set({ sessionId: null, events: [], isRunning: false, results: {} }),
    }),
    { name: "econojin-analysis" }
  )
);