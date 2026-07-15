/**
 * ============================================================================
 *  CarbonParams — carbon simulator engine
 * ============================================================================
 */

import type { SimulatorEngine, SimResult, VisualizationSpec } from "../types";

// ---------------------------------------------------------------------------
// Parameter type
// ---------------------------------------------------------------------------

export interface CarbonParamsParams {
  /** Energy consumption in MWh/year */
  energy?: number;
  /** Transport in km/year */
  transport?: number;
  /** Waste in tons/year */
  waste?: number;
}

// ---------------------------------------------------------------------------
// Presets
// ---------------------------------------------------------------------------

const PRESETS = [
  {
    id: "default",
    nameKey: "simulators.carbon.presetDefault",
    descriptionKey: "simulators.carbon.presetDefaultDesc",
    params: {},
  },
] as const;

// ---------------------------------------------------------------------------
// Engine
// ---------------------------------------------------------------------------

export const CarbonParams: SimulatorEngine<CarbonParamsParams> = {
  id: "carbon",
  nameKey: "simulators.carbon.name",
  descriptionKey: "simulators.carbon.description",
  icon: "🏭",
  audience: ["expert", "manager", "researcher"],
  parameters: [],
  presets: PRESETS,
  async run(params: CarbonParamsParams): Promise<SimResult> {
    const start = Date.now();
    await new Promise((r) => setTimeout(r, 300));

    const energy = params.energy ?? 1000;
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
    };

    return {
      data: result,
      summary: {
        titleKey: "simulators.carbon.resultTitle",
        metrics: [
          { labelKey: "simulators.carbon.metric1", value: result.value1 ?? "—" },
        ],
      },
      warnings: [],
      duration: Date.now() - start,
    };
  },
  visualize(_result: Record<string, unknown>): VisualizationSpec {
    return {
      type: "pie",
      data: {
        labels: ["Energy", "Transport", "Waste"],
        values: [0, 0, 0],
      },
      titleKey: "simulators.carbon.visualizationTitle",
    } as VisualizationSpec;
  },
};

// Alias for registry compatibility
export const carbonSimulator = CarbonParams;