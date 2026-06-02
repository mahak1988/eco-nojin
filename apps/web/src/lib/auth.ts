const TOKEN_KEY = "econojin_token";
const USER_KEY = "econojin_user";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

function setAuthCookie(token: string) {
  const maxAge = 60 * 60 * 24 * 7;
  document.cookie = `econojin_token=${encodeURIComponent(token)}; path=/; max-age=${maxAge}; SameSite=Lax`;
}

export function setSession(token: string, user: { fid: string; name?: string; phone?: string }) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  setAuthCookie(token);
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  document.cookie = "econojin_token=; path=/; max-age=0";
}

export function getStoredUser(): { fid: string; name?: string; phone?: string } | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export const PROTECTED_PREFIXES = [
  "/farmers",
  "/accounting",
  "/calendar",
  "/settings",
  "/ecomining",
];

export function isProtectedPath(pathname: string): boolean {
  return PROTECTED_PREFIXES.some((p) => pathname === p || pathname.startsWith(`${p}/`));
}
