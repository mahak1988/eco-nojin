import { apiFetch, v1 } from "./http";

export const communityApi = {
  listPosts: (params?: { skip?: number; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.skip != null) q.set("skip", String(params.skip));
    if (params?.limit != null) q.set("limit", String(params.limit));
    const qs = q.toString();
    return apiFetch(v1(`/community/posts${qs ? `?${qs}` : ""}`));
  },
};
