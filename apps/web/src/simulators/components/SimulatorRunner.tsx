/**
 * ============================================================================
 *  SimulatorRunner — generic UI for running any simulator
 * ============================================================================
 */

import { useState } from "react";

import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import type { SimulatorEngine, SimResult } from "../types";

export interface SimulatorRunnerProps {
  engine: SimulatorEngine;
}

export function SimulatorRunner({ engine }: SimulatorRunnerProps): JSX.Element {
  const { t, dir } = useLanguage();
  const [params, setParams] = useState<Record<string, unknown>>({});
  const [result, setResult] = useState<SimResult | null>(null);
  const [running, setRunning] = useState(false);

  const handleRun = async (): Promise<void> => {
    setRunning(true);
    try {
      const r = await engine.run(params);
      setResult(r);
    } finally {
      setRunning(false);
    }
  };

  const handlePreset = (presetId: string): void => {
    const preset = engine.presets.find((p) => p.id === presetId);
    if (preset) {
      setParams((prev) => ({ ...prev, ...preset.params }));
    }
  };

  return (
    <div dir={dir} className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-6">
        <div className="flex items-center gap-3">
          <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-3xl">
            {engine.icon}
          </span>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t(engine.nameKey)}</h1>
            <p className="mt-1 text-sm text-gray-600">{t(engine.descriptionKey)}</p>
          </div>
        </div>
      </header>

      {/* Presets */}
      {engine.presets.length > 0 && (
        <div className="mb-6">
          <h2 className="mb-3 text-sm font-semibold text-gray-900">{t("simulators.presets")}</h2>
          <div className="flex flex-wrap gap-2">
            {engine.presets.map((preset) => (
              <button
                key={preset.id}
                type="button"
                onClick={() => handlePreset(preset.id)}
                className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:border-emerald-500 hover:bg-emerald-50"
              >
                {t(preset.nameKey)}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Parameters */}
      {engine.parameters.length > 0 && (
        <div className="mb-6 rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="mb-4 text-sm font-semibold text-gray-900">{t("simulators.parameters")}</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {engine.parameters.map((param) => (
              <div key={param.key} className="space-y-1.5">
                <label className="block text-sm font-medium text-gray-700">
                  {t(param.labelKey)}
                  {param.unit && <span className="ms-1 text-gray-500">({param.unit})</span>}
                </label>
                <input
                  type={param.type === "number" ? "number" : "text"}
                  defaultValue={String(param.defaultValue)}
                  onChange={(e) => setParams((p) => ({ ...p, [param.key]: e.target.value }))}
                  className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Run button */}
      <button
        type="button"
        onClick={() => void handleRun()}
        disabled={running}
        className="flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-60"
      >
        {running ? <LoadingSpinner size="sm" variant="white" label={t("common.loading")} /> : t("simulators.run")}
      </button>

      {/* Results */}
      {result && (
        <div className="mt-8 space-y-6">
          {/* Summary */}
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="mb-4 text-sm font-semibold text-gray-900">{t(result.summary.titleKey)}</h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {result.summary.metrics.map((metric, i) => (
                <div key={i} className="rounded-lg bg-gray-50 p-4">
                  <p className="text-xs text-gray-500">{t(metric.labelKey)}</p>
                  <p className="mt-1 text-xl font-bold text-gray-900">
                    {metric.value}
                    {metric.unit && <span className="ms-1 text-sm font-normal text-gray-500">{metric.unit}</span>}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Warnings */}
          {result.warnings.length > 0 && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
              <ul className="space-y-1 text-sm text-amber-700">
                {result.warnings.map((w, i) => (<li key={i}>⚠️ {w}</li>))}
              </ul>
            </div>
          )}

          {/* Duration */}
          <p className="text-xs text-gray-400">
            {t("simulators.completedIn", { ms: result.duration })}
          </p>
        </div>
      )}
    </div>
  );
}
