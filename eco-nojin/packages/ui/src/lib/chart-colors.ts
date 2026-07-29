/**
 * chart-colors.ts — پالت رنگی مشترک نمودارها، نقشه‌های GIS و inline styleها
 *
 * مشکل: کتابخانه‌های نمودار (Recharts/Chart.js) و نقشه (Leaflet/MapLibre)
 * ذاتاً به مقدار hex در JavaScript نیاز دارند — Tailwind class در آن‌ها کار نمی‌کند.
 * راه‌حل: یک منبع واحد (single source of truth) برای همهٔ رنگ‌های JS-side.
 *
 * استفاده:
 *   import { CHART, GIS, UI, CHART_SERIES } from '@econojin/ui/lib/chart-colors';
 *   <Line stroke={CHART.amber} />
 *   <Layer color={GIS.vegetation} />
 */

// ── سری‌های نمودار (منطبق بر Tailwind default palette) ──
export const CHART = {
  emerald: CHART.emerald,   // برند / سری اصلی / مثبت
  blue:    CHART.blue,   // سری دوم
  amber:   CHART.amber,   // هشدار / سری سوم
  violet:  CHART.violet,   // سری چهارم
  sky:     CHART.sky,   // سری پنجم
  red:     CHART.red,   // خطر / منفی
  lime:    CHART.lime,   // سری ششم
  cyan:    GIS.water,   // سری هفتم
  green:   GIS.vegetation,   // سری هشتم
  white:   CHART.white,   // متن روی پس‌زمینه تیره
} as const;

/** پالت ترتیبی — برای حلقه روی سری‌های متعدد نمودار */
export const CHART_SERIES = [
  CHART.emerald, CHART.blue, CHART.amber, CHART.violet,
  CHART.sky, CHART.red, CHART.lime, CHART.cyan, CHART.green,
] as const;

// ── رنگ‌های GIS / نقشه ──
export const GIS = {
  vegetation: GIS.vegetation,   // پوشش گیاهی
  water:      GIS.water,   // پهنه‌های آبی
  urban:      CHART.violet,   // بافت شهری
  bare:       CHART.amber,   // زمین بایر / هشدار
  danger:     CHART.red,   // خطر / بحران
  grid:       UI.textMuted,   // خطوط گرید
  label:      UI.textBody,   // برچسب‌ها
  background: GIS.background,   // پس‌زمینه نقشه تیره
} as const;

// ── رنگ‌های UI (برای inline styleهای اجتناب‌ناپذیر) ──
export const UI = {
  surface:    UI.surface,   // slate-50
  surfaceAlt: UI.surfaceAlt,   // slate-100
  border:     UI.border,   // slate-200
  textMuted:  UI.textMuted,   // slate-400
  textBody:   UI.textBody,   // slate-500
  textDark:   UI.textDark,   // slate-800
} as const;

export type ChartColor = keyof typeof CHART;
export type GisColor   = keyof typeof GIS;
export type UiColor    = keyof typeof UI;