/**
 * ============================================================================
 *  SoilErosionParams — soilErosion simulator engine
 * ============================================================================
 */

import type { SimulatorEngine, SimResult, VisualizationSpec } from "../types";

// ---------------------------------------------------------------------------
// Parameter type
// ---------------------------------------------------------------------------

export interface SoilErosionParamsParams {
  /** R factor - rainfall erosivity */
  rFactor?: number;
  /** K factor - soil erodibility */
  kFactor?: number;
  /** LS factor - slope length-gradient */
  lsFactor?: number;
  /** C factor - cover management */
  cFactor?: number;
  /** P factor - support practice */
  pFactor?: number;
}

// ---------------------------------------------------------------------------
// Presets
// ---------------------------------------------------------------------------

const PRESETS = [
  {
    id: "default",
    nameKey: "simulators.soilErosion.presetDefault",
    descriptionKey: "simulators.soilErosion.presetDefaultDesc",
    params: {},
  },
] as const;

// ---------------------------------------------------------------------------
// Engine
// ---------------------------------------------------------------------------

export const SoilErosionParams: SimulatorEngine<SoilErosionParamsParams> = {
  id: "soilErosion",
  nameKey: "simulators.soilErosion.name",
  descriptionKey: "simulators.soilErosion.description",
  icon: "🏔️",
  audience: ["farmer", "expert"],
  parameters: [],
  presets: PRESETS,
  async run(params: SoilErosionParamsParams): Promise<SimResult> {
    const start = Date.now();
    await new Promise((r) => setTimeout(r, 300));

    const R = params.rFactor ?? 100;
    const K = params.kFactor ?? 0.3;
    const LS = params.lsFactor ?? 2;
    const C = params.cFactor ?? 0.5;
    const P = params.pFactor ?? 1;
    const erosion = R * K * LS * C * P;
    const result = {
      erosion: Math.round(erosion * 10) / 10,
      severity: erosion > 20 ? "high" : erosion > 10 ? "medium" : "low",
      value1: `${Math.round(erosion * 10) / 10} ton/ha/year`,
    };

    return {
      data: result,
      summary: {
        titleKey: "simulators.soilErosion.resultTitle",
        metrics: [
          { labelKey: "simulators.soilErosion.metric1", value: result.value1 ?? "—" },
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
        min: 0,
        max: 50,
      },
      titleKey: "simulators.soilErosion.visualizationTitle",
    } as VisualizationSpec;
  },
};

// Alias for registry compatibility
export const soilErosionSimulator = SoilErosionParams;