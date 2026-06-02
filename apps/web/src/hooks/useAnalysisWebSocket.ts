import { useEffect, useRef, useCallback } from "react";
import { useAppStore } from "@/store/useAppStore";

export function useAnalysisWebSocket(sessionId: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const { addEvent, setAnalyzing, setResult, clearAnalysis } = useAppStore();

  const connect = useCallback(() => {
    if (!sessionId) return;
    
    const url = `ws://localhost:8000/ws/analyze/${sessionId}`;
    wsRef.current = new WebSocket(url);
    
    wsRef.current.onopen = () => {
      console.log("✅ WebSocket connected");
      addEvent({ event_type: "connected", message: "✅ اتصال به سرور برقرار شد", timestamp: Date.now() });
    };
    
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        addEvent(data);
        
        if (data.event_type === "final") {
          setResult(data.data);
          setAnalyzing(false);
        } else if (data.event_type === "error") {
          setAnalyzing(false);
        }
      } catch (e) {
        console.error("WebSocket parse error:", e);
      }
    };
    
    wsRef.current.onclose = () => {
      console.log("🔌 WebSocket disconnected");
    };
    
    wsRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
      addEvent({ event_type: "error", message: "❌ خطا در اتصال WebSocket", timestamp: Date.now() });
      setAnalyzing(false);
    };
  }, [sessionId, addEvent, setAnalyzing, setResult]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (sessionId) {
      connect();
      return () => disconnect();
    }
  }, [sessionId, connect, disconnect]);

  return { connect, disconnect, isConnected: wsRef.current?.readyState === WebSocket.OPEN };
}
