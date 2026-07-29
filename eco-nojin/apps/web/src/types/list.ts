/** R14 list envelope (target shape for new endpoints). */

export interface ListMeta {
  total: number;
  page: number;
  pages: number;
  size: number;
}

export interface ListEnvelope<T> {
  data: T[];
  meta: ListMeta;
}

/** Legacy list shape still returned by some endpoints. */
export interface LegacyList<T> {
  items: T[];
  total: number;
  skip?: number;
  limit?: number;
}

export function legacyToEnvelope<T>(
  legacy: LegacyList<T>,
  page = 1,
  size = 20,
): ListEnvelope<T> {
  const total = legacy.total ?? legacy.items.length;
  const pages = size > 0 ? Math.max(1, Math.ceil(total / size)) : 1;
  return {
    data: legacy.items,
    meta: { total, page, pages, size },
  };
}
