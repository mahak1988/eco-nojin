/**
 * ============================================================================
 *  Simulator Registry — all 8 simulator engines
 * ============================================================================
 */

import type { SimulatorEngine } from "./types";
import { climateSimulator } from "./engines/climate";
import { hydrologySimulator } from "./engines/hydrology";
import { cropSimulator } from "./engines/crop";
import { carbonSimulator } from "./engines/carbon";
import { soilErosionSimulator } from "./engines/soilErosion";
import { floodSimulator } from "./engines/flood";
import { droughtSimulator } from "./engines/drought";
import { biodiversitySimulator } from "./engines/biodiversity";

// ---------------------------------------------------------------------------
// Type definitions
// ---------------------------------------------------------------------------

export type SimulatorAudience = "farmer" | "researcher" | "student" | "manager" | "expert";

// ---------------------------------------------------------------------------
// Registry
// ---------------------------------------------------------------------------

// Use `any` type parameters to avoid variance issues with specific param types
export const SIMULATORS: SimulatorEngine<any, any>[] = [
  climateSimulator,
  hydrologySimulator,
  cropSimulator,
  carbonSimulator,
  soilErosionSimulator,
  floodSimulator,
  droughtSimulator,
  biodiversitySimulator,
];

export function getSimulatorById(id: string): SimulatorEngine<any, any> | undefined {
  return SIMULATORS.find((s) => s.id === id);
}

export function getSimulatorsByAudience(audience: SimulatorAudience): SimulatorEngine<any, any>[] {
  return SIMULATORS.filter((s) => s.audience.includes(audience));
}

export type { SimulatorEngine } from "./types";