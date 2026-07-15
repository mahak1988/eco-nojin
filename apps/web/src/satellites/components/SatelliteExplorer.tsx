/**
 * ============================================================================
 *  SatelliteExplorer — browse and compare 15+ free satellites
 * ============================================================================
 */

import { useState } from "react";

import { useLanguage } from "@/hooks/useLanguage";
import { SATELLITES, SATELLITE_INDICES } from "../registry";
import { cn } from "@/lib/utils";

export function SatelliteExplorer(): JSX.Element {
  const { t, dir } = useLanguage();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filterAgency, setFilterAgency] = useState<string>("all");

  const agencies = [...new Set(SATELLITES.map((s) => s.agency))];
  const filtered = filterAgency === "all"
    ? SATELLITES
    : SATELLITES.filter((s) => s.agency === filterAgency);

  const selected = selectedId ? SATELLITES.find((s) => s.id === selectedId) : null;

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("satellites.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("satellites.subtitle")}</p>
      </header>

      {/* Agency filter */}
      <div className="mb-6 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => setFilterAgency("all")}
          className={cn(
            "rounded-lg px-3 py-1.5 text-sm font-medium transition",
            filterAgency === "all" ? "bg-emerald-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200",
          )}
        >
          {t("common.all")}
        </button>
        {agencies.map((a) => (
          <button
            key={a}
            type="button"
            onClick={() => setFilterAgency(a)}
            className={cn(
              "rounded-lg px-3 py-1.5 text-sm font-medium transition",
              filterAgency === a ? "bg-emerald-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200",
            )}
          >
            {a}
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Satellite list */}
        <div className="lg:col-span-1 space-y-2">
          {filtered.map((sat) => (
            <button
              key={sat.id}
              type="button"
              onClick={() => setSelectedId(sat.id)}
              className={cn(
                "flex w-full items-center gap-3 rounded-lg border p-3 text-start transition",
                selectedId === sat.id
                  ? "border-emerald-500 bg-emerald-50"
                  : "border-gray-200 bg-white hover:border-emerald-200",
              )}
            >
              <span className="text-2xl">{sat.icon}</span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-gray-900">{sat.name}</p>
                <p className="text-xs text-gray-500">{sat.agency} • {sat.resolution}</p>
              </div>
            </button>
          ))}
        </div>

        {/* Detail panel */}
        <div className="lg:col-span-2">
          {selected ? (
            <div className="rounded-xl border border-gray-200 bg-white p-6">
              <div className="flex items-center gap-3">
                <span className="flex h-14 w-14 items-center justify-center rounded-xl bg-emerald-50 text-3xl">
                  {selected.icon}
                </span>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{selected.name}</h2>
                  <p className="text-sm text-gray-500">
                    {selected.agency} • {t("satellites.launchYear")}: {selected.launchYear}
                  </p>
                </div>
              </div>

              <dl className="mt-6 grid grid-cols-2 gap-4 text-sm">
                <div>
                  <dt className="text-gray-500">{t("satellites.resolution")}</dt>
                  <dd className="mt-0.5 font-medium text-gray-900">{selected.resolution}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">{t("satellites.revisit")}</dt>
                  <dd className="mt-0.5 font-medium text-gray-900">
                    {selected.revisitDays === 0 ? t("satellites.variable") : `${selected.revisitDays} ${t("satellites.days")}`}
                  </dd>
                </div>
                <div>
                  <dt className="text-gray-500">{t("satellites.swath")}</dt>
                  <dd className="mt-0.5 font-medium text-gray-900">{selected.swath}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">{t("satellites.access")}</dt>
                  <dd className="mt-0.5 font-medium text-emerald-600">{t(`satellites.access_${selected.access}`)}</dd>
                </div>
              </dl>

              {/* Bands */}
              <div className="mt-6">
                <h3 className="text-sm font-semibold text-gray-900">{t("satellites.bands")}</h3>
                <div className="mt-2 overflow-x-auto">
                  <table className="w-full text-start text-sm">
                    <thead className="bg-gray-50 text-xs uppercase text-gray-500">
                      <tr>
                        <th className="px-3 py-2">{t("satellites.bandName")}</th>
                        <th className="px-3 py-2">{t("satellites.wavelength")}</th>
                        <th className="px-3 py-2">{t("satellites.application")}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {selected.bands.map((b) => (
                        <tr key={b.name}>
                          <td className="px-3 py-2 font-medium text-gray-900">{b.name}</td>
                          <td className="px-3 py-2 text-gray-600" dir="ltr">{b.wavelength}</td>
                          <td className="px-3 py-2 text-gray-600">{b.application}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Data source link */}
              <a
                href={selected.dataSource}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-6 inline-block rounded-lg bg-emerald-600 px-5 py-2 text-sm font-semibold text-white hover:bg-emerald-700"
              >
                {t("satellites.accessData")} →
              </a>
            </div>
          ) : (
            <div className="flex h-full min-h-[300px] items-center justify-center rounded-xl border border-dashed border-gray-300 p-12 text-center">
              <div>
                <div className="text-4xl">🛰️</div>
                <p className="mt-3 text-sm text-gray-500">{t("satellites.selectPrompt")}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Spectral indices */}
      <section className="mt-10">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("satellites.indicesTitle")}</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {SATELLITE_INDICES.map((idx) => (
            <div key={idx.id} className="rounded-xl border border-gray-200 bg-white p-4">
              <h3 className="text-sm font-semibold text-gray-900">{idx.name}</h3>
              <code dir="ltr" className="mt-2 block text-xs text-emerald-600">{idx.formula}</code>
              <p className="mt-2 text-xs text-gray-500">{idx.application}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
