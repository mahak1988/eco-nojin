/**
 * web hooks | هوک‌های React Query برای web
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

import { webApi } from "../api";
import type { HydrologyFrontend, HydrologyFrontendCreate, HydrologyFrontendUpdate } from "../types";

const QUERY_KEY = "web";

export function useListHydrologyFrontends(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: [QUERY_KEY, "list", params],
    queryFn: () => webApi.list(params),
  });
}

export function useHydrologyFrontend(id: number, options?: Partial<UseQueryOptions<HydrologyFrontend>>) {
  return useQuery({
    queryKey: [QUERY_KEY, "detail", id],
    queryFn: () => webApi.get(id),
    enabled: !!id,
    ...options,
  });
}

export function useCreateHydrologyFrontend() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: HydrologyFrontendCreate) => webApi.create(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

export function useUpdateHydrologyFrontend() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: HydrologyFrontendUpdate }) =>
      webApi.update(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

export function useDeleteHydrologyFrontend() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => webApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}
