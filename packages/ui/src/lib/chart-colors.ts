/**
 * chart-colors.ts — Unified color palette for charts (Recharts/Chart.js) and GIS (Leaflet/MapLibre).
 * Provides hex values for JavaScript-based rendering where Tailwind classes are inaccessible.
 * Single source of truth for JS-side colors.
 *
 * Usage:
 *   import { CHART, GIS, UI, CHART_SERIES } from '@econojin/ui/lib/chart-colors';
 *   <Line stroke={CHART.emerald} />
 *   <Layer color={GIS.vegetation} />
 */

// Chart colors (Tailwind-inspired palette)
export const CHART = {
  emerald: '#10b981', // Green / positive trends
  blue:    '#3b82f6', // Primary blue
  amber:   '#f59e0b', // Warning / medium
  violet:  '#8b5cf6', // Purple accent
  sky:     '#0ea5e9', // Sky blue
  red:     '#ef4444', // Danger / critical
  lime:    '#84cc16', // Lime green
  cyan:    '#06b6d4', // Cyan / water
  green:   '#22c55e', // Vegetation green
  white:   '#f8fafc', // Near-white for dark backgrounds
} as const;

/** Ordered chart palette for multi-line/multi-series charts */
export const CHART_SERIES = [
  CHART.emerald, CHART.blue, CHART.amber, CHART.violet,
  CHART.sky, CHART.red, CHART.lime, CHART.cyan, CHART.green,
] as const;

// GIS / map colors
export const GIS = {
  vegetation: '#22c55e', // Vegetation green
  water:      '#0ea5e9', // Water blue
  urban:      '#8b5cf6', // Built-up / urban
  bare:       '#f59e0b', // Bare soil / arid
  danger:     '#ef4444', // Fire / hazard
  grid:       '#94a3b8', // Grid lines (muted)
  label:      '#64748b', // Map labels (body text)
  background: '#1e293b', // Dark map background
} as const;

// UI inline colors (for non-Tailwind contexts: canvas, SVG, map controls)
export const UI = {
  surface:    '#f8fafc', // slate-50
  surfaceAlt: '#f1f5f9', // slate-100
  border:     '#e2e8f0', // slate-200
  textMuted:  '#94a3b8', // slate-400
  textBody:   '#64748b', // slate-500
  textDark:   '#1e293b', // slate-800
} as const;

export type ChartColor = keyof typeof CHART;
export type GisColor   = keyof typeof GIS;
export type UiColor    = keyof typeof UI;
