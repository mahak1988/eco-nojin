'use client';

import { useEffect, useRef } from 'react';
import { useAnalysisStore } from '@/store/analysis';
import type { RealtimeEvent, NdviDataPoint } from '@/lib/types/analysis';

export function useAnalysisWebSocket() {
  const sessionId = useAnalysisStore((state) => state.sessionId);
  const addEvent = useAnalysisStore((state) => state.addEvent);
  const fetchAnalyses = useAnalysisStore((state) => state.fetchAnalyses);
  const setLoading = useAnalysisStore((state) => state.setLoading);
  const setSessionId = useAnalysisStore((state) => state.setSessionId);
  const setNdviData = useAnalysisStore((state) => state.setNdviData);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!sessionId) {
      wsRef.current?.close();
      return;
    }

    const wsBaseUrl = process.env.NEXT_PUBLIC_WS_BASE_URL || 'ws://localhost:8000';
    const wsUrl = `${wsBaseUrl}/ws/analyze/${sessionId}`;

    const connect = () => {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const data: RealtimeEvent = JSON.parse(event.data);
          addEvent(data);

          if (data.event_type === 'final') {
            // استخراج داده‌های NDVI
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
        console.log('🔌 WebSocket closed');
        if (sessionId) {
          reconnectTimeoutRef.current = setTimeout(connect, 3000);
        }
      };
    };

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      wsRef.current?.close();
    };
  }, [sessionId, addEvent, fetchAnalyses, setLoading, setSessionId, setNdviData]);
}