/**
 * ============================================================================
 *  Alert Registry — mock alerts + helpers
 * ============================================================================
 */

import type { Alert, AlertRegistry } from "./types";

export const MOCK_ALERTS: AlertRegistry = [
  {
    id: "alert-001",
    category: "wildfire",
    severity: "critical",
    titleKey: "alerts.wildfire.title",
    descriptionKey: "alerts.wildfire.desc",
    region: "Zagros Mountains, Iran",
    triggeredAt: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
    acknowledged: false,
    channels: ["in-app", "email"],
    satellite: "VIIRS",
  },
  {
    id: "alert-002",
    category: "drought",
    severity: "high",
    titleKey: "alerts.drought.title",
    descriptionKey: "alerts.drought.desc",
    region: "Sistan-Baluchestan, Iran",
    triggeredAt: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
    acknowledged: false,
    channels: ["in-app", "email"],
    satellite: "SMAP",
  },
  {
    id: "alert-003",
    category: "flood",
    severity: "high",
    titleKey: "alerts.flood.title",
    descriptionKey: "alerts.flood.desc",
    region: "Caspian Sea coast, Iran",
    triggeredAt: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    acknowledged: false,
    channels: ["in-app", "sms"],
    satellite: "GPM",
  },
  {
    id: "alert-004",
    category: "air-quality",
    severity: "medium",
    titleKey: "alerts.airQuality.title",
    descriptionKey: "alerts.airQuality.desc",
    region: "Tehran, Iran",
    triggeredAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    acknowledged: true,
    channels: ["in-app"],
    satellite: "Sentinel-5P",
  },
  {
    id: "alert-005",
    category: "deforestation",
    severity: "medium",
    titleKey: "alerts.deforestation.title",
    descriptionKey: "alerts.deforestation.desc",
    region: "Northern forests, Iran",
    triggeredAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    acknowledged: true,
    channels: ["in-app", "email"],
    satellite: "Landsat-8",
  },
] as const;

export function getActiveAlerts(): Alert[] {
  return MOCK_ALERTS.filter((a) => !a.acknowledged);
}

export function getCriticalAlerts(): Alert[] {
  return MOCK_ALERTS.filter((a) => a.severity === "critical" && !a.acknowledged);
}
