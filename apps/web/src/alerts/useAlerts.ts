/**
 * ============================================================================
 *  useAlerts — hook for consuming alerts (API-backed)
 * ============================================================================
 */

import { useState, useEffect, useCallback, useMemo } from "react";
import type { Alert } from "./types";

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || "";

export interface UseAlertsReturn {
  alerts: Alert[];
  activeAlerts: Alert[];
  criticalAlerts: Alert[];
  unreadCount: number;
  loading: boolean;
  error: string | null;
  acknowledge: (id: string) => Promise<void>;
  refresh: () => Promise<void>;
}

export function useAlerts(): UseAlertsReturn {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/v1/alerts/`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setAlerts(data.alerts || []);
      setError(null);
    } catch (err: any) {
      setError(err.message);
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  const acknowledge = useCallback(async (id: string) => {
    try {
      await fetch(`${API_BASE}/api/v1/alerts/${id}/acknowledge`, { method: "POST" });
      setAlerts(prev => prev.map(a => a.id === id ? { ...a, acknowledged: true } : a));
    } catch (err: any) {
      setError(err.message);
    }
  }, []);

  const activeAlerts = useMemo(() => alerts.filter(a => !a.acknowledged), [alerts]);
  const criticalAlerts = useMemo(
    () => alerts.filter(a => a.severity === "critical" && !a.acknowledged),
    [alerts]
  );

  return {
    alerts,
    activeAlerts,
    criticalAlerts,
    unreadCount: activeAlerts.length,
    loading,
    error,
    acknowledge,
    refresh: fetchAlerts,
  };
}