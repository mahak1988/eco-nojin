/**
 * ============================================================================
 *  CropParams — crop simulator engine
 * ============================================================================
 */

import type { SimulatorEngine, SimResult, VisualizationSpec } from "../types";

// ---------------------------------------------------------------------------
// Parameter type
// ---------------------------------------------------------------------------

export interface CropParamsParams {
  /** Crop type */
  cropType?: "wheat" | "rice" | "corn" | "cotton";
  /** Irrigation in mm */
  irrigation?: number;
  /** Fertilizer in kg/ha */
  fertilizer?: number;
}

// ---------------------------------------------------------------------------
// Presets
// ---------------------------------------------------------------------------

const PRESETS = [
  {
    id: "default",
    nameKey: "simulators.crop.presetDefault",
    descriptionKey: "simulators.crop.presetDefaultDesc",
    params: {},
  },
] as const;

// ---------------------------------------------------------------------------
// Engine
// ---------------------------------------------------------------------------

export const CropParams: SimulatorEngine<CropParamsParams> = {
  id: "crop",
  nameKey: "simulators.crop.name",
  descriptionKey: "simulators.crop.description",
  icon: "🌾",
  audience: ["farmer", "student", "expert"],
  parameters: [],
  presets: PRESETS,
  async run(params: CropParamsParams): Promise<SimResult> {
    const start = Date.now();
    await new Promise((r) => setTimeout(r, 300));

    const cropType = params.cropType ?? "wheat";
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
    };

    return {
      data: result,
      summary: {
        titleKey: "simulators.crop.resultTitle",
        metrics: [
          { labelKey: "simulators.crop.metric1", value: result.value1 ?? "—" },
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
        labels: ["Base Yield", "Optimized Yield"],
        values: [0, 0],
      },
      titleKey: "simulators.crop.visualizationTitle",
    } as VisualizationSpec;
  },
};

// Alias for registry compatibility
export const cropSimulator = CropParams;