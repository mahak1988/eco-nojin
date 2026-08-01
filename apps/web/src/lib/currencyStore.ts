/** Multi-currency settings (IRR / USD / EUR + custom). Manual, persisted. */

export type CurrencyCode = "IRR" | "USD" | "EUR" | "GBP" | "TRY" | "AED" | "CUSTOM";

export type CurrencySettings = {
  primary: CurrencyCode;
  secondary: CurrencyCode;
  customCode: string;
  customSymbol: string;
  rates: Record<string, number>;
  displayFormat: "symbol_first" | "code_after";
};

const KEY = "econojin_currency_settings";

export const DEFAULT_RATES: Record<string, number> = {
  USD: 1,
  EUR: 0.92,
  GBP: 0.79,
  TRY: 34.5,
  AED: 3.67,
  IRR: 42000,
};

export const DEFAULT_CURRENCY: CurrencySettings = {
  primary: "IRR",
  secondary: "USD",
  customCode: "XAU",
  customSymbol: "\u2609",
  rates: { ...DEFAULT_RATES },
  displayFormat: "code_after",
};

export function readCurrencySettings(): CurrencySettings {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return { ...DEFAULT_CURRENCY, rates: { ...DEFAULT_RATES } };
    const parsed = JSON.parse(raw) as Partial<CurrencySettings>;
    return {
      ...DEFAULT_CURRENCY,
      ...parsed,
      rates: { ...DEFAULT_RATES, ...(parsed.rates || {}) },
    };
  } catch {
    return { ...DEFAULT_CURRENCY, rates: { ...DEFAULT_RATES } };
  }
}

export function writeCurrencySettings(s: CurrencySettings) {
  try {
    localStorage.setItem(KEY, JSON.stringify(s));
  } catch {
    /* ignore */
  }
}

export function convert(amount: number, from: string, to: string, rates: Record<string, number>): number {
  const f = rates[from] ?? 1;
  const t = rates[to] ?? 1;
  const inUsd = amount / f;
  return inUsd * t;
}

export function formatMoney(
  amount: number,
  code: string,
  settings: CurrencySettings,
  locale = "en-US"
): string {
  const symbol =
    code === "IRR"
      ? "\ufdfc"
      : code === "USD"
        ? "$"
        : code === "EUR"
          ? "\u20ac"
          : code === "GBP"
            ? "\u00a3"
            : code === "CUSTOM"
              ? settings.customSymbol
              : code;
  const label = code === "CUSTOM" ? settings.customCode : code;
  const n = amount.toLocaleString(locale, { maximumFractionDigits: code === "IRR" ? 0 : 2 });
  if (settings.displayFormat === "symbol_first") return `${symbol}${n}`;
  return `${n} ${label}`;
}
