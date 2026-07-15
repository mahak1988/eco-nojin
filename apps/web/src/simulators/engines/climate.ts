/**
 * ============================================================================
 *  ClimateParams — climate simulator engine
 * ============================================================================
 */

import type { SimulatorEngine, SimResult, VisualizationSpec } from "../types";

// ---------------------------------------------------------------------------
// Parameter type
// ---------------------------------------------------------------------------

export interface ClimateParamsParams {
  /** Temperature change in °C */
  temperatureDelta?: number;
  /** CO2 concentration in ppm */
  co2ppm?: number;
  /** Year for projection */
  year?: number;
}

// ---------------------------------------------------------------------------
// Presets
// ---------------------------------------------------------------------------

const PRESETS = [
  {
    id: "default",
    nameKey: "simulators.climate.presetDefault",
    descriptionKey: "simulators.climate.presetDefaultDesc",
    params: {},
  },
] as const;

// ---------------------------------------------------------------------------
// Engine
// ---------------------------------------------------------------------------

export const ClimateParams: SimulatorEngine<ClimateParamsParams> = {
  id: "climate",
  nameKey: "simulators.climate.name",
  descriptionKey: "simulators.climate.description",
  icon: "🌡️",
  audience: ["expert", "manager", "researcher"],
  parameters: [],
  presets: PRESETS,
  async run(params: ClimateParamsParams): Promise<SimResult> {
    const start = Date.now();
    await new Promise((r) => setTimeout(r, 300));

    const tempDelta = params.temperatureDelta ?? 2.0;
    const co2 = params.co2ppm ?? 420;
    const year = params.year ?? 2050;
    const projectedTemp = 1.5 + (tempDelta * (year - 2024) / 26);
    const result = {
      year,
      temperatureRise: Math.round(projectedTemp * 10) / 10,
      co2Level: co2,
      seaLevelRise: Math.round(projectedTemp * 20),
      value1: `${Math.round(projectedTemp * 10) / 10}°C`,
    };

    return {
      data: result,
      summary: {
        titleKey: "simulators.climate.resultTitle",
        metrics: [
          { labelKey: "simulators.climate.metric1", value: result.value1 ?? "—" },
        ],
      },
      warnings: [],
      duration: Date.now() - start,
    };
  },
  visualize(_result: Record<string, unknown>): VisualizationSpec {
    return {
      type: "line",
      data: {
        labels: ["2024", "2030", "2040", "2050"],
        values: [0, 0, 0, 0],
      },
      titleKey: "simulators.climate.visualizationTitle",
    } as VisualizationSpec;
  },
};

// Alias for registry compatibility
export const climateSimulator = ClimateParams;