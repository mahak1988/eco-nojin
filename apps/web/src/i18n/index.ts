/**
 * Lightweight i18n — source of truth: locale JSON under locales/{en,fa,ar}/.
 * Supported UI languages: English, Persian (fa), Arabic (ar).
 * Expand by adding locales/{code}/*.json and registering in catalogs.
 */

import arAuth from "./locales/ar/auth.json";
import arCommon from "./locales/ar/common.json";
import arSimulation from "./locales/ar/simulation.json";
import enAuth from "./locales/en/auth.json";
import enCommon from "./locales/en/common.json";
import enSimulation from "./locales/en/simulation.json";
import faAuth from "./locales/fa/auth.json";
import faCommon from "./locales/fa/common.json";
import faSimulation from "./locales/fa/simulation.json";

export type Locale = "en" | "fa" | "ar";

const catalogs: Record<Locale, Record<string, unknown>> = {
  en: { common: enCommon, auth: enAuth, simulation: enSimulation },
  fa: { common: faCommon, auth: faAuth, simulation: faSimulation },
  ar: { common: arCommon, auth: arAuth, simulation: arSimulation },
};

const STORAGE_KEY = "econojin_locale";

export function getStoredLocale(): Locale {
  try {
    const v = localStorage.getItem(STORAGE_KEY) as Locale | null;
    if (v && catalogs[v]) return v;
  } catch {
    /* ignore */
  }
  return "en";
}

export function setStoredLocale(locale: Locale): void {
  try {
    localStorage.setItem(STORAGE_KEY, locale);
  } catch {
    /* ignore */
  }
  if (typeof document !== "undefined") {
    document.documentElement.lang = locale;
    document.documentElement.dir = locale === "fa" || locale === "ar" ? "rtl" : "ltr";
  }
}

function dig(obj: unknown, path: string): string | undefined {
  const parts = path.split(".");
  let cur: unknown = obj;
  for (const p of parts) {
    if (cur == null || typeof cur !== "object") return undefined;
    cur = (cur as Record<string, unknown>)[p];
  }
  return typeof cur === "string" ? cur : undefined;
}

/** Translate key like "common.nav.farms" or "simulation.hubTitle". */
export function t(key: string, locale?: Locale): string {
  const loc = locale || getStoredLocale();
  const [ns, ...rest] = key.split(".");
  const path = rest.join(".");
  const pack = catalogs[loc]?.[ns] ?? catalogs.en[ns];
  const hit = dig(pack, path) ?? dig(catalogs.en[ns], path);
  return hit ?? key;
}

export const supportedLocales: Locale[] = ["en", "fa", "ar"];

/** How to add a new language: copy locales/en → locales/{code}, translate, add to Locale + catalogs. */
export const i18nExpandGuide =
  "Add locales/{code}/{common,auth,simulation}.json then extend Locale union and catalogs.";
