/**
 * ============================================================================
 *  useAiAgents — React Query hooks for AI agent operations
 * ============================================================================
 */

import {
  useQuery,
  useMutation,
  UseQueryOptions,
} from "@tanstack/react-query";
import {
  aiAgentService,
  Agent,
  ChatRequest,
} from "@/services/aiAgentService";

export const agentKeys = {
  all: ["agents"] as const,
  lists: () => [...agentKeys.all, "list"] as const,
  details: () => [...agentKeys.all, "detail"] as const,
  detail: (id: string) => [...agentKeys.details(), id] as const,
};

export const useAiAgents = (
  options?: Omit<UseQueryOptions<Agent[]>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: agentKeys.lists(),
    queryFn: () => aiAgentService.getAll(),
    ...options,
  });
};

export const useAiAgent = (
  id: string,
  options?: Omit<UseQueryOptions<Agent>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: agentKeys.detail(id),
    queryFn: () => aiAgentService.getById(id),
    enabled: !!id,
    ...options,
  });
};

export const useChat = () => {
  return useMutation({
    mutationFn: ({ agentId, request }: { agentId: string; request: ChatRequest }) =>
      aiAgentService.chat(agentId, request),
  });
};

export const useChatStream = () => {
  const streamChat = async function* (
    agentId: string,
    request: ChatRequest
  ): AsyncGenerator<string, void, unknown> {
    yield* aiAgentService.chatStream(agentId, request);
  };
  
  return { streamChat };
};

export const useChatState = (agentId: string) => {
  const chat = useChat();
  
  const sendMessage = async (message: string, history: any[] = []) => {
    const request: ChatRequest = { message, history };
    return chat.mutateAsync({ agentId, request });
  };
  
  return {
    sendMessage,
    isLoading: chat.isPending,
    error: chat.error,
    data: chat.data,
  };
};
