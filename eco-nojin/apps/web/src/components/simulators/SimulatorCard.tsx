// apps/web/src/components/simulators/SimulatorCard.tsx
// Dynamic, server-aware card. If a local model exists (COMPUTE[id]) it runs the
// animation AND asks the backend in parallel. If no local model exists (pure API
// simulator), it asks the backend directly. If the backend is unreachable and
// there is no local model, it shows a clear message (never a white screen).
import { useState } from "react";
import { Link } from "react-router-dom";
import { FlaskConical, Play, Pause, RotateCcw, Globe, Cpu, Loader2, CloudOff } from "lucide-react";
import type { SimConfig, SimState, SimType, Series, ParamDef } from "./simulatorsData";
import { COMPUTE } from "./simulatorsData";
import { SimulatorChart } from "./SimulatorChart";
import { runOnServer } from "../../lib/simulationApi";
import { simText, statusText, localeOf, type SimStrings, type SimLang } from "./simulatorsI18n";
import { simName, simDesc } from "./simulatorsI18nExt";

const STATUS_STYLE: Record<string, string> = {
  idle: "bg-stone-100 text-stone-600 ring-stone-600/15",
  running: "bg-amber-50 text-amber-700 ring-amber-600/15",
  done: "bg-green-50 text-green-700 ring-green-600/15",
};

type Source = "idle" | "pending" | "local" | "server" | "offline";

interface Props {
  config: SimConfig;
  state: SimState;
  paramDefs: ParamDef[];      // from API or PARAM_DEFS fallback
  strings: SimStrings;
  lang: SimLang;
  onParam: (key: string, value: number) => void;
  onRun: () => void;
  onStop: () => void;
  onReset: () => void;
  onServerResult?: (series: Series[]) => void;
}

export function SimulatorCard({ config, state, paramDefs, strings: s, lang, onParam, onRun, onStop, onReset, onServerResult }: Props) {
  const locale = localeOf(lang);
  const computeFn = COMPUTE[config.id];
  const hasLocal = !!computeFn;
  const localSeries: Series[] = hasLocal ? computeFn(state.params, config.seed) : [];
  const running = state.status === "running";

  const [source, setSource] = useState<Source>("idle");
  const [serverSeries, setServerSeries] = useState<Series[] | null>(null);

  const handleRun = () => {
    onRun();
    setSource("pending");
    setServerSeries(null);
    runOnServer(config.id, state.params).then((res) => {
      if (res) {
        setServerSeries(res.series);
        setSource("server");
        onServerResult?.(res.series);
      } else {
        setSource(hasLocal ? "local" : "offline");
      }
    });
  };

  const handleReset = () => { onReset(); setSource("idle"); setServerSeries(null); };

  // For local models: show server series once the animation completes.
  // For API-only simulators: show server series immediately when available.
  const showServer =
    source === "server" && !!serverSeries && (!hasLocal || state.progress >= 100);
  const displaySeries: Series[] = showServer ? (serverSeries as Series[]) : localSeries;

  const sourceBadge =
    source === "pending" ? { icon: Loader2, cls: "bg-stone-100 text-stone-600", spin: true, txt: "…" }
    : source === "offline" ? { icon: CloudOff, cls: "bg-red-50 text-red-600", spin: false, txt: "" }
    : showServer ? { icon: Globe, cls: "bg-blue-50 text-blue-700", spin: false, txt: "" }
    : source === "local" ? { icon: Cpu, cls: "bg-stone-100 text-stone-600", spin: false, txt: "" }
    : null;

  return (
    <article className="flex flex-col rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm transition-all hover:shadow-md sm:p-6">
      <div className="mb-3 flex items-start justify-between gap-3">
        <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-green-50 text-green-700 ring-1 ring-green-600/15">
          <FlaskConical className="h-5 w-5" />
        </span>
        <div className="flex items-center gap-1.5">
          {sourceBadge && (
            <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold ring-1 ${sourceBadge.cls}`} title="data source">
              <sourceBadge.icon className={`h-3 w-3 ${sourceBadge.spin ? "animate-spin" : ""}`} />{sourceBadge.txt}
            </span>
          )}
          <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-bold ring-1 ${STATUS_STYLE[state.status]}`}>
            {running && <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse" />}
            {statusText(s, state.status)}
          </span>
        </div>
      </div>

      <h3 className="font-display text-lg text-stone-800">{simName(config.id, lang, simText(s, config.nameKey))}</h3>
      <p className="mt-1 text-sm leading-relaxed text-stone-600">{simDesc(config.id, lang, simText(s, config.descKey))}</p>

      {/* dynamic parameter form (slider for numbers, select for options) */}
      <div className="mt-4 space-y-3 rounded-xl border border-stone-200 bg-stone-50/70 p-3">
        <p className="text-[11px] font-bold uppercase tracking-wide text-stone-400">{s.params}</p>
        {paramDefs.map((dd) => {
          const v = state.params[dd.key] ?? dd.default;
          if (dd.options && dd.options.length > 0) {
            return (
              <div key={dd.key}>
                <div className="mb-1 flex items-center justify-between text-xs font-bold">
                  <span className="text-stone-700">{simText(s, dd.labelKey)}</span>
                </div>
                <select value={String(v)} disabled={running}
                  onChange={(e) => onParam(dd.key, Number(e.target.value) || 0)}
                  className="w-full rounded-lg border border-stone-200 bg-white px-2 py-1.5 text-sm text-stone-800 outline-none focus:border-green-500 disabled:opacity-50">
                  {dd.options.map((opt) => <option key={opt} value={opt}>{opt}</option>)}
                </select>
              </div>
            );
          }
          return (
            <div key={dd.key}>
              <div className="mb-1 flex items-center justify-between text-xs font-bold">
                <span className="text-stone-700">{simText(s, dd.labelKey)}</span>
                <span className="tabular-nums text-green-700">
                  {v.toLocaleString(locale, { maximumFractionDigits: 1 })}{dd.unitKey ? ` ${simText(s, dd.unitKey)}` : ""}
                </span>
              </div>
              <input type="range" min={dd.min} max={dd.max} step={dd.step} value={v} disabled={running}
                onChange={(e) => onParam(dd.key, Number(e.target.value))} aria-label={simText(s, dd.labelKey)}
                className="h-2 w-full cursor-pointer appearance-none rounded-full bg-stone-200 accent-green-600 disabled:cursor-not-allowed disabled:opacity-50" />
            </div>
          );
        })}
      </div>

      <div className="mt-4">
        <div className="mb-1.5 flex items-center justify-between text-[11px] font-bold text-stone-500">
          <span>{s.output}</span>
          <span className="tabular-nums text-green-700">{Math.round(state.progress)}٪</span>
        </div>
        <div className="rounded-xl border border-stone-200 bg-white p-2">
          {displaySeries.length > 0 ? (
            <SimulatorChart series={displaySeries} progress={state.progress} strings={s} />
          ) : (
            <div className="flex flex-col items-center justify-center gap-2 py-8 text-center">
              {source === "offline" ? (
                <>
                  <CloudOff className="h-8 w-8 text-stone-300" />
                  <p className="text-xs text-stone-500">backend در دسترس نیست و این شبیه‌ساز مدل محلی ندارد</p>
                </>
              ) : (
                <p className="text-xs text-stone-400">{s.run} →</p>
              )}
            </div>
          )}
        </div>
        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-stone-100">
          <div className={`h-full rounded-full transition-[width] duration-150 ease-linear ${running ? "bg-amber-500" : state.status === "done" ? "bg-green-600" : "bg-stone-300"}`}
            style={{ width: `${state.progress}%` }} />
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between gap-2">
        <Link to={`/simulators/${config.id}`} className="inline-flex items-center gap-1 rounded-xl border border-green-200 bg-green-50 px-3 py-2 text-xs font-bold text-green-700 transition-colors hover:bg-green-100">ورود به شبیه‌ساز ←</Link>
          <span className="text-xs font-bold text-stone-500">{state.runs.toLocaleString(locale)} {s.runsLabel}</span>
        <div className="flex items-center gap-2">
          <button onClick={handleReset} aria-label={s.reset}
            className="grid h-9 w-9 place-items-center rounded-xl border border-stone-200 text-stone-600 transition-colors hover:bg-stone-50">
            <RotateCcw className="h-4 w-4" />
          </button>
          {running ? (
            <button onClick={onStop}
              className="inline-flex items-center gap-1.5 rounded-xl bg-red-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-red-700">
              <Pause className="h-4 w-4" />{s.stop}
            </button>
          ) : (
            <button onClick={handleRun}
              className="inline-flex items-center gap-1.5 rounded-xl bg-green-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
              <Play className="h-4 w-4" />{s.run}
            </button>
          )}
        </div>
      </div>
    </article>
  );
}
