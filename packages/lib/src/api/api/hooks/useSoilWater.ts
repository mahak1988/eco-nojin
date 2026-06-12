import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../client";
import { ENDPOINTS } from "../endpoints";
import { toast } from "react-hot-toast";
import type {
  ComprehensiveAnalysisRequest,
  ComprehensiveAnalysisResponse,
  Project,
  AnalysisReport,
  DashboardStats,
} from "../types/soilWater.types";

// ============================================================================
// DASHBOARD STATS
// ============================================================================
export function useDashboardStats() {
  return useQuery({
    queryKey: ["soil-water", "stats"],
    queryFn: async (): Promise<DashboardStats> =>
      apiClient.get(ENDPOINTS.SOIL_WATER.STATS),
    staleTime: 30 * 1000,
  });
}

// ============================================================================
// COMPREHENSIVE ANALYSIS
// ============================================================================
export function useComprehensiveAnalysis() {
  return useMutation({
    mutationFn: async (
      data: ComprehensiveAnalysisRequest
    ): Promise<ComprehensiveAnalysisResponse> =>
      apiClient.post(ENDPOINTS.SOIL_WATER.COMPREHENSIVE, data),
    onError: (error: any) => {
      toast.error(error?.PersianMessage || error?.message || "خطا در تحلیل");
    },
  });
}

// ============================================================================
// PROJECTS CRUD
// ============================================================================
export function useProjects(status?: string) {
  return useQuery({
    queryKey: ["soil-water", "projects", status],
    queryFn: async (): Promise<{ total: number; items: Project[] }> => {
      const params = status ? `?status=${status}` : "";
      return apiClient.get(ENDPOINTS.SOIL_WATER.PROJECTS.LIST + params);
    },
  });
}

export function useProject(id: number) {
  return useQuery({
    queryKey: ["soil-water", "projects", id],
    queryFn: async (): Promise<Project> =>
      apiClient.get(ENDPOINTS.SOIL_WATER.PROJECTS.DETAIL(id)),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: any): Promise<Project> =>
      apiClient.post(ENDPOINTS.SOIL_WATER.PROJECTS.CREATE, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["soil-water", "projects"] });
      toast.success("پروژه با موفقیت ایجاد شد");
    },
    onError: () => toast.error("خطا در ایجاد پروژه"),
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: any }): Promise<Project> =>
      apiClient.patch(ENDPOINTS.SOIL_WATER.PROJECTS.UPDATE(id), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["soil-water", "projects"] });
      toast.success("پروژه به‌روزرسانی شد");
    },
    onError: () => toast.error("خطا در به‌روزرسانی"),
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number): Promise<void> =>
      apiClient.delete(ENDPOINTS.SOIL_WATER.PROJECTS.DELETE(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["soil-water", "projects"] });
      toast.success("پروژه حذف شد");
    },
    onError: () => toast.error("خطا در حذف پروژه"),
  });
}

// ============================================================================
// ANALYSIS REPORTS CRUD
// ============================================================================
export function useReports(projectId?: number) {
  return useQuery({
    queryKey: ["soil-water", "reports", projectId],
    queryFn: async (): Promise<{ total: number; items: AnalysisReport[] }> => {
      const params = projectId ? `?project_id=${projectId}` : "";
      return apiClient.get(ENDPOINTS.SOIL_WATER.REPORTS.LIST + params);
    },
  });
}

export function useReport(id: number) {
  return useQuery({
    queryKey: ["soil-water", "reports", id],
    queryFn: async (): Promise<AnalysisReport> =>
      apiClient.get(ENDPOINTS.SOIL_WATER.REPORTS.DETAIL(id)),
    enabled: !!id,
  });
}

export function useCreateReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: any): Promise<AnalysisReport> =>
      apiClient.post(ENDPOINTS.SOIL_WATER.REPORTS.CREATE, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["soil-water", "reports"] });
      queryClient.invalidateQueries({ queryKey: ["soil-water", "projects"] });
      queryClient.invalidateQueries({ queryKey: ["soil-water", "stats"] });
      toast.success("تحلیل با موفقیت ذخیره شد");
    },
    onError: () => toast.error("خطا در ذخیره تحلیل"),
  });
}

export function useDeleteReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number): Promise<void> =>
      apiClient.delete(ENDPOINTS.SOIL_WATER.REPORTS.DELETE(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["soil-water", "reports"] });
      queryClient.invalidateQueries({ queryKey: ["soil-water", "stats"] });
      toast.success("تحلیل حذف شد");
    },
    onError: () => toast.error("خطا در حذف تحلیل"),
  });
}
