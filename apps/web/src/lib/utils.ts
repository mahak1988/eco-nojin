import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number, decimals: number = 0): string {
  return new Intl.NumberFormat("fa-IR", { minimumFractionDigits: decimals, maximumFractionDigits: decimals }).format(num);
}

export function formatCurrency(amount: number, currency: "IRR" | "USD" = "IRR"): string {
  return new Intl.NumberFormat("fa-IR", {
    style: "currency",
    currency: currency === "IRR" ? "IRR" : "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: currency === "USD" ? 2 : 0,
  }).format(amount);
}

export function formatDate(date: Date | string, format: "short" | "long" = "short"): string {
  const d = new Date(date);
  return new Intl.DateTimeFormat("fa-IR", {
    year: "numeric",
    month: "short",
    day: "numeric",
    ...(format === "long" && { hour: "2-digit", minute: "2-digit" }),
  }).format(d);
}
