import { useQuery } from "@tanstack/react-query";
import { communityApi } from "../api/community.api";

export function useCommunityPosts(limit = 20) {
  return useQuery({
    queryKey: ["community", "posts", limit],
    queryFn: async () => {
      try {
        const data = await communityApi.listPosts({ limit });
        return { data, source: "api" as const };
      } catch {
        return { data: null, source: "mock" as const };
      }
    },
  });
}
