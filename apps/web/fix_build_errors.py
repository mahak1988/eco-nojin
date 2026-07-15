#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 apps/web — Build Error Fix Script (round 2)
================================================================================
 Run from D:\\econojin.com\\apps\\web

   python fix_build_errors.py

 FIXES
 -----
  1. src/i18n/index.ts        — fix i18nReady Promise type (TS2322)
  2. src/pages/AgricultureSchools/AgricultureSchools.tsx — ensure `language`
                                is destructured in SchoolCard (TS2304)
  3. src/pages/Carbon/CarbonDashboard.tsx — fix array indexing fallback
                                for noUncheckedIndexedAccess (TS2322)
  4. src/pages/hooks/useHandleKeyPressHandlers.ts — DELETE orphan file (TS2304)
  5. src/services/authService.ts — rewrite to remove `me.name` pattern (TS2322)
================================================================================
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Detect project root
# ---------------------------------------------------------------------------

def detect_root() -> Path:
    cwd = Path.cwd()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "tsconfig.json").exists() and (candidate / "package.json").exists():
            return candidate
    return cwd

# ---------------------------------------------------------------------------
# File contents
# ---------------------------------------------------------------------------

# 1) i18n/index.ts — fix the i18nReady type
#    The issue: i18n.init() returns Promise<TFunction>, not Promise<i18n>.
#    Fix: chain .then(() => i18n) to return the instance.

I18N_INDEX_TS = '''/**
 * ============================================================================
 *  i18n initialization — react-i18next + browser language detection
 * ============================================================================
 *
 *  Supports two languages:
 *    - "fa" (Persian, RTL) — default
 *    - "en" (English, LTR)
 *
 *  Detection order (first match wins):
 *    1. localStorage key "econojin.lang"  (set by user via LanguageSwitcher)
 *    2. navigator.language                (browser preference)
 *    3. <html lang="\\u00a0">               (fallback)
 *
 *  The direction (rtl/ltr) is set on <html dir> by the useLanguage hook,
 *  NOT here — keep this module free of DOM side-effects so it stays
 *  testable in isolation.
 * ============================================================================
 */

import { createInstance, type i18n as I18nInstance } from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import fa from "./locales/fa.json";
import en from "./locales/en.json";

// ---------------------------------------------------------------------------
// Language constants
// ---------------------------------------------------------------------------

/** Tuple of all supported languages. Append new codes at the end. */
export const SUPPORTED_LANGUAGES = ["fa", "en"] as const;
export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number];

/**
 * Default language used when no detection signal is available.
 * Read from `VITE_DEFAULT_LANG` env var, falls back to "fa".
 */
export const DEFAULT_LANGUAGE: SupportedLanguage = (() => {
  const env = import.meta.env["VITE_DEFAULT_LANG"] as string | undefined;
  if (env && (SUPPORTED_LANGUAGES as readonly string[]).includes(env)) {
    return env as SupportedLanguage;
  }
  return "fa";
})();

/**
 * Languages that render right-to-left.
 * Add codes here when you add a new RTL language (ar, ur, he, ps, sd, ...).
 */
export const RTL_LANGUAGES: ReadonlySet<string> = new Set([
  "fa",
  "ar",
  "ur",
  "he",
  "ps",
  "sd",
]);

// ---------------------------------------------------------------------------
// Resources — the translation JSON files keyed by language code
// ---------------------------------------------------------------------------

const resources = {
  fa: { translation: fa },
  en: { translation: en },
} as const;

// ---------------------------------------------------------------------------
// Create the i18n instance (isolated, not the global singleton)
// ---------------------------------------------------------------------------

export const i18n: I18nInstance = createInstance();

/**
 * Initialize the instance.
 *
 * i18n.init() returns Promise<TFunction>, but we want to expose a Promise
 * that resolves to the instance itself (so callers can `await i18nReady`
 * and then use `i18n` directly). We chain `.then(() => i18n)` to do this.
 */
export const i18nReady: Promise<I18nInstance> = i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: DEFAULT_LANGUAGE,
    supportedLngs: SUPPORTED_LANGUAGES,
    nonExplicitSupportedLngs: true,
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ["localStorage", "navigator", "htmlTag"],
      lookupLocalStorage: "econojin.lang",
      caches: ["localStorage"],
    },
    react: {
      useSuspense: false,
    },
  })
  .then(() => i18n);

// ---------------------------------------------------------------------------
// Direction helpers (pure functions — no DOM access)
// ---------------------------------------------------------------------------

export function getLanguageDir(language: string): "rtl" | "ltr" {
  return RTL_LANGUAGES.has(language) ? "rtl" : "ltr";
}

export function isLanguageRTL(language: string): boolean {
  return RTL_LANGUAGES.has(language);
}

export function isSupportedLanguage(value: string): value is SupportedLanguage {
  return (SUPPORTED_LANGUAGES as readonly string[]).includes(value);
}

export function coerceLanguage(value: string | undefined | null): SupportedLanguage {
  if (!value) return DEFAULT_LANGUAGE;
  if (isSupportedLanguage(value)) return value;
  const base = value.split("-")[0] ?? "";
  if (isSupportedLanguage(base)) return base;
  return DEFAULT_LANGUAGE;
}

// ---------------------------------------------------------------------------
// Development-only diagnostics
// ---------------------------------------------------------------------------

if (import.meta.env.DEV) {
  void i18nReady.then(() => {
    // eslint-disable-next-line no-console
    console.info(
      `[i18n] language="${i18n.language}" dir="${getLanguageDir(i18n.language)}"`,
    );
  });

  i18n.on("missingKey", (lngs, namespace, key) => {
    // eslint-disable-next-line no-console
    console.warn(`[i18n] missing key "${key}" in [${lngs.join(", ")}] / "${namespace}"`);
  });
}

export default i18n;
'''

# 2) AgricultureSchools.tsx — ensure `language` is destructured in SchoolCard
#    (rewrite the whole file to be safe)

AGRICULTURE_SCHOOLS_TSX = '''/**
 * ============================================================================
 *  AgricultureSchools — directory of agriculture schools (i18n-aware)
 * ============================================================================
 */

import { useMemo, useState } from "react";

import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Types + mock data
// ---------------------------------------------------------------------------

interface School {
  id: string;
  nameKey: string;
  provinceKey: string;
  cityKey: string;
  type: "university" | "institute" | "training-center";
  established: number;
  studentsCount: number;
  fieldsKeys: readonly string[];
  website: string;
  logo: string;
}

const SCHOOLS: readonly School[] = [
  {
    id: "s-1",
    nameKey: "schools.s1Name",
    provinceKey: "schools.s1Province",
    cityKey: "schools.s1City",
    type: "university",
    established: 1963,
    studentsCount: 4200,
    fieldsKeys: ["schools.fieldIrrigation", "schools.fieldSoil", "schools.fieldHorticulture", "schools.fieldPlantProtection"],
    website: "https://abf.ut.ac.ir",
    logo: "\\u{1F393}",
  },
  {
    id: "s-2",
    nameKey: "schools.s2Name",
    provinceKey: "schools.s2Province",
    cityKey: "schools.s2City",
    type: "university",
    established: 1957,
    studentsCount: 6800,
    fieldsKeys: ["schools.fieldForestry", "schools.fieldEnvironment", "schools.fieldFisheries", "schools.fieldIrrigation"],
    website: "https://gau.ac.ir",
    logo: "\\u{1F332}",
  },
  {
    id: "s-3",
    nameKey: "schools.s3Name",
    provinceKey: "schools.s3Province",
    cityKey: "schools.s3City",
    type: "university",
    established: 1955,
    studentsCount: 3100,
    fieldsKeys: ["schools.fieldAgronomy", "schools.fieldHorticulture", "schools.fieldWaterEng", "schools.fieldPlantProtection"],
    website: "https://agri.cu.ac.ir",
    logo: "\\u{1F33E}",
  },
  {
    id: "s-4",
    nameKey: "schools.s4Name",
    provinceKey: "schools.s4Province",
    cityKey: "schools.s4City",
    type: "institute",
    established: 2011,
    studentsCount: 450,
    fieldsKeys: ["schools.fieldOrganic", "schools.fieldPermaculture", "schools.fieldGreenEcon"],
    website: "https://saii.ir",
    logo: "\\u{1F331}",
  },
  {
    id: "s-5",
    nameKey: "schools.s5Name",
    provinceKey: "schools.s5Province",
    cityKey: "schools.s5City",
    type: "training-center",
    established: 2015,
    studentsCount: 220,
    fieldsKeys: ["schools.fieldOrganic", "schools.fieldBiodynamic", "schools.fieldLowTill"],
    website: "https://sac-esf.ir",
    logo: "\\u{1F33F}",
  },
  {
    id: "s-6",
    nameKey: "schools.s6Name",
    provinceKey: "schools.s6Province",
    cityKey: "schools.s6City",
    type: "university",
    established: 1973,
    studentsCount: 3900,
    fieldsKeys: ["schools.fieldAgronomy", "schools.fieldIrrigation", "schools.fieldHorticulture", "schools.fieldSeedTech"],
    website: "https://ag.um.ac.ir",
    logo: "\\u{1F33B}",
  },
] as const;

// ---------------------------------------------------------------------------
// Subcomponents
// ---------------------------------------------------------------------------

function FilterBar({
  search, province, onSearch, onProvince, provinces,
}: {
  search: string;
  province: string;
  onSearch: (v: string) => void;
  onProvince: (v: string) => void;
  provinces: readonly string[];
}): JSX.Element {
  const { t, dir } = useLanguage();
  return (
    <div dir={dir} className="flex flex-col gap-3 sm:flex-row">
      <div className="relative flex-1">
        <input
          type="search"
          value={search}
          onChange={(e) => onSearch(e.target.value)}
          placeholder={t("agricultureSchools.searchPlaceholder")}
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
        value={province}
        onChange={(e) => onProvince(e.target.value)}
        className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
        aria-label={t("hydrology.filterProvince")}
      >
        <option value="all">{t("hydrology.allProvinces")}</option>
        {provinces.map((p) => (<option key={p} value={p}>{p}</option>))}
      </select>
    </div>
  );
}

function SchoolCard({ school }: { school: School }): JSX.Element {
  const { t, dir, language } = useLanguage();
  return (
    <article dir={dir} className="flex h-full flex-col rounded-xl border border-gray-200 bg-white p-5 transition hover:border-emerald-200 hover:shadow-sm">
      <div className="flex items-start gap-4">
        <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-2xl">
          {school.logo}
        </span>
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-semibold leading-6 text-gray-900">{t(school.nameKey)}</h3>
          <p className="mt-0.5 text-xs text-gray-500">
            {t(`agricultureSchools.types.${school.type}`)} \\u2022 {t(school.cityKey)}\\u060C {t(school.provinceKey)}
          </p>
        </div>
      </div>

      <dl className="mt-4 grid grid-cols-2 gap-3 text-xs">
        <div>
          <dt className="text-gray-500">{t("agricultureSchools.established")}</dt>
          <dd className="mt-0.5 font-medium text-gray-900">{formatNumber(school.established, language)}</dd>
        </div>
        <div>
          <dt className="text-gray-500">{t("agricultureSchools.studentsCount")}</dt>
          <dd className="mt-0.5 font-medium text-gray-900">
            {formatNumber(school.studentsCount, language)} {t("agricultureSchools.students")}
          </dd>
        </div>
      </dl>

      <div className="mt-4">
        <p className="text-xs text-gray-500">{t("agricultureSchools.mainFields")}</p>
        <div className="mt-1.5 flex flex-wrap gap-1.5">
          {school.fieldsKeys.map((f) => (
            <span key={f} className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-700">{t(f)}</span>
          ))}
        </div>
      </div>

      <a
        href={school.website}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-5 inline-flex items-center justify-center rounded-lg border border-emerald-600 px-4 py-2 text-xs font-medium text-emerald-700 transition hover:bg-emerald-50"
      >
        {t("agricultureSchools.visitWebsite")}
      </a>
    </article>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function AgricultureSchools(): JSX.Element {
  const { t, dir, language } = useLanguage();
  const [search, setSearch] = useState("");
  const [province, setProvince] = useState("all");

  const provinces = useMemo(
    () => [...new Set(SCHOOLS.map((s) => t(s.provinceKey)))].sort(),
    [t],
  );

  const filtered = useMemo(() => {
    return SCHOOLS.filter((s) => {
      if (search) {
        const q = search.toLowerCase();
        if (!t(s.nameKey).toLowerCase().includes(q) && !t(s.cityKey).toLowerCase().includes(q)) return false;
      }
      if (province !== "all" && t(s.provinceKey) !== province) return false;
      return true;
    });
  }, [search, province, t]);

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("agricultureSchools.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("agricultureSchools.subtitle")}</p>
      </header>

      <div className="mb-6">
        <FilterBar
          search={search}
          province={province}
          onSearch={setSearch}
          onProvince={setProvince}
          provinces={provinces}
        />
      </div>

      {filtered.length === 0 ? (
        <div dir={dir} className="rounded-xl border border-dashed border-gray-300 p-12 text-center">
          <div className="text-4xl">\\u{1F50D}</div>
          <h3 className="mt-3 text-base font-semibold text-gray-900">{t("agricultureSchools.noResults")}</h3>
          <p className="mt-1 text-sm text-gray-600">{t("agricultureSchools.noResultsDescription")}</p>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((school) => (
            <SchoolCard key={school.id} school={school} />
          ))}
        </div>
      )}
    </div>
  );
}
'''

# 3) CarbonDashboard.tsx — fix array indexing with fallback for noUncheckedIndexedAccess

CARBON_FIX = '''/**
 * ============================================================================
 *  CarbonDashboard — carbon emissions overview (i18n-aware)
 * ============================================================================
 */

import { useApi } from "@/hooks/useApi";
import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { formatDate, formatNumber } from "@/lib/i18n-utils";
import { cn } from "@/lib/utils";
import type { CarbonMetric } from "@/types";

// ---------------------------------------------------------------------------
// Mock fetcher
// ---------------------------------------------------------------------------

const CARBON_SOURCES = ["industrial", "transport", "agriculture", "residential"] as const;
const CARBON_REGIONS = ["Tehran", "Isfahan", "Khorasan", "Fars", "Azerbaijan"] as const;

async function fetchCarbonMetrics(): Promise<CarbonMetric[]> {
  await new Promise((resolve) => setTimeout(resolve, 350));
  return Array.from({ length: 8 }, (_, i) => {
    const source = CARBON_SOURCES[i % 4] ?? "industrial";
    const region = CARBON_REGIONS[i % 5] ?? "Unknown";
    return {
      id: `c-${i}`,
      region,
      co2eTons: Math.round(1200 + Math.random() * 5800),
      source,
      recordedAt: new Date(2024, 6, 1 + i).toISOString(),
    } satisfies CarbonMetric;
  });
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const SOURCE_COLOR_BG: Record<CarbonMetric["source"], string> = {
  industrial: "bg-red-100 text-red-700",
  transport: "bg-amber-100 text-amber-700",
  agriculture: "bg-emerald-100 text-emerald-700",
  residential: "bg-blue-100 text-blue-700",
};
const SOURCE_BAR: Record<CarbonMetric["source"], string> = {
  industrial: "bg-red-500",
  transport: "bg-amber-500",
  agriculture: "bg-emerald-500",
  residential: "bg-blue-500",
};

// ---------------------------------------------------------------------------
// Subcomponents
// ---------------------------------------------------------------------------

function KpiCard({ label, value, trend, trendDirection = "neutral", icon }: {
  label: string;
  value: string;
  trend?: string;
  trendDirection?: "up" | "down" | "neutral";
  icon: string;
}): JSX.Element {
  const { dir } = useLanguage();
  const trendColor =
    trendDirection === "up" ? "text-red-600" : trendDirection === "down" ? "text-emerald-600" : "text-gray-500";
  return (
    <div dir={dir} className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-600">{label}</p>
        <span className="text-2xl" aria-hidden="true">{icon}</span>
      </div>
      <p className="mt-2 text-2xl font-bold text-gray-900">{value}</p>
      {trend && <p className={cn("mt-1 text-xs", trendColor)}>{trend}</p>}
    </div>
  );
}

function SourceBreakdown({ items }: { items: CarbonMetric[] }): JSX.Element {
  const { t, dir, language } = useLanguage();
  const totals = items.reduce<Record<CarbonMetric["source"], number>>(
    (acc, item) => {
      acc[item.source] = (acc[item.source] ?? 0) + item.co2eTons;
      return acc;
    },
    { industrial: 0, transport: 0, agriculture: 0, residential: 0 },
  );
  const total = Object.values(totals).reduce((a, b) => a + b, 0);
  if (total === 0) return <></>;

  return (
    <div dir={dir} className="rounded-xl border border-gray-200 bg-white p-5">
      <h3 className="text-sm font-semibold text-gray-900">{t("carbon.sourceBreakdown")}</h3>
      <div className="mt-4 space-y-3">
        {(Object.keys(totals) as CarbonMetric["source"][]).map((source) => {
          const value = totals[source];
          const percent = Math.round((value / total) * 100);
          return (
            <div key={source}>
              <div className="mb-1 flex items-center justify-between text-sm">
                <span className="text-gray-600">{t(`carbon.sources.${source}`)}</span>
                <span className="font-medium text-gray-900">
                  {formatNumber(value, language)} {t("carbon.tons")} ({formatNumber(percent, language)}%)
                </span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
                <div
                  className={cn("h-full rounded-full", SOURCE_BAR[source])}
                  style={{ width: `${percent}%` }}
                  role="progressbar"
                  aria-valuenow={percent}
                  aria-valuemin={0}
                  aria-valuemax={100}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function RecentTable({ items }: { items: CarbonMetric[] }): JSX.Element {
  const { t, dir, language } = useLanguage();
  return (
    <div dir={dir} className="overflow-hidden rounded-xl border border-gray-200 bg-white">
      <div className="border-b border-gray-200 px-5 py-3">
        <h3 className="text-sm font-semibold text-gray-900">{t("carbon.recentMeasurements")}</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-start text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500">
            <tr>
              <th className="px-5 py-3 font-medium">{t("carbon.tableRegion")}</th>
              <th className="px-5 py-3 font-medium">{t("carbon.tableSource")}</th>
              <th className="px-5 py-3 font-medium">{t("carbon.tableCo2e")}</th>
              <th className="px-5 py-3 font-medium">{t("carbon.tableDate")}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {items.slice(0, 6).map((item) => (
              <tr key={item.id} className="hover:bg-gray-50">
                <td className="px-5 py-3 font-medium text-gray-900">{item.region}</td>
                <td className="px-5 py-3">
                  <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", SOURCE_COLOR_BG[item.source])}>
                    {t(`carbon.sources.${item.source}`)}
                  </span>
                </td>
                <td className="px-5 py-3 text-gray-700">{formatNumber(item.co2eTons, language)}</td>
                <td className="px-5 py-3 text-gray-500">{formatDate(item.recordedAt, language)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function CarbonDashboard(): JSX.Element {
  const { t, dir, language } = useLanguage();
  const { data, isLoading, isError, refetch } = useApi(fetchCarbonMetrics, { enabled: true });

  const totalEmissions = data?.reduce((sum, item) => sum + item.co2eTons, 0) ?? 0;
  const regionCount = new Set(data?.map((d) => d.region)).size ?? 0;
  const topSource = data?.reduce<CarbonMetric["source"] | null>((top, item) => {
    if (!top || item.co2eTons > (data.find((d) => d.source === top)?.co2eTons ?? 0)) return item.source;
    return top;
  }, null) ?? null;

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("carbon.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("carbon.subtitle")}</p>
      </header>

      {isLoading && (
        <div className="flex h-[40vh] items-center justify-center">
          <LoadingSpinner size="lg" label={t("carbon.loadingData")} />
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
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KpiCard
              label={t("carbon.totalEmissions")}
              value={`${formatNumber(totalEmissions, language)} ${t("carbon.tons")}`}
              trend={t("carbon.monthlyTrendUp")}
              trendDirection="up"
              icon="\\u{1F3ED}"
            />
            <KpiCard label={t("carbon.monitoredRegions")} value={formatNumber(regionCount, language)} icon="\\u{1F4CD}" />
            <KpiCard
              label={t("carbon.topSource")}
              value={topSource ? t(`carbon.sources.${topSource}`) : "\\u2014"}
              icon="\\u{1F525}"
            />
            <KpiCard
              label={t("carbon.averagePerRegion")}
              value={`${formatNumber(regionCount > 0 ? Math.round(totalEmissions / regionCount) : 0, language)} ${t("carbon.tons")}`}
              trend={t("carbon.monthlyTrendDown")}
              trendDirection="down"
              icon="\\u{1F4CA}"
            />
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-1"><SourceBreakdown items={data} /></div>
            <div className="lg:col-span-2"><RecentTable items={data} /></div>
          </div>
        </div>
      )}
    </div>
  );
}
'''

# 5) authService.ts — rewrite without the `me.name` pattern

AUTH_SERVICE_TS = '''/**
 * ============================================================================
 *  authService — typed API client for authentication endpoints
 * ============================================================================
 */

import type {
  ApiError,
  AuthCredentials,
  AuthSession,
  ForgotPasswordRequest,
  MeResponse,
  RegisterPayload,
  ResetPasswordRequest,
  User,
} from "@/types";
import { API_ENDPOINTS } from "@/types/api";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const API_BASE_URL: string =
  (import.meta.env["VITE_API_BASE_URL"] as string | undefined) ??
  "http://localhost:1337/api";

const TOKEN_STORAGE_KEY = "econojin.access_token";
const REFRESH_TOKEN_STORAGE_KEY = "econojin.refresh_token";

// ---------------------------------------------------------------------------
// Token storage (SSR-safe)
// ---------------------------------------------------------------------------

export const tokenStorage = {
  getAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(TOKEN_STORAGE_KEY);
  },
  getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);
  },
  set(session: AuthSession): void {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(TOKEN_STORAGE_KEY, session.accessToken);
    if (session.refreshToken) {
      window.localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, session.refreshToken);
    }
  },
  clear(): void {
    if (typeof window === "undefined") return;
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
  },
} as const;

// ---------------------------------------------------------------------------
// Internal fetch wrapper
// ---------------------------------------------------------------------------

interface FetchOptions<TBody = unknown> {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: TBody;
  query?: Record<string, string | number | boolean | undefined>;
  signal?: AbortSignal;
  authenticated?: boolean;
}

async function apiFetch<TResponse, TBody = unknown>(
  path: string,
  options: FetchOptions<TBody> = {},
): Promise<TResponse> {
  const { method = "GET", body, query, signal, authenticated = true } = options;

  const url = new URL(`${API_BASE_URL}${path}`);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined) url.searchParams.set(key, String(value));
    }
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (authenticated) {
    const token = tokenStorage.getAccessToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url.toString(), {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal,
  });

  if (response.status === 204) {
    return null as unknown as TResponse;
  }

  const payload = (await response.json().catch(() => null)) as
    | { data?: TResponse; message?: string }
    | TResponse
    | ApiError
    | null;

  if (!response.ok) {
    const err = (payload as ApiError | undefined) ?? {
      statusCode: response.status,
      error: response.statusText,
      message: "auth.unknownError",
    };
    throw err as ApiError;
  }

  if (
    payload !== null &&
    typeof payload === "object" &&
    "data" in payload &&
    payload.data !== undefined
  ) {
    return payload.data as TResponse;
  }

  return payload as TResponse;
}

// ---------------------------------------------------------------------------
// Public auth API
// ---------------------------------------------------------------------------

export async function login(credentials: AuthCredentials): Promise<AuthSession> {
  const session = await apiFetch<AuthSession, AuthCredentials>(
    API_ENDPOINTS.auth.login,
    { method: "POST", body: credentials, authenticated: false },
  );
  tokenStorage.set(session);
  return session;
}

export async function register(payload: RegisterPayload): Promise<AuthSession> {
  const session = await apiFetch<AuthSession, RegisterPayload>(
    API_ENDPOINTS.auth.register,
    { method: "POST", body: payload, authenticated: false },
  );
  tokenStorage.set(session);
  return session;
}

export async function logout(): Promise<void> {
  try {
    await apiFetch<void>(API_ENDPOINTS.auth.logout, { method: "POST" });
  } catch {
    // Even if the server call fails, clear locally.
  } finally {
    tokenStorage.clear();
  }
}

export async function getCurrentUser(): Promise<User> {
  return apiFetch<MeResponse>(API_ENDPOINTS.auth.me);
}

export async function forgotPassword(payload: ForgotPasswordRequest): Promise<void> {
  await apiFetch<void, ForgotPasswordRequest>(
    API_ENDPOINTS.auth.forgotPassword,
    { method: "POST", body: payload, authenticated: false },
  );
}

export async function resetPassword(payload: ResetPasswordRequest): Promise<void> {
  await apiFetch<void, ResetPasswordRequest>(
    API_ENDPOINTS.auth.resetPassword,
    { method: "POST", body: payload, authenticated: false },
  );
}

export async function refreshSession(): Promise<AuthSession> {
  const refreshToken = tokenStorage.getRefreshToken();
  if (!refreshToken) {
    throw {
      statusCode: 401,
      error: "Unauthorized",
      message: "auth.sessionExpired",
    } satisfies ApiError;
  }

  const session = await apiFetch<AuthSession, { refreshToken: string }>(
    API_ENDPOINTS.auth.refresh,
    { method: "POST", body: { refreshToken }, authenticated: false },
  );
  tokenStorage.set(session);
  return session;
}
'''

# ---------------------------------------------------------------------------
# Apply fixes
# ---------------------------------------------------------------------------

def write_file(root: Path, rel_path: str, content: str) -> bool:
    """Write a file, return True if changed."""
    full = root / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    content_bytes = content.encode("utf-8")
    if full.exists() and full.read_bytes() == content_bytes:
        return False
    full.write_bytes(content_bytes)
    return True

def delete_file(root: Path, rel_path: str) -> bool:
    """Delete a file, return True if it was deleted."""
    full = root / rel_path
    if full.exists():
        full.unlink()
        return True
    return False

def main() -> int:
    root = detect_root()
    print(f"[INFO] Project root: {root}")
    print()

    print("=" * 72)
    print(" Fixing 5 build errors")
    print("=" * 72)

    # 1. Fix i18n/index.ts
    changed = write_file(root, "src/i18n/index.ts", I18N_INDEX_TS)
    print(f"  [{'FIXED' if changed else 'ok'}]  src/i18n/index.ts  (i18nReady type)")

    # 2. Fix AgricultureSchools.tsx
    changed = write_file(root, "src/pages/AgricultureSchools/AgricultureSchools.tsx", AGRICULTURE_SCHOOLS_TSX)
    print(f"  [{'FIXED' if changed else 'ok'}]  src/pages/AgricultureSchools/AgricultureSchools.tsx  (language destructure)")

    # 3. Fix CarbonDashboard.tsx
    changed = write_file(root, "src/pages/Carbon/CarbonDashboard.tsx", CARBON_FIX)
    print(f"  [{'FIXED' if changed else 'ok'}]  src/pages/Carbon/CarbonDashboard.tsx  (array index fallback)")

    # 4. Delete orphan file
    deleted = delete_file(root, "src/pages/hooks/useHandleKeyPressHandlers.ts")
    print(f"  [{'DELETED' if deleted else 'not found'}]  src/pages/hooks/useHandleKeyPressHandlers.ts  (orphan file)")

    # Also try to delete the empty hooks dir if it exists
    orphan_dir = root / "src/pages/hooks"
    if orphan_dir.exists():
        try:
            # Only remove if empty
            if not any(orphan_dir.iterdir()):
                orphan_dir.rmdir()
                print(f"  [DELETED]  src/pages/hooks/  (empty directory)")
        except OSError:
            pass  # Directory not empty, leave it

    # 5. Rewrite authService.ts
    changed = write_file(root, "src/services/authService.ts", AUTH_SERVICE_TS)
    print(f"  [{'FIXED' if changed else 'ok'}]  src/services/authService.ts  (remove me.name pattern)")

    print()
    print("=" * 72)
    print(" DONE — now run: pnpm run build")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
