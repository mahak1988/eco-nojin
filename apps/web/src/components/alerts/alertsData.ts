// apps/web/src/components/alerts/alertsData.ts
export type AlertLevel = "critical" | "warning" | "info" | "success";

export interface Alert {
  id: string;
  level: AlertLevel;
  titleKey: string;   // کلید در alertsI18n
  messageKey: string; // کلید در alertsI18n
  timestamp: string;  // ISO — برای timeAgo
  read: boolean;
}

// timestampها نسبت به «اکنون» ساخته می‌شوند تا timeAgo همیشه تازه بماند
const hoursAgo = (h: number) => new Date(Date.now() - h * 3_600_000).toISOString();
const daysAgo = (d: number) => hoursAgo(d * 24);

export const MOCK_ALERTS: Alert[] = [
  { id: "a1", level: "critical", titleKey: "al1_t", messageKey: "al1_m", timestamp: hoursAgo(2), read: false },
  { id: "a2", level: "critical", titleKey: "al2_t", messageKey: "al2_m", timestamp: hoursAgo(4), read: false },
  { id: "a3", level: "warning", titleKey: "al3_t", messageKey: "al3_m", timestamp: hoursAgo(6), read: false },
  { id: "a4", level: "warning", titleKey: "al4_t", messageKey: "al4_m", timestamp: hoursAgo(9), read: false },
  { id: "a5", level: "warning", titleKey: "al5_t", messageKey: "al5_m", timestamp: hoursAgo(12), read: true },
  { id: "a6", level: "info", titleKey: "al6_t", messageKey: "al6_m", timestamp: daysAgo(1), read: true },
  { id: "a7", level: "info", titleKey: "al7_t", messageKey: "al7_m", timestamp: daysAgo(1), read: false },
  { id: "a8", level: "success", titleKey: "al8_t", messageKey: "al8_m", timestamp: daysAgo(2), read: true },
  { id: "a9", level: "success", titleKey: "al9_t", messageKey: "al9_m", timestamp: daysAgo(3), read: true },
];

export interface AlertCounts {
  critical: number;
  warning: number;
  info: number;
  success: number;
  unread: number;
}

// شمارش derived — جایگزین اعداد hardcoded (رفع باگ منطقی)
export function countAlerts(alerts: Alert[]): AlertCounts {
  const c: AlertCounts = { critical: 0, warning: 0, info: 0, success: 0, unread: 0 };
  for (const a of alerts) {
    c[a.level]++;
    if (!a.read) c.unread++;
  }
  return c;
}