import { useEffect, useRef } from 'react';
import { useAnalysisStore } from '../store/useAnalysisStore';
import { RealtimeEvent, NdviDataPoint } from '../types';

export function useAnalysisWebSocket() {
  const sessionId = useAnalysisStore((state) => state.sessionId);
  const addEvent = useAnalysisStore((state) => state.addEvent);
  const fetchAnalyses = useAnalysisStore((state) => state.fetchAnalyses);
  const setLoading = useAnalysisStore((state) => state.setLoading);
  const setSessionId = useAnalysisStore((state) => state.setSessionId);
  const setNdviData = useAnalysisStore((state) => state.setNdviData); // جدید
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!sessionId) {
      wsRef.current?.close();
      return;
    }

    const connect = () => {
      const wsUrl = `ws://localhost:8000/ws/analyze/${sessionId}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const data: RealtimeEvent = JSON.parse(event.data);
          addEvent(data);

          if (data.event_type === 'final') {
            // 🚀 منطق استخراج داده‌ها به اینجا منتقل شد
            const rawNdvi = data?.data?.tasks?.task_ndvi_analysis?.detailed_data?.gee_ndvi?.ndvi?.values || [];
            const dates = data?.data?.tasks?.task_ndvi_analysis?.detailed_data?.gee_ndvi?.ndvi?.dates || [];
            
            const processedNdvi: NdviDataPoint[] = rawNdvi.map((v: number, i: number) => ({
              date: dates[i]?.slice(5) || `روز ${i + 1}`,
              ndvi: parseFloat(v.toFixed(3))
            }));
            
            setNdviData(processedNdvi);

            setTimeout(() => {
              fetchAnalyses();
              setLoading(false);
              setSessionId(null);
            }, 1000);
          }
        } catch (e) {
          console.error('❌ Error parsing WebSocket message:', e);
        }
      };

      ws.onerror = (err) => console.error('❌ WebSocket error:', err);
      ws.onclose = () => {
        if (sessionId) reconnectTimeoutRef.current = setTimeout(connect, 3000);
      };
    };

    connect();

    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      wsRef.current?.close();
    };
  }, [sessionId, addEvent, fetchAnalyses, setLoading, setSessionId, setNdviData]);
}