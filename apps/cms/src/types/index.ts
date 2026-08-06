/** Minimal shared shape used by scaffold tests — not a Strapi content-type. */
export interface Cms {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type CmsCreate = Omit<Cms, 'id' | 'created_at' | 'updated_at'>;
export type CmsUpdate = Partial<CmsCreate>;
export interface CmsListResponse {
  data: Cms[];
  meta?: { total?: number };
}
