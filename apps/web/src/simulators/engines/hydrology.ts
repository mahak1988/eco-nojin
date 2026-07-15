/**
 * ============================================================================
 *  HydrologyParams — hydrology simulator engine
 * ============================================================================
 */

import type { SimulatorEngine, SimResult, VisualizationSpec } from "../types";

// ---------------------------------------------------------------------------
// Parameter type
// ---------------------------------------------------------------------------

export interface HydrologyParamsParams {
  /** Rainfall in mm */
  rainfall?: number;
  /** Area in km² */
  area?: number;
  /** Runoff coefficient 0-1 */
  runoffCoeff?: number;
}

// ---------------------------------------------------------------------------
// Presets
// ---------------------------------------------------------------------------

const PRESETS = [
  {
    id: "default",
    nameKey: "simulators.hydrology.presetDefault",
    descriptionKey: "simulators.hydrology.presetDefaultDesc",
    params: {},
  },
] as const;

// ---------------------------------------------------------------------------
// Engine
// ---------------------------------------------------------------------------

export const HydrologyParams: SimulatorEngine<HydrologyParamsParams> = {
  id: "hydrology",
  nameKey: "simulators.hydrology.name",
  descriptionKey: "simulators.hydrology.description",
  icon: "💧",
  audience: ["expert", "manager"],
  parameters: [],
  presets: PRESETS,
  async run(params: HydrologyParamsParams): Promise<SimResult> {
    const start = Date.now();
    await new Promise((r) => setTimeout(r, 300));

    const rainfall = params.rainfall ?? 500;
    const area = params.area ?? 100;
    const coeff = params.runoffCoeff ?? 0.3;
    const runoffVolume = rainfall * area * coeff * 1000;
    const result = {
      rainfall,
      area,
      runoffCoeff: coeff,
      runoffVolume: Math.round(runoffVolume),
      value1: `${Math.round(runoffVolume).toLocaleString()} m³`,
    };

    return {
      data: result,
      summary: {
        titleKey: "simulators.hydrology.resultTitle",
        metrics: [
          { labelKey: "simulators.hydrology.metric1", value: result.value1 ?? "—" },
        ],
      },
      warnings: [],
      duration: Date.now() - start,
    };
  },
  visualize(_result: Record<string, unknown>): VisualizationSpec {
    return {
      type: "bar",
      data: {
        labels: ["Rainfall", "Runoff", "Infiltration"],
        values: [0, 0, 0],
      },
      titleKey: "simulators.hydrology.visualizationTitle",
    } as VisualizationSpec;
  },
};

// Alias for registry compatibility
export const hydrologySimulator = HydrologyParams;