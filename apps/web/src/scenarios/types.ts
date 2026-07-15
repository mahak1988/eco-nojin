/**
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
