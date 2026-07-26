import { apiFetch, v1 } from "./http";
import type { AccountingSummary, Account } from "../types/accounting";

export const accountingApi = {
  summary: () => apiFetch<AccountingSummary>(v1("/accounting/summary")),

  accounts: (limit = 50) =>
    apiFetch<{ items: Account[]; total: number } | Account[]>(
      v1(`/accounting/accounts?limit=${limit}`),
    ),

  invoices: (limit = 50) =>
    apiFetch(v1(`/accounting/invoices?limit=${limit}`)),
};
