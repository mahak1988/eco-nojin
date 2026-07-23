/**
 * هوک‌های API سناریو و مقایسه
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../client";
import { ENDPOINTS } from "../endpoints";
import { toast } from "react-hot-toast";

// ─── Types ──────────────────────────────────────────────────

export interface PresetScenario {
  id: string;
  name: string;
  name_en: string;
  description: string;
  category: string;
  params: Record<string, any>;
}

export interface ScenarioResult {
  scenario_id: string;
  scenario_name: string;
  metrics: Record<string, any>;
  outputs?: Record<string, any>;
  execution_time_ms?: number;
  status: string;
}

export interface ComparisonData {
  metrics_comparison: Record<string, Record<string, number>>;
  charts: Record<string, any>;
}

export interface ComparisonResult {
  id: string;
  name: string;
  scenarios: Array<{
    id: string;
    name: string;
    simulator_id: string;
    metrics: Record<string, any>;
    outputs?: Record<string, any>;
    status: string;
  }>;
  comparison_type: string;
  comparison_data: ComparisonData;
  notes?: string;
}

export interface ChainStep {
  step: number;
  simulator_id: string;
  status: string;
  metrics: Record<string, any>;
  execution_time_ms?: number;
  error?: string;
}

export interface ChainResult {
  chain_id: string;
  chain_name: string;
  steps: ChainStep[];
  final_outputs: Record<string, any>;
  total_execution_time_ms: number;
}

// ─── Hooks: سناریوهای پیش‌فرض ──────────────────────────────

export function usePresetScenarios(simulatorId: string) {
  return useQuery({
    queryKey: ["presets", simulatorId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/v1/simulation/presets/${simulatorId}`);
      return data as { simulator_id: string; scenarios: PresetScenario[] };
    },
    enabled: !!simulatorId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useAllPresets() {
  return useQuery({
    queryKey: ["presets", "all"],
    queryFn: async () => {
      const { data } = await apiClient.get("/api/v1/simulation/presets");
      return data as Array<{ simulator_id: string; scenarios: PresetScenario[] }>;
    },
    staleTime: 5 * 60 * 1000,
  });
}

// ─── Hooks: اجرای سناریو ───────────────────────────────────

export function useRunScenario() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      scenarioId: string;
      overrideParams?: Record<string, any>;
    }) => {
      const { data } = await apiClient.post(
        `/api/v1/simulation/scenarios/${params.scenarioId}/run`,
        { override_params: params.overrideParams }
      );
      return data as ScenarioResult;
    },
    onSuccess: (data) => {
      toast.success(`سناریوی «${data.scenario_name}» با موفقیت اجرا شد`);
      queryClient.invalidateQueries({ queryKey: ["scenario-results"] });
    },
    onError: (error: any) => {
      toast.error(`خطا در اجرای سناریو: ${error.message}`);
    },
  });
}

// ─── Hooks: مقایسه ─────────────────────────────────────────

export function useCreateComparison() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      name: string;
      scenarioIds: string[];
      comparisonType?: string;
      notes?: string;
    }) => {
      const { data } = await apiClient.post("/api/v1/simulation/comparisons", {
        name: params.name,
        scenario_ids: params.scenarioIds,
        comparison_type: params.comparisonType || "side_by_side",
        notes: params.notes,
      });
      return data as ComparisonResult;
    },
    onSuccess: (data) => {
      toast.success(`مقایسهٔ «${data.name}» ایجاد شد`);
      queryClient.invalidateQueries({ queryKey: ["comparisons"] });
    },
    onError: (error: any) => {
      toast.error(`خطا در ایجاد مقایسه: ${error.message}`);
    },
  });
}

export function useComparisons() {
  return useQuery({
    queryKey: ["comparisons"],
    queryFn: async () => {
      const { data } = await apiClient.get("/api/v1/simulation/comparisons");
      return data as any[];
    },
  });
}

// ─── Hooks: زنجیره‌سازی ────────────────────────────────────

export function useRunChain() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (chainId: string) => {
      const { data } = await apiClient.post(
        `/api/v1/simulation/chains/${chainId}/run`
      );
      return data as ChainResult;
    },
    onSuccess: (data) => {
      toast.success(`زنجیرهٔ «${data.chain_name}» اجرا شد`);
      queryClient.invalidateQueries({ queryKey: ["chains"] });
    },
    onError: (error: any) => {
      toast.error(`خطا در اجرای زنجیره: ${error.message}`);
    },
  });
}

export function useCreateChain() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      name: string;
      steps: Array<{
        simulator_id: string;
        params: Record<string, any>;
        input_from?: string;
        output_mapping?: Record<string, string>;
      }>;
    }) => {
      const { data } = await apiClient.post("/api/v1/simulation/chains", params);
      return data;
    },
    onSuccess: () => {
      toast.success("زنجیرهٔ مدل ایجاد شد");
      queryClient.invalidateQueries({ queryKey: ["chains"] });
    },
  });
}

export function useChains() {
  return useQuery({
    queryKey: ["chains"],
    queryFn: async () => {
      const { data } = await apiClient.get("/api/v1/simulation/chains");
      return data as any[];
    },
  });
}
