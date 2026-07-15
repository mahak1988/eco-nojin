/**
 * ============================================================================
 *  User Service — CRUD operations for users
 * ============================================================================
 */

import { apiClient } from "@/lib/api-client";
import type { User } from "@/types";

export interface UserCreate {
  email: string;
  password: string;
  full_name?: string;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  is_active?: boolean;
}

export interface UserListResponse {
  items: User[];
  total: number;
  page: number;
  pageSize: number;
}

const ENDPOINTS = {
  users: "/users",
  userById: (id: number | string) => `/users/${id}`,
} as const;

export const userService = {
  async getAll(params?: { page?: number; pageSize?: number }): Promise<UserListResponse> {
    const response = await apiClient.get<UserListResponse>(ENDPOINTS.users, { params });
    return response.data;
  },
  
  async getById(id: number | string): Promise<User> {
    const response = await apiClient.get<User>(ENDPOINTS.userById(id));
    return response.data;
  },
  
  async create(data: UserCreate): Promise<User> {
    const response = await apiClient.post<User>(ENDPOINTS.users, data);
    return response.data;
  },
  
  async update(id: number | string, data: UserUpdate): Promise<User> {
    const response = await apiClient.put<User>(ENDPOINTS.userById(id), data);
    return response.data;
  },
  
  async delete(id: number | string): Promise<void> {
    await apiClient.delete(ENDPOINTS.userById(id));
  },
};

export default userService;
