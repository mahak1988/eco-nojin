/**
 * ============================================================================
 *  DroughtParams — drought simulator engine
 * ============================================================================
 */

import type { SimulatorEngine, SimResult, VisualizationSpec } from "../types";

// ---------------------------------------------------------------------------
// Parameter type
// ---------------------------------------------------------------------------

export interface DroughtParamsParams {
  /** Rainfall in mm */
  rainfall?: number;
  /** Average rainfall in mm */
  avgRainfall?: number;
  /** Standard deviation */
  stdDev?: number;
}

// ---------------------------------------------------------------------------
// Presets
// ---------------------------------------------------------------------------

const PRESETS = [
  {
    id: "default",
    nameKey: "simulators.drought.presetDefault",
    descriptionKey: "simulators.drought.presetDefaultDesc",
    params: {},
  },
] as const;

// ---------------------------------------------------------------------------
// Engine
// ---------------------------------------------------------------------------

export const DroughtParams: SimulatorEngine<DroughtParamsParams> = {
  id: "drought",
  nameKey: "simulators.drought.name",
  descriptionKey: "simulators.drought.description",
  icon: "🏜️",
  audience: ["expert", "manager", "farmer"],
  parameters: [],
  presets: PRESETS,
  async run(params: DroughtParamsParams): Promise<SimResult> {
    const start = Date.now();
    await new Promise((r) => setTimeout(r, 300));

    const rainfall = params.rainfall ?? 200;
    const avg = params.avgRainfall ?? 300;
    const std = params.stdDev ?? 80;
    const spi = (rainfall - avg) / std;
    const result = {
      rainfall, avgRainfall: avg, stdDev: std,
      spi: Math.round(spi * 100) / 100,
      category: spi < -2 ? "extreme" : spi < -1.5 ? "severe" : spi < -1 ? "moderate" : spi < 0 ? "mild" : "normal",
      value1: `${Math.round(spi * 100) / 100}`,
    };

    return {
      data: result,
      summary: {
        titleKey: "simulators.drought.resultTitle",
        metrics: [
          { labelKey: "simulators.drought.metric1", value: result.value1 ?? "—" },
        ],
      },
      warnings: [],
      duration: Date.now() - start,
    };
  },
  visualize(_result: Record<string, unknown>): VisualizationSpec {
    return {
      type: "gauge",
      data: {
        value: 0,
        min: -3,
        max: 3,
      },
      titleKey: "simulators.drought.visualizationTitle",
    } as VisualizationSpec;
  },
};

// Alias for registry compatibility
export const droughtSimulator = DroughtParams;