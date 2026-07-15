/**
 * ============================================================================
 *  BiodiversityParams — biodiversity simulator engine
 * ============================================================================
 */

import type { SimulatorEngine, SimResult, VisualizationSpec } from "../types";

// ---------------------------------------------------------------------------
// Parameter type
// ---------------------------------------------------------------------------

export interface BiodiversityParamsParams {
  /** Habitat area in km² */
  habitatArea?: number;
  /** Degradation 0-1 */
  degradation?: number;
  /** Threat level 0-1 */
  threat?: number;
}

// ---------------------------------------------------------------------------
// Presets
// ---------------------------------------------------------------------------

const PRESETS = [
  {
    id: "default",
    nameKey: "simulators.biodiversity.presetDefault",
    descriptionKey: "simulators.biodiversity.presetDefaultDesc",
    params: {},
  },
] as const;

// ---------------------------------------------------------------------------
// Engine
// ---------------------------------------------------------------------------

export const BiodiversityParams: SimulatorEngine<BiodiversityParamsParams> = {
  id: "biodiversity",
  nameKey: "simulators.biodiversity.name",
  descriptionKey: "simulators.biodiversity.description",
  icon: "🦋",
  audience: ["researcher", "expert"],
  parameters: [],
  presets: PRESETS,
  async run(params: BiodiversityParamsParams): Promise<SimResult> {
    const start = Date.now();
    await new Promise((r) => setTimeout(r, 300));

    const habitat = params.habitatArea ?? 500;
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
    };

    return {
      data: result,
      summary: {
        titleKey: "simulators.biodiversity.resultTitle",
        metrics: [
          { labelKey: "simulators.biodiversity.metric1", value: result.value1 ?? "—" },
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
        labels: ["Habitat Quality", "Species Richness"],
        values: [0, 0],
      },
      titleKey: "simulators.biodiversity.visualizationTitle",
    } as VisualizationSpec;
  },
};

// Alias for registry compatibility
export const biodiversitySimulator = BiodiversityParams;