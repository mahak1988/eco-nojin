import { useEffect, useMemo, useState, useCallback, useRef } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  ArrowLeft,
  Play,
  Pause,
  RotateCcw,
  Download,
  Loader2,
  Globe,
  Cpu,
  CloudOff,
  FlaskConical,
  Info,
  Settings2,
  LineChart as LineChartIcon,
} from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SimulatorChart } from "../components/simulators/SimulatorChart";
import {
  SIM_STR,
  simText,
  statusText,
  localeOf,
  type SimLang,
  type SimStrings,
} from "../components/simulators/simulatorsI18n";
import { simName, simDesc } from "../components/simulators/simulatorsI18nExt";
import { paramLabel, paramUnit } from "../components/simulators/paramI18n";
import {
  COMPUTE,
  defaultParams,
  SIM_CONFIGS,
  type Series,
  type ParamDef,
  type SimConfig,
  type SimType,
} from "../components/simulators/simulatorsData";
import { runOnServer, API_BASE, API_V1 } from "../lib/simulationApi";

/* ─────────────────────────────────────────────────────────────────────────────
   Types
───────────────────────────────────────────────────────────────────────────── */

interface ParamValue {
  key: string;
  value: number;
}

type RunMode = "client" | "server";
type PageStatus = "loading" | "ready" | "not_found";

/* ─────────────────────────────────────────────────────────────────────────────
   Helpers
───────────────────────────────────────────────────────────────────────────── */

function clamp(v: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, v));
}

function seriesToCSV(series: Series[], simId: string): string {
  if (!series.length) return "";
  const headers = ["step", ...series.map((s) => s.label)];
  const maxLen = Math.max(...series.map((s) => s.data.length));
  const rows: string[] = [headers.join(",")];
  for (let i = 0; i < maxLen; i++) {
    const row = [String(i)];
    for (const s of series) {
      row.push(s.data[i] !== undefined ? s.data[i].toFixed(4) : "");
    }
    rows.push(row.join(","));
  }
  return rows.join("\n");
}

function downloadCSV(csv: string, filename: string) {
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

/* ─────────────────────────────────────────────────────────────────────────────
   Sub-components
───────────────────────────────────────────────────────────────────────────── */

function ParamSlider({
  param,
  value,
  onChange,
  strings,
  lang,
}: {
  param: ParamDef;
  value: number;
  onChange: (v: number) => void;
  strings: SimStrings;
  lang: SimLang;
}) {
  const label = paramLabel(param.key, lang);
  const unit = paramUnit(param.key, lang);
  const step = param.step ?? (param.max - param.min) / 100;

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-sm">
        <label className="font-medium text-gray-700 dark:text-gray-300">
          {label}
        </label>
        <span className="tabular-nums text-gray-500 dark:text-gray-400">
          {value.toFixed(param.decimals ?? 1)}
          {unit ? ` ${unit}` : ""}
        </span>
      </div>
      <input
        type="range"
        min={param.min}
        max={param.max}
        step={step}
        value={value}
        onChange={(e) => onChange(clamp(Number(e.target.value), param.min, param.max))}
        className="w-full h-2 rounded-full appearance-none cursor-pointer
                   bg-gray-200 dark:bg-gray-700
                   accent-emerald-600 dark:accent-emerald-400"
      />
      <div className="flex justify-between text-[10px] text-gray-400">
        <span>{param.min}</span>
        <span>{param.max}</span>
      </div>
    </div>
  );
}

function MetaBadge({
  icon: Icon,
  label,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
}) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 dark:bg-gray-800 px-2.5 py-1 text-xs text-gray-600 dark:text-gray-300">
      <Icon className="h-3 w-3" />
      {label}
    </span>
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
   Main Page Component
───────────────────────────────────────────────────────────────────────────── */

export default function SimulatorDetailPage() {
  const { simId } = useParams<{ simId: string }>();
  const navigate = useNavigate();
  const { lang } = useLang();
  const s = SIM_STR[lang as SimLang] ?? SIM_STR.fa;
  const locale = localeOf(lang as SimLang);

  /* ── State ── */
  const [pageStatus, setPageStatus] = useState<PageStatus>("loading");
  const [config, setConfig] = useState<SimConfig | null>(null);
  const [params, setParams] = useState<Record<string, number>>({});
  const [series, setSeries] = useState<Series[]>([]);
  const [progress, setProgress] = useState(0);
  const [running, setRunning] = useState(false);
  const [runMode, setRunMode] = useState<RunMode>("client");
  const [error, setError] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState(0);

  const abortRef = useRef<AbortController | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  /* ── Load simulator config ── */
  useEffect(() => {
    if (!simId) {
      setPageStatus("not_found");
      return;
    }
    const found = SIM_CONFIGS.find((c) => c.id === simId);
    if (!found) {
      setPageStatus("not_found");
      return;
    }
    setConfig(found);
    setParams(defaultParams(found.id));
    setPageStatus("ready");
  }, [simId]);

  /* ── Cleanup on unmount ── */
  useEffect(() => {
    return () => {
      abortRef.current?.abort();
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  /* ── Derived ── */
  const name = useMemo(
    () => (config ? simName(config.id, lang as SimLang) : ""),
    [config, lang]
  );
  const desc = useMemo(
    () => (config ? simDesc(config.id, lang as SimLang) : ""),
    [config, lang]
  );

  /* ── Handlers ── */
  const handleParamChange = useCallback((key: string, value: number) => {
    setParams((prev) => ({ ...prev, [key]: value }));
  }, []);

  const handleReset = useCallback(() => {
    if (!config) return;
    setParams(defaultParams(config.id));
    setSeries([]);
    setProgress(0);
    setError(null);
    setElapsed(0);
  }, [config]);

  const startTimer = useCallback(() => {
    const start = Date.now();
    timerRef.current = setInterval(() => {
      setElapsed(Math.round((Date.now() - start) / 100) / 10);
    }, 100);
  }, []);

  const stopTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const handleRun = useCallback(async () => {
    if (!config || running) return;

    setRunning(true);
    setError(null);
    setSeries([]);
    setProgress(0);
    setElapsed(0);
    startTimer();

    const abort = new AbortController();
    abortRef.current = abort;

    try {
      if (runMode === "client" && COMPUTE[config.id]) {
        /* ── Client-side computation ── */
        const computeFn = COMPUTE[config.id];
        const totalSteps = 100;

        for (let step = 0; step <= totalSteps; step++) {
          if (abort.signal.aborted) break;

          const t = step / totalSteps;
          const result = computeFn(params, t);

          setSeries((prev) => {
            if (step === 0) return result;
            return result.map((newS, i) => ({
              ...newS,
              data: [...(prev[i]?.data ?? []), ...newS.data.slice(prev[i]?.data.length ?? 0)],
            }));
          });
          setProgress(Math.round((step / totalSteps) * 100));

          // Yield to UI thread
          await new Promise((r) => setTimeout(r, 16));
        }
      } else {
        /* ── Server-side computation ── */
        const response = await runOnServer(config.id, params, abort.signal);

        if (response && response.series) {
          setSeries(response.series);
          setProgress(100);
        } else {
          throw new Error("Empty response from server");
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") {
        // User cancelled — not an error
      } else {
        const msg = err instanceof Error ? err.message : "Unknown error";
        setError(msg);
        // Fallback to client if server failed
        if (runMode === "server" && COMPUTE[config.id]) {
          setRunMode("client");
        }
      }
    } finally {
      setRunning(false);
      stopTimer();
      abortRef.current = null;
    }
  }, [config, params, running, runMode, startTimer, stopTimer]);

  const handleStop = useCallback(() => {
    abortRef.current?.abort();
    setRunning(false);
    stopTimer();
  }, [stopTimer]);

  const handleDownload = useCallback(() => {
    if (!config || !series.length) return;
    const csv = seriesToCSV(series, config.id);
    downloadCSV(csv, `${config.id}_results.csv`);
  }, [config, series]);

  /* ── Render: Loading ── */
  if (pageStatus === "loading") {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
      </div>
    );
  }

  /* ── Render: Not Found ── */
  if (pageStatus === "not_found" || !config) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <FlaskConical className="h-12 w-12 text-gray-300" />
        <p className="text-lg text-gray-500">{simText(s, "not_found")}</p>
        <Link
          to="/simulators"
          className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          {simText(s, "back_to_list")}
        </Link>
      </div>
    );
  }

  /* ── Render: Ready ── */
  return (
    <div className="mx-auto max-w-6xl px-4 py-8 space-y-8">
      {/* Header */}
      <header className="space-y-3">
        <Link
          to="/simulators"
          className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-emerald-600 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          {simText(s, "back_to_list")}
        </Link>

        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-1">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {name}
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 max-w-2xl">
              {desc}
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <MetaBadge icon={FlaskConical} label={config.category ?? "—"} />
            <MetaBadge icon={Cpu} label={`v${config.version ?? "1.0"}`} />
            {config.tags?.map((tag) => (
              <MetaBadge key={tag} icon={Info} label={tag} />
            ))}
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ── Left Panel: Parameters ── */}
        <aside className="lg:col-span-1 space-y-4">
          <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-5 space-y-5">
            <div className="flex items-center gap-2">
              <Settings2 className="h-4 w-4 text-emerald-600" />
              <h2 className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                {simText(s, "parameters")}
              </h2>
            </div>

            {config.params.map((p: ParamDef) => (
              <ParamSlider
                key={p.key}
                param={p}
                value={params[p.key] ?? p.min}
                onChange={(v) => handleParamChange(p.key, v)}
                strings={s}
                lang={lang as SimLang}
              />
            ))}
          </div>

          {/* Run Controls */}
          <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-5 space-y-4">
            {/* Mode Toggle */}
            <div className="flex items-center gap-2 text-xs">
              <button
                onClick={() => setRunMode("client")}
                className={`inline-flex items-center gap-1 rounded-md px-2.5 py-1.5 font-medium transition-colors ${
                  runMode === "client"
                    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300"
                    : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
                }`}
              >
                <Cpu className="h-3 w-3" />
                {simText(s, "client_mode")}
              </button>
              <button
                onClick={() => setRunMode("server")}
                className={`inline-flex items-center gap-1 rounded-md px-2.5 py-1.5 font-medium transition-colors ${
                  runMode === "server"
                    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300"
                    : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
                }`}
              >
                <Globe className="h-3 w-3" />
                {simText(s, "server_mode")}
              </button>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              {!running ? (
                <button
                  onClick={handleRun}
                  className="flex-1 inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-emerald-700 active:scale-[0.98] transition-all"
                >
                  <Play className="h-4 w-4" />
                  {simText(s, "run")}
                </button>
              ) : (
                <button
                  onClick={handleStop}
                  className="flex-1 inline-flex items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-red-700 active:scale-[0.98] transition-all"
                >
                  <Pause className="h-4 w-4" />
                  {simText(s, "stop")}
                </button>
              )}

              <button
                onClick={handleReset}
                disabled={running}
                className="inline-flex items-center justify-center gap-1.5 rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-2.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-40 transition-colors"
                title={simText(s, "reset")}
              >
                <RotateCcw className="h-4 w-4" />
              </button>
            </div>

            {/* Progress */}
            {running && (
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs text-gray-500">
                  <span>{simText(s, "running")}…</span>
                  <span>{progress}%</span>
                </div>
                <div className="h-1.5 w-full rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-emerald-500 transition-all duration-200"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Elapsed Time */}
            {elapsed > 0 && (
              <p className="text-[11px] text-gray-400 text-center">
                {elapsed.toFixed(1)}s
              </p>
            )}

            {/* Error */}
            {error && (
              <div className="flex items-start gap-2 rounded-lg bg-red-50 dark:bg-red-900/20 p-3 text-xs text-red-700 dark:text-red-300">
                <CloudOff className="h-4 w-4 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}
          </div>
        </aside>

        {/* ── Right Panel: Chart & Results ── */}
        <main className="lg:col-span-2 space-y-4">
          {/* Chart Card */}
          <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <LineChartIcon className="h-4 w-4 text-emerald-600" />
                <h2 className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                  {simText(s, "results")}
                </h2>
              </div>

              {series.length > 0 && (
                <button
                  onClick={handleDownload}
                  className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 dark:border-gray-600 px-2.5 py-1.5 text-xs text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  <Download className="h-3.5 w-3.5" />
                  CSV
                </button>
              )}
            </div>

            {series.length > 0 ? (
              <SimulatorChart series={series} progress={progress} strings={s} />
            ) : (
              <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                <FlaskConical className="h-10 w-10 mb-3 opacity-40" />
                <p className="text-sm">{simText(s, "no_results_yet")}</p>
              </div>
            )}
          </div>

          {/* Series Legend / Summary */}
          {series.length > 0 && (
            <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-5">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
                {simText(s, "series_legend")}
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {series.map((sr, i) => {
                  const lastVal = sr.data[sr.data.length - 1];
                  const maxVal = Math.max(...sr.data);
                  const minVal = Math.min(...sr.data);
                  return (
                    <div
                      key={i}
                      className="flex items-center gap-3 rounded-lg bg-gray-50 dark:bg-gray-800 p-3"
                    >
                      <span
                        className="h-3 w-3 rounded-full shrink-0"
                        style={{ backgroundColor: sr.color ?? `hsl(${i * 60}, 70%, 50%)` }}
                      />
                      <div className="min-w-0 flex-1">
                        <p className="text-xs font-medium text-gray-700 dark:text-gray-300 truncate">
                          {sr.label}
                        </p>
                        <p className="text-[11px] text-gray-400 tabular-nums">
                          {simText(s, "last")}: {lastVal?.toFixed(3) ?? "—"}
                          {" · "}
                          {simText(s, "max")}: {maxVal.toFixed(3)}
                          {" · "}
                          {simText(s, "min")}: {minVal.toFixed(3)}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}