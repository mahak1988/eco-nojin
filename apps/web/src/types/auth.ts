export interface AuthUser {
  id: number | string;
  email: string;
  full_name?: string;
  is_active?: boolean;
  is_superuser?: boolean;
  role?: string;
}

export interface AuthState {
  user: AuthUser | null;
  token: string | null;
  loading: boolean;
}
