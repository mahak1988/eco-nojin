/**
 * cms API client | کلاینت API cms
 *
 * Auto-scaffolded by phase1_complete_apps.py
 * Adjust the BASE_URL and import axios from your preferred location.
 */

import axios, { AxiosInstance } from "axios";

import type {
  Cms,
  CmsCreate,
  CmsUpdate,
  CmsListResponse,
} from "../types";

const API_BASE_URL =
  (import.meta as any).env?.VITE_API_BASE_URL || "/api/v1";

const client: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

export const cmsApi = {
  async list(params?: { skip?: number; limit?: number }): Promise<CmsListResponse> {
    const { data } = await client.get(`/cms`, { params });
    return data;
  },

  async get(id: number): Promise<Cms> {
    const { data } = await client.get(`/cms/${id}`);
    return data;
  },

  async create(payload: CmsCreate): Promise<Cms> {
    const { data } = await client.post(`/cms`, payload);
    return data;
  },

  async update(id: number, payload: CmsUpdate): Promise<Cms> {
    const { data } = await client.patch(`/cms/${id}`, payload);
    return data;
  },

  async delete(id: number): Promise<void> {
    await client.delete(`/cms/${id}`);
  },
};
