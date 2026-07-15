#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 apps/web — Batch 2 Generator (27 remaining files + i18n keys + App.tsx update)
================================================================================
 Run from D:\\econojin.com\\apps\\web

   python generate_batch2.py

 CREATES
 -------
  24 page files (Batch 2 from the original analyzer report):
    - BiodiversityDashboard, Blog, Careers, ContactUs, Daneshyar, DecisionYar
    - DroughtDashboard
    - EcoCoin/{Challenges, EcoCoinDashboard, Mining, Rewards, Wallet}
    - EconomicModels, EcosystemDashboard, EcosystemRestoration
    - EnergyDashboard, FAQ, ForgotPassword
    - GIS/{FlowAccumulationAnalysis, GISDashboard, LandCoverAnalysis,
           SlopeAnalysis, ViewshedAnalysis, WatershedAnalysis}

  1 Profile page (referenced in Header but missing):
    - pages/Profile/Profile.tsx

  1 root file:
    - index.html

 UPDATES
 -------
  - src/App.tsx        (adds routes for all new pages)
  - src/i18n/locales/fa.json  (adds ~200 keys)
  - src/i18n/locales/en.json  (adds ~200 keys)
================================================================================
"""

from __future__ import annotations

import json
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
# Helper
# ---------------------------------------------------------------------------

def write_file(root: Path, rel_path: str, content: str) -> bool:
    full = root / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    content_bytes = content.encode("utf-8")
    if full.exists() and full.read_bytes() == content_bytes:
        return False
    full.write_bytes(content_bytes)
    return True

# ---------------------------------------------------------------------------
# Dashboard-style pages (Biodiversity, Drought, Ecosystem, Energy)
# These follow the same pattern as CarbonDashboard / SoilDashboard
# ---------------------------------------------------------------------------

def make_dashboard_page(class_name: str, route: str, i18n_prefix: str, icon: str) -> str:
    return f'''/**
 * ============================================================================
 *  {class_name} — {i18n_prefix} dashboard (i18n-aware)
 * ============================================================================
 */

import {{ useApi }} from "@/hooks/useApi";
import {{ useLanguage }} from "@/hooks/useLanguage";
import {{ LoadingSpinner }} from "@/components/common/LoadingSpinner";
import {{ formatNumber }} from "@/lib/i18n-utils";

// ---------------------------------------------------------------------------
// Mock fetcher — replace with real API call
// ---------------------------------------------------------------------------

interface Metric {{
  id: string;
  region: string;
  value: number;
  unit: string;
  recordedAt: string;
}}

async function fetchMetrics(): Promise<Metric[]> {{
  await new Promise((resolve) => setTimeout(resolve, 300));
  const regions = ["Tehran", "Isfahan", "Fars", "Khorasan", "Gilan"];
  return Array.from({{ length: 6 }}, (_, i) => ({{
    id: `m-${{i}}`,
    region: regions[i % 5] ?? "Unknown",
    value: Math.round(100 + Math.random() * 900),
    unit: "unit",
    recordedAt: new Date(2024, 6, 1 + i).toISOString(),
  }}));
}}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function {class_name}(): JSX.Element {{
  const {{ t, dir, language }} = useLanguage();
  const {{ data, isLoading, isError, refetch }} = useApi(fetchMetrics, {{ enabled: true }});

  const totalValue = data?.reduce((sum, item) => sum + item.value, 0) ?? 0;
  const regionCount = new Set(data?.map((d) => d.region)).size ?? 0;
  const avgValue = regionCount > 0 ? Math.round(totalValue / regionCount) : 0;

  return (
    <div dir={{dir}} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{{t("{i18n_prefix}.title")}}</h1>
        <p className="mt-1 text-sm text-gray-600">{{t("{i18n_prefix}.subtitle")}}</p>
      </header>

      {{isLoading && (
        <div className="flex h-[40vh] items-center justify-center">
          <LoadingSpinner size="lg" label={{t("common.loading")}} />
        </div>
      )}}

      {{isError && (
        <div dir={{dir}} className="rounded-xl border border-red-200 bg-red-50 p-8 text-center">
          <p className="text-sm text-red-700">{{t("documents.loadError")}}</p>
          <button
            type="button"
            onClick={{() => void refetch()}}
            className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700"
          >
            {{t("common.retry")}}
          </button>
        </div>
      )}}

      {{data && (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-600">{{t("{i18n_prefix}.totalValue")}}</p>
                <span className="text-2xl" aria-hidden="true">{icon}</span>
              </div>
              <p className="mt-2 text-2xl font-bold text-gray-900">{{formatNumber(totalValue, language)}}</p>
            </div>
            <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-600">{{t("{i18n_prefix}.regions")}}</p>
                <span className="text-2xl" aria-hidden="true">📍</span>
              </div>
              <p className="mt-2 text-2xl font-bold text-gray-900">{{formatNumber(regionCount, language)}}</p>
            </div>
            <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-600">{{t("{i18n_prefix}.average")}}</p>
                <span className="text-2xl" aria-hidden="true">📊</span>
              </div>
              <p className="mt-2 text-2xl font-bold text-gray-900">{{formatNumber(avgValue, language)}}</p>
            </div>
          </div>

          <div dir={{dir}} className="overflow-hidden rounded-xl border border-gray-200 bg-white">
            <div className="border-b border-gray-200 px-5 py-3">
              <h3 className="text-sm font-semibold text-gray-900">{{t("{i18n_prefix}.tableTitle")}}</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-start text-sm">
                <thead className="bg-gray-50 text-xs uppercase text-gray-500">
                  <tr>
                    <th className="px-5 py-3 font-medium">{{t("carbon.tableRegion")}}</th>
                    <th className="px-5 py-3 font-medium">{{t("{i18n_prefix}.tableValue")}}</th>
                    <th className="px-5 py-3 font-medium">{{t("carbon.tableDate")}}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {{data.map((item) => (
                    <tr key={{item.id}} className="hover:bg-gray-50">
                      <td className="px-5 py-3 font-medium text-gray-900">{{item.region}}</td>
                      <td className="px-5 py-3 text-gray-700">{{formatNumber(item.value, language)}} {{item.unit}}</td>
                      <td className="px-5 py-3 text-gray-500">{{item.recordedAt.split("T")[0]}}</td>
                    </tr>
                  ))}}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}}
    </div>
  );
}}
'''

# ---------------------------------------------------------------------------
# Simple content page (Blog, Careers, Daneshyar, DecisionYar, EconomicModels,
# EcosystemRestoration)
# ---------------------------------------------------------------------------

def make_simple_page(class_name: str, i18n_prefix: str, icon: str) -> str:
    return f'''/**
 * ============================================================================
 *  {class_name} — {i18n_prefix} page (i18n-aware)
 * ============================================================================
 */

import {{ useLanguage }} from "@/hooks/useLanguage";

export function {class_name}(): JSX.Element {{
  const {{ t, dir }} = useLanguage();

  return (
    <div dir={{dir}} className="mx-auto max-w-4xl px-4 py-8">
      <header className="mb-8 text-center">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-emerald-50 text-4xl">
          {icon}
        </div>
        <h1 className="mt-4 text-3xl font-bold text-gray-900">{{t("{i18n_prefix}.title")}}</h1>
        <p className="mt-2 text-sm text-gray-600">{{t("{i18n_prefix}.subtitle")}}</p>
      </header>

      <div className="space-y-6">
        <section className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-900">{{t("{i18n_prefix}.section1Title")}}</h2>
          <p className="mt-3 text-sm leading-7 text-gray-600">{{t("{i18n_prefix}.section1Body")}}</p>
        </section>

        <section className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-900">{{t("{i18n_prefix}.section2Title")}}</h2>
          <p className="mt-3 text-sm leading-7 text-gray-600">{{t("{i18n_prefix}.section2Body")}}</p>
        </section>

        <section className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-900">{{t("{i18n_prefix}.section3Title")}}</h2>
          <p className="mt-3 text-sm leading-7 text-gray-600">{{t("{i18n_prefix}.section3Body")}}</p>
        </section>
      </div>
    </div>
  );
}}
'''

# ---------------------------------------------------------------------------
# ContactUs — form-based page
# ---------------------------------------------------------------------------

CONTACT_US_TSX = '''/**
 * ============================================================================
 *  ContactUs — contact form page (i18n-aware)
 * ============================================================================
 */

import { useState, type FormEvent } from "react";

import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { cn } from "@/lib/utils";

export function ContactUs(): JSX.Element {
  const { t, dir } = useLanguage();
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setSubmitting(true);
    await new Promise((r) => setTimeout(r, 800));
    setSubmitting(false);
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div dir={dir} className="mx-auto max-w-2xl px-4 py-16 text-center">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-emerald-100 text-4xl">✓</div>
        <h1 className="mt-4 text-2xl font-bold text-gray-900">{t("contactUs.successTitle")}</h1>
        <p className="mt-2 text-sm text-gray-600">{t("contactUs.successBody")}</p>
      </div>
    );
  }

  return (
    <div dir={dir} className="mx-auto max-w-2xl px-4 py-8">
      <header className="mb-8 text-center">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-emerald-50 text-4xl">✉️</div>
        <h1 className="mt-4 text-3xl font-bold text-gray-900">{t("contactUs.title")}</h1>
        <p className="mt-2 text-sm text-gray-600">{t("contactUs.subtitle")}</p>
      </header>

      <div className="rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid gap-5 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">{t("contactUs.name")}</label>
              <input
                id="name"
                type="text"
                required
                value={form.name}
                onChange={(e) => setForm((s) => ({ ...s, name: e.target.value }))}
                className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
              />
            </div>
            <div className="space-y-1.5">
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">{t("contactUs.email")}</label>
              <input
                id="email"
                type="email"
                required
                dir="ltr"
                value={form.email}
                onChange={(e) => setForm((s) => ({ ...s, email: e.target.value }))}
                className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <label htmlFor="subject" className="block text-sm font-medium text-gray-700">{t("contactUs.subject")}</label>
            <input
              id="subject"
              type="text"
              required
              value={form.subject}
              onChange={(e) => setForm((s) => ({ ...s, subject: e.target.value }))}
              className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
            />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="message" className="block text-sm font-medium text-gray-700">{t("contactUs.message")}</label>
            <textarea
              id="message"
              required
              rows={5}
              value={form.message}
              onChange={(e) => setForm((s) => ({ ...s, message: e.target.value }))}
              className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
            />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-60"
          >
            {submitting ? <LoadingSpinner size="sm" variant="white" label={t("common.loading")} /> : t("contactUs.send")}
          </button>
        </form>
      </div>
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# FAQ — accordion page
# ---------------------------------------------------------------------------

FAQ_TSX = '''/**
 * ============================================================================
 *  FAQ — frequently asked questions (i18n-aware, accordion)
 * ============================================================================
 */

import { useState } from "react";

import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/lib/utils";

const FAQ_ITEMS = [
  { qKey: "faq.q1", aKey: "faq.a1" },
  { qKey: "faq.q2", aKey: "faq.a2" },
  { qKey: "faq.q3", aKey: "faq.a3" },
  { qKey: "faq.q4", aKey: "faq.a4" },
  { qKey: "faq.q5", aKey: "faq.a5" },
  { qKey: "faq.q6", aKey: "faq.a6" },
] as const;

export function FAQ(): JSX.Element {
  const { t, dir } = useLanguage();
  const [openIdx, setOpenIdx] = useState<number | null>(0);

  return (
    <div dir={dir} className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-8 text-center">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-emerald-50 text-4xl">❓</div>
        <h1 className="mt-4 text-3xl font-bold text-gray-900">{t("faq.title")}</h1>
        <p className="mt-2 text-sm text-gray-600">{t("faq.subtitle")}</p>
      </header>

      <div className="space-y-3">
        {FAQ_ITEMS.map((item, idx) => {
          const isOpen = openIdx === idx;
          return (
            <div key={item.qKey} className="overflow-hidden rounded-xl border border-gray-200 bg-white">
              <button
                type="button"
                onClick={() => setOpenIdx(isOpen ? null : idx)}
                aria-expanded={isOpen}
                className="flex w-full items-center justify-between gap-4 px-5 py-4 text-start"
              >
                <span className="text-sm font-semibold text-gray-900">{t(item.qKey)}</span>
                <span className={cn("text-gray-400 transition-transform", isOpen && "rotate-180")} aria-hidden="true">▼</span>
              </button>
              {isOpen && (
                <div className="border-t border-gray-100 px-5 py-4">
                  <p className="text-sm leading-7 text-gray-600">{t(item.aKey)}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# ForgotPassword
# ---------------------------------------------------------------------------

FORGOT_PASSWORD_TSX = '''/**
 * ============================================================================
 *  ForgotPassword — password reset request page (i18n-aware)
 * ============================================================================
 */

import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";

export function ForgotPassword(): JSX.Element {
  const { t, dir } = useLanguage();
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setSubmitting(true);
    await new Promise((r) => setTimeout(r, 800));
    setSubmitting(false);
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div dir={dir} className="flex min-h-screen items-center justify-center bg-gradient-to-br from-emerald-50 to-teal-50 px-4">
        <div className="w-full max-w-md text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 text-3xl">✓</div>
          <h1 className="mt-4 text-2xl font-bold text-gray-900">{t("forgotPassword.successTitle")}</h1>
          <p className="mt-2 text-sm text-gray-600">{t("forgotPassword.successBody")}</p>
          <Link to="/login" className="mt-6 inline-block rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700">
            {t("user.login")}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div dir={dir} className="flex min-h-screen items-center justify-center bg-gradient-to-br from-emerald-50 to-teal-50 px-4 py-12">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <span className="inline-flex h-14 w-14 items-center justify-center rounded-xl bg-emerald-600 text-white">
            <svg className="h-8 w-8" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2L3 7v6c0 4.4 3.1 8.3 7 9 3.9-.7 7-4.6 7-9V7l-7-5z" /></svg>
          </span>
          <h1 className="mt-4 text-2xl font-bold text-gray-900">{t("forgotPassword.title")}</h1>
          <p className="mt-1 text-sm text-gray-600">{t("forgotPassword.subtitle")}</p>
        </div>

        <div className="rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-1.5">
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">{t("auth.email")}</label>
              <input
                id="email"
                type="email"
                required
                dir="ltr"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t("auth.emailPlaceholder")}
                className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-60"
            >
              {submitting ? <LoadingSpinner size="sm" variant="white" label={t("common.loading")} /> : t("forgotPassword.sendButton")}
            </button>
          </form>
          <p className="mt-6 text-center text-sm text-gray-600">
            <Link to="/login" className="font-semibold text-emerald-600 hover:text-emerald-700">{t("auth.haveAccount")}</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# EcoCoin pages
# ---------------------------------------------------------------------------

ECOCOIN_DASHBOARD_TSX = '''/**
 * ============================================================================
 *  EcoCoinDashboard — EcoCoin overview (i18n-aware)
 * ============================================================================
 */

import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";

const QUICK_LINKS = [
  { to: "/ecocoin/wallet", labelKey: "ecoCoin.wallet", icon: "👛" },
  { to: "/ecocoin/mining", labelKey: "ecoCoin.mining", icon: "⛏️" },
  { to: "/ecocoin/challenges", labelKey: "ecoCoin.challenges", icon: "🏆" },
  { to: "/ecocoin/rewards", labelKey: "ecoCoin.rewards", icon: "🎁" },
] as const;

export function EcoCoinDashboard(): JSX.Element {
  const { t, dir, language } = useLanguage();

  const stats = [
    { labelKey: "ecoCoin.balance", value: formatNumber(1250, language), suffix: "ECO" },
    { labelKey: "ecoCoin.minedThisMonth", value: formatNumber(320, language), suffix: "ECO" },
    { labelKey: "ecoCoin.challengesCompleted", value: formatNumber(8, language), suffix: "" },
    { labelKey: "ecoCoin.rank", value: formatNumber(142, language), suffix: "" },
  ];

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("ecoCoin.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("ecoCoin.subtitle")}</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((s) => (
          <div key={s.labelKey} className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-600">{t(s.labelKey)}</p>
            <p className="mt-2 text-2xl font-bold text-gray-900">
              {s.value}
              {s.suffix && <span className="ms-1 text-sm font-normal text-gray-500">{s.suffix}</span>}
            </p>
          </div>
        ))}
      </div>

      <h2 className="mb-4 mt-8 text-lg font-semibold text-gray-900">{t("dashboard.quickAccess")}</h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {QUICK_LINKS.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className="group rounded-xl border border-gray-200 bg-white p-5 transition hover:border-emerald-200 hover:shadow-md"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-2xl">{link.icon}</div>
            <h3 className="mt-4 text-base font-semibold text-gray-900">{t(link.labelKey)}</h3>
          </Link>
        ))}
      </div>
    </div>
  );
}
'''

ECOCOIN_WALLET_TSX = '''/**
 * ============================================================================
 *  EcoCoin Wallet — balance + transactions (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";
import { cn } from "@/lib/utils";

interface Tx { id: string; type: "credit" | "debit"; descKey: string; amount: number; date: string; }
const TXS: readonly Tx[] = [
  { id: "1", type: "credit", descKey: "ecoCoin.txReward", amount: 50, date: "2024-07-10" },
  { id: "2", type: "debit", descKey: "ecoCoin.txPurchase", amount: 30, date: "2024-07-08" },
  { id: "3", type: "credit", descKey: "ecoCoin.txMining", amount: 15, date: "2024-07-05" },
  { id: "4", type: "credit", descKey: "ecoCoin.txChallenge", amount: 100, date: "2024-07-01" },
] as const;

export function Wallet(): JSX.Element {
  const { t, dir, language } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-4xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("ecoCoin.wallet")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("ecoCoin.walletSubtitle")}</p>
      </header>

      <div className="mb-6 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-700 p-6 text-white">
        <p className="text-sm text-emerald-100">{t("ecoCoin.balance")}</p>
        <p className="mt-2 text-4xl font-bold">{formatNumber(1250, language)} ECO</p>
      </div>

      <div dir={dir} className="overflow-hidden rounded-xl border border-gray-200 bg-white">
        <div className="border-b border-gray-200 px-5 py-3">
          <h3 className="text-sm font-semibold text-gray-900">{t("ecoCoin.recentTransactions")}</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-start text-sm">
            <thead className="bg-gray-50 text-xs uppercase text-gray-500">
              <tr>
                <th className="px-5 py-3 font-medium">{t("accounting.tableDescription")}</th>
                <th className="px-5 py-3 font-medium">{t("accounting.tableAmount")}</th>
                <th className="px-5 py-3 font-medium">{t("accounting.tableDate")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {TXS.map((tx) => (
                <tr key={tx.id} className="hover:bg-gray-50">
                  <td className="px-5 py-3 font-medium text-gray-900">{t(tx.descKey)}</td>
                  <td className={cn("px-5 py-3 font-medium", tx.type === "credit" ? "text-emerald-600" : "text-gray-700")}>
                    {tx.type === "credit" ? "+" : "−"}{formatNumber(tx.amount, language)} ECO
                  </td>
                  <td className="px-5 py-3 text-gray-500" dir="ltr">{tx.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
'''

ECOCOIN_MINING_TSX = '''/**
 * ============================================================================
 *  EcoCoin Mining — mining dashboard (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";

export function Mining(): JSX.Element {
  const { t, dir, language } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-4xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("ecoCoin.mining")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("ecoCoin.miningSubtitle")}</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-600">{t("ecoCoin.hashRate")}</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{formatNumber(42, language)} H/s</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-600">{t("ecoCoin.minedToday")}</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{formatNumber(12, language)} ECO</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-600">{t("ecoCoin.minedTotal")}</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{formatNumber(580, language)} ECO</p>
        </div>
      </div>

      <div className="mt-6 rounded-xl border border-gray-200 bg-white p-8 text-center">
        <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-emerald-50 text-5xl">⛏️</div>
        <h2 className="mt-4 text-lg font-semibold text-gray-900">{t("ecoCoin.miningStatus")}</h2>
        <p className="mt-1 text-sm text-gray-600">{t("ecoCoin.miningActive")}</p>
        <button
          type="button"
          className="mt-6 rounded-lg bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700"
        >
          {t("ecoCoin.stopMining")}
        </button>
      </div>
    </div>
  );
}
'''

ECOCOIN_CHALLENGES_TSX = '''/**
 * ============================================================================
 *  EcoCoin Challenges — environmental challenges (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";
import { cn } from "@/lib/utils";

interface Challenge { id: string; titleKey: string; descKey: string; reward: number; status: "active" | "completed"; }
const CHALLENGES: readonly Challenge[] = [
  { id: "1", titleKey: "ecoCoin.ch1Title", descKey: "ecoCoin.ch1Desc", reward: 50, status: "active" },
  { id: "2", titleKey: "ecoCoin.ch2Title", descKey: "ecoCoin.ch2Desc", reward: 100, status: "active" },
  { id: "3", titleKey: "ecoCoin.ch3Title", descKey: "ecoCoin.ch3Desc", reward: 30, status: "completed" },
  { id: "4", titleKey: "ecoCoin.ch4Title", descKey: "ecoCoin.ch4Desc", reward: 75, status: "active" },
  { id: "5", titleKey: "ecoCoin.ch5Title", descKey: "ecoCoin.ch5Desc", reward: 200, status: "active" },
] as const;

export function Challenges(): JSX.Element {
  const { t, dir, language } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-4xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("ecoCoin.challenges")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("ecoCoin.challengesSubtitle")}</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2">
        {CHALLENGES.map((ch) => (
          <article key={ch.id} className="rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-base font-semibold text-gray-900">{t(ch.titleKey)}</h3>
                <p className="mt-1 text-sm text-gray-600">{t(ch.descKey)}</p>
              </div>
              <span className={cn(
                "shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium",
                ch.status === "completed" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700",
              )}>
                {ch.status === "completed" ? t("ecoCoin.completed") : t("ecoCoin.active")}
              </span>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <span className="text-sm font-semibold text-emerald-600">+{formatNumber(ch.reward, language)} ECO</span>
              {ch.status === "active" && (
                <button type="button" className="rounded-lg bg-emerald-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-emerald-700">
                  {t("ecoCoin.startChallenge")}
                </button>
              )}
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
'''

ECOCOIN_REWARDS_TSX = '''/**
 * ============================================================================
 *  EcoCoin Rewards — reward store (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";

interface Reward { id: string; nameKey: string; descKey: string; cost: number; icon: string; }
const REWARDS: readonly Reward[] = [
  { id: "1", nameKey: "ecoCoin.rw1Name", descKey: "ecoCoin.rw1Desc", cost: 500, icon: "📱" },
  { id: "2", nameKey: "ecoCoin.rw2Name", descKey: "ecoCoin.rw2Desc", cost: 1000, icon: "🌱" },
  { id: "3", nameKey: "ecoCoin.rw3Name", descKey: "ecoCoin.rw3Desc", cost: 300, icon: "📚" },
  { id: "4", nameKey: "ecoCoin.rw4Name", descKey: "ecoCoin.rw4Desc", cost: 2000, icon: "🎫" },
  { id: "5", nameKey: "ecoCoin.rw5Name", descKey: "ecoCoin.rw5Desc", cost: 750, icon: "♻️" },
  { id: "6", nameKey: "ecoCoin.rw6Name", descKey: "ecoCoin.rw6Desc", cost: 1500, icon: "🎁" },
] as const;

export function Rewards(): JSX.Element {
  const { t, dir, language } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("ecoCoin.rewards")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("ecoCoin.rewardsSubtitle")}</p>
      </header>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {REWARDS.map((rw) => (
          <article key={rw.id} className="flex h-full flex-col rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-emerald-50 text-3xl">{rw.icon}</div>
            <h3 className="mt-4 text-sm font-semibold text-gray-900">{t(rw.nameKey)}</h3>
            <p className="mt-1 flex-1 text-xs leading-5 text-gray-600">{t(rw.descKey)}</p>
            <div className="mt-4 flex items-center justify-between">
              <span className="text-sm font-bold text-emerald-600">{formatNumber(rw.cost, language)} ECO</span>
              <button
                type="button"
                className="rounded-lg border border-emerald-600 px-3 py-1.5 text-xs font-medium text-emerald-700 transition hover:bg-emerald-50"
              >
                {t("ecoCoin.redeem")}
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# GIS pages — all follow the same analysis-page pattern
# ---------------------------------------------------------------------------

def make_gis_page(class_name: str, i18n_prefix: str, icon: str) -> str:
    return f'''/**
 * ============================================================================
 *  {class_name} — {i18n_prefix} analysis page (i18n-aware)
 * ============================================================================
 */

import {{ useLanguage }} from "@/hooks/useLanguage";
import {{ formatNumber }} from "@/lib/i18n-utils";

export function {class_name}(): JSX.Element {{
  const {{ t, dir, language }} = useLanguage();

  return (
    <div dir={{dir}} className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{{t("{i18n_prefix}.title")}}</h1>
        <p className="mt-1 text-sm text-gray-600">{{t("{i18n_prefix}.subtitle")}}</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-600">{{t("gis.analysisArea")}}</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{{formatNumber(2450, language)}} km²</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-600">{{t("gis.dataPoints")}}</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{{formatNumber(12450, language)}}</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-600">{{t("gis.lastUpdate")}}</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">2024-07-11</p>
        </div>
      </div>

      <div className="mt-6 rounded-xl border border-gray-200 bg-white p-8">
        <div className="flex h-64 flex-col items-center justify-center gap-3 rounded-lg bg-gray-50">
          <span className="text-6xl">{icon}</span>
          <p className="text-sm text-gray-500">{{t("gis.mapPlaceholder")}}</p>
        </div>
      </div>

      <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="text-base font-semibold text-gray-900">{{t("gis.results")}}</h2>
        <p className="mt-2 text-sm leading-6 text-gray-600">{{t("{i18n_prefix}.resultDescription")}}</p>
      </div>
    </div>
  );
}}
'''

GIS_DASHBOARD_TSX = '''/**
 * ============================================================================
 *  GISDashboard — GIS analysis overview (i18n-aware)
 * ============================================================================
 */

import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";

const ANALYSES = [
  { to: "/gis/flow-accumulation", labelKey: "gis.flowAccumulation", icon: "💧" },
  { to: "/gis/land-cover", labelKey: "gis.landCover", icon: "🌲" },
  { to: "/gis/slope", labelKey: "gis.slope", icon: "⛰️" },
  { to: "/gis/viewshed", labelKey: "gis.viewshed", icon: "👁️" },
  { to: "/gis/watershed", labelKey: "gis.watershed", icon: "🏞️" },
] as const;

export function GISDashboard(): JSX.Element {
  const { t, dir } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("gis.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("gis.subtitle")}</p>
      </header>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {ANALYSES.map((a) => (
          <Link
            key={a.to}
            to={a.to}
            className="group rounded-xl border border-gray-200 bg-white p-5 transition hover:border-emerald-200 hover:shadow-md"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-2xl">{a.icon}</div>
            <h3 className="mt-4 text-base font-semibold text-gray-900">{t(a.labelKey)}</h3>
            <p className="mt-3 text-xs font-medium text-emerald-600 transition group-hover:translate-x-1">{t("common.back")} ←</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# Profile page
# ---------------------------------------------------------------------------

PROFILE_TSX = '''/**
 * ============================================================================
 *  Profile — user profile page (i18n-aware)
 * ============================================================================
 */

import { useState, type FormEvent } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";

export function Profile(): JSX.Element {
  const { user } = useAuth();
  const { t, dir } = useLanguage();
  const [form, setForm] = useState({
    displayName: user?.displayName ?? "",
    firstName: user?.firstName ?? "",
    lastName: user?.lastName ?? "",
    bio: user?.bio ?? "",
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  if (!user) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <LoadingSpinner size="md" label={t("common.loading")} />
      </div>
    );
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setSaving(true);
    await new Promise((r) => setTimeout(r, 600));
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const initials = (user.displayName || user.username)
    .split(" ").map((p) => p.charAt(0)).slice(0, 2).join("").toUpperCase();

  return (
    <div dir={dir} className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("profile.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("profile.subtitle")}</p>
      </header>

      {/* Profile header card */}
      <div className="mb-6 rounded-2xl border border-gray-200 bg-white p-6">
        <div className="flex items-center gap-4">
          {user.avatarUrl ? (
            <img src={user.avatarUrl} alt={user.displayName} className="h-20 w-20 rounded-full object-cover ring-4 ring-emerald-50" />
          ) : (
            <span className="flex h-20 w-20 items-center justify-center rounded-full bg-emerald-600 text-2xl font-semibold text-white ring-4 ring-emerald-50">
              {initials}
            </span>
          )}
          <div>
            <h2 className="text-xl font-bold text-gray-900">{user.displayName}</h2>
            <p className="text-sm text-gray-500" dir="ltr">@{user.username}</p>
            <span className="mt-1 inline-block rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-medium text-emerald-700">
              {t(`user.${user.role}` !== "user." + user.role ? "user." + user.role : "common.appName")}
            </span>
          </div>
        </div>
      </div>

      {/* Edit form */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("profile.editInfo")}</h2>

        {saved && (
          <div role="alert" className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            {t("profile.savedSuccessfully")}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid gap-5 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label htmlFor="firstName" className="block text-sm font-medium text-gray-700">{t("profile.firstName")}</label>
              <input
                id="firstName"
                type="text"
                value={form.firstName}
                onChange={(e) => setForm((s) => ({ ...s, firstName: e.target.value }))}
                className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
              />
            </div>
            <div className="space-y-1.5">
              <label htmlFor="lastName" className="block text-sm font-medium text-gray-700">{t("profile.lastName")}</label>
              <input
                id="lastName"
                type="text"
                value={form.lastName}
                onChange={(e) => setForm((s) => ({ ...s, lastName: e.target.value }))}
                className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <label htmlFor="displayName" className="block text-sm font-medium text-gray-700">{t("auth.displayName")}</label>
            <input
              id="displayName"
              type="text"
              value={form.displayName}
              onChange={(e) => setForm((s) => ({ ...s, displayName: e.target.value }))}
              className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
            />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="bio" className="block text-sm font-medium text-gray-700">{t("profile.bio")}</label>
            <textarea
              id="bio"
              rows={4}
              value={form.bio}
              onChange={(e) => setForm((s) => ({ ...s, bio: e.target.value }))}
              className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
            />
          </div>
          <div className="flex items-center justify-end gap-3">
            <button
              type="submit"
              disabled={saving}
              className="flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-60"
            >
              {saving ? <LoadingSpinner size="sm" variant="white" label={t("common.loading")} /> : t("common.save")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# index.html
# ---------------------------------------------------------------------------

INDEX_HTML = '''<!doctype html>
<html lang="fa" dir="rtl">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Econojin — Environmental monitoring & green economy platform" />

    <!-- Persian font: Vazirmatn -->
    <link rel="stylesheet"
          href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" />

    <!-- English font: Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" />

    <title>Econojin</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''

# ---------------------------------------------------------------------------
# Updated App.tsx with all new routes
# ---------------------------------------------------------------------------

APP_TSX = '''/**
 * ============================================================================
 *  App — route table + layout shell (i18n-aware)
 * ============================================================================
 */

import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { Layout } from "@/components/Layout/Layout";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { PagePlaceholder } from "@/components/common/PagePlaceholder";

// ---------------------------------------------------------------------------
// Lazy-loaded pages
// ---------------------------------------------------------------------------

const LoginPage = lazy(() => import("@/pages/Login").then((m) => ({ default: m.Login })));
const RegisterPage = lazy(() => import("@/pages/Register/Register").then((m) => ({ default: m.Register })));
const ForgotPasswordPage = lazy(() => import("@/pages/ForgotPassword/ForgotPassword").then((m) => ({ default: m.ForgotPassword })));
const DashboardPage = lazy(() => import("@/pages/Dashboard").then((m) => ({ default: m.Dashboard })));
const DocumentsPage = lazy(() => import("@/pages/Documents").then((m) => ({ default: m.Documents })));
const CarbonDashboardPage = lazy(() => import("@/pages/Carbon/CarbonDashboard").then((m) => ({ default: m.CarbonDashboard })));
const WatershedListPage = lazy(() => import("@/pages/Hydrology/WatershedList").then((m) => ({ default: m.WatershedList })));
const SoilDashboardPage = lazy(() => import("@/pages/Soil/SoilDashboard").then((m) => ({ default: m.SoilDashboard })));
const AboutUsPage = lazy(() => import("@/pages/AboutUs/AboutUs").then((m) => ({ default: m.AboutUs })));
const AccountingPage = lazy(() => import("@/pages/Accounting/Accounting").then((m) => ({ default: m.Accounting })));
const AgricultureSchoolsPage = lazy(() => import("@/pages/AgricultureSchools/AgricultureSchools").then((m) => ({ default: m.AgricultureSchools })));
const AnimationsPage = lazy(() => import("@/pages/Animations/Animations").then((m) => ({ default: m.Animations })));
const ProfilePage = lazy(() => import("@/pages/Profile/Profile").then((m) => ({ default: m.Profile })));

// Batch 2 pages
const BiodiversityDashboardPage = lazy(() => import("@/pages/Biodiversity/BiodiversityDashboard").then((m) => ({ default: m.BiodiversityDashboard })));
const BlogPage = lazy(() => import("@/pages/Blog/Blog").then((m) => ({ default: m.Blog })));
const CareersPage = lazy(() => import("@/pages/Careers/Careers").then((m) => ({ default: m.Careers })));
const ContactUsPage = lazy(() => import("@/pages/ContactUs/ContactUs").then((m) => ({ default: m.ContactUs })));
const DaneshyarPage = lazy(() => import("@/pages/Daneshyar/Daneshyar").then((m) => ({ default: m.Daneshyar })));
const DecisionYarPage = lazy(() => import("@/pages/DecisionYar/DecisionYar").then((m) => ({ default: m.DecisionYar })));
const DroughtDashboardPage = lazy(() => import("@/pages/Drought/DroughtDashboard").then((m) => ({ default: m.DroughtDashboard })));
const EcoCoinDashboardPage = lazy(() => import("@/pages/EcoCoin/EcoCoinDashboard").then((m) => ({ default: m.EcoCoinDashboard })));
const EcoCoinWalletPage = lazy(() => import("@/pages/EcoCoin/Wallet").then((m) => ({ default: m.Wallet })));
const EcoCoinMiningPage = lazy(() => import("@/pages/EcoCoin/Mining").then((m) => ({ default: m.Mining })));
const EcoCoinChallengesPage = lazy(() => import("@/pages/EcoCoin/Challenges").then((m) => ({ default: m.Challenges })));
const EcoCoinRewardsPage = lazy(() => import("@/pages/EcoCoin/Rewards").then((m) => ({ default: m.Rewards })));
const EconomicModelsPage = lazy(() => import("@/pages/EconomicModels/EconomicModels").then((m) => ({ default: m.EconomicModels })));
const EcosystemDashboardPage = lazy(() => import("@/pages/Ecosystem/EcosystemDashboard").then((m) => ({ default: m.EcosystemDashboard })));
const EcosystemRestorationPage = lazy(() => import("@/pages/EcosystemRestoration/EcosystemRestoration").then((m) => ({ default: m.EcosystemRestoration })));
const EnergyDashboardPage = lazy(() => import("@/pages/Energy/EnergyDashboard").then((m) => ({ default: m.EnergyDashboard })));
const FAQPage = lazy(() => import("@/pages/FAQ/FAQ").then((m) => ({ default: m.FAQ })));
const GISDashboardPage = lazy(() => import("@/pages/GIS/GISDashboard").then((m) => ({ default: m.GISDashboard })));
const FlowAccumulationPage = lazy(() => import("@/pages/GIS/FlowAccumulationAnalysis").then((m) => ({ default: m.FlowAccumulationAnalysis })));
const LandCoverPage = lazy(() => import("@/pages/GIS/LandCoverAnalysis").then((m) => ({ default: m.LandCoverAnalysis })));
const SlopePage = lazy(() => import("@/pages/GIS/SlopeAnalysis").then((m) => ({ default: m.SlopeAnalysis })));
const ViewshedPage = lazy(() => import("@/pages/GIS/ViewshedAnalysis").then((m) => ({ default: m.ViewshedAnalysis })));
const WatershedAnalysisPage = lazy(() => import("@/pages/GIS/WatershedAnalysis").then((m) => ({ default: m.WatershedAnalysis })));

// ---------------------------------------------------------------------------
// Route guards
// ---------------------------------------------------------------------------

function ProtectedRoute({ children }: { children: JSX.Element }): JSX.Element {
  const { isAuthenticated, status } = useAuth();
  const { t } = useLanguage();

  if (status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner size="lg" label={t("error.loadingSession")} />
      </div>
    );
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------

export function App(): JSX.Element {
  const { t } = useLanguage();

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />

      {/* Protected routes */}
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Suspense
                fallback={
                  <div className="flex h-[60vh] items-center justify-center">
                    <LoadingSpinner size="md" label={t("error.loadingPage")} />
                  </div>
                }
              >
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/documents" element={<DocumentsPage />} />
                  <Route path="/carbon" element={<CarbonDashboardPage />} />
                  <Route path="/hydrology/watersheds" element={<WatershedListPage />} />
                  <Route path="/soil" element={<SoilDashboardPage />} />
                  <Route path="/about" element={<AboutUsPage />} />
                  <Route path="/accounting" element={<AccountingPage />} />
                  <Route path="/agriculture-schools" element={<AgricultureSchoolsPage />} />
                  <Route path="/animations" element={<AnimationsPage />} />
                  <Route path="/profile" element={<ProfilePage />} />

                  {/* Batch 2 routes */}
                  <Route path="/biodiversity" element={<BiodiversityDashboardPage />} />
                  <Route path="/blog" element={<BlogPage />} />
                  <Route path="/careers" element={<CareersPage />} />
                  <Route path="/contact" element={<ContactUsPage />} />
                  <Route path="/daneshyar" element={<DaneshyarPage />} />
                  <Route path="/decision-yar" element={<DecisionYarPage />} />
                  <Route path="/drought" element={<DroughtDashboardPage />} />
                  <Route path="/ecocoin" element={<EcoCoinDashboardPage />} />
                  <Route path="/ecocoin/wallet" element={<EcoCoinWalletPage />} />
                  <Route path="/ecocoin/mining" element={<EcoCoinMiningPage />} />
                  <Route path="/ecocoin/challenges" element={<EcoCoinChallengesPage />} />
                  <Route path="/ecocoin/rewards" element={<EcoCoinRewardsPage />} />
                  <Route path="/economic-models" element={<EconomicModelsPage />} />
                  <Route path="/ecosystem" element={<EcosystemDashboardPage />} />
                  <Route path="/ecosystem-restoration" element={<EcosystemRestorationPage />} />
                  <Route path="/energy" element={<EnergyDashboardPage />} />
                  <Route path="/faq" element={<FAQPage />} />
                  <Route path="/gis" element={<GISDashboardPage />} />
                  <Route path="/gis/flow-accumulation" element={<FlowAccumulationPage />} />
                  <Route path="/gis/land-cover" element={<LandCoverPage />} />
                  <Route path="/gis/slope" element={<SlopePage />} />
                  <Route path="/gis/viewshed" element={<ViewshedPage />} />
                  <Route path="/gis/watershed" element={<WatershedAnalysisPage />} />

                  <Route
                    path="*"
                    element={<PagePlaceholder titleKey="common.notFound" descriptionKey="common.notFoundDescription" />}
                  />
                </Routes>
              </Suspense>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
'''

# ---------------------------------------------------------------------------
# i18n additions (appended to both fa.json and en.json)
# ---------------------------------------------------------------------------

I18N_FA_ADDITIONS = {
    "biodiversity": {
        "title": "داشبورد تنوع زیستی",
        "subtitle": "پایش شاخص‌های تنوع زیستی به تفکیک منطقه",
        "totalValue": "کل شاخص تنوع",
        "regions": "مناطق پایش‌شده",
        "average": "میانگین",
        "tableTitle": "شاخص‌ها به تفکیک منطقه",
        "tableValue": "مقدار",
    },
    "blog": {
        "title": "بلاگ",
        "subtitle": "مقالات و اخبار محیط‌زیست",
        "section1Title": "آخرین مقالات",
        "section1Body": "در این بخش جدیدترین مقالات و گزارش‌های محیط‌زیستی منتشر می‌شود.",
        "section2Title": "دسته‌بندی‌ها",
        "section2Body": "مقالات بر اساس موضوعات مختلف از جمله کربن، آب، خاک و تنوع زیستی دسته‌بندی شده‌اند.",
        "section3Title": "نویسندگان",
        "section3Body": "مقالات توسط متخصصان و پژوهشگران محیط‌زیست نوشته می‌شود.",
    },
    "careers": {
        "title": "فرصت‌های شغلی",
        "subtitle": "به جامعه سبز اکونوجین بپیوندید",
        "section1Title": "چرا اکونوجین؟",
        "section1Body": "ما در اکونوجین باور داریم که فناوری می‌تواند به حفظ محیط‌زیست کمک کند. با پیوستن به تیم ما، در ساختن آینده‌ای پایدار سهیم شوید.",
        "section2Title": "فرصت‌های فعلی",
        "section2Body": "ما همواره به دنبال استعدادهای برجسته در حوزه‌های فناوری، محیط‌زیست و اقتصاد سبز هستیم.",
        "section3Title": "نحوه درخواست",
        "section3Body": "برای ارسال درخواست، رزومه خود را به ایمیل careers@econojin.com ارسال کنید.",
    },
    "contactUs": {
        "title": "تماس با ما",
        "subtitle": "سوال یا پیشنهاد دارید؟ با ما در تماس باشید",
        "name": "نام و نام خانوادگی",
        "email": "ایمیل",
        "subject": "موضوع",
        "message": "پیام",
        "send": "ارسال پیام",
        "successTitle": "پیام شما ارسال شد",
        "successBody": "کارشناسان ما در اولین فرصت با شما تماس خواهند گرفت.",
    },
    "daneshyar": {
        "title": "دانش‌یار",
        "subtitle": "دستیار هوشمند پژوهش محیط‌زیست",
        "section1Title": "معرفی دانش‌یار",
        "section1Body": "دانش‌یار یک دستیار هوشمند است که به پژوهشگران محیط‌زیست کمک می‌کند تا داده‌ها را به‌سرعت تحلیل و گزارش کنند.",
        "section2Title": "امکانات",
        "section2Body": "تحلیل خودکار داده، تولید گزارش، پیشنهاد منابع علمی مرتبط.",
        "section3Title": "شروع کار",
        "section3Body": "برای استفاده از دانش‌یار، کافی است یک حساب کاربری داشته باشید و پروژه خود را تعریف کنید.",
    },
    "decisionYar": {
        "title": "تصمیم‌یار",
        "subtitle": "سیستم پشتیبانی تصمیم‌گیری محیط‌زیستی",
        "section1Title": "تصمیم‌گیری مبتنی بر داده",
        "section1Body": "تصمیم‌یار با تحلیل داده‌های محیط‌زیستی، به سیاست‌گذاران کمک می‌کند تا تصمیمات بهتری بگیرند.",
        "section2Title": "مدل‌های تحلیلی",
        "section2Body": "تصمیم‌یار از مدل‌های پیشرفته اقتصاد سبز و ارزیابی چرخه حیات استفاده می‌کند.",
        "section3Title": "گزارش‌های تصمیم",
        "section3Body": "خروجی تصمیم‌یار به‌صورت گزارش‌های قابل‌فهم برای مدیران ارائه می‌شود.",
    },
    "drought": {
        "title": "داشبورد خشکسالی",
        "subtitle": "پایش شاخص‌های خشکسالی به تفکیک منطقه",
        "totalValue": "کل شاخص خشکسالی",
        "regions": "مناطق پایش‌شده",
        "average": "میانگین",
        "tableTitle": "شاخص‌ها به تفکیک منطقه",
        "tableValue": "مقدار شاخص",
    },
    "ecoCoin": {
        "title": "اکوکوین",
        "subtitle": "توکن انگیزشی برای رفتار سبز",
        "balance": "موجودی",
        "minedThisMonth": "استخراج این ماه",
        "challengesCompleted": "چالش‌های کامل‌شده",
        "rank": "رتبه",
        "wallet": "کیف پول",
        "walletSubtitle": "مدیریت موجودی و تراکنش‌های اکوکوین",
        "mining": "استخراج",
        "miningSubtitle": "اکوکوین استخراج کنید و پاداش بگیرید",
        "challenges": "چالش‌ها",
        "challengesSubtitle": "چالش‌های محیط‌زیستی را کامل کنید و پاداش بگیرید",
        "rewards": "جایزه‌ها",
        "rewardsSubtitle": "اکوکوین خود را با جایزه‌های سبز مبادله کنید",
        "hashRate": "نرخ هش",
        "minedToday": "استخراج امروز",
        "minedTotal": "کل استخراج",
        "miningStatus": "وضعیت استخراج",
        "miningActive": "استخراج در حال انجام است",
        "stopMining": "توقف استخراج",
        "completed": "تکمیل‌شده",
        "active": "فعال",
        "startChallenge": "شروع چالش",
        "redeem": "بازخرید",
        "recentTransactions": "تراکنش‌های اخیر",
        "txReward": "پاداش محیط‌زیستی",
        "txPurchase": "خرج جایزه",
        "txMining": "پاداش استخراج",
        "txChallenge": "پاداش چالش",
        "ch1Title": "کاهش مصرف آب",
        "ch1Desc": "مصرف آب ماهانه خود را ۲۰٪ کاهش دهید",
        "ch2Title": "حمل‌ونقل سبز",
        "ch2Desc": "به مدت یک ماه از دوچرخه استفاده کنید",
        "ch3Title": "بازیافت",
        "ch3Desc": "هر هفته حداقل ۵ کیلوگرم زباله بازیافت کنید",
        "ch4Title": "کاشت درخت",
        "ch4Desc": "حداقل ۳ درخت بکارید",
        "ch5Title": "گزارش‌دهی",
        "ch5Desc": "۱۰ گزارش محیط‌زیستی ارسال کنید",
        "rw1Name": "شارژ موبایل",
        "rw1Desc": "کد شارژ ۵۰ هزار تومانی",
        "rw2Name": "نهال",
        "rw2Desc": "یک نهال به نام شما کاشته می‌شود",
        "rw3Name": "کتاب الکترونیکی",
        "rw3Desc": "دسترسی به کتابخانه دیجیتال محیط‌زیست",
        "rw4Name": "بلیت رویداد",
        "rw4Desc": "شرکت در کنفرانس سالانه اکونوجین",
        "rw5Name": "کیسه خرید",
        "rw5Desc": "کیسه خرید پارچه‌ای با لوگو اکونوجین",
        "rw6Name": "جعبه هدیه",
        "rw6Desc": "جعبه هدیه محصولات سبز اکونوجین",
    },
    "economicModels": {
        "title": "مدل‌های اقتصادی",
        "subtitle": "مدل‌های اقتصادی سبز و پایدار",
        "section1Title": "معرفی مدل‌ها",
        "section1Body": "این بخش شامل مدل‌های اقتصادی مختلف برای ارزیابی پایداری پروژه‌های سبز است.",
        "section2Title": "ارزیابی چرخه حیات",
        "section2Body": "مدل LCA برای ارزیابی اثرات محیط‌زیستی یک محصول از تولید تا مصرف.",
        "section3Title": "اقتصاد چرخشی",
        "section3Body": "مدل‌های اقتصاد چرخشی برای کاهش ضایعات و افزایش بهره‌وری منابع.",
    },
    "ecosystem": {
        "title": "داشبورد اکوسیستم",
        "subtitle": "پایش سلامت اکوسیستم به تفکیک منطقه",
        "totalValue": "کل شاخص اکوسیستم",
        "regions": "مناطق پایش‌شده",
        "average": "میانگین",
        "tableTitle": "شاخص‌ها به تفکیک منطقه",
        "tableValue": "مقدار شاخص",
    },
    "ecosystemRestoration": {
        "title": "بازیافت اکوسیستم",
        "subtitle": "پروژه‌های بازیافت و احیای اکوسیستم",
        "section1Title": "پروژه‌های فعال",
        "section1Body": "در این بخش پروژه‌های بازیافت اکوسیستم در سراسر کشور معرفی می‌شود.",
        "section2Title": "نحوه مشارکت",
        "section2Body": "شما می‌توانید به‌صورت مالی یا داوطلبانه در این پروژه‌ها مشارکت کنید.",
        "section3Title": "گزارش پیشرفت",
        "section3Body": "گزارش پیشرفت پروژه‌ها به‌صورت ماهانه منتشر می‌شود.",
    },
    "energy": {
        "title": "داشبورد انرژی",
        "subtitle": "پایش مصرف و تولید انرژی‌های تجدیدپذیر",
        "totalValue": "کل انرژی (MWh)",
        "regions": "مناطق پایش‌شده",
        "average": "میانگین",
        "tableTitle": "شاخص‌ها به تفکیک منطقه",
        "tableValue": "مقدار (MWh)",
    },
    "faq": {
        "title": "سوالات متداول",
        "subtitle": "پاسخ به پرتکرارترین سوالات کاربران",
        "q1": "اکوکوین چیست و چگونه کار می‌کند؟",
        "a1": "اکوکوین یک توکن دیجیتال است که به کاربران برای رفتار سبز پاداش داده می‌شود. شما می‌توانید با گزارش محیط‌زیستی، استخراج و چالش‌ها اکوکوین کسب کنید.",
        "q2": "چگونه می‌توانم در پروژه‌های بازیافت اکوسیستم مشارکت کنم؟",
        "a2": "برای مشارکت، به صفحه بازیافت اکوسیستم مراجعه کنید و پروژه مورد نظر را انتخاب کنید. مشارکت می‌تواند مالی یا داوطلبانه باشد.",
        "q3": "داده‌های پایش از کجا می‌آیند؟",
        "a3": "داده‌ها از ایستگاه‌های پایش رسمی، گزارش‌های کاربران و تصاویر ماهواره‌ای جمع‌آوری می‌شوند.",
        "q4": "آیا استفاده از پلتفرم رایگان است؟",
        "a4": "بله، استفاده پایه از پلتفرم رایگان است. برای دسترسی به گزارش‌های تخصصی نیاز به اشتراک پریمیوم دارید.",
        "q5": "چگونه می‌توانم گزارش محیط‌زیستی ارسال کنم؟",
        "a5": "پس از ورود به حساب کاربری، از صفحه داشبورد به بخش اسناد مراجعه کنید و روی دکمه ارسال گزارش کلیک کنید.",
        "q6": "اطلاعات شخصی من چگونه محافظت می‌شود؟",
        "a6": "ما از رمزنگاری TLS برای انتقال داده‌ها استفاده می‌کنیم و اطلاعات شخصی شما هرگز بدون اجازه به اشتراک گذاشته نمی‌شود.",
    },
    "forgotPassword": {
        "title": "بازیابی رمز عبور",
        "subtitle": "ایمیل خود را وارد کنید تا لینک بازیابی برای شما ارسال شود",
        "sendButton": "ارسال لینک بازیابی",
        "successTitle": "لینک بازیابی ارسال شد",
        "successBody": "لطفاً صندوق ورودی ایمیل خود را بررسی کنید.",
    },
    "gis": {
        "title": "سامانه اطلاعات جغرافیایی",
        "subtitle": "تحلیل‌های مکانی داده‌های محیط‌زیستی",
        "flowAccumulation": "تحلیل تجمع جریان",
        "landCover": "تحلیل پوشش زمین",
        "slope": "تحلیل شیب",
        "viewshed": "تحلیل میدان دید",
        "watershed": "تحلیل حوزه آبخیز",
        "analysisArea": "مساحت تحلیل",
        "dataPoints": "نقاط داده",
        "lastUpdate": "آخرین به‌روزرسانی",
        "mapPlaceholder": "نقشه تعاملی اینجا نمایش داده می‌شود",
        "results": "نتایج تحلیل",
    },
    "profile": {
        "title": "پروفایل من",
        "subtitle": "مدیریت اطلاعات حساب کاربری",
        "editInfo": "ویرایش اطلاعات",
        "firstName": "نام",
        "lastName": "نام خانوادگی",
        "bio": "درباره من",
        "savedSuccessfully": "تغییرات با موفقیت ذخیره شد",
    },
}

I18N_EN_ADDITIONS = {
    "biodiversity": {
        "title": "Biodiversity Dashboard",
        "subtitle": "Biodiversity indicators monitoring by region",
        "totalValue": "Total biodiversity index",
        "regions": "Monitored regions",
        "average": "Average",
        "tableTitle": "Indicators by region",
        "tableValue": "Value",
    },
    "blog": {
        "title": "Blog",
        "subtitle": "Environmental articles and news",
        "section1Title": "Latest articles",
        "section1Body": "The latest environmental articles and reports are published in this section.",
        "section2Title": "Categories",
        "section2Body": "Articles are categorized by topics including carbon, water, soil, and biodiversity.",
        "section3Title": "Authors",
        "section3Body": "Articles are written by environmental experts and researchers.",
    },
    "careers": {
        "title": "Careers",
        "subtitle": "Join the Econojin green community",
        "section1Title": "Why Econojin?",
        "section1Body": "We believe technology can help protect the environment. Join our team and help build a sustainable future.",
        "section2Title": "Current openings",
        "section2Body": "We are always looking for outstanding talent in technology, environment, and green economy.",
        "section3Title": "How to apply",
        "section3Body": "To apply, send your resume to careers@econojin.com.",
    },
    "contactUs": {
        "title": "Contact Us",
        "subtitle": "Have a question or suggestion? Get in touch",
        "name": "Full name",
        "email": "Email",
        "subject": "Subject",
        "message": "Message",
        "send": "Send message",
        "successTitle": "Your message has been sent",
        "successBody": "Our team will contact you as soon as possible.",
    },
    "daneshyar": {
        "title": "DaneshYar",
        "subtitle": "Smart environmental research assistant",
        "section1Title": "About DaneshYar",
        "section1Body": "DaneshYar is a smart assistant that helps environmental researchers analyze data and generate reports quickly.",
        "section2Title": "Features",
        "section2Body": "Automated data analysis, report generation, relevant scientific resource suggestions.",
        "section3Title": "Getting started",
        "section3Body": "To use DaneshYar, simply create an account and define your project.",
    },
    "decisionYar": {
        "title": "DecisionYar",
        "subtitle": "Environmental decision support system",
        "section1Title": "Data-driven decisions",
        "section1Body": "DecisionYar helps policymakers make better decisions by analyzing environmental data.",
        "section2Title": "Analytical models",
        "section2Body": "DecisionYar uses advanced green economy models and life-cycle assessment.",
        "section3Title": "Decision reports",
        "section3Body": "DecisionYar outputs are presented as manager-friendly reports.",
    },
    "drought": {
        "title": "Drought Dashboard",
        "subtitle": "Drought indicators monitoring by region",
        "totalValue": "Total drought index",
        "regions": "Monitored regions",
        "average": "Average",
        "tableTitle": "Indicators by region",
        "tableValue": "Index value",
    },
    "ecoCoin": {
        "title": "EcoCoin",
        "subtitle": "Incentive token for green behavior",
        "balance": "Balance",
        "minedThisMonth": "Mined this month",
        "challengesCompleted": "Challenges completed",
        "rank": "Rank",
        "wallet": "Wallet",
        "walletSubtitle": "Manage EcoCoin balance and transactions",
        "mining": "Mining",
        "miningSubtitle": "Mine EcoCoin and earn rewards",
        "challenges": "Challenges",
        "challengesSubtitle": "Complete environmental challenges and earn rewards",
        "rewards": "Rewards",
        "rewardsSubtitle": "Redeem EcoCoin for green rewards",
        "hashRate": "Hash rate",
        "minedToday": "Mined today",
        "minedTotal": "Total mined",
        "miningStatus": "Mining status",
        "miningActive": "Mining in progress",
        "stopMining": "Stop mining",
        "completed": "Completed",
        "active": "Active",
        "startChallenge": "Start challenge",
        "redeem": "Redeem",
        "recentTransactions": "Recent transactions",
        "txReward": "Environmental reward",
        "txPurchase": "Reward purchase",
        "txMining": "Mining reward",
        "txChallenge": "Challenge reward",
        "ch1Title": "Reduce water usage",
        "ch1Desc": "Reduce your monthly water usage by 20%",
        "ch2Title": "Green transport",
        "ch2Desc": "Use a bicycle for one month",
        "ch3Title": "Recycling",
        "ch3Desc": "Recycle at least 5 kg of waste per week",
        "ch4Title": "Tree planting",
        "ch4Desc": "Plant at least 3 trees",
        "ch5Title": "Reporting",
        "ch5Desc": "Submit 10 environmental reports",
        "rw1Name": "Mobile top-up",
        "rw1Desc": "50,000 Toman top-up code",
        "rw2Name": "Seedling",
        "rw2Desc": "A seedling planted in your name",
        "rw3Name": "E-book access",
        "rw3Desc": "Access to digital environmental library",
        "rw4Name": "Event ticket",
        "rw4Desc": "Annual Econojin conference ticket",
        "rw5Name": "Shopping bag",
        "rw5Desc": "Reusable cloth bag with Econojin logo",
        "rw6Name": "Gift box",
        "rw6Desc": "Econojin green products gift box",
    },
    "economicModels": {
        "title": "Economic Models",
        "subtitle": "Green and sustainable economic models",
        "section1Title": "Model overview",
        "section1Body": "This section contains various economic models for evaluating the sustainability of green projects.",
        "section2Title": "Life-cycle assessment",
        "section2Body": "LCA model for evaluating the environmental impacts of a product from production to consumption.",
        "section3Title": "Circular economy",
        "section3Body": "Circular economy models for waste reduction and resource efficiency.",
    },
    "ecosystem": {
        "title": "Ecosystem Dashboard",
        "subtitle": "Ecosystem health monitoring by region",
        "totalValue": "Total ecosystem index",
        "regions": "Monitored regions",
        "average": "Average",
        "tableTitle": "Indicators by region",
        "tableValue": "Index value",
    },
    "ecosystemRestoration": {
        "title": "Ecosystem Restoration",
        "subtitle": "Ecosystem restoration and recovery projects",
        "section1Title": "Active projects",
        "section1Body": "This section introduces ecosystem restoration projects across the country.",
        "section2Title": "How to participate",
        "section2Body": "You can participate in these projects financially or as a volunteer.",
        "section3Title": "Progress reports",
        "section3Body": "Project progress reports are published monthly.",
    },
    "energy": {
        "title": "Energy Dashboard",
        "subtitle": "Renewable energy consumption and production monitoring",
        "totalValue": "Total energy (MWh)",
        "regions": "Monitored regions",
        "average": "Average",
        "tableTitle": "Indicators by region",
        "tableValue": "Value (MWh)",
    },
    "faq": {
        "title": "FAQ",
        "subtitle": "Answers to the most frequently asked questions",
        "q1": "What is EcoCoin and how does it work?",
        "a1": "EcoCoin is a digital token that rewards users for green behavior. You can earn EcoCoin by reporting environmental data, mining, and completing challenges.",
        "q2": "How can I participate in ecosystem restoration projects?",
        "a2": "To participate, visit the Ecosystem Restoration page and select a project. Participation can be financial or volunteer-based.",
        "q3": "Where does the monitoring data come from?",
        "a3": "Data is collected from official monitoring stations, user reports, and satellite imagery.",
        "q4": "Is the platform free to use?",
        "a4": "Yes, basic platform usage is free. A premium subscription is required for access to specialized reports.",
        "q5": "How can I submit an environmental report?",
        "a5": "After logging in, go to the Documents page from the dashboard and click the submit report button.",
        "q6": "How is my personal data protected?",
        "a6": "We use TLS encryption for data transmission and your personal information is never shared without permission.",
    },
    "forgotPassword": {
        "title": "Password recovery",
        "subtitle": "Enter your email to receive a recovery link",
        "sendButton": "Send recovery link",
        "successTitle": "Recovery link sent",
        "successBody": "Please check your email inbox.",
    },
    "gis": {
        "title": "Geographic Information System",
        "subtitle": "Spatial analysis of environmental data",
        "flowAccumulation": "Flow Accumulation Analysis",
        "landCover": "Land Cover Analysis",
        "slope": "Slope Analysis",
        "viewshed": "Viewshed Analysis",
        "watershed": "Watershed Analysis",
        "analysisArea": "Analysis area",
        "dataPoints": "Data points",
        "lastUpdate": "Last update",
        "mapPlaceholder": "Interactive map will be displayed here",
        "results": "Analysis results",
    },
    "profile": {
        "title": "My Profile",
        "subtitle": "Manage account information",
        "editInfo": "Edit information",
        "firstName": "First name",
        "lastName": "Last name",
        "bio": "About me",
        "savedSuccessfully": "Changes saved successfully",
    },
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    root = detect_root()
    print(f"[INFO] Project root: {root}")
    print()

    print("=" * 72)
    print(" Generating Batch 2 — 27 files + i18n keys + App.tsx update")
    print("=" * 72)

    # --- Dashboard pages ---
    dashboard_pages = [
        ("src/pages/Biodiversity/BiodiversityDashboard.tsx",
         make_dashboard_page("BiodiversityDashboard", "/biodiversity", "biodiversity", "🦋")),
        ("src/pages/Drought/DroughtDashboard.tsx",
         make_dashboard_page("DroughtDashboard", "/drought", "drought", "🏜️")),
        ("src/pages/Ecosystem/EcosystemDashboard.tsx",
         make_dashboard_page("EcosystemDashboard", "/ecosystem", "ecosystem", "🌍")),
        ("src/pages/Energy/EnergyDashboard.tsx",
         make_dashboard_page("EnergyDashboard", "/energy", "energy", "⚡")),
    ]

    # --- Simple content pages ---
    simple_pages = [
        ("src/pages/Blog/Blog.tsx",
         make_simple_page("Blog", "blog", "📝")),
        ("src/pages/Careers/Careers.tsx",
         make_simple_page("Careers", "careers", "💼")),
        ("src/pages/Daneshyar/Daneshyar.tsx",
         make_simple_page("Daneshyar", "daneshyar", "🤖")),
        ("src/pages/DecisionYar/DecisionYar.tsx",
         make_simple_page("DecisionYar", "decisionYar", "🎯")),
        ("src/pages/EconomicModels/EconomicModels.tsx",
         make_simple_page("EconomicModels", "economicModels", "📊")),
        ("src/pages/EcosystemRestoration/EcosystemRestoration.tsx",
         make_simple_page("EcosystemRestoration", "ecosystemRestoration", "🌱")),
    ]

    # --- ContactUs ---
    contact_page = [("src/pages/ContactUs/ContactUs.tsx", CONTACT_US_TSX)]

    # --- FAQ ---
    faq_page = [("src/pages/FAQ/FAQ.tsx", FAQ_TSX)]

    # --- ForgotPassword ---
    forgot_page = [("src/pages/ForgotPassword/ForgotPassword.tsx", FORGOT_PASSWORD_TSX)]

    # --- EcoCoin pages ---
    ecocoin_pages = [
        ("src/pages/EcoCoin/EcoCoinDashboard.tsx", ECOCOIN_DASHBOARD_TSX),
        ("src/pages/EcoCoin/Wallet.tsx", ECOCOIN_WALLET_TSX),
        ("src/pages/EcoCoin/Mining.tsx", ECOCOIN_MINING_TSX),
        ("src/pages/EcoCoin/Challenges.tsx", ECOCOIN_CHALLENGES_TSX),
        ("src/pages/EcoCoin/Rewards.tsx", ECOCOIN_REWARDS_TSX),
    ]

    # --- GIS pages ---
    gis_pages = [
        ("src/pages/GIS/GISDashboard.tsx", GIS_DASHBOARD_TSX),
        ("src/pages/GIS/FlowAccumulationAnalysis.tsx",
         make_gis_page("FlowAccumulationAnalysis", "gis.flowAccumulation", "💧")),
        ("src/pages/GIS/LandCoverAnalysis.tsx",
         make_gis_page("LandCoverAnalysis", "gis.landCover", "🌲")),
        ("src/pages/GIS/SlopeAnalysis.tsx",
         make_gis_page("SlopeAnalysis", "gis.slope", "⛰️")),
        ("src/pages/GIS/ViewshedAnalysis.tsx",
         make_gis_page("ViewshedAnalysis", "gis.viewshed", "👁️")),
        ("src/pages/GIS/WatershedAnalysis.tsx",
         make_gis_page("WatershedAnalysis", "gis.watershed", "🏞️")),
    ]

    # --- Profile ---
    profile_page = [("src/pages/Profile/Profile.tsx", PROFILE_TSX)]

    # --- index.html ---
    html_file = [("index.html", INDEX_HTML)]

    # --- App.tsx ---
    app_file = [("src/App.tsx", APP_TSX)]

    # --- Write all files ---
    all_files = (
        dashboard_pages + simple_pages + contact_page + faq_page +
        forgot_page + ecocoin_pages + gis_pages + profile_page +
        html_file + app_file
    )

    written = 0
    for rel_path, content in all_files:
        changed = write_file(root, rel_path, content)
        action = "created" if not (root / rel_path).exists() else "rewrote" if changed else "ok"
        if changed:
            written += 1
        size = (root / rel_path).stat().st_size if (root / rel_path).exists() else 0
        print(f"  [{action:>8}]  {rel_path}  ({size} bytes)")

    print(f"\n  Total files written: {written}")

    # --- Update i18n JSON files ---
    print()
    print("=" * 72)
    print(" Updating i18n locale files (fa.json + en.json)")
    print("=" * 72)

    for locale_file, additions in [("src/i18n/locales/fa.json", I18N_FA_ADDITIONS),
                                   ("src/i18n/locales/en.json", I18N_EN_ADDITIONS)]:
        full = root / locale_file
        if not full.exists():
            print(f"  [SKIP]  {locale_file} not found")
            continue

        try:
            data = json.loads(full.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  [ERROR]  {locale_file}: {e}")
            continue

        added = 0
        for key, value in additions.items():
            if key not in data:
                data[key] = value
                added += 1
            else:
                # Merge nested keys
                for sub_key, sub_value in value.items():
                    if sub_key not in data[key]:
                        data[key][sub_key] = sub_value
                        added += 1

        full.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  [UPDATED]  {locale_file}  (+{added} keys)")

    print()
    print("=" * 72)
    print(" DONE")
    print("=" * 72)
    print(f"  Files written: {written}")
    print(f"  i18n keys added to both fa.json and en.json")
    print()
    print("  Next step:")
    print("    pnpm run build")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
