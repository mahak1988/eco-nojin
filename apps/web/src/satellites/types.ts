/**
 * ============================================================================
 *  Satellite Framework — Type Definitions
 * ============================================================================
 */

export type SatelliteAgency = "ESA" | "NASA" | "NASA/USGS" | "NASA/NOAA" | "NASA/JAXA" | "NASA/GFZ" | "UCSB" | "NOAA";

export type SatelliteAccess = "free" | "free-with-registration" | "tiered";

export interface SatelliteBand {
  name: string;
  wavelength: string;
  resolution: string;
  application: string;
}

export interface Satellite {
  id: string;
  name: string;
  agency: SatelliteAgency;
  launchYear: number;
  resolution: string;
  revisitDays: number;
  swath: string;
  access: SatelliteAccess;
  dataSource: string;
  descriptionKey: string;
  bands: readonly SatelliteBand[];
  applications: readonly string[];
  icon: string;
}

export interface SatelliteIndex {
  id: string;
  formula: string;
  name: string;
  application: string;
}

export type SatelliteRegistry = readonly Satellite[];
