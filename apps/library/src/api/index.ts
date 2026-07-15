/**
 * library API client | کلاینت API library
 *
 * Auto-scaffolded by phase1_complete_apps.py
 * Adjust the BASE_URL and import axios from your preferred location.
 */

import axios, { AxiosInstance } from "axios";

import type {
  Library,
  LibraryCreate,
  LibraryUpdate,
  LibraryListResponse,
} from "../types";

const API_BASE_URL =
  (import.meta as any).env?.VITE_API_BASE_URL || "/api/v1";

const client: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

export const libraryApi = {
  async list(params?: { skip?: number; limit?: number }): Promise<LibraryListResponse> {
    const { data } = await client.get(`/library`, { params });
    return data;
  },

  async get(id: number): Promise<Library> {
    const { data } = await client.get(`/library/${id}`);
    return data;
  },

  async create(payload: LibraryCreate): Promise<Library> {
    const { data } = await client.post(`/library`, payload);
    return data;
  },

  async update(id: number, payload: LibraryUpdate): Promise<Library> {
    const { data } = await client.patch(`/library/${id}`, payload);
    return data;
  },

  async delete(id: number): Promise<void> {
    await client.delete(`/library/${id}`);
  },
};
