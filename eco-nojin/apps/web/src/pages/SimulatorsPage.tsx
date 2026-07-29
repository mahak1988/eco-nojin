// apps/web/src/pages/SimulatorsPage.tsx
// API-driven: loads the simulator list + parameter schemas from the backend.
// Falls back to the 4 built-in simulators if the backend is unreachable
// (Vite lesson: never a white screen). Central tick loop drives local animations.
import { useEffect, useMemo, useState } from "react";
import { FlaskConical, Search, Download, Check, Loader2, Globe, Cpu } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { SimulatorStats } from "../components/simulators/SimulatorStats";
import { SimulatorCard } from "../components/simulators/SimulatorCard";
import { SIM_STR, simText, statusText, filterText, localeOf, type SimLang } from "../components/simulators/simulatorsI18n";
import {
  SIM_CONFIGS, PARAM_DEFS, defaultParams, downloadCSV,
  type SimState, type SimType, type FilterStatus, type SimConfig, type ParamDef,
} from "../components/simulators/simulatorsData";
import { fetchSimulators, fetchParameters, type ApiParam } from "../lib/simulationApi";

const FILTERS: FilterStatus[] = ["all", "idle", "running", "done"];

// deterministic seed from a string
const hashSeed = (s: string): number => {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h) % 100000;
};

// Convert an API parameter schema to the UI ParamDef shape.
function apiParamToDef(p: ApiParam): ParamDef {
  const min = p.min_value ?? 0;
  const max = p.max_value ?? (p.type === "int" ? 100 : 100);
  const span = max - min || 1;
  return {
    key: p.name,
    labelKey: p.label || p.name,   // direct label (simText falls back to the key)
    min,
    max,
    step: p.type === "int" ? 1 : +(span / 100).toPrecision(2) || 1,
    default: typeof p.default === "number" ? p.default : 0,
    unitKey: p.unit || undefined,
    options: p.type === "select" && Array.isArray(p.options) ? p.options : undefined,
  };
}

export default function SimulatorsPage() {
  const { lang } = useLang();
  const s = SIM_STR[lang as SimLang];
  const locale = localeOf(lang as SimLang);

  const [configs, setConfigs] = useState<SimConfig[]>(SIM_CONFIGS);
  const [paramDefs, setParamDefs] = useState<Record<string, ParamDef[]>>(PARAM_DEFS);
  const [states, setStates] = useState<Record<string, SimState>>(() =>
    Object.fromEntries(SIM_CONFIGS.map((c) => [c.id, { params: defaultParams(c.id), progress: 0, status: "idle" as const, runs: 0 }])));
  const [backend, setBackend] = useState<"loading" | "online" | "offline">("loading");
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<FilterStatus>("all");
  const [exported, setExported] = useState(false);

  // ── Load simulators + parameter schemas from the backend ──
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const sims = await fetchSimulators();
      if (cancelled) return;
      if (!sims || sims.length === 0) {
        setBackend("offline");   // keep the 4 built-in simulators
        return;
      }
      const paramResults = await Promise.all(sims.map((sim) => fetchParameters(sim.id)));
      if (cancelled) return;

      const newConfigs: SimConfig[] = sims.map((sim) => ({
        id: sim.id,
        nameKey: sim.name,            // direct name (simText falls back to the key)
        descKey: sim.description,
        seed: hashSeed(sim.id),
      }));
      const newDefs: Record<string, ParamDef[]> = {};
      const newStates: Record<string, SimState> = {};
      sims.forEach((sim, i) => {
        const defs = (paramResults[i] ?? []).map(apiParamToDef);
        newDefs[sim.id] = defs;
        newStates[sim.id] = {
          params: Object.fromEntries(defs.map((d) => [d.key, d.default])),
          progress: 0,
          status: "idle",
          runs: 0,
        };
      });
      setConfigs(newConfigs);
      setParamDefs(newDefs);
      setStates(newStates);
      setBackend("online");
    })();
    return () => { cancelled = true; };
  }, []);

  // ── Central tick loop (drives local animations) ──
  useEffect(() => {
    const id = setInterval(() => {
      setStates((prev) => {
        let changed = false;
        const next: Record<string, SimState> = { ...prev };
        for (const k in next) {
          if (next[k].status === "running") {
            const np = Math.min(100, next[k].progress + 4);
            if (np !== next[k].progress) {
              changed = true;
              const done = np >= 100;
              next[k] = { ...next[k], progress: np, status: done ? "done" : "running", runs: done ? next[k].runs + 1 : next[k].runs };
            }
          }
        }
        return changed ? next : prev;
      });
    }, 110);
    return () => clearInterval(id);
  }, []);

  const setParam = (id: string, key: string, value: number) =>
    setStates((p) => ({ ...p, [id]: { ...p[id], params: { ...p[id].params, [key]: value }, progress: 0, status: "idle" } }));
  const run = (id: string) =>
    setStates((p) => ({ ...p, [id]: { ...p[id], status: "running", progress: p[id].status === "done" ? 0 : p[id].progress } }));
  const stop = (id: string) =>
    setStates((p) => ({ ...p, [id]: { ...p[id], status: "idle" } }));
  const reset = (id: string) =>
    setStates((p) => ({ ...p, [id]: { params: Object.fromEntries((paramDefs[id] ?? []).map((d) => [d.key, d.default])), progress: 0, status: "idle", runs: p[id].runs } }));

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return configs.filter((c) =>
      (filter === "all" || states[c.id]?.status === filter) &&
      (q === "" || simText(s, c.nameKey).toLowerCase().includes(q))
    );
  }, [search, filter, states, configs, lang]); // eslint-disable-line react-hooks/exhaustive-deps

  const exportAll = () => {
    const header = s.csvHeaders.split(",");
    const rows = configs.map((c) => {
      const st = states[c.id];
      const params = (paramDefs[c.id] ?? []).map((d) => `${d.key}=${st.params[d.key]}`).join(" ");
      return [simText(s, c.nameKey), statusText(s, st.status), String(st.runs), String(Math.round(st.progress)), params]
        .map((x) => `"${x.replace(/"/g, '""')}"`).join(",");
    });
    downloadCSV("simulators.csv", [header.join(","), ...rows].join("\n"));
    setExported(true); setTimeout(() => setExported(false), 1800);
  };

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15"><FlaskConical className="h-5 w-5 text-green-700" /></div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* backend status badge */}
            <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-bold ring-1 ${
              backend === "online" ? "bg-blue-50 text-blue-700 ring-blue-600/15"
              : backend === "offline" ? "bg-stone-100 text-stone-600 ring-stone-600/15"
              : "bg-amber-50 text-amber-700 ring-amber-600/15"}`}>
              {backend === "loading" ? <Loader2 className="h-3.5 w-3.5 animate-spin" />
                : backend === "online" ? <Globe className="h-3.5 w-3.5" />
                : <Cpu className="h-3.5 w-3.5" />}
              {backend === "online" ? `${configs.length} شبیه‌ساز (سرور)` : backend === "offline" ? "حالت محلی" : "در حال اتصال…"}
            </span>
            <button onClick={exportAll}
              className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold shadow-sm transition-all hover:-translate-y-0.5 ${exported ? "bg-green-50 text-green-700" : "bg-green-600 text-white hover:bg-green-700"}`}>
              {exported ? <Check className="h-4 w-4" /> : <Download className="h-4 w-4" />}{s.exportAll}
            </button>
          </div>
        </div>
      </SectionReveal>

      <SimulatorStats states={states} strings={s} />

      <SectionReveal delay={90}>
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[200px] flex-1">
            <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
              className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
          </div>
          <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
            {FILTERS.map((f) => (
              <button key={f} onClick={() => setFilter(f)}
                className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${filter === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"}`}>
                {filterText(s, f)}
              </button>
            ))}
          </div>
        </div>
      </SectionReveal>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
          <FlaskConical className="h-10 w-10 text-stone-300" />
          <p className="text-stone-500">{simText(s, "filterAll")}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
          {filtered.map((c, i) => (
            <SectionReveal key={c.id} delay={Math.min(i * 70, 240)}>
              <SimulatorCard
                config={c}
                state={states[c.id]}
                paramDefs={paramDefs[c.id] ?? []}
                strings={s}
                lang={lang as SimLang}
                onParam={(k, v) => setParam(c.id, k, v)}
                onRun={() => run(c.id)}
                onStop={() => stop(c.id)}
                onReset={() => reset(c.id)}
              />
            </SectionReveal>
          ))}
        </div>
      )}
    </div>
  );
}
