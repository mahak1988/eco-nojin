import { apiFetch, v1 } from "./http";

export const adminApi = {
  users: () => apiFetch(v1("/users")).catch(() => ({ items: [], total: 0 })),

  health: () => apiFetch("/health").catch(() => ({ status: "unknown" })),

  modules: () => apiFetch("/modules").catch(() => ({ modules: [], total: 0 })),
};
