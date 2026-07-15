/**
 * web API client | کلاینت API web
 *
 * Auto-scaffolded by phase1_complete_apps.py
 * Adjust the BASE_URL and import axios from your preferred location.
 */

import axios, { AxiosInstance } from "axios";

import type {
  HydrologyFrontend,
  HydrologyFrontendCreate,
  HydrologyFrontendUpdate,
  HydrologyFrontendListResponse,
} from "../types";

const API_BASE_URL =
  (import.meta as any).env?.VITE_API_BASE_URL || "/api/v1";

const client: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

export const webApi = {
  async list(params?: { skip?: number; limit?: number }): Promise<HydrologyFrontendListResponse> {
    const { data } = await client.get(`/web`, { params });
    return data;
  },

  async get(id: number): Promise<HydrologyFrontend> {
    const { data } = await client.get(`/web/${id}`);
    return data;
  },

  async create(payload: HydrologyFrontendCreate): Promise<HydrologyFrontend> {
    const { data } = await client.post(`/web`, payload);
    return data;
  },

  async update(id: number, payload: HydrologyFrontendUpdate): Promise<HydrologyFrontend> {
    const { data } = await client.patch(`/web/${id}`, payload);
    return data;
  },

  async delete(id: number): Promise<void> {
    await client.delete(`/web/${id}`);
  },
};
