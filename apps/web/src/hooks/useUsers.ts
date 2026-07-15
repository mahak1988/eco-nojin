/**
 * ============================================================================
 *  useUsers — React Query hooks for user operations
 * ============================================================================
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
} from "@tanstack/react-query";
import { userService, UserCreate, UserUpdate } from "@/services/userService";
import type { User } from "@/types";

export const userKeys = {
  all: ["users"] as const,
  lists: () => [...userKeys.all, "list"] as const,
  list: (params: Record<string, any>) => [...userKeys.lists(), params] as const,
  details: () => [...userKeys.all, "detail"] as const,
  detail: (id: number | string) => [...userKeys.details(), id] as const,
};

export const useUsers = (
  params?: { page?: number; pageSize?: number },
  options?: Omit<UseQueryOptions<any>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: userKeys.list(params || {}),
    queryFn: () => userService.getAll(params),
    ...options,
  });
};

export const useUser = (
  id: number | string,
  options?: Omit<UseQueryOptions<User>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => userService.getById(id),
    enabled: !!id,
    ...options,
  });
};

export const useCreateUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: UserCreate) => userService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number | string; data: UserUpdate }) =>
      userService.update(id, data),
    onSuccess: (data, variables) => {
      queryClient.setQueryData(userKeys.detail(variables.id), data);
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};

export const useDeleteUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number | string) => userService.delete(id),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: userKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};
