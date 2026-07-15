/**
 * ============================================================================
 *  AI Agent Service — Chat and agent operations
 * ============================================================================
 */

import { apiClient } from "@/lib/api-client";

export interface Agent {
  id: string;
  name: string;
  description: string;
  type: "financial" | "research" | "support" | "admin" | "code_assistant" | "data_analyst";
  capabilities: string[];
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
  history?: ChatMessage[];
  context?: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  agent_id: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

const ENDPOINTS = {
  agents: "/ai-agents",
  agentById: (id: string) => `/ai-agents/${id}`,
  chat: (id: string) => `/ai-agents/${id}/chat`,
  chatStream: (id: string) => `/ai-agents/${id}/chat/stream`,
} as const;

export const aiAgentService = {
  async getAll(): Promise<Agent[]> {
    const response = await apiClient.get<Agent[]>(ENDPOINTS.agents);
    return response.data;
  },
  
  async getById(id: string): Promise<Agent> {
    const response = await apiClient.get<Agent>(ENDPOINTS.agentById(id));
    return response.data;
  },
  
  async chat(agentId: string, request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>(
      ENDPOINTS.chat(agentId),
      request
    );
    return response.data;
  },
  
  async *chatStream(
    agentId: string,
    request: ChatRequest
  ): AsyncGenerator<string, void, unknown> {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
    const token = localStorage.getItem("econojin.access_token");
    
    const response = await fetch(
      `${API_BASE_URL}/api/v1${ENDPOINTS.chatStream(agentId)}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(request),
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const reader = response.body?.getReader();
    if (!reader) throw new Error("Response body is not readable");
    
    const decoder = new TextDecoder();
    
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") return;
            yield data;
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },
};

export default aiAgentService;
