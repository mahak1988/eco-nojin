// Stub for useScenarioApi - Phase 0 fix
// TODO: Implement actual API integration in Phase 1

export interface ScenarioRun {
  id: string;
  name: string;
  status: 'idle' | 'running' | 'completed' | 'failed';
  metrics?: Record<string, number>;
}

export function useScenarioApi(): { runs: ScenarioRun[]; loading: boolean; error: string | null } {
  return { runs: [], loading: false, error: null };
}

export interface ChainResult { id: string; status: string; }
export interface ChainStep { id: string; label: string; }
export function useCreateChain(): { create: (data: Record<string, unknown>) => Promise<ChainResult> } { return { create: async () => ({ id: '', status: 'pending' }) }; }
export function useRunChain(): { run: (id: string) => Promise<ChainResult> } { return { run: async () => ({ id: '', status: 'pending' }) }; }
export function useCreateComparison(): { create: (data: Record<string, unknown>) => Promise<{ id: string }> } { return { create: async () => ({ id: '' }) }; }
export interface ComparisonResult { id: string; status: string; }
