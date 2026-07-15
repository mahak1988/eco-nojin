/**
 * ============================================================================
 *  Simulator Framework — Type Definitions
 * ============================================================================
 */

/** Target audience for a simulator. */
export type SimulatorAudience = "farmer" | "student" | "expert" | "manager" | "researcher";

/** A single input parameter for a simulator. */
export interface SimParameterDef<T = unknown> {
  key: keyof T & string;
  labelKey: string;
  type: "number" | "select" | "slider" | "toggle" | "text";
  unit?: string;
  min?: number;
  max?: number;
  step?: number;
  defaultValue: T[keyof T];
  options?: readonly { value: string; labelKey: string }[];
  helpKey?: string;
}

/** A preset scenario for quick setup. */
export interface SimPreset<P> {
  id: string;
  nameKey: string;
  descriptionKey: string;
  params: Partial<P>;
}

/** The result of running a simulator. */
export interface SimResult<R = Record<string, unknown>> {
  data: R;
  summary: SimResultSummary;
  warnings: string[];
  duration: number; // milliseconds
}

export interface SimResultSummary {
  titleKey: string;
  metrics: { labelKey: string; value: string | number; unit?: string }[];
}

/** Visualization specification for rendering results. */
export interface VisualizationSpec {
  type: "line" | "bar" | "pie" | "heatmap" | "table" | "gauge" | "map";
  titleKey: string;
  data: unknown;
  options?: Record<string, unknown>;
}

/** The unified interface every simulator engine must implement. */
export interface SimulatorEngine<P = Record<string, unknown>, R = Record<string, unknown>> {
  id: string;
  nameKey: string;
  descriptionKey: string;
  icon: string;
  audience: readonly SimulatorAudience[];
  parameters: readonly SimParameterDef<P>[];
  presets: readonly SimPreset<P>[];
  run: (params: P) => Promise<SimResult<R>>;
  visualize: (result: R) => VisualizationSpec;
}

/** Registry of all simulators. */
export type SimulatorRegistry = readonly SimulatorEngine[];
