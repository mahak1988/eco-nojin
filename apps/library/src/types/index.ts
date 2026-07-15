/**
 * library types | انواع TypeScript برای library
 *
 * Auto-scaffolded by phase1_complete_apps.py
 */

export interface Library {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LibraryCreate {
  name: string;
  description?: string;
}

export interface LibraryUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
}

export interface LibraryListResponse {
  items: Library[];
  total: number;
  skip: number;
  limit: number;
}

export type LibraryStatus = "active" | "inactive" | "pending";
