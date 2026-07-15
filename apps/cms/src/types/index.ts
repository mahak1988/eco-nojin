/**
 * cms types | انواع TypeScript برای cms
 *
 * Auto-scaffolded by phase1_complete_apps.py
 */

export interface Cms {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CmsCreate {
  name: string;
  description?: string;
}

export interface CmsUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
}

export interface CmsListResponse {
  items: Cms[];
  total: number;
  skip: number;
  limit: number;
}

export type CmsStatus = "active" | "inactive" | "pending";
