/**
 * ============================================================================
 *  WatershedList — searchable, filterable watershed table (i18n-aware)
 * ============================================================================
 */

import { useMemo, useState } from "react";

import { useApi } from "@/hooks/useApi";
import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { formatNumber } from "@/lib/i18n-utils";
import { cn } from "@/lib/utils";
import type { Watershed } from "@/types";

// ---------------------------------------------------------------------------
// Mock fetcher
// ---------------------------------------------------------------------------

async function fetchWatersheds(): Promise<Watershed[]> {
  await new Promise((resolve) => setTimeout(resolve, 300));
  const provinces = ["Tehran", "Isfahan", "Fars", "Khorasan", "Gilan", "Azerbaijan"];
  const statuses: Watershed["status"][] = ["monitored", "unmonitored", "critical"];
  return Array.from({ length: 18 }, (_, i) => ({
    id: `ws-${i + 1}` as Watershed["id"],
    name: `Watershed ${i + 1}`,
    code: `W-${String(1000 + i)}`,
    areaKm2: Math.round(500 + Math.random() * 9500),
    province: provinces[i % provinces.length] ?? "Unknown",
    averageRainfallMm: Math.round(150 + Math.random() * 850),
    status: statuses[i % 3] ?? "monitored",
    lastUpdated: new Date(2024, 5, 1 + i).toISOString(),
  }));
}

// ---------------------------------------------------------------------------
// Status badge
// ---------------------------------------------------------------------------

const STATUS_CONFIG: Record<Watershed["status"], { className: string }> = {
  monitored: { className: "bg-emerald-100 text-emerald-700" },
  unmonitored: { className: "bg-gray-100 text-gray-700" },
  critical: { className: "bg-red-100 text-red-700" },
};

function StatusBadge({ status }: { status: Watershed["status"] }): JSX.Element {
  const { t } = useLanguage();
  const config = STATUS_CONFIG[status];
  return (
    <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-medium", config.className)}>
      {t(`hydrology.statuses.${status}`)}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Filters
// ---------------------------------------------------------------------------

interface FilterState {
  search: string;
  province: string;
  status: Watershed["status"] | "all";
}

const INITIAL_FILTERS: FilterState = { search: "", province: "all", status: "all" };

function FilterBar({
  filters,
  onChange,
  provinces,
}: {
  filters: FilterState;
  onChange: (next: FilterState) => void;
  provinces: readonly string[];
}): JSX.Element {
  const { t, dir } = useLanguage();
  return (
    <div dir={dir} className="flex flex-col gap-3 sm:flex-row sm:items-center">
      <div className="relative flex-1">
        <input
          type="search"
          value={filters.search}
          onChange={(e) => onChange({ ...filters, search: e.target.value })}
          placeholder={t("hydrology.searchPlaceholder")}
          className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 pe-10 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
        />
        <svg
          className="pointer-events-none absolute end-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>

      <select
        value={filters.province}
        onChange={(e) => onChange({ ...filters, province: e.target.value })}
        className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
        aria-label={t("hydrology.filterProvince")}
      >
        <option value="all">{t("hydrology.allProvinces")}</option>
        {provinces.map((p) => (<option key={p} value={p}>{p}</option>))}
      </select>

      <select
        value={filters.status}
        onChange={(e) => onChange({ ...filters, status: e.target.value as FilterState["status"] })}
        className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
        aria-label={t("hydrology.filterStatus")}
      >
        <option value="all">{t("hydrology.allStatuses")}</option>
        <option value="monitored">{t("hydrology.statuses.monitored")}</option>
        <option value="unmonitored">{t("hydrology.statuses.unmonitored")}</option>
        <option value="critical">{t("hydrology.statuses.critical")}</option>
      </select>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sortable header
// ---------------------------------------------------------------------------

type SortKey = "name" | "areaKm2" | "averageRainfallMm";
type SortDir = "asc" | "desc";

function SortButton({ label, active, direction, onClick }: {
  label: string;
  active: boolean;
  direction: SortDir;
  onClick: () => void;
}): JSX.Element {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-1 font-medium transition",
        active ? "text-emerald-700" : "text-gray-500 hover:text-gray-700",
      )}
    >
      {label}
      <span aria-hidden="true">{active ? (direction === "asc" ? "▲" : "▼") : "↕"}</span>
    </button>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function WatershedList(): JSX.Element {
  const { t, dir, language } = useLanguage();
  const { data, isLoading, isError, refetch } = useApi(fetchWatersheds, { enabled: true });
  const [filters, setFilters] = useState<FilterState>(INITIAL_FILTERS);
  const [sortKey, setSortKey] = useState<SortKey>("name");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  const provinces = useMemo(
    () => [...new Set(data?.map((d) => d.province) ?? [])].sort(),
    [data],
  );

  const filtered = useMemo(() => {
    if (!data) return [];
    const result = data.filter((w) => {
      if (filters.search) {
        const q = filters.search.toLowerCase();
        if (!w.name.toLowerCase().includes(q) && !w.code.toLowerCase().includes(q)) return false;
      }
      if (filters.province !== "all" && w.province !== filters.province) return false;
      if (filters.status !== "all" && w.status !== filters.status) return false;
      return true;
    });

    result.sort((a, b) => {
      const dirMul = sortDir === "asc" ? 1 : -1;
      if (sortKey === "name") return a.name.localeCompare(b.name) * dirMul;
      return ((a[sortKey] - b[sortKey]) * dirMul);
    });
    return result;
  }, [data, filters, sortKey, sortDir]);

  const toggleSort = (key: SortKey): void => {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(key); setSortDir("asc"); }
  };

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("hydrology.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("hydrology.subtitle")}</p>
      </header>

      <div className="mb-4">
        <FilterBar filters={filters} onChange={setFilters} provinces={provinces} />
      </div>

      {isLoading && (
        <div className="flex h-[40vh] items-center justify-center">
          <LoadingSpinner size="lg" label={t("common.loading")} />
        </div>
      )}

      {isError && (
        <div dir={dir} className="rounded-xl border border-red-200 bg-red-50 p-8 text-center">
          <p className="text-sm text-red-700">{t("documents.loadError")}</p>
          <button
            type="button"
            onClick={() => void refetch()}
            className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700"
          >
            {t("common.retry")}
          </button>
        </div>
      )}

      {data && (
        <div dir={dir} className="overflow-hidden rounded-xl border border-gray-200 bg-white">
          <div className="overflow-x-auto">
            <table className="w-full text-start text-sm">
              <thead className="border-b border-gray-200 bg-gray-50 text-xs">
                <tr>
                  <th className="px-5 py-3">
                    <SortButton label={t("hydrology.tableName")} active={sortKey === "name"} direction={sortDir} onClick={() => toggleSort("name")} />
                  </th>
                  <th className="px-5 py-3 font-medium text-gray-500">{t("hydrology.tableCode")}</th>
                  <th className="px-5 py-3 font-medium text-gray-500">{t("hydrology.tableProvince")}</th>
                  <th className="px-5 py-3">
                    <SortButton label={t("hydrology.tableArea")} active={sortKey === "areaKm2"} direction={sortDir} onClick={() => toggleSort("areaKm2")} />
                  </th>
                  <th className="px-5 py-3">
                    <SortButton label={t("hydrology.tableRainfall")} active={sortKey === "averageRainfallMm"} direction={sortDir} onClick={() => toggleSort("averageRainfallMm")} />
                  </th>
                  <th className="px-5 py-3 font-medium text-gray-500">{t("hydrology.tableStatus")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.length === 0 ? (
                  <tr><td colSpan={6} className="px-5 py-12 text-center text-sm text-gray-500">{t("hydrology.noResults")}</td></tr>
                ) : (
                  filtered.map((w) => (
                    <tr key={w.id} className="hover:bg-gray-50">
                      <td className="px-5 py-3 font-medium text-gray-900">{w.name}</td>
                      <td className="px-5 py-3 text-gray-600" dir="ltr">{w.code}</td>
                      <td className="px-5 py-3 text-gray-700">{w.province}</td>
                      <td className="px-5 py-3 text-gray-700">{formatNumber(w.areaKm2, language)}</td>
                      <td className="px-5 py-3 text-gray-700">{formatNumber(w.averageRainfallMm, language)}</td>
                      <td className="px-5 py-3"><StatusBadge status={w.status} /></td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
