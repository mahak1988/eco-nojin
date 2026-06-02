import { useEffect, useRef } from "react";
import { useAnalysisStore } from "../store/useAnalysisStore";

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null);
  const { addEvent, setSession, reset } = useAnalysisStore();

  const connect = (sessionId: string) => {
    setSession(sessionId);
    const url = `ws://localhost:8000/ws/analyze/${sessionId}`;
    ws.current = new WebSocket(url);

    ws.current.onmessage = (e) => {
      const data = JSON.parse(e.data);
      addEvent(data);
      if (data.event_type === "final" || data.event_type === "error") {
        ws.current?.close();
      }
    };

    ws.current.onclose = () => reset();
  };

  return { connect };
}