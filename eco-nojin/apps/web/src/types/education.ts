export interface Course {
  id: number | string;
  title: string;
  description?: string;
  category?: string;
  level?: string;
  instructor?: string;
  is_published?: boolean;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  skip?: number;
  limit?: number;
}
