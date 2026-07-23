// apps/web/src/components/analytics/analyticsData.ts
export type Period = "7d" | "30d" | "90d" | "1y";
export type KpiColor = "green" | "amber" | "blue" | "violet";

export interface Kpi {
  key: string;
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  trend: number;
  color: KpiColor;
}

export interface DonutSegment {
  key: string;
  value: number;
  color: string;
}

export const PERIODS: Period[] = ["7d", "30d", "90d", "1y"];

export const KPI_BY_PERIOD: Record<Period, Kpi[]> = {
  "7d": [
    { key: "revenue", value: 18400, prefix: "$", trend: 6.4, color: "green" },
    { key: "carbon", value: 2840, trend: 4.1, color: "amber" },
    { key: "users", value: 3120, trend: 11.2, color: "blue" },
    { key: "roi", value: 16.8, suffix: "%", decimals: 1, trend: 1.8, color: "violet" },
  ],
  "30d": [
    { key: "revenue", value: 84250, prefix: "$", trend: 12.5, color: "green" },
    { key: "carbon", value: 12450, trend: 8.2, color: "amber" },
    { key: "users", value: 3456, trend: 23.1, color: "blue" },
    { key: "roi", value: 18.4, suffix: "%", decimals: 1, trend: 3.2, color: "violet" },
  ],
  "90d": [
    { key: "revenue", value: 236000, prefix: "$", trend: 9.7, color: "green" },
    { key: "carbon", value: 35800, trend: 6.5, color: "amber" },
    { key: "users", value: 3380, trend: 15.4, color: "blue" },
    { key: "roi", value: 17.6, suffix: "%", decimals: 1, trend: 2.4, color: "violet" },
  ],
  "1y": [
    { key: "revenue", value: 912000, prefix: "$", trend: 18.3, color: "green" },
    { key: "carbon", value: 142000, trend: 14.8, color: "amber" },
    { key: "users", value: 3456, trend: 31.6, color: "blue" },
    { key: "roi", value: 19.2, suffix: "%", decimals: 1, trend: 4.7, color: "violet" },
  ],
};

// ۶ نقطه به ازای هر دوره (برای نمودار خطی)
export const REVENUE_SERIES: Record<Period, number[]> = {
  "7d": [2100, 2400, 2250, 2800, 3100, 2950],
  "30d": [11200, 12800, 13500, 14600, 16200, 17950],
  "90d": [32000, 36500, 39800, 42500, 45200, 48250],
  "1y": [52000, 58000, 61000, 66000, 69000, 74000],
};

// ۵ سنجه (ترتیب: efficiency, quality, speed, sustainability, innovation)
export const PERFORMANCE_METRICS: Record<Period, number[]> = {
  "7d": [78, 84, 72, 88, 65],
  "30d": [82, 88, 76, 91, 70],
  "90d": [80, 86, 79, 89, 73],
  "1y": [85, 90, 82, 93, 78],
};

export const PROJECT_DISTRIBUTION: DonutSegment[] = [
  { key: "reforestation", value: 38, color: "#15803d" },
  { key: "water", value: 24, color: "#1d4ed8" },
  { key: "solar", value: 18, color: "#d97706" },
  { key: "research", value: 12, color: "#7c3aed" },
  { key: "community", value: 8, color: "#be123c" },
];