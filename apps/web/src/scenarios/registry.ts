/**
 * ============================================================================
 *  Scenario Registry — 10 preset environmental scenarios
 * ============================================================================
 */


import type { Scenario } from "./types";
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
