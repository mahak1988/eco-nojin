/**
 * library hooks | هوک‌های React Query برای library
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

import { libraryApi } from "../api";
import type { Library, LibraryCreate, LibraryUpdate } from "../types";

const QUERY_KEY = "library";

export function useListLibrarys(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: [QUERY_KEY, "list", params],
    queryFn: () => libraryApi.list(params),
  });
}

export function useLibrary(id: number, options?: Partial<UseQueryOptions<Library>>) {
  return useQuery({
    queryKey: [QUERY_KEY, "detail", id],
    queryFn: () => libraryApi.get(id),
    enabled: !!id,
    ...options,
  });
}

export function useCreateLibrary() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: LibraryCreate) => libraryApi.create(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

export function useUpdateLibrary() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: LibraryUpdate }) =>
      libraryApi.update(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}

export function useDeleteLibrary() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => libraryApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
}
