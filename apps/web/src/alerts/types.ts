/**
 * ============================================================================
 *  Alert System — Type Definitions
 * ============================================================================
 */

export type AlertSeverity = "info" | "low" | "medium" | "high" | "critical";
export type AlertChannel = "in-app" | "email" | "sms" | "web-push";
export type AlertCategory = "flood" | "wildfire" | "drought" | "pest" | "air-quality" | "deforestation";

export interface Alert {
  id: string;
  category: AlertCategory;
  severity: AlertSeverity;
  titleKey: string;
  descriptionKey: string;
  region: string;
  triggeredAt: string;
  acknowledged: boolean;
  channels: readonly AlertChannel[];
  satellite?: string;
  metadata?: Readonly<Record<string, unknown>>;
}

export type AlertRegistry = readonly Alert[];
