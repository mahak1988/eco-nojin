// apps/web/src/components/simulators/simulatorsData.ts
// Deterministic client-side models (no Math.random) + params + helpers.
// Now API-driven: SimType is a free string; PARAM_DEFS/COMPUTE are keyed by id
// and only the 4 built-in simulators have local models (fallback when offline).
export type SimType = string;
export type SimStatus = "idle" | "running" | "done";
export type FilterStatus = "all" | SimStatus;

export interface ParamDef {
  key: string;
  labelKey: string;          // may be a direct label (simText falls back to the key itself)
  min: number; max: number; step: number; default: number;
  unitKey?: string;
  options?: string[];        // for select-type params (from API)
}
export interface Series {
  labelKey: string;
  label?: string;            // direct label from backend (preferred over labelKey)
  color: string;
  values: number[];
  kind?: "line" | "bars";
  fill?: boolean;
}
export interface SimConfig {
  id: SimType;
  nameKey: string;           // may be a direct name (simText falls back to the key itself)
  descKey: string;
  seed: number;
}
export interface SimState {
  params: Record<string, number>;
  progress: number;          // 0..100
  status: SimStatus;
  runs: number;
}

// Built-in (offline fallback) simulators
export const SIM_CONFIGS: SimConfig[] = [
  { id: "climate",     nameKey: "n_climate",     descKey: "d_climate",     seed: 1 },
  { id: "water",       nameKey: "n_water",       descKey: "d_water",       seed: 2 },
  { id: "agriculture", nameKey: "n_agriculture", descKey: "d_agriculture", seed: 3 },
  { id: "energy",      nameKey: "n_energy",      descKey: "d_energy",      seed: 4 },
];

export const PARAM_DEFS: Record<string, ParamDef[]> = {
  climate: [
    { key: "co2", labelKey: "p_co2", min: 380, max: 520, step: 5, default: 420, unitKey: "u_ppm" },
    { key: "sensitivity", labelKey: "p_sens", min: 1.5, max: 4.5, step: 0.1, default: 3, unitKey: "u_c" },
  ],
  water: [
    { key: "rainfall", labelKey: "p_rain", min: 0, max: 100, step: 1, default: 55, unitKey: "u_mm" },
    { key: "wdemand", labelKey: "p_wdemand", min: 0, max: 100, step: 1, default: 45, unitKey: "u_pct" },
  ],
  agriculture: [
    { key: "water", labelKey: "p_awater", min: 0, max: 100, step: 1, default: 70, unitKey: "u_pct" },
    { key: "temp", labelKey: "p_atemp", min: 10, max: 38, step: 1, default: 24, unitKey: "u_c" },
    { key: "soil", labelKey: "p_soil", min: 20, max: 100, step: 1, default: 75, unitKey: "u_pct" },
  ],
  energy: [
    { key: "solar", labelKey: "p_solar", min: 0, max: 200, step: 5, default: 120, unitKey: "u_mw" },
    { key: "wind", labelKey: "p_wind", min: 0, max: 200, step: 5, default: 90, unitKey: "u_mw" },
    { key: "edemand", labelKey: "p_edemand", min: 20, max: 200, step: 5, default: 110, unitKey: "u_mw" },
  ],
};

export const defaultParams = (id: SimType): Record<string, number> =>
  Object.fromEntries((PARAM_DEFS[id] ?? []).map((p) => [p.key, p.default]));

// deterministic pseudo-random (seed+index) → chart doesn't jump on re-render
const rand = (n: number, seed: number): number => {
  const x = Math.sin(n * 12.9898 + seed * 78.233) * 43758.5453;
  return x - Math.floor(x);
};
const clamp = (v: number, lo: number, hi: number): number => Math.max(lo, Math.min(hi, v));

// Local models — only the 4 built-in simulators. API simulators have no local
// model and rely entirely on the backend (server series).
export const COMPUTE: Record<string, (p: Record<string, number>, seed: number) => Series[]> = {
  // ── built-in (offline) simulators ──
  climate: (p, seed) => {
    const N = 32, base = 14;
    const values = Array.from({ length: N }, (_, t) => {
      const trend = (p.sensitivity ?? 3) * (((p.co2 ?? 420) - 380) / 140) * (t / (N - 1));
      const seasonal = 2.2 * Math.sin((t / N) * Math.PI * 4);
      const noise = (rand(t, seed) - 0.5) * 0.8;
      return +(base + trend + seasonal + noise).toFixed(2);
    });
    return [{ labelKey: "l_temp", color: "#dc2626", values, kind: "line", fill: true }];
  },
  water: (p, seed) => {
    const N = 32; let r = 60;
    const values = Array.from({ length: N }, (_, t) => {
      const inflow = (p.rainfall ?? 55) * 0.6 + (rand(t, seed) - 0.3) * 8;
      const outflow = (p.wdemand ?? 45) * 0.5 + 4;
      r = clamp(r + inflow - outflow, 0, 100);
      return +r.toFixed(1);
    });
    return [{ labelKey: "l_reservoir", color: "#0284c7", values, kind: "line", fill: true }];
  },
  agriculture: (p, seed) => {
    const N = 8;
    const values = Array.from({ length: N }, (_, t) => {
      const wf = 1 - Math.abs((p.water ?? 70) - 70) / 100;
      const tf = 1 - Math.abs((p.temp ?? 24) - 24) / 20;
      const season = 0.7 + 0.3 * Math.sin((t / N) * Math.PI * 2);
      const noise = 0.9 + (rand(t, seed) - 0.5) * 0.15;
      return +Math.max(0, ((p.soil ?? 75) / 100) * wf * tf * season * noise * 100).toFixed(0);
    });
    return [{ labelKey: "l_yield", color: "#16a34a", values, kind: "bars" }];
  },
  energy: (p, seed) => {
    const N = 32;
    const gen = Array.from({ length: N }, (_, t) => {
      const day = Math.max(0, Math.sin((t / N) * Math.PI * 2 - Math.PI / 2));
      const s = (p.solar ?? 120) * day * 0.9;
      const w = (p.wind ?? 90) * (0.4 + 0.6 * rand(t, seed));
      return +(s + w).toFixed(0);
    });
    const demand = Array.from({ length: N }, (_, t) =>
      +((p.edemand ?? 110) * (0.6 + 0.4 * Math.sin((t / N) * Math.PI * 2 + 1))).toFixed(0));
    return [
      { labelKey: "l_generation", color: "#16a34a", values: gen, kind: "line", fill: true },
      { labelKey: "l_demand", color: "#78716c", values: demand, kind: "line" },
    ];
  },

  // ── API simulators: local fallback models (deterministic) ──
  urban: (p, seed) => {
    const N = 30; let pop = p.initial_population ?? 100000; let area = p.urban_area_km2 ?? 50;
    const gr = (p.growth_rate ?? 2) / 100;
    const popS: number[] = [Math.round(pop)], areaS: number[] = [+area.toFixed(2)];
    for (let t = 0; t < N; t++) {
      pop *= 1 + gr * (1 + 0.1 * (rand(t, seed) - 0.5));
      area *= 1 + gr * 0.7 * (1 + 0.1 * (rand(t + 50, seed) - 0.5));
      popS.push(Math.round(pop)); areaS.push(+area.toFixed(2));
    }
    return [
      { labelKey: "population", label: "Population", color: "#7c3aed", values: popS, kind: "line", fill: true },
      { labelKey: "urban_area", label: "Urban Area (km2)", color: "#dc2626", values: areaS, kind: "line" },
    ];
  },
  dssat: (p, seed) => {
    const N = 88; const pot = p.potential_yield ?? 10; const stress = Math.min(p.water_factor ?? 0.9, p.nitrogen_factor ?? 0.9);
    const bm: number[] = [];
    for (let t = 0; t < N; t++) {
      const prog = t / N;
      bm.push(+(pot * stress * 8 * (1 / (1 + Math.exp(-8 * (prog - 0.5))))).toFixed(2));
    }
    return [{ labelKey: "biomass", label: "Biomass (t/ha)", color: "#16a34a", values: bm, kind: "line", fill: true }];
  },
  aquacrop: (p, seed) => {
    const N = 150; const fc = (p.field_capacity ?? 30) / 100; const wp = (p.wilting_point ?? 14) / 100;
    let sw = fc * 0.3 * 1000; const swS: number[] = []; const bmS: number[] = []; let bm = 0;
    for (let t = 0; t < N; t++) {
      const season = Math.sin(Math.PI * t / N);
      const rain = (p.fallback_precip ?? 250) / N * (1 + 0.5 * season);
      const et0 = (p.fallback_et0 ?? 5) * (0.6 + 0.6 * season);
      sw = clamp(sw + rain + (p.total_irrigation ?? 250) / N - et0 * 1.1, 0, fc * 1.3 * 1000);
      bm += 33.7 * Math.max(0, et0 * 0.8) * 0.1;
      swS.push(+sw.toFixed(1)); bmS.push(+(bm / 100).toFixed(2));
    }
    return [
      { labelKey: "soil_water", label: "Soil Water (mm)", color: "#0284c7", values: swS, kind: "line", fill: true },
      { labelKey: "biomass", label: "Biomass (t/ha)", color: "#16a34a", values: bmS, kind: "line" },
    ];
  },
  wofost: (p, seed) => {
    const N = 140; const water = p.water_availability ?? 0.8; const bm: number[] = []; const lai: number[] = []; let cum = 0;
    for (let t = 0; t < N; t++) {
      const prog = t / N;
      const laiT = 6 * water * (1 / (1 + Math.exp(-10 * (prog - 0.35))));
      cum += 2.2 * 7.5 * (1 - Math.exp(-0.6 * laiT)) * water;
      bm.push(+(cum / 100).toFixed(2)); lai.push(+laiT.toFixed(2));
    }
    return [
      { labelKey: "biomass", label: "Biomass (t/ha)", color: "#16a34a", values: bm, kind: "line", fill: true },
      { labelKey: "lai", label: "Leaf Area Index", color: "#0284c7", values: lai, kind: "line" },
    ];
  },
  "crop-model": (p, seed) => {
    const N = 120; const pot = p.potential_yield ?? 10; const stress = Math.min(p.water_factor ?? 0.85, p.nutrient_factor ?? 0.9);
    const bm: number[] = [];
    for (let t = 0; t < N; t++) {
      const prog = t / N;
      bm.push(+(pot * stress * 8 * (1 / (1 + Math.exp(-8 * (prog - 0.5))))).toFixed(2));
    }
    return [{ labelKey: "biomass", label: "Biomass (t/ha)", color: "#16a34a", values: bm, kind: "line", fill: true }];
  },
  swat: (p, seed) => {
    const N = 24; const precip = p.precipitation ?? 800; const rc = p.runoff_coef ?? 0.35; const bf = p.baseflow ?? 120;
    const flow: number[] = []; const runoff: number[] = [];
    for (let t = 0; t < N; t++) {
      const seasonal = 1 + 0.5 * Math.sin(2 * Math.PI * t / 12 - Math.PI / 2);
      const pm = precip / 12 * seasonal + (rand(t, seed) - 0.5) * 15;
      const ro = Math.max(0, pm * rc);
      flow.push(+(ro + bf / 12).toFixed(1)); runoff.push(+ro.toFixed(1));
    }
    return [
      { labelKey: "streamflow", label: "Streamflow (mm/mo)", color: "#0284c7", values: flow, kind: "line", fill: true },
      { labelKey: "surface_runoff", label: "Surface Runoff (mm/mo)", color: "#f59e0b", values: runoff, kind: "line" },
    ];
  },
  weap: (p, seed) => {
    const N = 24; const supply = p.supply ?? 500; const dAgri = p.demand_agri ?? 300;
    const dDom = p.demand_domestic ?? 100; const dInd = p.demand_industrial ?? 80;
    const sup: number[] = []; const dem: number[] = []; const unmet: number[] = [];
    for (let t = 0; t < N; t++) {
      const seasonal = 1 + 0.4 * Math.sin(2 * Math.PI * t / 12 - Math.PI / 2);
      const inflow = supply / 12 * seasonal;
      const demand = dDom / 12 + dInd / 12 + dAgri / 12 * (2 - seasonal);
      sup.push(+inflow.toFixed(1)); dem.push(+demand.toFixed(1));
      unmet.push(+Math.max(0, demand - inflow).toFixed(2));
    }
    return [
      { labelKey: "supply", label: "Supply (MCM/mo)", color: "#0284c7", values: sup, kind: "line", fill: true },
      { labelKey: "demand", label: "Demand (MCM/mo)", color: "#dc2626", values: dem, kind: "line" },
      { labelKey: "unmet", label: "Unmet (MCM/mo)", color: "#f59e0b", values: unmet, kind: "bars" },
    ];
  },
  rothc: (p, seed) => {
    const N = 50; let soc = p.initial_soc ?? 50; const cin = p.carbon_input ?? 3;
    const k = 0.5; const socS: number[] = [+soc.toFixed(2)];
    for (let t = 0; t < N; t++) {
      soc = Math.max(1, soc + cin - k * soc + (rand(t, seed) - 0.5) * 0.1);
      socS.push(+soc.toFixed(2));
    }
    return [{ labelKey: "soc", label: "Soil Organic Carbon (t C/ha)", color: "#16a34a", values: socS, kind: "line", fill: true }];
  },
  century: (p, seed) => {
    const N = 100; let active = (p.initial_soc ?? 60) * 0.15; let passive = (p.initial_soc ?? 60) * 0.85;
    const cin = p.annual_input ?? 4; const total: number[] = [+(active + passive).toFixed(2)];
    for (let t = 0; t < N; t++) {
      active += cin - 0.1 * active + 0.01 * passive;
      passive += 0.04 * active - 0.01 * passive;
      active = Math.max(0.1, active); passive = Math.max(0.1, passive);
      total.push(+(active + passive).toFixed(2));
    }
    return [{ labelKey: "total_soc", label: "Total SOC (t C/ha)", color: "#16a34a", values: total, kind: "line", fill: true }];
  },
  cba: (p, seed) => {
    const N = 25; const inv = p.initial_investment ?? 10; const benefit = p.annual_benefit ?? 2.5; const om = p.annual_cost ?? 0.5;
    const cash: number[] = [-inv]; let cum = -inv;
    for (let t = 1; t <= N; t++) {
      cum += benefit * (1 + 0.05 * (rand(t, seed) - 0.5)) - om;
      cash.push(+cum.toFixed(2));
    }
    return [{ labelKey: "cumulative_cash", label: "Cumulative Cash Flow (M USD)", color: "#16a34a", values: cash, kind: "line", fill: true }];
  },
  invest: (p, seed) => {
    const N = 11; const forest = p.forest_area ?? 5000; const cFor = p.carbon_density_forest ?? 150;
    const carbon: number[] = []; const habitat: number[] = [];
    for (let i = 0; i < N; i++) {
      const frac = i / (N - 1);
      const fNow = forest * (1 - frac); const aNow = (p.agri_area ?? 3000) + forest * frac;
      carbon.push(+((fNow * cFor + aNow * cFor * 0.25) / 1000).toFixed(1));
      habitat.push(+((fNow * 0.9 + aNow * 0.36) / (fNow + aNow)).toFixed(3));
    }
    return [
      { labelKey: "carbon", label: "Carbon Storage (kt C)", color: "#16a34a", values: carbon, kind: "line", fill: true },
      { labelKey: "habitat", label: "Habitat Quality", color: "#f59e0b", values: habitat, kind: "line" },
    ];
  },
  homer: (p, seed) => {
    const N = 30; const solar = p.solar_kw ?? 100; const wind = p.wind_kw ?? 50; const demand = p.demand_kw ?? 80;
    const gen: number[] = []; const dem: number[] = [];
    for (let t = 0; t < N; t++) {
      const s = solar * (p.irradiance ?? 5) * 0.75 * (1 + 0.1 * (rand(t, seed) - 0.5));
      const v = Math.max(0, (p.wind_speed ?? 6) + (rand(t + 50, seed) - 0.5) * 2);
      const w = wind * 24 * 0.35 * Math.min(1, Math.pow(v / 12, 3));
      gen.push(+(s + w).toFixed(1));
      dem.push(+(demand * 24 * (0.6 + 0.2 * Math.sin(2 * Math.PI * t / 365))).toFixed(1));
    }
    return [
      { labelKey: "generation", label: "Generation (kWh/day)", color: "#16a34a", values: gen, kind: "line", fill: true },
      { labelKey: "demand", label: "Demand (kWh/day)", color: "#dc2626", values: dem, kind: "line" },
    ];
  },
  rusle2: (p, seed) => {
    const R = p.R ?? 150; const K = p.K ?? 0.32; const LS = p.LS ?? 1.5; const C = p.C ?? 0.2; const P = p.P ?? 0.8;
    const A = R * K * LS * C * P;
    const monthly: number[] = [];
    for (let t = 0; t < 12; t++) {
      const seasonal = 1 + 0.8 * Math.sin(2 * Math.PI * t / 12 - Math.PI / 3);
      monthly.push(+Math.max(0, A / 12 * seasonal).toFixed(2));
    }
    return [{ labelKey: "monthly_erosion", label: "Monthly Soil Loss (t/ha)", color: "#a16207", values: monthly, kind: "bars" }];
  },

};

// ── KPI derived ──
export const totalRuns = (st: Record<string, SimState>): number =>
  Object.values(st).reduce((s, x) => s + x.runs, 0);
export const countStatus = (st: Record<string, SimState>, s: SimStatus): number =>
  Object.values(st).filter((x) => x.status === s).length;

// ── CSV robust (no network/chunk) ──
export function downloadCSV(filename: string, csv: string): void {
  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
