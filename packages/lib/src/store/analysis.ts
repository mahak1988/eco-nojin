import { create } from 'zustand';

interface AnalysisState {
  data: unknown;
  setData: (data: unknown) => void;
}

export const useAnalysisStore = create<AnalysisState>((set: (partial: Partial<AnalysisState>) => void) => ({
  data: null,
  setData: (data: unknown) => set({ data }),
}));