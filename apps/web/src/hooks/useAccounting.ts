import { useQuery } from "@tanstack/react-query";
import { accountingApi } from "../api/accounting.api";

export function useAccountingSummary() {
  return useQuery({
    queryKey: ["accounting", "summary"],
    queryFn: async () => {
      try {
        const data = await accountingApi.summary();
        return { data, source: "api" as const };
      } catch {
        return { data: null, source: "mock" as const };
      }
    },
  });
}

export function useAccounts() {
  return useQuery({
    queryKey: ["accounting", "accounts"],
    queryFn: async () => {
      try {
        const data = await accountingApi.accounts();
        const items = Array.isArray(data) ? data : data?.items ?? [];
        return { items, source: "api" as const };
      } catch {
        return { items: [], source: "mock" as const };
      }
    },
  });
}
