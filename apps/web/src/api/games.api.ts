import { apiFetch, v1 } from "./http";

export const gamesApi = {
  vocabulary: () => apiFetch(v1("/games/vocabulary")).catch(() => []),
  quizzes: () => apiFetch(v1("/games/quizzes")).catch(() => []),
};
