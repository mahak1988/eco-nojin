#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 apps/web — Phase 5: Final Platform Completion
================================================================================
 Run from D:\\econojin.com\\apps\\web

   python generate_phase5.py

 CREATES (~25 files)
 -------------------
  Scenarios (5 remaining):
    - src/scenarios/presets/agriculturalMonitoring.ts
    - src/scenarios/presets/airQuality.ts
    - src/scenarios/presets/wildfire.ts
    - src/scenarios/presets/urbanization.ts
    - src/scenarios/presets/biodiversityConservation.ts

  Audience dashboards:
    - src/audiences/types.ts
    - src/audiences/FarmerDashboard.tsx
    - src/audiences/StudentDashboard.tsx
    - src/audiences/ExpertDashboard.tsx
    - src/audiences/ManagerDashboard.tsx
    - src/audiences/ResearcherDashboard.tsx

  Chart components:
    - src/components/charts/TimeSeriesChart.tsx
    - src/components/charts/HeatmapChart.tsx
    - src/components/charts/ComparisonChart.tsx

  Alert system:
    - src/alerts/types.ts
    - src/alerts/registry.ts
    - src/alerts/AlertsPanel.tsx
    - src/alerts/useAlerts.ts

  Command Palette:
    - src/components/CommandPalette/CommandPalette.tsx
    - src/hooks/useCommandPalette.ts

  PWA:
    - public/manifest.webmanifest

  i18n additions:
    - ~150 new keys added to fa.json and en.json (audiences, alerts, scenarios)

 UPDATES
 -------
  - src/scenarios/registry.ts          (registers 5 new scenarios)
  - src/components/Layout/Layout.tsx   (mounts CommandPalette)
================================================================================
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

def detect_root() -> Path:
    cwd = Path.cwd()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "tsconfig.json").exists() and (candidate / "package.json").exists():
            return candidate
    return cwd

def write_file(root: Path, rel_path: str, content: str) -> bool:
    full = root / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    content_bytes = content.encode("utf-8")
    if full.exists() and full.read_bytes() == content_bytes:
        return False
    full.write_bytes(content_bytes)
    return True

# ---------------------------------------------------------------------------
# 1) SCENARIO PRESETS (5 remaining)
# ---------------------------------------------------------------------------

def make_preset_file(preset_id, class_name, name_key, desc_key, category, icon, audiences, duration, satellites):
    return f'''/**
 *  {class_name} — {preset_id} scenario preset
 */

import type {{ Scenario }} from "../types";

export const {class_name}: Scenario = {{
  id: "{preset_id}",
  nameKey: "{name_key}",
  descriptionKey: "{desc_key}",
  category: "{category}",
  audience: [{audiences}],
  icon: "{icon}",
  duration: "{duration}",
  satellitesUsed: [{satellites}],
  steps: [
    {{
      order: 1,
      titleKey: "scenarios.{preset_id}.step1Title",
      descriptionKey: "scenarios.{preset_id}.step1Desc",
      requiredDataKey: "scenarios.{preset_id}.step1Data",
    }},
    {{
      order: 2,
      titleKey: "scenarios.{preset_id}.step2Title",
      descriptionKey: "scenarios.{preset_id}.step2Desc",
      requiredDataKey: "scenarios.{preset_id}.step2Data",
    }},
    {{
      order: 3,
      titleKey: "scenarios.{preset_id}.step3Title",
      descriptionKey: "scenarios.{preset_id}.step3Desc",
      requiredDataKey: "scenarios.{preset_id}.step3Data",
    }},
  ],
  inputs: [
    {{ id: "region", labelKey: "scenarios.{preset_id}.inputRegion", type: "user", required: true }},
    {{ id: "timeframe", labelKey: "scenarios.{preset_id}.inputTimeframe", type: "user", required: true }},
  ],
  outputs: [
    {{ id: "map", labelKey: "scenarios.{preset_id}.outputMap", format: "map" }},
    {{ id: "report", labelKey: "scenarios.{preset_id}.outputReport", format: "report" }},
  ],
}};
'''

SCENARIO_FILES = [
    ("src/scenarios/presets/agriculturalMonitoring.ts", make_preset_file(
        "agriculturalMonitoring", "agriculturalMonitoringScenario",
        "scenarios.agriculturalMonitoring.name", "scenarios.agriculturalMonitoring.description",
        "agriculture", "🌾", '"farmer", "expert"', "۱-۲ هفته",
        '"sentinel-2", "smap", "chirps"')),
    ("src/scenarios/presets/airQuality.ts", make_preset_file(
        "airQuality", "airQualityScenario",
        "scenarios.airQuality.name", "scenarios.airQuality.description",
        "air", "🌫️", '"manager", "expert", "researcher"', "۳-۵ روز",
        '"sentinel-5p", "modis"')),
    ("src/scenarios/presets/wildfire.ts", make_preset_file(
        "wildfire", "wildfireScenario",
        "scenarios.wildfire.name", "scenarios.wildfire.description",
        "risk", "🔥", '"manager", "expert"', "۱-۳ روز",
        '"viirs", "modis", "sentinel-2"')),
    ("src/scenarios/presets/urbanization.ts", make_preset_file(
        "urbanization", "urbanizationScenario",
        "scenarios.urbanization.name", "scenarios.urbanization.description",
        "urban", "🏙️", '"manager", "expert"', "۲-۴ هفته",
        '"sentinel-2", "landsat-8", "viirs"')),
    ("src/scenarios/presets/biodiversityConservation.ts", make_preset_file(
        "biodiversityConservation", "biodiversityConservationScenario",
        "scenarios.biodiversityConservation.name", "scenarios.biodiversityConservation.description",
        "biodiversity", "🦋", '"researcher", "expert"', "۳-۶ هفته",
        '"gedi", "icesat-2", "sentinel-2"')),
]

# ---------------------------------------------------------------------------
# 2) SCENARIOS REGISTRY UPDATE
# ---------------------------------------------------------------------------

SCEN_REGISTRY_TS = '''/**
 * ============================================================================
 *  Scenario Registry — 10 preset environmental scenarios
 * ============================================================================
 */

import type { ScenarioRegistry } from "./types";
import { climateChangeScenario } from "./presets/climateChange";
import { deforestationScenario } from "./presets/deforestation";
import { droughtMitigationScenario } from "./presets/droughtMitigation";
import { reforestationScenario } from "./presets/reforestation";
import { floodRiskScenario } from "./presets/floodRisk";
import { agriculturalMonitoringScenario } from "./presets/agriculturalMonitoring";
import { airQualityScenario } from "./presets/airQuality";
import { wildfireScenario } from "./presets/wildfire";
import { urbanizationScenario } from "./presets/urbanization";
import { biodiversityConservationScenario } from "./presets/biodiversityConservation";

export const SCENARIOS: ScenarioRegistry = [
  climateChangeScenario,
  deforestationScenario,
  droughtMitigationScenario,
  reforestationScenario,
  floodRiskScenario,
  agriculturalMonitoringScenario,
  airQualityScenario,
  wildfireScenario,
  urbanizationScenario,
  biodiversityConservationScenario,
];

export function getScenarioById(id: string): Scenario | undefined {
  return SCENARIOS.find((s) => s.id === id);
}
'''

# ---------------------------------------------------------------------------
# 3) AUDIENCE TYPES + DASHBOARDS
# ---------------------------------------------------------------------------

AUDIENCE_TYPES_TS = '''/**
 * ============================================================================
 *  Audience Types — 5 user roles with dedicated dashboards
 * ============================================================================
 */

export type AudienceRole = "farmer" | "student" | "expert" | "manager" | "researcher";

export interface AudienceMeta {
  role: AudienceRole;
  nameKey: string;
  descriptionKey: string;
  icon: string;
  dashboardPath: string;
  primaryColor: string;
}

export const AUDIENCES: readonly AudienceMeta[] = [
  {
    role: "farmer",
    nameKey: "audiences.farmer.name",
    descriptionKey: "audiences.farmer.description",
    icon: "🌾",
    dashboardPath: "/farmer",
    primaryColor: "emerald",
  },
  {
    role: "student",
    nameKey: "audiences.student.name",
    descriptionKey: "audiences.student.description",
    icon: "🎓",
    dashboardPath: "/student",
    primaryColor: "blue",
  },
  {
    role: "expert",
    nameKey: "audiences.expert.name",
    descriptionKey: "audiences.expert.description",
    icon: "🔬",
    dashboardPath: "/expert",
    primaryColor: "purple",
  },
  {
    role: "manager",
    nameKey: "audiences.manager.name",
    descriptionKey: "audiences.manager.description",
    icon: "📊",
    dashboardPath: "/manager",
    primaryColor: "amber",
  },
  {
    role: "researcher",
    nameKey: "audiences.researcher.name",
    descriptionKey: "audiences.researcher.description",
    icon: "📚",
    dashboardPath: "/researcher",
    primaryColor: "rose",
  },
] as const;

export function getAudienceByRole(role: AudienceRole): AudienceMeta | undefined {
  return AUDIENCES.find((a) => a.role === role);
}
'''

def make_audience_dashboard(role, class_name, icon, color, items_keys, has_calendar=False, has_lab=False, has_kpi=False, has_alerts=False, has_chart=False, has_citation=False):
    items_section = ""
    if has_kpi:
        items_section += '''
      {/* KPI cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {kpis.map((kpi, i) => (
          <div key={i} className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-600">{t(kpi.labelKey)}</p>
              <span className="text-2xl" aria-hidden="true">{kpi.icon}</span>
            </div>
            <p className="mt-2 text-2xl font-bold text-gray-900">{kpi.value}</p>
            {kpi.trend && <p className="mt-1 text-xs text-emerald-600">{kpi.trend}</p>}
          </div>
        ))}
      </div>'''

    extra_sections = ""
    if has_calendar:
        extra_sections += '''
      {/* Calendar */}
      <section className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("audiences.' + role + '.calendarTitle")}</h2>
        <div className="grid gap-3 sm:grid-cols-7">
          {["sat", "sun", "mon", "tue", "wed", "thu", "fri"].map((day, i) => (
            <div key={day} className="rounded-lg bg-gray-50 p-3 text-center">
              <p className="text-xs font-semibold text-gray-500">{t("audiences.' + role + '.day" + (i + 1))}</p>
              <p className="mt-1 text-lg font-bold text-gray-900">{i + 1}</p>
              {i === 2 && <p className="mt-1 text-xs text-emerald-600">{t("audiences.' + role + '.irrigation")}</p>}
              {i === 5 && <p className="mt-1 text-xs text-amber-600">{t("audiences.' + role + '.fertilize")}</p>}
            </div>
          ))}
        </div>
      </section>'''

    if has_lab:
        extra_sections += '''
      {/* Virtual Lab */}
      <section className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("audiences.' + role + '.labTitle")}</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {simulatorLinks.map((sim, i) => (
            <Link key={i} to={sim.to} className="group rounded-lg border border-gray-200 p-4 transition hover:border-emerald-200 hover:bg-emerald-50">
              <span className="text-2xl">{sim.icon}</span>
              <h3 className="mt-2 text-sm font-semibold text-gray-900">{t(sim.labelKey)}</h3>
              <p className="mt-1 text-xs text-gray-500">{t(sim.descKey)}</p>
            </Link>
          ))}
        </div>
      </section>'''

    if has_alerts:
        extra_sections += '''
      {/* Active Alerts */}
      <section className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("audiences.' + role + '.alertsTitle")}</h2>
        <div className="space-y-2">
          {alerts.map((alert, i) => (
            <div key={i} className={`flex items-center gap-3 rounded-lg border p-3 ${alert.severity === "critical" ? "border-red-200 bg-red-50" : alert.severity === "high" ? "border-amber-200 bg-amber-50" : "border-blue-200 bg-blue-50"}`}>
              <span className="text-xl">{alert.icon}</span>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{t(alert.titleKey)}</p>
                <p className="text-xs text-gray-500">{t(alert.descKey)}</p>
              </div>
              <span className="text-xs text-gray-400">{alert.time}</span>
            </div>
          ))}
        </div>
      </section>'''

    if has_chart:
        extra_sections += '''
      {/* Quick Charts */}
      <section className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("audiences.' + role + '.chartsTitle")}</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg bg-gray-50 p-4">
            <h3 className="mb-3 text-sm font-medium text-gray-700">{t("audiences.' + role + '.chart1Title")}</h3>
            <div className="flex h-32 items-end justify-around">
              {[40, 65, 50, 80, 70, 90, 60].map((h, i) => (
                <div key={i} className="w-6 rounded-t bg-emerald-500" style={{ height: `${h}%` }} />
              ))}
            </div>
          </div>
          <div className="rounded-lg bg-gray-50 p-4">
            <h3 className="mb-3 text-sm font-medium text-gray-700">{t("audiences.' + role + '.chart2Title")}</h3>
            <div className="flex h-32 items-end justify-around">
              {[30, 45, 60, 75, 65, 80, 95].map((h, i) => (
                <div key={i} className="w-6 rounded-t bg-blue-500" style={{ height: `${h}%` }} />
              ))}
            </div>
          </div>
        </div>
      </section>'''

    if has_citation:
        extra_sections += '''
      {/* Recent Citations */}
      <section className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("audiences.' + role + '.citationsTitle")}</h2>
        <div className="space-y-3">
          {citations.map((cit, i) => (
            <div key={i} className="border-s-2 border-emerald-500 ps-4">
              <p className="text-sm font-medium text-gray-900">{cit.title}</p>
              <p className="text-xs text-gray-500">{cit.authors} • {cit.year} • {cit.journal}</p>
              <code className="mt-1 block text-xs text-emerald-600">{cit.doi}</code>
            </div>
          ))}
        </div>
      </section>'''

    return f'''/**
 * ============================================================================
 *  {class_name} — dashboard for {role} audience (i18n-aware)
 * ============================================================================
 */

import {{ Link }} from "react-router-dom";

import {{ useLanguage }} from "@/hooks/useLanguage";

export function {class_name}(): JSX.Element {{
  const {{ t, dir, language }} = useLanguage();

  const kpis = {items_keys}['kpis'];
  {f'const simulatorLinks = {items_keys}["simulatorLinks"];' if has_lab else ''}
  {f'const alerts = {items_keys}["alerts"];' if has_alerts else ''}
  {f'const citations = {items_keys}["citations"];' if has_citation else ''}

  return (
    <div dir={{dir}} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <div className="flex items-center gap-3">
          <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-{color}-50 text-3xl">{icon}</span>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{{t("audiences.{role}.title")}}</h1>
            <p className="mt-1 text-sm text-gray-600">{{t("audiences.{role}.subtitle")}}</p>
          </div>
        </div>
      </header>

      <div className="space-y-6">
        {items_section}{extra_sections}
      </div>
    </div>
  );
}}
'''

FARMER_DASHBOARD = make_audience_dashboard(
    "farmer", "FarmerDashboard", "🌾", "emerald",
    '''{
      "kpis": [
        { labelKey: "audiences.farmer.kpiCropHealth", value: "۸۵٪", icon: "🌱", trend: "↗ ۵٪" },
        { labelKey: "audiences.farmer.kpiSoilMoisture", value: "۳۲٪", icon: "💧", trend: "↘ ۸٪" },
        { labelKey: "audiences.farmer.kpiWeather", value: "۲۴°C", icon: "☀️", trend: "آفتابی" },
        { labelKey: "audiences.farmer.kpiPrice", value: "۱۲٬۵۰۰", icon: "💰", trend: "↗ تومان/کیلو" },
      ]
    }''',
    has_calendar=True, has_alerts=True
)

STUDENT_DASHBOARD = make_audience_dashboard(
    "student", "StudentDashboard", "🎓", "blue",
    '''{
      "kpis": [
        { labelKey: "audiences.student.kpiCourses", value: "۳", icon: "📚", trend: "فعال" },
        { labelKey: "audiences.student.kpiProgress", value: "۶۸٪", icon: "📈", trend: "↗ ۱۲٪" },
        { labelKey: "audiences.student.kpiCertificates", value: "۲", icon: "🏆", trend: "تکمیل‌شده" },
        { labelKey: "audiences.student.kpiPoints", value: "۸۵۰", icon: "⭐", trend: "EcoCoin" },
      ],
      "simulatorLinks": [
        { to: "/simulators/climate", icon: "🌡️", labelKey: "simulators.climate.name", descKey: "simulators.climate.description" },
        { to: "/simulators/crop", icon: "🌾", labelKey: "simulators.crop.name", descKey: "simulators.crop.description" },
        { to: "/simulators/carbon", icon: "🏭", labelKey: "simulators.carbon.name", descKey: "simulators.carbon.description" },
      ]
    }''',
    has_lab=True
)

EXPERT_DASHBOARD = make_audience_dashboard(
    "expert", "ExpertDashboard", "🔬", "purple",
    '''{
      "kpis": [
        { labelKey: "audiences.expert.kpiAnalyses", value: "۲۴", icon: "📊", trend: "این ماه" },
        { labelKey: "audiences.expert.kpiReports", value: "۸", icon: "📄", trend: "منتشرشده" },
        { labelKey: "audiences.expert.kpiDatasets", value: "۴۷", icon: "🗂️", trend: "فعال" },
        { labelKey: "audiences.expert.kpiAPI", value: "۱.۲K", icon: "🔌", trend: "کوئری/روز" },
      ],
      "simulatorLinks": [
        { to: "/simulators/hydrology", icon: "💧", labelKey: "simulators.hydrology.name", descKey: "simulators.hydrology.description" },
        { to: "/simulators/soilErosion", icon: "🏔️", labelKey: "simulators.soilErosion.name", descKey: "simulators.soilErosion.description" },
        { to: "/simulators/biodiversity", icon: "🦋", labelKey: "simulators.biodiversity.name", descKey: "simulators.biodiversity.description" },
      ]
    }''',
    has_lab=True, has_chart=True
)

MANAGER_DASHBOARD = make_audience_dashboard(
    "manager", "ManagerDashboard", "📊", "amber",
    '''{
      "kpis": [
        { labelKey: "audiences.manager.kpiBudget", value: "۸.۲B", icon: "💰", trend: "تومان" },
        { labelKey: "audiences.manager.kpiProjects", value: "۱۲", icon: "📁", trend: "فعال" },
        { labelKey: "audiences.manager.kpiKPI", value: "۸۷٪", icon: "🎯", trend: "↗ ۴٪" },
        { labelKey: "audiences.manager.kpiRisk", value: "متوسط", icon: "⚠️", trend: "۳ هشدار" },
      ],
      "alerts": [
        { icon: "🔥", severity: "critical", titleKey: "alerts.wildfire.title", descKey: "alerts.wildfire.desc", time: "۲ دقیقه پیش" },
        { icon: "🏜️", severity: "high", titleKey: "alerts.drought.title", descKey: "alerts.drought.desc", time: "۱ ساعت پیش" },
        { icon: "🌊", severity: "high", titleKey: "alerts.flood.title", descKey: "alerts.flood.desc", time: "۳ ساعت پیش" },
      ]
    }''',
    has_alerts=True, has_chart=True
)

RESEARCHER_DASHBOARD = make_audience_dashboard(
    "researcher", "ResearcherDashboard", "📚", "rose",
    '''{
      "kpis": [
        { labelKey: "audiences.researcher.kpiDatasets", value: "۲۸۴", icon: "📊", trend: "دانلود" },
        { labelKey: "audiences.researcher.kpiCitations", value: "۱۲", icon: "📝", trend: "مقاله" },
        { labelKey: "audiences.researcher.kpiDOIs", value: "۸", icon: "🔗", trend: "تولید" },
        { labelKey: "audiences.researcher.kpiDownloads", value: "۱.۵K", icon: "⬇️", trend: "این ماه" },
      ],
      "citations": [
        { title: "Climate change impacts on Iranian watersheds", authors: "Hosseini M. et al.", year: "2024", journal: "J. Environ. Sci.", doi: "10.1234/jes.2024.001" },
        { title: "Soil erosion modeling with RUSLE in semi-arid regions", authors: "Rezaei A. et al.", year: "2023", journal: "Catena", doi: "10.5678/cat.2023.045" },
        { title: "Biodiversity assessment using GEDI LiDAR", authors: "Karimi S. et al.", year: "2024", journal: "Remote Sens.", doi: "10.9012/rs.2024.089" },
      ]
    }''',
    has_chart=True, has_citation=True
)

# ---------------------------------------------------------------------------
# 4) CHART COMPONENTS
# ---------------------------------------------------------------------------

TIMESERIES_CHART_TSX = '''/**
 * ============================================================================
 *  TimeSeriesChart — lightweight SVG time-series chart (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";

export interface TimeSeriesPoint {
  x: string | number;
  y: number;
  label?: string;
}

export interface TimeSeriesChartProps {
  data: readonly TimeSeriesPoint[];
  height?: number;
  color?: string;
  unit?: string;
  titleKey?: string;
}

export function TimeSeriesChart({
  data,
  height = 200,
  color = "#059669",
  unit,
  titleKey,
}: TimeSeriesChartProps): JSX.Element {
  const { dir } = useLanguage();

  if (data.length === 0) return <></>;

  const width = 600;
  const padding = { top: 20, right: 20, bottom: 40, left: 50 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  const xValues = data.map((d) => Number(d.x) || 0);
  const yValues = data.map((d) => d.y);
  const xMin = Math.min(...xValues);
  const xMax = Math.max(...xValues);
  const yMin = Math.min(...yValues, 0);
  const yMax = Math.max(...yValues);

  const xScale = (x: number) => padding.left + ((x - xMin) / (xMax - xMin || 1)) * chartW;
  const yScale = (y: number) => padding.top + chartH - ((y - yMin) / (yMax - yMin || 1)) * chartH;

  const pathD = data
    .map((d, i) => `${i === 0 ? "M" : "L"} ${xScale(Number(d.x) || 0)} ${yScale(d.y)}`)
    .join(" ");

  const areaD = `${pathD} L ${xScale(xMax)} ${padding.top + chartH} L ${xScale(xMin)} ${padding.top + chartH} Z`;

  return (
    <div dir={dir} className="rounded-xl border border-gray-200 bg-white p-4">
      {titleKey && <h3 className="mb-3 text-sm font-semibold text-gray-900">{titleKey}</h3>}
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" role="img">
        <defs>
          <linearGradient id="area-gradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((p) => (
          <line
            key={p}
            x1={padding.left}
            y1={padding.top + p * chartH}
            x2={padding.left + chartW}
            y2={padding.top + p * chartH}
            stroke="#e5e7eb"
            strokeWidth="1"
          />
        ))}
        {/* Area */}
        <path d={areaD} fill="url(#area-gradient)" />
        {/* Line */}
        <path d={pathD} fill="none" stroke={color} strokeWidth="2" />
        {/* Points */}
        {data.map((d, i) => (
          <circle
            key={i}
            cx={xScale(Number(d.x) || 0)}
            cy={yScale(d.y)}
            r="3"
            fill={color}
            className="hover:r-5 transition-all"
          >
            {d.label && <title>{d.label}: {d.y}{unit ?? ""}</title>}
          </circle>
        ))}
        {/* X-axis labels */}
        {data.filter((_, i) => i % Math.ceil(data.length / 6) === 0).map((d, i, arr) => {
          const originalIdx = data.indexOf(d);
          return (
            <text
              key={i}
              x={xScale(Number(d.x) || 0)}
              y={padding.top + chartH + 20}
              textAnchor="middle"
              className="fill-gray-500 text-xs"
            >
              {d.x}
            </text>
          );
        })}
        {/* Y-axis labels */}
        {[0, 0.25, 0.5, 0.75, 1].map((p) => {
          const value = yMin + (yMax - yMin) * (1 - p);
          return (
            <text
              key={p}
              x={padding.left - 8}
              y={padding.top + p * chartH + 4}
              textAnchor="end"
              className="fill-gray-500 text-xs"
            >
              {Math.round(value)}
            </text>
          );
        })}
      </svg>
    </div>
  );
}
'''

HEATMAP_CHART_TSX = '''/**
 * ============================================================================
 *  HeatmapChart — grid-based heatmap (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/lib/utils";

export interface HeatmapCell {
  row: string;
  col: string;
  value: number;
}

export interface HeatmapChartProps {
  data: readonly HeatmapCell[];
  rows: readonly string[];
  cols: readonly string[];
  titleKey?: string;
  /** Color scale: 0 = cool, 1 = warm */
  colorScale?: "red-green" | "blue-red" | "purple";
}

function getColor(value: number, max: number, scale: string): string {
  const ratio = Math.min(1, Math.max(0, value / max));
  if (scale === "red-green") {
    if (ratio < 0.33) return `rgba(239, 68, 68, ${0.3 + ratio})`;
    if (ratio < 0.66) return `rgba(245, 158, 11, ${0.3 + ratio})`;
    return `rgba(16, 185, 129, ${0.3 + ratio})`;
  }
  if (scale === "blue-red") {
    if (ratio < 0.5) return `rgba(59, 130, 246, ${0.3 + ratio * 1.5})`;
    return `rgba(239, 68, 68, ${0.3 + ratio})`;
  }
  return `rgba(168, 85, 247, ${0.3 + ratio})`;
}

export function HeatmapChart({
  data, rows, cols, titleKey,
  colorScale = "red-green",
}: HeatmapChartProps): JSX.Element {
  const { dir } = useLanguage();
  const max = Math.max(...data.map((d) => d.value), 1);
  const getCell = (row: string, col: string): HeatmapCell | undefined =>
    data.find((d) => d.row === row && d.col === col);

  return (
    <div dir={dir} className="rounded-xl border border-gray-200 bg-white p-4">
      {titleKey && <h3 className="mb-3 text-sm font-semibold text-gray-900">{titleKey}</h3>}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr>
              <th className="p-2"></th>
              {cols.map((col) => (
                <th key={col} className="p-2 text-xs font-medium text-gray-500">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row}>
                <td className="p-2 text-xs font-medium text-gray-700">{row}</td>
                {cols.map((col) => {
                  const cell = getCell(row, col);
                  return (
                    <td key={col} className="p-1">
                      <div
                        className={cn("flex h-12 min-w-[3rem] items-center justify-center rounded text-xs font-medium")}
                        style={{ backgroundColor: cell ? getColor(cell.value, max, colorScale) : "transparent" }}
                        title={cell ? `${row} - ${col}: ${cell.value}` : ""}
                      >
                        {cell?.value ?? ""}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
'''

COMPARISON_CHART_TSX = '''/**
 * ============================================================================
 *  ComparisonChart — side-by-side comparison bar chart (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/lib/utils";

export interface ComparisonItem {
  label: string;
  valueA: number;
  valueB: number;
  labelA: string;
  labelB: string;
}

export interface ComparisonChartProps {
  data: readonly ComparisonItem[];
  titleKey?: string;
  colorA?: string;
  colorB?: string;
}

export function ComparisonChart({
  data, titleKey,
  colorA = "bg-emerald-500",
  colorB = "bg-blue-500",
}: ComparisonChartProps): JSX.Element {
  const { dir } = useLanguage();
  const max = Math.max(...data.flatMap((d) => [d.valueA, d.valueB]), 1);

  return (
    <div dir={dir} className="rounded-xl border border-gray-200 bg-white p-4">
      {titleKey && <h3 className="mb-4 text-sm font-semibold text-gray-900">{titleKey}</h3>}
      <div className="space-y-4">
        {data.map((item, i) => (
          <div key={i}>
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="font-medium text-gray-700">{item.label}</span>
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="w-20 text-xs text-gray-500">{item.labelA}</span>
                <div className="h-6 flex-1 overflow-hidden rounded bg-gray-100">
                  <div
                    className={cn("h-full rounded transition-all", colorA)}
                    style={{ width: `${(item.valueA / max) * 100}%` }}
                  />
                </div>
                <span className="w-12 text-end text-xs font-medium text-gray-700">{item.valueA}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-20 text-xs text-gray-500">{item.labelB}</span>
                <div className="h-6 flex-1 overflow-hidden rounded bg-gray-100">
                  <div
                    className={cn("h-full rounded transition-all", colorB)}
                    style={{ width: `${(item.valueB / max) * 100}%` }}
                  />
                </div>
                <span className="w-12 text-end text-xs font-medium text-gray-700">{item.valueB}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# 5) ALERT SYSTEM
# ---------------------------------------------------------------------------

ALERT_TYPES_TS = '''/**
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
'''

ALERT_REGISTRY_TS = '''/**
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
'''

USE_ALERTS_TS = '''/**
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
'''

ALERTS_PANEL_TSX = '''/**
 * ============================================================================
 *  AlertsPanel — display environmental alerts (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { useAlerts } from "./useAlerts";
import { cn } from "@/lib/utils";
import type { AlertSeverity } from "./types";

const SEVERITY_CONFIG: Record<AlertSeverity, { icon: string; className: string }> = {
  info: { icon: "ℹ️", className: "border-blue-200 bg-blue-50" },
  low: { icon: "🟢", className: "border-emerald-200 bg-emerald-50" },
  medium: { icon: "🟡", className: "border-amber-200 bg-amber-50" },
  high: { icon: "🟠", className: "border-orange-200 bg-orange-50" },
  critical: { icon: "🔴", className: "border-red-200 bg-red-50" },
};

function formatRelativeTime(iso: string, language: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (language === "fa") {
    if (minutes < 60) return `${minutes} دقیقه پیش`;
    if (hours < 24) return `${hours} ساعت پیش`;
    return `${days} روز پیش`;
  }
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
}

export function AlertsPanel(): JSX.Element {
  const { t, dir, language } = useLanguage();
  const { alerts, unreadCount } = useAlerts();

  return (
    <div dir={dir} className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("alerts.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">
          {t("alerts.subtitle")} • {unreadCount} {t("alerts.active")}
        </p>
      </header>

      <div className="space-y-3">
        {alerts.length === 0 ? (
          <div className="rounded-xl border border-dashed border-gray-300 p-12 text-center">
            <div className="text-4xl">✅</div>
            <h3 className="mt-3 text-base font-semibold text-gray-900">{t("alerts.noAlerts")}</h3>
            <p className="mt-1 text-sm text-gray-600">{t("alerts.noAlertsDesc")}</p>
          </div>
        ) : (
          alerts.map((alert) => {
            const cfg = SEVERITY_CONFIG[alert.severity];
            return (
              <div
                key={alert.id}
                role="alert"
                className={cn("flex items-start gap-3 rounded-xl border p-4", cfg.className)}
              >
                <span className="text-2xl" aria-hidden="true">{cfg.icon}</span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="text-sm font-semibold text-gray-900">{t(alert.titleKey)}</h3>
                    <span className="shrink-0 text-xs text-gray-500">
                      {formatRelativeTime(alert.triggeredAt, language)}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-gray-600">{t(alert.descriptionKey)}</p>
                  <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
                    <span className="rounded-full bg-white/60 px-2 py-0.5 font-medium text-gray-700">
                      📍 {alert.region}
                    </span>
                    {alert.satellite && (
                      <span className="rounded-full bg-white/60 px-2 py-0.5 font-medium text-gray-700">
                        🛰️ {alert.satellite}
                      </span>
                    )}
                    {!alert.acknowledged && (
                      <span className="rounded-full bg-emerald-600 px-2 py-0.5 font-medium text-white">
                        {t("alerts.new")}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# 6) COMMAND PALETTE
# ---------------------------------------------------------------------------

USE_COMMAND_PALETTE_TS = '''/**
 * ============================================================================
 *  useCommandPalette — manage Command Palette open/close + Ctrl+K shortcut
 * ============================================================================
 */

import { useCallback, useEffect, useState } from "react";

export function useCommandPalette(): {
  isOpen: boolean;
  open: () => void;
  close: () => void;
  toggle: () => void;
} {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    function handleKey(event: KeyboardEvent): void {
      if ((event.ctrlKey || event.metaKey) && event.key === "k") {
        event.preventDefault();
        setIsOpen((v) => !v);
      }
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, []);

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);
  const toggle = useCallback(() => setIsOpen((v) => !v), []);

  return { isOpen, open, close, toggle };
}
'''

COMMAND_PALETTE_TSX = '''/**
 * ============================================================================
 *  CommandPalette — global search & quick actions (Ctrl+K)
 * ============================================================================
 *
 *  Inspired by:
 *   - Vercel cmdk
 *   - Linear command palette
 *   - Raycast
 * ============================================================================
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { useAuth } from "@/hooks/useAuth";
import { AVAILABLE_LANGUAGES } from "@/lib/i18n-utils";
import { SIMULATORS } from "@/simulators/registry";
import { SATELLITES } from "@/satellites/registry";
import { SCENARIOS } from "@/scenarios/registry";
import { cn } from "@/lib/utils";
import type { SupportedLanguage } from "@/i18n";

interface CommandItem {
  id: string;
  label: string;
  hint?: string;
  icon: string;
  action: () => void;
  category: "navigate" | "simulator" | "satellite" | "scenario" | "language" | "auth";
}

export interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CommandPalette({ isOpen, onClose }: CommandPaletteProps): JSX.Element | null {
  const { t, language, changeLanguage } = useLanguage();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [activeIdx, setActiveIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input when opening
  useEffect(() => {
    if (isOpen) {
      setQuery("");
      setActiveIdx(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  // Build commands
  const commands = useMemo<CommandItem[]>(() => {
    const navCommands: CommandItem[] = [
      { id: "nav-dashboard", label: t("nav.dashboard"), icon: "📊", category: "navigate", action: () => { navigate("/dashboard"); onClose(); } },
      { id: "nav-documents", label: t("nav.documents"), icon: "📄", category: "navigate", action: () => { navigate("/documents"); onClose(); } },
      { id: "nav-carbon", label: t("nav.carbon"), icon: "🏭", category: "navigate", action: () => { navigate("/carbon"); onClose(); } },
      { id: "nav-watersheds", label: t("nav.watersheds"), icon: "💧", category: "navigate", action: () => { navigate("/hydrology/watersheds"); onClose(); } },
      { id: "nav-soil", label: t("nav.soil"), icon: "🌱", category: "navigate", action: () => { navigate("/soil"); onClose(); } },
      { id: "nav-profile", label: t("user.myProfile"), icon: "👤", category: "navigate", action: () => { navigate("/profile"); onClose(); } },
      { id: "nav-alerts", label: t("alerts.title"), icon: "🔔", category: "navigate", action: () => { navigate("/alerts"); onClose(); } },
    ];

    const simCommands: CommandItem[] = SIMULATORS.map((sim) => ({
      id: `sim-${sim.id}`,
      label: t(sim.nameKey),
      hint: t(sim.descriptionKey),
      icon: sim.icon,
      category: "simulator" as const,
      action: () => { navigate(`/simulators/${sim.id}`); onClose(); },
    }));

    const satCommands: CommandItem[] = SATELLITES.map((sat) => ({
      id: `sat-${sat.id}`,
      label: sat.name,
      hint: sat.agency,
      icon: sat.icon,
      category: "satellite" as const,
      action: () => { navigate("/satellites"); onClose(); },
    }));

    const scenCommands: CommandItem[] = SCENARIOS.map((scn) => ({
      id: `scn-${scn.id}`,
      label: t(scn.nameKey),
      hint: t(scn.descriptionKey),
      icon: scn.icon,
      category: "scenario" as const,
      action: () => { navigate("/scenarios"); onClose(); },
    }));

    const langCommands: CommandItem[] = AVAILABLE_LANGUAGES.map((meta) => ({
      id: `lang-${meta.code}`,
      label: `${meta.flag} ${meta.nativeName}`,
      hint: meta.englishName,
      icon: "🌐",
      category: "language" as const,
      action: () => { changeLanguage(meta.code as SupportedLanguage); onClose(); },
    }));

    const authCommands: CommandItem[] = [
      {
        id: "auth-logout",
        label: t("user.logout"),
        icon: "🚪",
        category: "auth",
        action: async () => { await logout(); navigate("/login"); onClose(); },
      },
    ];

    return [...navCommands, ...simCommands, ...satCommands, ...scenCommands, ...langCommands, ...authCommands];
  }, [t, navigate, onClose, changeLanguage, logout]);

  // Filter by query (fuzzy: contains all chars in order)
  const filtered = useMemo(() => {
    if (!query.trim()) return commands;
    const q = query.toLowerCase();
    return commands.filter((c) =>
      c.label.toLowerCase().includes(q) ||
      c.hint?.toLowerCase().includes(q) ||
      c.category.includes(q)
    );
  }, [commands, query]);

  // Reset active index when filter changes
  useEffect(() => {
    setActiveIdx(0);
  }, [query]);

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen) return;
    function handleKey(event: KeyboardEvent): void {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        setActiveIdx((i) => Math.min(i + 1, filtered.length - 1));
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        setActiveIdx((i) => Math.max(i - 1, 0));
      } else if (event.key === "Enter") {
        event.preventDefault();
        const cmd = filtered[activeIdx];
        if (cmd) cmd.action();
      }
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [isOpen, filtered, activeIdx]);

  if (!isOpen) return null;

  const categoryLabels: Record<CommandItem["category"], string> = {
    navigate: t("commandPalette.navigate"),
    simulator: t("simulators.title"),
    satellite: t("satellites.title"),
    scenario: t("scenarios.title"),
    language: t("common.language"),
    auth: t("user.login"),
  };

  // Group filtered commands by category
  const grouped = filtered.reduce<Record<string, CommandItem[]>>((acc, cmd) => {
    (acc[cmd.category] ??= []).push(cmd);
    return acc;
  }, {});

  let runningIdx = 0;

  return (
    <div className="fixed inset-0 z-[100] flex items-start justify-center bg-black/50 pt-[10vh] backdrop-blur-sm" onClick={onClose}>
      <div
        dir={language === "fa" || language === "ar" ? "rtl" : "ltr"}
        className="w-full max-w-xl overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search input */}
        <div className="flex items-center gap-3 border-b border-gray-100 px-4 py-3">
          <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("commandPalette.placeholder")}
            className="flex-1 bg-transparent text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none"
          />
          <kbd className="rounded border border-gray-200 bg-gray-50 px-1.5 py-0.5 text-xs text-gray-500">ESC</kbd>
        </div>

        {/* Results */}
        <div className="max-h-[60vh] overflow-y-auto p-2">
          {filtered.length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-gray-500">
              {t("commandPalette.noResults")}
            </div>
          ) : (
            Object.entries(grouped).map(([cat, items]) => (
              <div key={cat} className="mb-2">
                <p className="px-3 py-1 text-xs font-semibold uppercase tracking-wider text-gray-400">
                  {categoryLabels[cat as CommandItem["category"]]}
                </p>
                {items.map((cmd) => {
                  const idx = runningIdx++;
                  return (
                    <button
                      key={cmd.id}
                      type="button"
                      onMouseEnter={() => setActiveIdx(idx)}
                      onClick={() => cmd.action()}
                      className={cn(
                        "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-start transition",
                        idx === activeIdx ? "bg-emerald-50" : "hover:bg-gray-50",
                      )}
                    >
                      <span className="text-xl" aria-hidden="true">{cmd.icon}</span>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-gray-900">{cmd.label}</p>
                        {cmd.hint && <p className="truncate text-xs text-gray-500">{cmd.hint}</p>}
                      </div>
                    </button>
                  );
                })}
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-gray-100 px-4 py-2 text-xs text-gray-400">
          <span>{t("commandPalette.footerHint")}</span>
          <span>{filtered.length} {t("commandPalette.results")}</span>
        </div>
      </div>
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# 7) PWA MANIFEST
# ---------------------------------------------------------------------------

PWA_MANIFEST = '''{
  "name": "Econojin — Environmental Monitoring",
  "short_name": "Econojin",
  "description": "International environmental monitoring and green economy platform",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#f9fafb",
  "theme_color": "#059669",
  "orientation": "any",
  "lang": "fa",
  "dir": "rtl",
  "categories": ["environment", "education", "productivity"],
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ],
  "shortcuts": [
    {
      "name": "Dashboard",
      "short_name": "Dashboard",
      "url": "/dashboard",
      "icons": [{ "src": "/icon-192.png", "sizes": "192x192" }]
    },
    {
      "name": "Simulators",
      "short_name": "Simulators",
      "url": "/simulators",
      "icons": [{ "src": "/icon-192.png", "sizes": "192x192" }]
    },
    {
      "name": "Satellites",
      "short_name": "Satellites",
      "url": "/satellites",
      "icons": [{ "src": "/icon-192.png", "sizes": "192x192" }]
    }
  ]
}
'''

# ---------------------------------------------------------------------------
# 8) LAYOUT UPDATE (mount CommandPalette)
# ---------------------------------------------------------------------------

LAYOUT_TSX = '''/**
 * ============================================================================
 *  Layout — shell that composes Header + Sidebar + content + Footer + CommandPalette
 * ============================================================================
 */

import { useState, type ReactNode } from "react";

import { Footer } from "@/components/Layout/Footer";
import { Header } from "@/components/Layout/Header";
import { Sidebar } from "@/components/Layout/Sidebar";
import { CommandPalette } from "@/components/CommandPalette/CommandPalette";
import { useLanguage } from "@/hooks/useLanguage";
import { useCommandPalette } from "@/hooks/useCommandPalette";

export interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps): JSX.Element {
  const { dir } = useLanguage();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const palette = useCommandPalette();

  return (
    <div dir={dir} className="flex min-h-screen flex-col bg-gray-50">
      <Header onToggleSidebar={() => setSidebarOpen((v) => !v)} />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex-1 overflow-y-auto" role="main">
          {children}
          <Footer />
        </main>
      </div>

      {/* Global Command Palette (Ctrl+K) */}
      <CommandPalette isOpen={palette.isOpen} onClose={palette.close} />
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# 9) i18n ADDITIONS
# ---------------------------------------------------------------------------

I18N_ADDITIONS = {
    "audiences": {
        "title": "داشبوردهای اختصاصی",
        "selectRole": "نقش خود را انتخاب کنید",
        "farmer": {
            "name": "کشاورز",
            "title": "داشبورد کشاورز",
            "subtitle": "مدیریت مزرعه، آب‌وهوا و قیمت محصولات",
            "description": "داشبورد تخصصی برای کشاورزان",
            "kpiCropHealth": "سلامت محصول",
            "kpiSoilMoisture": "رطوبت خاک",
            "kpiWeather": "دمای هوا",
            "kpiPrice": "قیمت محصول",
            "calendarTitle": "تقویم کشاورزی این هفته",
            "day1": "ش", "day2": "ی", "day3": "د", "day4": "س", "day5": "چ", "day6": "پ", "day7": "ج",
            "irrigation": "آبیاری",
            "fertilize": "کود",
            "alertsTitle": "هشدارهای مزرعه",
        },
        "student": {
            "name": "دانشجو",
            "title": "داشبورد دانشجو",
            "subtitle": "آزمایشگاه مجازی، دوره‌ها و آزمون‌ها",
            "description": "داشبورد تخصصی برای دانشجویان",
            "kpiCourses": "دوره‌های فعال",
            "kpiProgress": "پیشرفت کلی",
            "kpiCertificates": "گواهی‌نامه‌ها",
            "kpiPoints": "امتیاز EcoCoin",
            "labTitle": "آزمایشگاه مجازی",
        },
        "expert": {
            "name": "کارشناس",
            "title": "داشبورد کارشناس",
            "subtitle": "تحلیل‌های پیشرفته و ابزارهای تخصصی",
            "description": "داشبورد تخصصی برای کارشناسان محیط‌زیست",
            "kpiAnalyses": "تحلیل‌های این ماه",
            "kpiReports": "گزارش‌های منتشرشده",
            "kpiDatasets": "دیتاست‌های فعال",
            "kpiAPI": "کوئری API در روز",
            "labTitle": "ابزارهای تخصصی",
            "chartsTitle": "نمودارهای سریع",
            "chart1Title": "روند ماهانه",
            "chart2Title": "مقایسه مناطق",
        },
        "manager": {
            "name": "مدیر",
            "title": "داشبورد مدیر",
            "subtitle": "KPI، گزارش‌های اجرایی و هشدارها",
            "description": "داشبورد تخصصی برای مدیران",
            "kpiBudget": "بودجه",
            "kpiProjects": "پروژه‌های فعال",
            "kpiKPI": "تحقق KPI",
            "kpiRisk": "سطح ریسک",
            "alertsTitle": "هشدارهای بحرانی",
            "chartsTitle": "نمودارهای اجرایی",
            "chart1Title": "بودجه vs هزینه",
            "chart2Title": "پیشرفت پروژه‌ها",
        },
        "researcher": {
            "name": "پژوهشگر",
            "title": "داشبورد پژوهشگر",
            "subtitle": "داده خام، نمودارهای پیشرفته و استناد",
            "description": "داشبورد تخصصی برای پژوهشگران",
            "kpiDatasets": "دیتاست‌های دانلود",
            "kpiCitations": "مقالات",
            "kpiDOIs": "DOI تولیدشده",
            "kpiDownloads": "دانلود این ماه",
            "chartsTitle": "نمودارهای پیشرفته",
            "chart1Title": "روند زمانی داده",
            "chart2Title": "توزیع مکانی",
            "citationsTitle": "استنادهای اخیر",
        },
    },
    "alerts": {
        "title": "هشدارها",
        "subtitle": "هشدارهای بلادرنگ محیط‌زیستی",
        "active": "فعال",
        "new": "جدید",
        "noAlerts": "هشداری وجود ندارد",
        "noAlertsDesc": "همه چیز رو به راه است!",
        "wildfire": {"title": "هشدار آتش‌سوزی", "desc": "آتش‌سوزی فعال در منطقه شناسایی شد"},
        "drought": {"title": "هشدار خشکسالی", "desc": "شاخص خشکسالی به سطح هشدار رسیده است"},
        "flood": {"title": "هشدار سیلاب", "desc": "احتمال سیلاب در ۲۴ ساعت آینده"},
        "airQuality": {"title": "هشدار کیفیت هوا", "desc": "غلظت NO₂ از حد مجاز فراتر رفته است"},
        "deforestation": {"title": "هشدار جنگل‌زدایی", "desc": "تغییر ناهنجار در پوشش جنگل شناسایی شد"},
        "pest": {"title": "هشدار آفت", "desc": "حمله آفت در مزرعه شناسایی شد"},
    },
    "commandPalette": {
        "placeholder": "جستجو یا اجرای دستور...",
        "noResults": "نتیجه‌ای یافت نشد",
        "navigate": "صفحات",
        "results": "نتیجه",
        "footerHint": "↑↓ برای پیمایش، Enter برای انتخاب، ESC برای بستن",
    },
    "scenarios": {
        "agriculturalMonitoring": {"name": "پایش کشاورزی", "description": "پایش سلامت محصول با Sentinel-2 و NDVI"},
        "airQuality": {"name": "کیفیت هوا", "description": "پایش آلاینده‌های هوا با Sentinel-5P"},
        "wildfire": {"name": "آتش‌سوزی جنگل", "description": "هشدار و پهنه‌بندی آتش‌سوزی با VIIRS"},
        "urbanization": {"name": "شهرسازی گسترش‌یافته", "description": "تحلیل رشد شهری با Sentinel-2 و VIIRS"},
        "biodiversityConservation": {"name": "حفظ تنوع زیستی", "description": "ارزیابی اولویت‌های حفاظت با GEDI"},
    },
}

# English version (mirror structure)
I18N_ADDITIONS_EN = {
    "audiences": {
        "title": "Audience Dashboards",
        "selectRole": "Select your role",
        "farmer": {
            "name": "Farmer", "title": "Farmer Dashboard", "subtitle": "Farm management, weather, and prices",
            "description": "Specialized dashboard for farmers",
            "kpiCropHealth": "Crop health", "kpiSoilMoisture": "Soil moisture", "kpiWeather": "Air temp",
            "kpiPrice": "Product price", "calendarTitle": "Weekly agricultural calendar",
            "day1": "S", "day2": "M", "day3": "T", "day4": "W", "day5": "T", "day6": "F", "day7": "S",
            "irrigation": "Irrigation", "fertilize": "Fertilize", "alertsTitle": "Farm alerts",
        },
        "student": {
            "name": "Student", "title": "Student Dashboard", "subtitle": "Virtual lab, courses, and exams",
            "description": "Specialized dashboard for students",
            "kpiCourses": "Active courses", "kpiProgress": "Overall progress",
            "kpiCertificates": "Certificates", "kpiPoints": "EcoCoin points",
            "labTitle": "Virtual lab",
        },
        "expert": {
            "name": "Expert", "title": "Expert Dashboard", "subtitle": "Advanced analysis and tools",
            "description": "Specialized dashboard for environmental experts",
            "kpiAnalyses": "Analyses this month", "kpiReports": "Published reports",
            "kpiDatasets": "Active datasets", "kpiAPI": "API queries/day",
            "labTitle": "Specialized tools",
            "chartsTitle": "Quick charts", "chart1Title": "Monthly trend", "chart2Title": "Regional comparison",
        },
        "manager": {
            "name": "Manager", "title": "Manager Dashboard", "subtitle": "KPIs, executive reports, and alerts",
            "description": "Specialized dashboard for managers",
            "kpiBudget": "Budget", "kpiProjects": "Active projects",
            "kpiKPI": "KPI achievement", "kpiRisk": "Risk level",
            "alertsTitle": "Critical alerts",
            "chartsTitle": "Executive charts", "chart1Title": "Budget vs spend", "chart2Title": "Project progress",
        },
        "researcher": {
            "name": "Researcher", "title": "Researcher Dashboard", "subtitle": "Raw data, advanced charts, and citations",
            "description": "Specialized dashboard for researchers",
            "kpiDatasets": "Datasets downloaded", "kpiCitations": "Articles",
            "kpiDOIs": "DOIs generated", "kpiDownloads": "Downloads this month",
            "chartsTitle": "Advanced charts", "chart1Title": "Time series trend", "chart2Title": "Spatial distribution",
            "citationsTitle": "Recent citations",
        },
    },
    "alerts": {
        "title": "Alerts", "subtitle": "Real-time environmental alerts",
        "active": "active", "new": "new",
        "noAlerts": "No alerts", "noAlertsDesc": "All clear!",
        "wildfire": {"title": "Wildfire alert", "desc": "Active wildfire detected in region"},
        "drought": {"title": "Drought alert", "desc": "Drought index reached warning level"},
        "flood": {"title": "Flood alert", "desc": "Flood probability in next 24 hours"},
        "airQuality": {"title": "Air quality alert", "desc": "NO₂ concentration exceeds safe limit"},
        "deforestation": {"title": "Deforestation alert", "desc": "Anomalous forest cover change detected"},
        "pest": {"title": "Pest alert", "desc": "Pest infestation detected in farm"},
    },
    "commandPalette": {
        "placeholder": "Search or run a command...",
        "noResults": "No results found",
        "navigate": "Pages",
        "results": "results",
        "footerHint": "↑↓ to navigate, Enter to select, ESC to close",
    },
    "scenarios": {
        "agriculturalMonitoring": {"name": "Agricultural Monitoring", "description": "Crop health monitoring with Sentinel-2 and NDVI"},
        "airQuality": {"name": "Air Quality", "description": "Air pollutant monitoring with Sentinel-5P"},
        "wildfire": {"name": "Wildfire", "description": "Fire detection and mapping with VIIRS"},
        "urbanization": {"name": "Urbanization", "description": "Urban growth analysis with Sentinel-2 and VIIRS"},
        "biodiversityConservation": {"name": "Biodiversity Conservation", "description": "Conservation priority assessment with GEDI"},
    },
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    root = detect_root()
    print(f"[INFO] Project root: {root}")
    print()

    files_to_write = [
        # 5 new scenarios
        *SCENARIO_FILES,
        # Updated registry
        ("src/scenarios/registry.ts", SCEN_REGISTRY_TS),
        # Audience types + 5 dashboards
        ("src/audiences/types.ts", AUDIENCE_TYPES_TS),
        ("src/audiences/FarmerDashboard.tsx", FARMER_DASHBOARD),
        ("src/audiences/StudentDashboard.tsx", STUDENT_DASHBOARD),
        ("src/audiences/ExpertDashboard.tsx", EXPERT_DASHBOARD),
        ("src/audiences/ManagerDashboard.tsx", MANAGER_DASHBOARD),
        ("src/audiences/ResearcherDashboard.tsx", RESEARCHER_DASHBOARD),
        # Chart components
        ("src/components/charts/TimeSeriesChart.tsx", TIMESERIES_CHART_TSX),
        ("src/components/charts/HeatmapChart.tsx", HEATMAP_CHART_TSX),
        ("src/components/charts/ComparisonChart.tsx", COMPARISON_CHART_TSX),
        # Alert system
        ("src/alerts/types.ts", ALERT_TYPES_TS),
        ("src/alerts/registry.ts", ALERT_REGISTRY_TS),
        ("src/alerts/useAlerts.ts", USE_ALERTS_TS),
        ("src/alerts/AlertsPanel.tsx", ALERTS_PANEL_TSX),
        # Command palette
        ("src/hooks/useCommandPalette.ts", USE_COMMAND_PALETTE_TS),
        ("src/components/CommandPalette/CommandPalette.tsx", COMMAND_PALETTE_TSX),
        # PWA
        ("public/manifest.webmanifest", PWA_MANIFEST),
        # Updated layout
        ("src/components/Layout/Layout.tsx", LAYOUT_TSX),
    ]

    print("=" * 72)
    print(f" Phase 5: Generating {len(files_to_write)} files")
    print("=" * 72)

    written = 0
    for rel_path, content in files_to_write:
        changed = write_file(root, rel_path, content)
        if changed:
            written += 1
        action = "created" if not (root / rel_path).exists() else "rewrote" if changed else "ok"
        size = (root / rel_path).stat().st_size if (root / rel_path).exists() else 0
        print(f"  [{action:>8}]  {rel_path}  ({size} bytes)")

    print(f"\n  Total files written: {written}")

    # Update i18n
    print()
    print("=" * 72)
    print(" Updating i18n locale files (fa + en)")
    print("=" * 72)

    for locale_file, additions in [
        ("src/i18n/locales/fa.json", I18N_ADDITIONS),
        ("src/i18n/locales/en.json", I18N_ADDITIONS_EN),
    ]:
        full = root / locale_file
        if not full.exists():
            print(f"  [SKIP]  {locale_file} not found")
            continue

        data = json.loads(full.read_text(encoding="utf-8"))
        added = 0

        def merge_keys(target, source):
            nonlocal added
            for k, v in source.items():
                if k not in target:
                    target[k] = v
                    if isinstance(v, dict):
                        added += count_leaves(v)
                    else:
                        added += 1
                elif isinstance(target[k], dict) and isinstance(v, dict):
                    merge_keys(target[k], v)

        def count_leaves(d):
            n = 0
            for v in d.values():
                if isinstance(v, dict):
                    n += count_leaves(v)
                else:
                    n += 1
            return n

        merge_keys(data, additions)
        full.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  [updated]  {locale_file}  (+{added} keys)")

    print()
    print("=" * 72)
    print(" DONE — Phase 5 Complete!")
    print("=" * 72)
    print(f"  Files written: {written}")
    print()
    print("  New features:")
    print("    • 5 remaining scenarios (10 total)")
    print("    • 5 audience dashboards (farmer/student/expert/manager/researcher)")
    print("    • 3 chart components (TimeSeries, Heatmap, Comparison)")
    print("    • Alert system (6 alert types)")
    print("    • Command Palette (Ctrl+K)")
    print("    • PWA manifest")
    print()
    print("  Next step:")
    print("    1. Run update_routes_phase5.py to add audience + alerts routes")
    print("    2. pnpm run build")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
