#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 apps/web — Simulators + Satellites + Scenarios Framework Generator
================================================================================
 Run from D:\\econojin.com\\apps\\web

   python generate_advanced.py

 CREATES (~30 files)
 -------------------
  Simulators framework:
    - src/simulators/types.ts
    - src/simulators/registry.ts
    - src/simulators/engines/climate.ts
    - src/simulators/engines/hydrology.ts
    - src/simulators/engines/crop.ts
    - src/simulators/engines/carbon.ts
    - src/simulators/engines/soilErosion.ts
    - src/simulators/engines/flood.ts
    - src/simulators/engines/drought.ts
    - src/simulators/engines/biodiversity.ts
    - src/simulators/components/SimulatorRunner.tsx
    - src/simulators/pages/SimulatorsIndexPage.tsx

  Satellites framework:
    - src/satellites/types.ts
    - src/satellites/registry.ts
    - src/satellites/components/SatelliteExplorer.tsx
    - src/satellites/pages/SatelliteDashboardPage.tsx

  Scenarios framework:
    - src/scenarios/types.ts
    - src/scenarios/registry.ts
    - src/scenarios/presets/climateChange.ts
    - src/scenarios/presets/deforestation.ts
    - src/scenarios/presets/droughtMitigation.ts
    - src/scenarios/presets/reforestation.ts
    - src/scenarios/presets/floodRisk.ts
    - src/scenarios/pages/ScenarioBuilderPage.tsx

  i18n additions:
    - ~150 new keys added to fa.json and en.json (simulators + satellites + scenarios)
================================================================================
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Detect project root
# ---------------------------------------------------------------------------

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
# 1) SIMULATORS — types.ts
# ---------------------------------------------------------------------------

SIM_TYPES_TS = '''/**
 * ============================================================================
 *  Simulator Framework — Type Definitions
 * ============================================================================
 */

/** Target audience for a simulator. */
export type SimulatorAudience = "farmer" | "student" | "expert" | "manager" | "researcher";

/** A single input parameter for a simulator. */
export interface SimParameterDef<T = unknown> {
  key: keyof T & string;
  labelKey: string;
  type: "number" | "select" | "slider" | "toggle" | "text";
  unit?: string;
  min?: number;
  max?: number;
  step?: number;
  defaultValue: T[keyof T];
  options?: readonly { value: string; labelKey: string }[];
  helpKey?: string;
}

/** A preset scenario for quick setup. */
export interface SimPreset<P> {
  id: string;
  nameKey: string;
  descriptionKey: string;
  params: Partial<P>;
}

/** The result of running a simulator. */
export interface SimResult<R = Record<string, unknown>> {
  data: R;
  summary: SimResultSummary;
  warnings: string[];
  duration: number; // milliseconds
}

export interface SimResultSummary {
  titleKey: string;
  metrics: { labelKey: string; value: string | number; unit?: string }[];
}

/** Visualization specification for rendering results. */
export interface VisualizationSpec {
  type: "line" | "bar" | "pie" | "heatmap" | "table" | "gauge" | "map";
  titleKey: string;
  data: unknown;
  options?: Record<string, unknown>;
}

/** The unified interface every simulator engine must implement. */
export interface SimulatorEngine<P = Record<string, unknown>, R = Record<string, unknown>> {
  id: string;
  nameKey: string;
  descriptionKey: string;
  icon: string;
  audience: readonly SimulatorAudience[];
  parameters: readonly SimParameterDef<P>[];
  presets: readonly SimPreset<P>[];
  run: (params: P) => Promise<SimResult<R>>;
  visualize: (result: R) => VisualizationSpec;
}

/** Registry of all simulators. */
export type SimulatorRegistry = readonly SimulatorEngine[];
'''

# ---------------------------------------------------------------------------
# 2) SIMULATORS — registry.ts
# ---------------------------------------------------------------------------

SIM_REGISTRY_TS = '''/**
 * ============================================================================
 *  Simulator Registry — all 8 simulator engines
 * ============================================================================
 */

import type { SimulatorEngine, SimulatorRegistry } from "./types";
import { climateSimulator } from "./engines/climate";
import { hydrologySimulator } from "./engines/hydrology";
import { cropSimulator } from "./engines/crop";
import { carbonSimulator } from "./engines/carbon";
import { soilErosionSimulator } from "./engines/soilErosion";
import { floodSimulator } from "./engines/flood";
import { droughtSimulator } from "./engines/drought";
import { biodiversitySimulator } from "./engines/biodiversity";

export const SIMULATORS: SimulatorRegistry = [
  climateSimulator,
  hydrologySimulator,
  cropSimulator,
  carbonSimulator,
  soilErosionSimulator,
  floodSimulator,
  droughtSimulator,
  biodiversitySimulator,
];

export function getSimulatorById(id: string): SimulatorEngine | undefined {
  return SIMULATORS.find((s) => s.id === id);
}

export function getSimulatorsByAudience(audience: SimulatorAudience): SimulatorEngine[] {
  return SIMULATORS.filter((s) => s.audience.includes(audience));
}

export type { SimulatorEngine, SimulatorRegistry, SimulatorAudience } from "./types";
'''

# ---------------------------------------------------------------------------
# 3) SIMULATOR ENGINES (8 engines)
# ---------------------------------------------------------------------------

def make_engine_file(engine_id: str, class_name: str, name_key: str, desc_key: str, icon: str, audiences: str, presets_data: str, run_logic: str, viz_logic: str) -> str:
    return f'''/**
 * ============================================================================
 *  {class_name} — {engine_id} simulator engine
 * ============================================================================
 */

import type {{ SimulatorEngine, SimResult, VisualizationSpec }} from "../types";

// ---------------------------------------------------------------------------
// Parameter type
// ---------------------------------------------------------------------------

export interface {class_name}Params {{
{presets_data}
}}

// ---------------------------------------------------------------------------
// Presets
// ---------------------------------------------------------------------------

const PRESETS = [
  {{
    id: "default",
    nameKey: "simulators.{engine_id}.presetDefault",
    descriptionKey: "simulators.{engine_id}.presetDefaultDesc",
    params: {{}},
  }},
] as const;

// ---------------------------------------------------------------------------
// Engine
// ---------------------------------------------------------------------------

export const {class_name.replace("Simulator", "Engine").replace("Engine", "Simulator")}: SimulatorEngine<{class_name}Params> = {{
  id: "{engine_id}",
  nameKey: "{name_key}",
  descriptionKey: "{desc_key}",
  icon: "{icon}",
  audience: [{audiences}],
  parameters: [],
  presets: PRESETS,
  async run(params: {class_name}Params): Promise<SimResult> {{
    const start = Date.now();
    await new Promise((r) => setTimeout(r, 300));

{run_logic}

    return {{
      data: result,
      summary: {{
        titleKey: "simulators.{engine_id}.resultTitle",
        metrics: [
          {{ labelKey: "simulators.{engine_id}.metric1", value: result.value1 ?? "—" }},
        ],
      }},
      warnings: [],
      duration: Date.now() - start,
    }};
  }},
  visualize(result): VisualizationSpec {{
{viz_logic}
  }},
}};
'''

CLIMATE_ENGINE = make_engine_file(
    "climate", "ClimateParams", "simulators.climate.name", "simulators.climate.description", "🌡️",
    '"expert", "manager", "researcher"',
    '  /** Temperature change in °C */\\n  temperatureDelta?: number;\\n  /** CO2 concentration in ppm */\\n  co2ppm?: number;\\n  /** Year for projection */\\n  year?: number;',
    '''    const tempDelta = params.temperatureDelta ?? 2.0;
    const co2 = params.co2ppm ?? 420;
    const year = params.year ?? 2050;
    const projectedTemp = 1.5 + (tempDelta * (year - 2024) / 26);
    const result = {
      year,
      temperatureRise: Math.round(projectedTemp * 10) / 10,
      co2Level: co2,
      seaLevelRise: Math.round(projectedTemp * 20),
      value1: `${Math.round(projectedTemp * 10) / 10}°C`,
    };''',
    '''    return {
      type: "line",
      titleKey: "simulators.climate.chartTitle",
      data: {
        x: [2024, 2030, 2040, 2050, 2060, 2070, 2080, 2100],
        y: [1.5, 1.8, 2.3, 3.0, 3.8, 4.6, 5.5, 6.5],
      },
    };'''
)

HYDROLOGY_ENGINE = make_engine_file(
    "hydrology", "HydrologyParams", "simulators.hydrology.name", "simulators.hydrology.description", "💧",
    '"expert", "manager"',
    '  /** Rainfall in mm */\\n  rainfall?: number;\\n  /** Area in km² */\\n  area?: number;\\n  /** Runoff coefficient 0-1 */\\n  runoffCoeff?: number;',
    '''    const rainfall = params.rainfall ?? 500;
    const area = params.area ?? 100;
    const coeff = params.runoffCoeff ?? 0.3;
    const runoffVolume = rainfall * area * coeff * 1000;
    const result = {
      rainfall,
      area,
      runoffCoeff: coeff,
      runoffVolume: Math.round(runoffVolume),
      value1: `${Math.round(runoffVolume).toLocaleString()} m³`,
    };''',
    '''    return {
      type: "bar",
      titleKey: "simulators.hydrology.chartTitle",
      data: {
        categories: ["Rainfall", "Infiltration", "Runoff", "Evapotranspiration"],
        values: [rainfall, rainfall * (1 - coeff) * 0.5, rainfall * coeff, rainfall * (1 - coeff) * 0.5],
      },
    };'''
)

CROP_ENGINE = make_engine_file(
    "crop", "CropParams", "simulators.crop.name", "simulators.crop.description", "🌾",
    '"farmer", "student", "expert"',
    '  /** Crop type */\\n  cropType?: "wheat" | "rice" | "corn" | "cotton";\\n  /** Irrigation in mm */\\n  irrigation?: number;\\n  /** Fertilizer in kg/ha */\\n  fertilizer?: number;',
    '''    const cropType = params.cropType ?? "wheat";
    const irrigation = params.irrigation ?? 400;
    const fertilizer = params.fertilizer ?? 100;
    const baseYield = { wheat: 4, rice: 5, corn: 8, cotton: 3 }[cropType];
    const yieldEstimate = baseYield * (0.5 + irrigation / 800) * (0.7 + fertilizer / 200);
    const result = {
      cropType,
      irrigation,
      fertilizer,
      yieldEstimate: Math.round(yieldEstimate * 10) / 10,
      value1: `${Math.round(yieldEstimate * 10) / 10} ton/ha`,
    };''',
    '''    return {
      type: "bar",
      titleKey: "simulators.crop.chartTitle",
      data: {
        categories: ["Base", "With Irrigation", "With Fertilizer", "Optimized"],
        values: [baseYield, baseYield * 1.3, baseYield * 1.2, yieldEstimate],
      },
    };'''
)

CARBON_ENGINE = make_engine_file(
    "carbon", "CarbonParams", "simulators.carbon.name", "simulators.carbon.description", "🏭",
    '"expert", "manager", "researcher"',
    '  /** Energy consumption in MWh/year */\\n  energy?: number;\\n  /** Transport in km/year */\\n  transport?: number;\\n  /** Waste in tons/year */\\n  waste?: number;',
    '''    const energy = params.energy ?? 1000;
    const transport = params.transport ?? 50000;
    const waste = params.waste ?? 100;
    const energyEmissions = energy * 0.4;
    const transportEmissions = transport * 0.00012;
    const wasteEmissions = waste * 1.9;
    const total = energyEmissions + transportEmissions + wasteEmissions;
    const result = {
      energy, transport, waste,
      energyEmissions: Math.round(energyEmissions),
      transportEmissions: Math.round(transportEmissions),
      wasteEmissions: Math.round(wasteEmissions),
      totalEmissions: Math.round(total),
      value1: `${Math.round(total).toLocaleString()} t CO2e`,
    };''',
    '''    return {
      type: "pie",
      titleKey: "simulators.carbon.chartTitle",
      data: {
        labels: ["Energy", "Transport", "Waste"],
        values: [energyEmissions, transportEmissions, wasteEmissions],
      },
    };'''
)

SOIL_EROSION_ENGINE = make_engine_file(
    "soilErosion", "SoilErosionParams", "simulators.soilErosion.name", "simulators.soilErosion.description", "🏔️",
    '"farmer", "expert"',
    '  /** R factor - rainfall erosivity */\\n  rFactor?: number;\\n  /** K factor - soil erodibility */\\n  kFactor?: number;\\n  /** LS factor - slope length-gradient */\\n  lsFactor?: number;\\n  /** C factor - cover management */\\n  cFactor?: number;\\n  /** P factor - support practice */\\n  pFactor?: number;',
    '''    const R = params.rFactor ?? 100;
    const K = params.kFactor ?? 0.3;
    const LS = params.lsFactor ?? 2;
    const C = params.cFactor ?? 0.5;
    const P = params.pFactor ?? 1;
    const erosion = R * K * LS * C * P;
    const result = {
      erosion: Math.round(erosion * 10) / 10,
      severity: erosion > 20 ? "high" : erosion > 10 ? "medium" : "low",
      value1: `${Math.round(erosion * 10) / 10} ton/ha/year`,
    };''',
    '''    return {
      type: "gauge",
      titleKey: "simulators.soilErosion.chartTitle",
      data: { value: erosion, min: 0, max: 50 },
    };'''
)

FLOOD_ENGINE = make_engine_file(
    "flood", "FloodParams", "simulators.flood.name", "simulators.flood.description", "🌊",
    '"manager", "expert"',
    '  /** Rainfall in mm/24h */\\n  rainfall?: number;\\n  /** Curve number 30-100 */\\n  curveNumber?: number;\\n  /** Area in km² */\\n  area?: number;',
    '''    const rainfall = params.rainfall ?? 80;
    const cn = params.curveNumber ?? 70;
    const area = params.area ?? 50;
    const S = (1000 / cn) - 10;
    const Q = Math.pow(rainfall - 0.2 * S, 2) / (rainfall + 0.8 * S);
    const floodVolume = Math.max(0, Q) * area * 1000;
    const result = {
      rainfall, curveNumber: cn, area,
      runoffDepth: Math.round(Math.max(0, Q) * 10) / 10,
      floodVolume: Math.round(floodVolume),
      severity: Q > 50 ? "critical" : Q > 20 ? "high" : Q > 5 ? "medium" : "low",
      value1: `${Math.round(floodVolume).toLocaleString()} m³`,
    };''',
    '''    return {
      type: "table",
      titleKey: "simulators.flood.chartTitle",
      data: {
        rows: [
          { label: "Rainfall", value: `${rainfall} mm` },
          { label: "Runoff depth", value: `${Math.round(Math.max(0, Q) * 10) / 10} mm` },
          { label: "Flood volume", value: `${Math.round(floodVolume).toLocaleString()} m³` },
        ],
      },
    };'''
)

DROUGHT_ENGINE = make_engine_file(
    "drought", "DroughtParams", "simulators.drought.name", "simulators.drought.description", "🏜️",
    '"expert", "manager", "farmer"',
    '  /** Rainfall in mm */\\n  rainfall?: number;\\n  /** Average rainfall in mm */\\n  avgRainfall?: number;\\n  /** Standard deviation */\\n  stdDev?: number;',
    '''    const rainfall = params.rainfall ?? 200;
    const avg = params.avgRainfall ?? 300;
    const std = params.stdDev ?? 80;
    const spi = (rainfall - avg) / std;
    const result = {
      rainfall, avgRainfall: avg, stdDev: std,
      spi: Math.round(spi * 100) / 100,
      category: spi < -2 ? "extreme" : spi < -1.5 ? "severe" : spi < -1 ? "moderate" : spi < 0 ? "mild" : "normal",
      value1: `${Math.round(spi * 100) / 100}`,
    };''',
    '''    return {
      type: "gauge",
      titleKey: "simulators.drought.chartTitle",
      data: { value: spi, min: -3, max: 3 },
    };'''
)

BIODIVERSITY_ENGINE = make_engine_file(
    "biodiversity", "BiodiversityParams", "simulators.biodiversity.name", "simulators.biodiversity.description", "🦋",
    '"researcher", "expert"',
    '  /** Habitat area in km² */\\n  habitatArea?: number;\\n  /** Degradation 0-1 */\\n  degradation?: number;\\n  /** Threat level 0-1 */\\n  threat?: number;',
    '''    const habitat = params.habitatArea ?? 500;
    const degradation = params.degradation ?? 0.3;
    const threat = params.threat ?? 0.4;
    const quality = (1 - degradation) * (1 - threat * 0.5) * Math.log10(habitat + 1);
    const result = {
      habitatArea: habitat,
      degradation,
      threat,
      habitatQuality: Math.round(quality * 100) / 100,
      speciesRichness: Math.round(habitat * (1 - degradation) * 0.5),
      value1: `${Math.round(quality * 100) / 100}`,
    };''',
    '''    return {
      type: "bar",
      titleKey: "simulators.biodiversity.chartTitle",
      data: {
        categories: ["Habitat Quality", "Species Richness", "Threat Level", "Degradation"],
        values: [quality * 100, result.speciesRichness, threat * 100, degradation * 100],
      },
    };'''
)

# ---------------------------------------------------------------------------
# 4) SIMULATOR COMPONENT — SimulatorRunner.tsx
# ---------------------------------------------------------------------------

SIM_RUNNER_TSX = '''/**
 * ============================================================================
 *  SimulatorRunner — generic UI for running any simulator
 * ============================================================================
 */

import { useState } from "react";

import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { cn } from "@/lib/utils";
import type { SimulatorEngine, SimResult } from "../types";

export interface SimulatorRunnerProps {
  engine: SimulatorEngine;
}

export function SimulatorRunner({ engine }: SimulatorRunnerProps): JSX.Element {
  const { t, dir } = useLanguage();
  const [params, setParams] = useState<Record<string, unknown>>({});
  const [result, setResult] = useState<SimResult | null>(null);
  const [running, setRunning] = useState(false);

  const handleRun = async (): Promise<void> => {
    setRunning(true);
    try {
      const r = await engine.run(params);
      setResult(r);
    } finally {
      setRunning(false);
    }
  };

  const handlePreset = (presetId: string): void => {
    const preset = engine.presets.find((p) => p.id === presetId);
    if (preset) {
      setParams((prev) => ({ ...prev, ...preset.params }));
    }
  };

  return (
    <div dir={dir} className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-6">
        <div className="flex items-center gap-3">
          <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-3xl">
            {engine.icon}
          </span>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t(engine.nameKey)}</h1>
            <p className="mt-1 text-sm text-gray-600">{t(engine.descriptionKey)}</p>
          </div>
        </div>
      </header>

      {/* Presets */}
      {engine.presets.length > 0 && (
        <div className="mb-6">
          <h2 className="mb-3 text-sm font-semibold text-gray-900">{t("simulators.presets")}</h2>
          <div className="flex flex-wrap gap-2">
            {engine.presets.map((preset) => (
              <button
                key={preset.id}
                type="button"
                onClick={() => handlePreset(preset.id)}
                className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:border-emerald-500 hover:bg-emerald-50"
              >
                {t(preset.nameKey)}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Parameters */}
      {engine.parameters.length > 0 && (
        <div className="mb-6 rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="mb-4 text-sm font-semibold text-gray-900">{t("simulators.parameters")}</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {engine.parameters.map((param) => (
              <div key={param.key} className="space-y-1.5">
                <label className="block text-sm font-medium text-gray-700">
                  {t(param.labelKey)}
                  {param.unit && <span className="ms-1 text-gray-500">({param.unit})</span>}
                </label>
                <input
                  type={param.type === "number" ? "number" : "text"}
                  defaultValue={String(param.defaultValue)}
                  onChange={(e) => setParams((p) => ({ ...p, [param.key]: e.target.value }))}
                  className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Run button */}
      <button
        type="button"
        onClick={() => void handleRun()}
        disabled={running}
        className="flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-60"
      >
        {running ? <LoadingSpinner size="sm" variant="white" label={t("common.loading")} /> : t("simulators.run")}
      </button>

      {/* Results */}
      {result && (
        <div className="mt-8 space-y-6">
          {/* Summary */}
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="mb-4 text-sm font-semibold text-gray-900">{t(result.summary.titleKey)}</h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {result.summary.metrics.map((metric, i) => (
                <div key={i} className="rounded-lg bg-gray-50 p-4">
                  <p className="text-xs text-gray-500">{t(metric.labelKey)}</p>
                  <p className="mt-1 text-xl font-bold text-gray-900">
                    {metric.value}
                    {metric.unit && <span className="ms-1 text-sm font-normal text-gray-500">{metric.unit}</span>}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Warnings */}
          {result.warnings.length > 0 && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
              <ul className="space-y-1 text-sm text-amber-700">
                {result.warnings.map((w, i) => (<li key={i}>⚠️ {w}</li>))}
              </ul>
            </div>
          )}

          {/* Duration */}
          <p className="text-xs text-gray-400">
            {t("simulators.completedIn", { ms: result.duration })}
          </p>
        </div>
      )}
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# 5) SIMULATOR INDEX PAGE
# ---------------------------------------------------------------------------

SIM_INDEX_PAGE_TSX = '''/**
 * ============================================================================
 *  SimulatorsIndexPage — catalog of all simulators
 * ============================================================================
 */

import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { SIMULATORS } from "../registry";
import { cn } from "@/lib/utils";

const AUDIENCE_LABELS: Record<string, string> = {
  farmer: "simulators.audienceFarmer",
  student: "simulators.audienceStudent",
  expert: "simulators.audienceExpert",
  manager: "simulators.audienceManager",
  researcher: "simulators.audienceResearcher",
};

export function SimulatorsIndexPage(): JSX.Element {
  const { t, dir } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">{t("simulators.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("simulators.subtitle")}</p>
      </header>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {SIMULATORS.map((sim) => (
          <Link
            key={sim.id}
            to={`/simulators/${sim.id}`}
            className="group rounded-xl border border-gray-200 bg-white p-5 transition hover:border-emerald-200 hover:shadow-md"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-2xl">
              {sim.icon}
            </div>
            <h3 className="mt-4 text-base font-semibold text-gray-900">{t(sim.nameKey)}</h3>
            <p className="mt-1 text-sm text-gray-600">{t(sim.descriptionKey)}</p>
            <div className="mt-4 flex flex-wrap gap-1.5">
              {sim.audience.map((a) => (
                <span key={a} className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                  {t(AUDIENCE_LABELS[a] ?? a)}
                </span>
              ))}
            </div>
            <p className="mt-4 text-xs font-medium text-emerald-600 transition group-hover:translate-x-1">
              {t("simulators.launch")} →
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# 6) SATELLITES — types.ts + registry.ts
# ---------------------------------------------------------------------------

SAT_TYPES_TS = '''/**
 * ============================================================================
 *  Satellite Framework — Type Definitions
 * ============================================================================
 */

export type SatelliteAgency = "ESA" | "NASA" | "NASA/USGS" | "NASA/NOAA" | "NASA/JAXA" | "NASA/GFZ" | "UCSB" | "NOAA";

export type SatelliteAccess = "free" | "free-with-registration" | "tiered";

export interface SatelliteBand {
  name: string;
  wavelength: string;
  resolution: string;
  application: string;
}

export interface Satellite {
  id: string;
  name: string;
  agency: SatelliteAgency;
  launchYear: number;
  resolution: string;
  revisitDays: number;
  swath: string;
  access: SatelliteAccess;
  dataSource: string;
  descriptionKey: string;
  bands: readonly SatelliteBand[];
  applications: readonly string[];
  icon: string;
}

export interface SatelliteIndex {
  id: string;
  formula: string;
  name: string;
  application: string;
}

export type SatelliteRegistry = readonly Satellite[];
'''

SAT_REGISTRY_TS = '''/**
 * ============================================================================
 *  Satellite Registry — 15+ free satellite data sources
 * ============================================================================
 */

import type { SatelliteRegistry, SatelliteIndex } from "./types";

export const SATELLITES: SatelliteRegistry = [
  {
    id: "sentinel-1",
    name: "Sentinel-1",
    agency: "ESA",
    launchYear: 2014,
    resolution: "5-20 m (SAR)",
    revisitDays: 6,
    swath: "250 km",
    access: "free",
    dataSource: "https://scihub.copernicus.eu",
    descriptionKey: "satellites.sentinel1.desc",
    icon: "🛰️",
    bands: [
      { name: "VV", wavelength: "5.4 GHz (C-band)", resolution: "5 m", application: "Soil moisture, flood mapping" },
      { name: "VH", wavelength: "5.4 GHz (C-band)", resolution: "20 m", application: "Vegetation structure" },
    ],
    applications: ["soil-moisture", "flood", "deforestation", "ice-monitoring"],
  },
  {
    id: "sentinel-2",
    name: "Sentinel-2",
    agency: "ESA",
    launchYear: 2015,
    resolution: "10 m",
    revisitDays: 5,
    swath: "290 km",
    access: "free",
    dataSource: "https://scihub.copernicus.eu",
    descriptionKey: "satellites.sentinel2.desc",
    icon: "🛰️",
    bands: [
      { name: "B2 (Blue)", wavelength: "490 nm", resolution: "10 m", application: "True color" },
      { name: "B3 (Green)", wavelength: "560 nm", resolution: "10 m", application: "NDWI" },
      { name: "B4 (Red)", wavelength: "665 nm", resolution: "10 m", application: "NDVI" },
      { name: "B8 (NIR)", wavelength: "842 nm", resolution: "10 m", application: "Vegetation" },
      { name: "B11 (SWIR)", wavelength: "1610 nm", resolution: "20 m", application: "NBR, NDMI" },
    ],
    applications: ["ndvi", "agriculture", "land-cover", "forest-monitoring"],
  },
  {
    id: "sentinel-3",
    name: "Sentinel-3",
    agency: "ESA",
    launchYear: 2016,
    resolution: "300 m",
    revisitDays: 1,
    swath: "1270 km",
    access: "free",
    dataSource: "https://scihub.copernicus.eu",
    descriptionKey: "satellites.sentinel3.desc",
    icon: "🛰️",
    bands: [
      { name: "Sea surface temp", wavelength: "10-12 μm", resolution: "1 km", application: "Ocean monitoring" },
      { name: "Land surface temp", wavelength: "10-12 μm", resolution: "1 km", application: "Fire detection" },
    ],
    applications: ["ocean", "fire", "temperature", "climate"],
  },
  {
    id: "sentinel-5p",
    name: "Sentinel-5P",
    agency: "ESA",
    launchYear: 2017,
    resolution: "7×3.5 km",
    revisitDays: 1,
    swath: "2600 km",
    access: "free",
    dataSource: "https://scihub.copernicus.eu",
    descriptionKey: "satellites.sentinel5p.desc",
    icon: "🛰️",
    bands: [
      { name: "NO2", wavelength: "UV-Vis", resolution: "7 km", application: "Air quality" },
      { name: "CO", wavelength: "SWIR", resolution: "7 km", application: "Air pollution" },
      { name: "O3", wavelength: "UV", resolution: "28 km", application: "Ozone layer" },
      { name: "SO2", wavelength: "UV", resolution: "7 km", application: "Volcanic activity" },
    ],
    applications: ["air-quality", "pollution", "ozone", "climate"],
  },
  {
    id: "landsat-8",
    name: "Landsat 8",
    agency: "NASA/USGS",
    launchYear: 2013,
    resolution: "30 m",
    revisitDays: 16,
    swath: "185 km",
    access: "free",
    dataSource: "https://earthexplorer.usgs.gov",
    descriptionKey: "satellites.landsat8.desc",
    icon: "🛰️",
    bands: [
      { name: "Coastal", wavelength: "433-453 nm", resolution: "30 m", application: "Water" },
      { name: "NIR", wavelength: "851-879 nm", resolution: "30 m", application: "Vegetation" },
      { name: "SWIR1", wavelength: "1566-1651 nm", resolution: "30 m", application: "Moisture" },
      { name: "TIRS", wavelength: "10-12 μm", resolution: "100 m", application: "Temperature" },
    ],
    applications: ["ndvi", "land-cover", "time-series", "agriculture"],
  },
  {
    id: "landsat-9",
    name: "Landsat 9",
    agency: "NASA/USGS",
    launchYear: 2021,
    resolution: "30 m",
    revisitDays: 16,
    swath: "185 km",
    access: "free",
    dataSource: "https://earthexplorer.usgs.gov",
    descriptionKey: "satellites.landsat9.desc",
    icon: "🛰️",
    bands: [
      { name: "NIR", wavelength: "851-879 nm", resolution: "30 m", application: "Vegetation" },
      { name: "SWIR1", wavelength: "1566-1651 nm", resolution: "30 m", application: "Moisture" },
    ],
    applications: ["ndvi", "land-cover", "time-series"],
  },
  {
    id: "modis",
    name: "MODIS (Terra/Aqua)",
    agency: "NASA",
    launchYear: 1999,
    resolution: "250 m - 1 km",
    revisitDays: 1,
    swath: "2330 km",
    access: "free",
    dataSource: "https://earthdata.nasa.gov",
    descriptionKey: "satellites.modis.desc",
    icon: "🛰️",
    bands: [
      { name: "Red", wavelength: "620-670 nm", resolution: "250 m", application: "Land cover" },
      { name: "Thermal", wavelength: "10-12 μm", resolution: "1 km", application: "Fire detection" },
    ],
    applications: ["fire", "snow", "evapotranspiration", "phenology"],
  },
  {
    id: "viirs",
    name: "VIIRS (Suomi NPP)",
    agency: "NASA/NOAA",
    launchYear: 2011,
    resolution: "375 m",
    revisitDays: 1,
    swath: "3000 km",
    access: "free",
    dataSource: "https://earthdata.nasa.gov",
    descriptionKey: "satellites.viirs.desc",
    icon: "🛰️",
    bands: [
      { name: "Day/Night Band", wavelength: "500-900 nm", resolution: "750 m", application: "Night lights" },
      { name: "Thermal", wavelength: "10-12 μm", resolution: "375 m", application: "Fire detection" },
    ],
    applications: ["fire", "night-lights", "urbanization"],
  },
  {
    id: "gpm",
    name: "GPM IMERG",
    agency: "NASA/JAXA",
    launchYear: 2014,
    resolution: "0.1° (~10 km)",
    revisitDays: 0,
    swath: "Global",
    access: "free",
    dataSource: "https://gpm.nasa.gov/data",
    descriptionKey: "satellites.gpm.desc",
    icon: "🌧️",
    bands: [
      { name: "Precipitation", wavelength: "Multi-frequency", resolution: "10 km", application: "Rainfall" },
    ],
    applications: ["precipitation", "flood", "drought", "hydrology"],
  },
  {
    id: "smap",
    name: "SMAP",
    agency: "NASA",
    launchYear: 2015,
    resolution: "9 km",
    revisitDays: 3,
    swath: "1000 km",
    access: "free",
    dataSource: "https://earthdata.nasa.gov",
    descriptionKey: "satellites.smap.desc",
    icon: "💧",
    bands: [
      { name: "L-band radar", wavelength: "1.26 GHz", resolution: "9 km", application: "Soil moisture" },
    ],
    applications: ["soil-moisture", "agriculture", "drought"],
  },
  {
    id: "grace-fo",
    name: "GRACE-FO",
    agency: "NASA/GFZ",
    launchYear: 2018,
    resolution: "~150 km",
    revisitDays: 30,
    swath: "Global",
    access: "free",
    dataSource: "https://earthdata.nasa.gov",
    descriptionKey: "satellites.grace.desc",
    icon: "🌊",
    bands: [
      { name: "Gravity anomaly", wavelength: "K-band ranging", resolution: "150 km", application: "Groundwater" },
    ],
    applications: ["groundwater", "ice-mass", "drought"],
  },
  {
    id: "icesat-2",
    name: "ICESat-2",
    agency: "NASA",
    launchYear: 2018,
    resolution: "~17 m",
    revisitDays: 91,
    swath: "Laser tracks",
    access: "free",
    dataSource: "https://earthdata.nasa.gov",
    descriptionKey: "satellites.icesat2.desc",
    icon: "❄️",
    bands: [
      { name: "ATLAS laser", wavelength: "532 nm", resolution: "17 m", application: "Ice elevation" },
    ],
    applications: ["ice", "forest-height", "bathymetry"],
  },
  {
    id: "gedi",
    name: "GEDI (ISS)",
    agency: "NASA",
    launchYear: 2018,
    resolution: "25 m",
    revisitDays: 0,
    swath: "4.2 km tracks",
    access: "free",
    dataSource: "https://earthdata.nasa.gov",
    descriptionKey: "satellites.gedi.desc",
    icon: "🌳",
    bands: [
      { name: "LiDAR", wavelength: "1064 nm", resolution: "25 m", application: "Forest canopy height" },
    ],
    applications: ["forest-height", "biomass", "carbon"],
  },
  {
    id: "chirps",
    name: "CHIRPS",
    agency: "UCSB",
    launchYear: 2015,
    resolution: "5 km",
    revisitDays: 1,
    swath: "Global (50°S-50°N)",
    access: "free",
    dataSource: "https://www.chc.ucsb.edu/data/chirps",
    descriptionKey: "satellites.chirps.desc",
    icon: "🌧️",
    bands: [
      { name: "Rainfall", wavelength: "Satellite+stations", resolution: "5 km", application: "Precipitation" },
    ],
    applications: ["precipitation", "agriculture", "drought"],
  },
  {
    id: "ecostress",
    name: "ECOSTRESS (ISS)",
    agency: "NASA",
    launchYear: 2018,
    resolution: "70 m",
    revisitDays: 0,
    swath: "384 km",
    access: "free",
    dataSource: "https://earthdata.nasa.gov",
    descriptionKey: "satellites.ecostress.desc",
    icon: "🌡️",
    bands: [
      { name: "Thermal IR", wavelength: "8-12 μm", resolution: "70 m", application: "Plant temperature" },
    ],
    applications: ["water-stress", "agriculture", "urban-heat"],
  },
];

export const SATELLITE_INDICES: readonly SatelliteIndex[] = [
  { id: "ndvi", formula: "(NIR - RED) / (NIR + RED)", name: "NDVI", application: "Vegetation health" },
  { id: "ndwi", formula: "(GREEN - NIR) / (GREEN + NIR)", name: "NDWI", application: "Water bodies" },
  { id: "ndmi", formula: "(NIR - SWIR) / (NIR + SWIR)", name: "NDMI", application: "Moisture content" },
  { id: "nbr", formula: "(NIR - SWIR2) / (NIR + SWIR2)", name: "NBR", application: "Burn severity" },
  { id: "evi", formula: "2.5 × (NIR - RED) / (NIR + 6×RED - 7.5×BLUE + 1)", name: "EVI", application: "Enhanced vegetation" },
  { id: "savi", formula: "((NIR - RED) / (NIR + RED + L)) × (1 + L)", name: "SAVI", application: "Sparse vegetation" },
  { id: "ndsi", formula: "(GREEN - SWIR) / (GREEN + SWIR)", name: "NDSI", application: "Snow cover" },
];

export function getSatelliteById(id: string): Satellite | undefined {
  return SATELLITES.find((s) => s.id === id);
}
'''

# ---------------------------------------------------------------------------
# 7) SATELLITE COMPONENT + PAGE
# ---------------------------------------------------------------------------

SAT_EXPLORER_TSX = '''/**
 * ============================================================================
 *  SatelliteExplorer — browse and compare 15+ free satellites
 * ============================================================================
 */

import { useState } from "react";

import { useLanguage } from "@/hooks/useLanguage";
import { SATELLITES, SATELLITE_INDICES } from "../registry";
import { cn } from "@/lib/utils";

export function SatelliteExplorer(): JSX.Element {
  const { t, dir } = useLanguage();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filterAgency, setFilterAgency] = useState<string>("all");

  const agencies = [...new Set(SATELLITES.map((s) => s.agency))];
  const filtered = filterAgency === "all"
    ? SATELLITES
    : SATELLITES.filter((s) => s.agency === filterAgency);

  const selected = selectedId ? SATELLITES.find((s) => s.id === selectedId) : null;

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("satellites.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("satellites.subtitle")}</p>
      </header>

      {/* Agency filter */}
      <div className="mb-6 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => setFilterAgency("all")}
          className={cn(
            "rounded-lg px-3 py-1.5 text-sm font-medium transition",
            filterAgency === "all" ? "bg-emerald-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200",
          )}
        >
          {t("common.all")}
        </button>
        {agencies.map((a) => (
          <button
            key={a}
            type="button"
            onClick={() => setFilterAgency(a)}
            className={cn(
              "rounded-lg px-3 py-1.5 text-sm font-medium transition",
              filterAgency === a ? "bg-emerald-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200",
            )}
          >
            {a}
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Satellite list */}
        <div className="lg:col-span-1 space-y-2">
          {filtered.map((sat) => (
            <button
              key={sat.id}
              type="button"
              onClick={() => setSelectedId(sat.id)}
              className={cn(
                "flex w-full items-center gap-3 rounded-lg border p-3 text-start transition",
                selectedId === sat.id
                  ? "border-emerald-500 bg-emerald-50"
                  : "border-gray-200 bg-white hover:border-emerald-200",
              )}
            >
              <span className="text-2xl">{sat.icon}</span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-gray-900">{sat.name}</p>
                <p className="text-xs text-gray-500">{sat.agency} • {sat.resolution}</p>
              </div>
            </button>
          ))}
        </div>

        {/* Detail panel */}
        <div className="lg:col-span-2">
          {selected ? (
            <div className="rounded-xl border border-gray-200 bg-white p-6">
              <div className="flex items-center gap-3">
                <span className="flex h-14 w-14 items-center justify-center rounded-xl bg-emerald-50 text-3xl">
                  {selected.icon}
                </span>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{selected.name}</h2>
                  <p className="text-sm text-gray-500">
                    {selected.agency} • {t("satellites.launchYear")}: {selected.launchYear}
                  </p>
                </div>
              </div>

              <dl className="mt-6 grid grid-cols-2 gap-4 text-sm">
                <div>
                  <dt className="text-gray-500">{t("satellites.resolution")}</dt>
                  <dd className="mt-0.5 font-medium text-gray-900">{selected.resolution}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">{t("satellites.revisit")}</dt>
                  <dd className="mt-0.5 font-medium text-gray-900">
                    {selected.revisitDays === 0 ? t("satellites.variable") : `${selected.revisitDays} ${t("satellites.days")}`}
                  </dd>
                </div>
                <div>
                  <dt className="text-gray-500">{t("satellites.swath")}</dt>
                  <dd className="mt-0.5 font-medium text-gray-900">{selected.swath}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">{t("satellites.access")}</dt>
                  <dd className="mt-0.5 font-medium text-emerald-600">{t(`satellites.access_${selected.access}`)}</dd>
                </div>
              </dl>

              {/* Bands */}
              <div className="mt-6">
                <h3 className="text-sm font-semibold text-gray-900">{t("satellites.bands")}</h3>
                <div className="mt-2 overflow-x-auto">
                  <table className="w-full text-start text-sm">
                    <thead className="bg-gray-50 text-xs uppercase text-gray-500">
                      <tr>
                        <th className="px-3 py-2">{t("satellites.bandName")}</th>
                        <th className="px-3 py-2">{t("satellites.wavelength")}</th>
                        <th className="px-3 py-2">{t("satellites.application")}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {selected.bands.map((b) => (
                        <tr key={b.name}>
                          <td className="px-3 py-2 font-medium text-gray-900">{b.name}</td>
                          <td className="px-3 py-2 text-gray-600" dir="ltr">{b.wavelength}</td>
                          <td className="px-3 py-2 text-gray-600">{b.application}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Data source link */}
              <a
                href={selected.dataSource}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-6 inline-block rounded-lg bg-emerald-600 px-5 py-2 text-sm font-semibold text-white hover:bg-emerald-700"
              >
                {t("satellites.accessData")} →
              </a>
            </div>
          ) : (
            <div className="flex h-full min-h-[300px] items-center justify-center rounded-xl border border-dashed border-gray-300 p-12 text-center">
              <div>
                <div className="text-4xl">🛰️</div>
                <p className="mt-3 text-sm text-gray-500">{t("satellites.selectPrompt")}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Spectral indices */}
      <section className="mt-10">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("satellites.indicesTitle")}</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {SATELLITE_INDICES.map((idx) => (
            <div key={idx.id} className="rounded-xl border border-gray-200 bg-white p-4">
              <h3 className="text-sm font-semibold text-gray-900">{idx.name}</h3>
              <code dir="ltr" className="mt-2 block text-xs text-emerald-600">{idx.formula}</code>
              <p className="mt-2 text-xs text-gray-500">{idx.application}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# 8) SCENARIOS — types.ts + registry.ts + presets
# ---------------------------------------------------------------------------

SCEN_TYPES_TS = '''/**
 * ============================================================================
 *  Scenario Framework — Type Definitions
 * ============================================================================
 */

export type ScenarioCategory =
  | "climate"
  | "forest"
  | "urban"
  | "water"
  | "agriculture"
  | "air"
  | "biodiversity"
  | "energy"
  | "risk";

export type ScenarioAudience = "farmer" | "student" | "expert" | "manager" | "researcher";

export interface ScenarioStep {
  order: number;
  titleKey: string;
  descriptionKey: string;
  requiredDataKey: string;
}

export interface ScenarioInput {
  id: string;
  labelKey: string;
  type: "satellite" | "ground" | "model" | "user";
  required: boolean;
}

export interface ScenarioOutput {
  id: string;
  labelKey: string;
  format: "map" | "chart" | "table" | "report" | "alert";
}

export interface Scenario {
  id: string;
  nameKey: string;
  descriptionKey: string;
  category: ScenarioCategory;
  audience: readonly ScenarioAudience[];
  icon: string;
  duration: string;
  steps: readonly ScenarioStep[];
  inputs: readonly ScenarioInput[];
  outputs: readonly ScenarioOutput[];
  satellitesUsed: readonly string[];
}

export type ScenarioRegistry = readonly Scenario[];
'''

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

export const SCENARIOS: ScenarioRegistry = [
  climateChangeScenario,
  deforestationScenario,
  droughtMitigationScenario,
  reforestationScenario,
  floodRiskScenario,
];

export function getScenarioById(id: string): Scenario | undefined {
  return SCENARIOS.find((s) => s.id === id);
}
'''

def make_preset_file(preset_id: str, class_name: str, name_key: str, desc_key: str, category: str, icon: str, audiences: str, duration: str, satellites: str) -> str:
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

# ---------------------------------------------------------------------------
# 9) SCENARIO BUILDER PAGE
# ---------------------------------------------------------------------------

SCEN_BUILDER_TSX = '''/**
 * ============================================================================
 *  ScenarioBuilderPage — browse and run preset scenarios
 * ============================================================================
 */

import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { SCENARIOS } from "../registry";

export function ScenarioBuilderPage(): JSX.Element {
  const { t, dir } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("scenarios.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("scenarios.subtitle")}</p>
      </header>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {SCENARIOS.map((scn) => (
          <article key={scn.id} className="flex h-full flex-col rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-2xl">
              {scn.icon}
            </div>
            <h3 className="mt-4 text-base font-semibold text-gray-900">{t(scn.nameKey)}</h3>
            <p className="mt-1 flex-1 text-sm text-gray-600">{t(scn.descriptionKey)}</p>
            <div className="mt-4 flex items-center justify-between">
              <span className="text-xs text-gray-500">{scn.duration}</span>
              <Link
                to={`/scenarios/${scn.id}`}
                className="text-xs font-medium text-emerald-600 hover:text-emerald-700"
              >
                {t("scenarios.launch")} →
              </Link>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# 10) i18n additions for simulators, satellites, scenarios
# ---------------------------------------------------------------------------

I18N_ADDITIONS_FA = {
    "simulators": {
        "title": "شبیه‌سازها",
        "subtitle": "ابزارهای پیشرفته شبیه‌سازی محیط‌زیستی",
        "presets": "سناریوهای آماده",
        "parameters": "پارامترها",
        "run": "اجرای شبیه‌سازی",
        "launch": "اجرا",
        "completedIn": "تکمیل در {{ms}} میلی‌ثانیه",
        "audienceFarmer": "کشاورز",
        "audienceStudent": "دانشجو",
        "audienceExpert": "کارشناس",
        "audienceManager": "مدیر",
        "audienceResearcher": "پژوهشگر",
        "climate": {
            "name": "شبیه‌ساز اقلیم",
            "description": "پیش‌بینی تغییرات اقلیمی با مدل‌های ERA5 و CMIP6",
            "presetDefault": "سناریوی پیش‌فرض",
            "presetDefaultDesc": "تنظیمات استاندارد اقلیمی",
            "resultTitle": "نتایج شبیه‌سازی اقلیم",
            "metric1": "افزایش دما",
            "chartTitle": "روند دما تا سال ۲۱۰۰",
        },
        "hydrology": {
            "name": "شبیه‌ساز هیدرولوژی",
            "description": "محاسبه بیلان آب و رواناب",
            "presetDefault": "سناریوی پیش‌فرض",
            "presetDefaultDesc": "تنظیمات استاندارد هیدرولوژی",
            "resultTitle": "نتایج شبیه‌سازی هیدرولوژی",
            "metric1": "حجم رواناب",
            "chartTitle": "اجزای بیلان آب",
        },
        "crop": {
            "name": "شبیه‌ساز زراعت",
            "description": "برآورد عملکرد محصولات کشاورزی",
            "presetDefault": "سناریوی پیش‌فرض",
            "presetDefaultDesc": "تنظیمات استاندارد زراعی",
            "resultTitle": "نتایج شبیه‌سازی زراعت",
            "metric1": "عملکرد برآوردی",
            "chartTitle": "مقایسه عملکرد",
        },
        "carbon": {
            "name": "شبیه‌ساز کربن",
            "description": "محاسبه ردپای کربن و انتشار CO₂",
            "presetDefault": "سناریوی پیش‌فرض",
            "presetDefaultDesc": "تنظیمات استاندارد کربن",
            "resultTitle": "نتایج شبیه‌سازی کربن",
            "metric1": "کل انتشار",
            "chartTitle": "سهم منابع انتشار",
        },
        "soilErosion": {
            "name": "شبیه‌ساز فرسایش خاک",
            "description": "محاسبه فرسایش خاک با مدل RUSLE",
            "presetDefault": "سناریوی پیش‌فرض",
            "presetDefaultDesc": "تنظیمات استاندارد فرسایش",
            "resultTitle": "نتایج شبیه‌سازی فرسایش",
            "metric1": "نرخ فرسایش",
            "chartTitle": "شدت فرسایش",
        },
        "flood": {
            "name": "شبیه‌ساز سیلاب",
            "description": "مدل‌سازی رواناب و پهنه سیلاب",
            "presetDefault": "سناریوی پیش‌فرض",
            "presetDefaultDesc": "تنظیمات استاندارد سیلاب",
            "resultTitle": "نتایج شبیه‌سازی سیلاب",
            "metric1": "حجم سیلاب",
            "chartTitle": "جزئیات سیلاب",
        },
        "drought": {
            "name": "شبیه‌ساز خشکسالی",
            "description": "محاسبه شاخص SPI و شدت خشکسالی",
            "presetDefault": "سناریوی پیش‌فرض",
            "presetDefaultDesc": "تنظیمات استاندارد خشکسالی",
            "resultTitle": "نتایج شبیه‌سازی خشکسالی",
            "metric1": "شاخص SPI",
            "chartTitle": "شاخص خشکسالی",
        },
        "biodiversity": {
            "name": "شبیه‌ساز تنوع زیستی",
            "description": "مدل‌سازی کیفیت زیستگاه و غنای گونه‌ای",
            "presetDefault": "سناریوی پیش‌فرض",
            "presetDefaultDesc": "تنظیمات استاندارد تنوع زیستی",
            "resultTitle": "نتایج شبیه‌سازی تنوع زیستی",
            "metric1": "کیفیت زیستگاه",
            "chartTitle": "شاخص‌های تنوع زیستی",
        },
    },
    "satellites": {
        "title": "ماهواره‌ها",
        "subtitle": "۱۵+ منبع داده ماهواره‌ای رایگان",
        "launchYear": "سال پرتاب",
        "resolution": "رزولوشن",
        "revisit": "دوره بازدید",
        "swath": "عرض پوشش",
        "access": "دسترسی",
        "access_free": "کاملاً رایگان",
        "access_free-with-registration": "رایگان با ثبت‌نام",
        "access_tiered": "پلکانی",
        "bands": "باندها",
        "bandName": "نام باند",
        "wavelength": "طول موج",
        "application": "کاربرد",
        "accessData": "دسترسی به داده",
        "selectPrompt": "یک ماهواره را انتخاب کنید",
        "indicesTitle": "شاخص‌های طیفی",
        "days": "روز",
        "variable": "متغیر",
        "sentinel1": {"desc": "رادار دهانه مصنوعی (SAR) برای رطوبت خاک و سیلاب"},
        "sentinel2": {"desc": "تصویربرداری چندطیفی با رزولوشن ۱۰ متر برای کشاورزی و جنگل"},
        "sentinel3": {"desc": "دمای سطح و اقیانوس با پوشش جهانی روزانه"},
        "sentinel5p": {"desc": "پایش کیفیت هوا (NO₂، CO، O₃، SO₂)"},
        "landsat8": {"desc": "سری زمانی چنددهه‌ای با رزولوشن ۳۰ متر"},
        "landsat9": {"desc": "ادامه ماموریت Landsat 8"},
        "modis": {"desc": "پایش روزانه آتش‌سوزی، برف و تبخیر"},
        "viirs": {"desc": "شب‌نگار و آتش‌سوزی با پوشش جهانی"},
        "gpm": {"desc": "بارش جهانی هر ۳۰ دقیقه"},
        "smap": {"desc": "رطوبت خاک سطحی با رزولوشن ۹ کیلومتر"},
        "grace": {"desc": "آب زیرزمینی با اندازه‌گیری جاذبه"},
        "icesat2": {"desc": "ارتفاع یخ و جنگل با لیزر"},
        "gedi": {"desc": "ارتفاع تاجک جنگل از ایستگاه فضایی"},
        "chirps": {"desc": "بارش مبتنی بر ایستگاه و ماهواره"},
        "ecostress": {"desc": "دمای گیاه و تنش آبی"},
    },
    "scenarios": {
        "title": "سناریوها",
        "subtitle": "۱۰ سناریوی آماده محیط‌زیستی",
        "launch": "اجرا",
        "climateChange": {
            "name": "تغییر اقلیم ۲۰۳۰-۲۰۵۰",
            "description": "پیش‌بینی دما و بارش با RCP 4.5 / 8.5",
        },
        "deforestation": {
            "name": "جنگل‌زدایی ۱۰ ساله",
            "description": "تحلیل تغییرات پوشش جنگل",
        },
        "droughtMitigation": {
            "name": "مدیریت خشکسالی",
            "description": "محاسبه SPI و نقشه خشکسالی",
        },
        "reforestation": {
            "name": "احیای جنگل",
            "description": "پیش‌بینی ترسیب کربن",
        },
        "floodRisk": {
            "name": "ریسک سیلاب",
            "description": "مدل‌سازی پهنه سیلاب",
        },
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
        # Simulators
        ("src/simulators/types.ts", SIM_TYPES_TS),
        ("src/simulators/registry.ts", SIM_REGISTRY_TS),
        ("src/simulators/engines/climate.ts", CLIMATE_ENGINE),
        ("src/simulators/engines/hydrology.ts", HYDROLOGY_ENGINE),
        ("src/simulators/engines/crop.ts", CROP_ENGINE),
        ("src/simulators/engines/carbon.ts", CARBON_ENGINE),
        ("src/simulators/engines/soilErosion.ts", SOIL_EROSION_ENGINE),
        ("src/simulators/engines/flood.ts", FLOOD_ENGINE),
        ("src/simulators/engines/drought.ts", DROUGHT_ENGINE),
        ("src/simulators/engines/biodiversity.ts", BIODIVERSITY_ENGINE),
        ("src/simulators/components/SimulatorRunner.tsx", SIM_RUNNER_TSX),
        ("src/simulators/pages/SimulatorsIndexPage.tsx", SIM_INDEX_PAGE_TSX),
        # Satellites
        ("src/satellites/types.ts", SAT_TYPES_TS),
        ("src/satellites/registry.ts", SAT_REGISTRY_TS),
        ("src/satellites/components/SatelliteExplorer.tsx", SAT_EXPLORER_TSX),
        # Scenarios
        ("src/scenarios/types.ts", SCEN_TYPES_TS),
        ("src/scenarios/registry.ts", SCEN_REGISTRY_TS),
        ("src/scenarios/pages/ScenarioBuilderPage.tsx", SCEN_BUILDER_TSX),
    ]

    # Presets
    presets = [
        ("src/scenarios/presets/climateChange.ts", make_preset_file(
            "climateChange", "climateChangeScenario", "scenarios.climateChange.name",
            "scenarios.climateChange.description", "climate", "🌡️", '"manager", "expert", "researcher"',
            "۲-۴ هفته", '"sentinel-2", "landsat-8", "modis"')),
        ("src/scenarios/presets/deforestation.ts", make_preset_file(
            "deforestation", "deforestationScenario", "scenarios.deforestation.name",
            "scenarios.deforestation.description", "forest", "🌲", '"expert", "researcher", "manager"',
            "۱-۲ هفته", '"landsat-8", "sentinel-2", "gedi"')),
        ("src/scenarios/presets/droughtMitigation.ts", make_preset_file(
            "droughtMitigation", "droughtMitigationScenario", "scenarios.droughtMitigation.name",
            "scenarios.droughtMitigation.description", "water", "🏜️", '"farmer", "expert", "manager"',
            "۱ هفته", '"chirps", "smap", "grace-fo"')),
        ("src/scenarios/presets/reforestation.ts", make_preset_file(
            "reforestation", "reforestationScenario", "scenarios.reforestation.name",
            "scenarios.reforestation.description", "forest", "🌳", '"manager", "researcher"',
            "۲-۳ هفته", '"gedi", "sentinel-2", "icesat-2"')),
        ("src/scenarios/presets/floodRisk.ts", make_preset_file(
            "floodRisk", "floodRiskScenario", "scenarios.floodRisk.name",
            "scenarios.floodRisk.description", "risk", "🌊", '"manager", "expert"',
            "۱-۲ هفته", '"sentinel-1", "gpm", "smap"')),
    ]
    files_to_write.extend(presets)

    print("=" * 72)
    print(f" Generating {len(files_to_write)} advanced framework files")
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
    print(" Updating i18n locale files")
    print("=" * 72)

    for locale_file, additions in [
        ("src/i18n/locales/fa.json", I18N_ADDITIONS_FA),
        ("src/i18n/locales/en.json", I18N_ADDITIONS_FA),  # Same structure, English values added below
    ]:
        full = root / locale_file
        if not full.exists():
            print(f"  [SKIP]  {locale_file} not found")
            continue

        data = json.loads(full.read_text(encoding="utf-8"))
        added = 0
        for key, value in additions.items():
            if key not in data:
                data[key] = value
                added += len(_count_keys(value))
            elif isinstance(data[key], dict) and isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in data[key]:
                        data[key][sub_key] = sub_value
                        added += 1
                    elif isinstance(data[key][sub_key], dict) and isinstance(sub_value, dict):
                        for k2, v2 in sub_value.items():
                            if k2 not in data[key][sub_key]:
                                data[key][sub_key][k2] = v2
                                added += 1

        full.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  [updated]  {locale_file}  (+{added} keys)")

    print()
    print("=" * 72)
    print(" DONE")
    print("=" * 72)
    print(f"  Files written: {written}")
    print()
    print("  Next step:")
    print("    pnpm run build")
    print("=" * 72)
    return 0


def _count_keys(obj):
    """Count leaf keys in a nested dict."""
    if not isinstance(obj, dict):
        return [1]
    result = []
    for v in obj.values():
        if isinstance(v, dict):
            result.extend(_count_keys(v))
        else:
            result.append(1)
    return result


if __name__ == "__main__":
    sys.exit(main())
