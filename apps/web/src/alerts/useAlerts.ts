/**
 * ============================================================================
 *  useAlerts — hook for consuming alerts
 * ============================================================================
 */

import { useMemo } from "react";

import { MOCK_ALERTS, getActiveAlerts, getCriticalAlerts } from "./registry";
import type { Alert } from "./types";

export interface UseAlertsReturn {
  alerts: readonly Alert[];
  activeAlerts: Alert[];
  criticalAlerts: Alert[];
  unreadCount: number;
}

export function useAlerts(): UseAlertsReturn {
  const activeAlerts = useMemo(() => getActiveAlerts(), []);
  const criticalAlerts = useMemo(() => getCriticalAlerts(), []);

  return {
    alerts: MOCK_ALERTS,
    activeAlerts,
    criticalAlerts,
    unreadCount: activeAlerts.length,
  };
}
