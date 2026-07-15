/**
 * ============================================================================
 *  FloodParams — flood simulator engine
 * ============================================================================
 */

import type { SimulatorEngine, SimResult, VisualizationSpec } from "../types";

// ---------------------------------------------------------------------------
// Parameter type
// ---------------------------------------------------------------------------

export interface FloodParamsParams {
  /** Rainfall in mm/24h */
  rainfall?: number;
  /** Curve number 30-100 */
  curveNumber?: number;
  /** Area in km² */
  area?: number;
}

// ---------------------------------------------------------------------------
// Presets
// ---------------------------------------------------------------------------

const PRESETS = [
  {
    id: "default",
    nameKey: "simulators.flood.presetDefault",
    descriptionKey: "simulators.flood.presetDefaultDesc",
    params: {},
  },
] as const;

// ---------------------------------------------------------------------------
// Engine
// ---------------------------------------------------------------------------

export const FloodParams: SimulatorEngine<FloodParamsParams> = {
  id: "flood",
  nameKey: "simulators.flood.name",
  descriptionKey: "simulators.flood.description",
  icon: "🌊",
  audience: ["manager", "expert"],
  parameters: [],
  presets: PRESETS,
  async run(params: FloodParamsParams): Promise<SimResult> {
    const start = Date.now();
    await new Promise((r) => setTimeout(r, 300));

    const rainfall = params.rainfall ?? 80;
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
    };

    return {
      data: result,
      summary: {
        titleKey: "simulators.flood.resultTitle",
        metrics: [
          { labelKey: "simulators.flood.metric1", value: result.value1 ?? "—" },
        ],
      },
      warnings: [],
      duration: Date.now() - start,
    };
  },
  visualize(_result: Record<string, unknown>): VisualizationSpec {
    return {
      type: "table",
      data: {
        rows: [],
      },
      titleKey: "simulators.flood.visualizationTitle",
    } as VisualizationSpec;
  },
};

// Alias for registry compatibility
export const floodSimulator = FloodParams;