/**
 * cms hooks | هوک‌های React Query برای cms
 *
 * Auto-scaffolded by phase1_complete_apps.py
 * Requires @tanstack/react-query to be installed in the workspace.
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
} from "@tanstack/react-query";

import { cmsApi } from "../api";
import type { Cms, CmsCreate, CmsUpdate } from "../types";

const QUERY_KEY = "cms";

export function useListCmss(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: [QUERY_KEY, "list", params],
    queryFn: () => cmsApi.list(params),
  });
}

export function useCms(id: number, options?: Partial<UseQueryOptions<Cms>>) {
  return useQuery({
    queryKey: [QUERY_KEY, "detail", id],
    queryFn: () => cmsApi.get(id),
    enabled: !!id,
    ...options,
  });
}

export function useCreateCms() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CmsCreate) => cmsApi.create(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

export function useUpdateCms() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: CmsUpdate }) =>
      cmsApi.update(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

export function useDeleteCms() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => cmsApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}
