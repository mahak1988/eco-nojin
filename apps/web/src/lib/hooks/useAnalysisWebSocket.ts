import { useEffect, useRef, useCallback, useState } from "react";
import { useAppStore } from "@/store/useAppStore";

// ۱. تعریف تایپ‌های دقیق برای جلوگیری از خطاهای Runtime
export interface WSMessage {
  event_type: "connected" | "progress" | "final" | "error" | string;
  message: string;
  timestamp: number;
  data?: unknown;
}

export function useAnalysisWebSocket(sessionId: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isManualCloseRef = useRef(false); // جلوگیری از اتصال مجدد وقتی خودمان قطع کردیم

  // ۲. رفع باگ بحرانی: استفاده از useState برای اتصال تا UI آپدیت شود
  const [isConnected, setIsConnected] = useState(false);

  const MAX_RETRIES = 5;
  const BASE_DELAY = 1000; // 1 ثانیه

  // پاک‌سازی تایمرهای اتصال مجدد
  const clearReconnectTimeout = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  };

  const connect = useCallback(() => {
    if (!sessionId) return;

    // پاک‌سازی اتصال قبلی در صورت وجود
    if (wsRef.current) {
      wsRef.current.close();
    }

    // ۳. تولید داینامیک آدرس (تشخیص خودکار ws و wss برای Production)
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsBase = process.env.NEXT_PUBLIC_WS_URL || `${protocol}//${window.location.host}`;
    const url = `${wsBase}/ws/analyze/${sessionId}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      reconnectAttemptsRef.current = 0; // ریست کردن تعداد تلاش‌ها پس از اتصال موفق
      
      // ۴. استفاده از getState() برای جلوگیری از Stale Closure
      useAppStore.getState().addEvent({
        event_type: "connected",
        message: "ارتباط با سرور تحلیل برقرار شد.",
        timestamp: Date.now(),
      });
    };

    ws.onmessage = (event) => {
      try {
        const data: WSMessage = JSON.parse(event.data);
        useAppStore.getState().addEvent(data);

        if (data.event_type === "final") {
          useAppStore.getState().setResult(data.data);
          useAppStore.getState().setAnalyzing(false);
          isManualCloseRef.current = true; // جلوگیری از تلاش مجدد بعد از دریافت جواب نهایی
          ws.close();
        } else if (data.event_type === "error") {
          useAppStore.getState().setAnalyzing(false);
        }
      } catch (error) {
        console.error("WebSocket parse error:", error);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      wsRef.current = null;

      // ۵. منطق اتصال مجدد (Auto-Reconnect with Exponential Backoff)
      if (!isManualCloseRef.current && reconnectAttemptsRef.current < MAX_RETRIES) {
        const delay = BASE_DELAY * Math.pow(2, reconnectAttemptsRef.current);
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current += 1;
          connect();
        }, delay);
      }
    };

    ws.onerror = () => {
      useAppStore.getState().addEvent({
        event_type: "error",
        message: "خطا در برقراری ارتباط با سرور تحلیل",
        timestamp: Date.now(),
      });
      // نیازی به setAnalyzing(false) اینجا نیست، چون بلافاصله onclose صدا زده می‌شود.
    };
  }, [sessionId]);

  const disconnect = useCallback(() => {
    isManualCloseRef.current = true;
    clearReconnectTimeout();
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  useEffect(() => {
    if (sessionId) {
      isManualCloseRef.current = false;
      connect();
    }

    // ۶. Cleanup اصولی برای جلوگیری از Memory Leak هنگام unmount شدن کامپوننت
    return () => {
      disconnect();
    };
  }, [sessionId, connect, disconnect]);

  return { connect, disconnect, isConnected };
}