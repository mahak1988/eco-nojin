import { useQuery } from "@tanstack/react-query";
import { adminApi } from "../api/admin.api";

export function useAdminOverview() {
  return useQuery({
    queryKey: ["admin", "overview"],
    queryFn: async () => {
      const [health, modules] = await Promise.all([
        adminApi.health(),
        adminApi.modules(),
      ]);
      return { health, modules };
    },
  });
}
