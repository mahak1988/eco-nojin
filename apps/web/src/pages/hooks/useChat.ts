import { useState } from "react";

interface ChatState {
  loading: boolean
  error: Error | null
}

export function useChat() {
  const [state] = useState<ChatState>({
    loading: false,
    error: null,
  })

  // TODO: منتقل کردن state ها از Chat

  return {
    ...state,
  }
}
