#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Legal Pages Complete Setup
======================================
Creates LegalLayout, Terms, Privacy pages + updates fa.json
Uses Python for proper UTF-8 handling.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_SRC = PROJECT_ROOT / "apps" / "web" / "src"

# ============================================================================
# File Paths
# ============================================================================
LEGAL_LAYOUT_PATH = WEB_SRC / "components" / "Legal" / "LegalLayout.tsx"
TERMS_PATH = WEB_SRC / "pages" / "Legal" / "Terms.tsx"
PRIVACY_PATH = WEB_SRC / "pages" / "Legal" / "Privacy.tsx"
FA_JSON_PATH = WEB_SRC / "i18n" / "locales" / "fa.json"

# ============================================================================
# 1. LegalLayout Component (Shortened for brevity, fully functional)
# ============================================================================
LEGAL_LAYOUT_CONTENT = '''/**
 * ============================================================================
 *  LegalLayout.tsx — Shared layout component for legal pages
 * ============================================================================
 */
import { useState, useEffect, ReactNode } from "react";
import { Link } from "react-router-dom";
import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/lib/utils";

export interface TableOfContentsItem { id: string; title: string; level?: number; }
export interface LegalLayoutProps { title: string; subtitle?: string; lastUpdated: string; toc: TableOfContentsItem[]; children: ReactNode; }

export function LegalLayout({ title, subtitle, lastUpdated, toc, children }: LegalLayoutProps): JSX.Element {
  const { dir, t } = useLanguage();
  const [activeSection, setActiveSection] = useState<string>("");
  const [isTocOpen, setIsTocOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const sections = toc.map((item) => document.getElementById(item.id));
      const scrollPosition = window.scrollY + 150;
      for (let i = sections.length - 1; i >= 0; i--) {
        const section = sections[i];
        if (section && section.offsetTop <= scrollPosition) { setActiveSection(toc[i].id); break; }
      }
    };
    window.addEventListener("scroll", handleScroll);
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, [toc]);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      window.scrollTo({ top: element.getBoundingClientRect().top + window.scrollY - 100, behavior: "smooth" });
      setIsTocOpen(false);
    }
  };

  return (
    <div dir={dir} className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-emerald-50/30">
      <header className="relative overflow-hidden bg-gradient-to-br from-emerald-900 via-emerald-800 to-teal-900 text-white">
        <div className="relative mx-auto max-w-5xl px-6 py-16 sm:py-20 lg:px-8">
          <Link to="/" className="mb-8 inline-flex items-center gap-2 text-sm text-emerald-100 transition hover:text-white">
            <svg className="h-4 w-4 rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
            {t("legal.backToHome")}
          </Link>
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-6xl">{title}</h1>
          {subtitle && <p className="mt-4 max-w-2xl text-lg text-emerald-100 leading-relaxed">{subtitle}</p>}
          <div className="mt-6 flex flex-wrap items-center gap-4 text-sm text-emerald-200">
            <span className="inline-flex items-center gap-2">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
              {t("legal.lastUpdated")}: {lastUpdated}
            </span>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-12 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-[280px_1fr]">
          <aside className="hidden lg:block">
            <div className="sticky top-24">
              <h3 className="mb-4 text-xs font-bold uppercase tracking-wider text-gray-500">{t("legal.tableOfContents")}</h3>
              <nav className="space-y-1 border-s-2 border-gray-100 ps-4">
                {toc.map((item) => (
                  <button key={item.id} onClick={() => scrollToSection(item.id)} className={cn("block w-full text-start text-sm transition-all", activeSection === item.id ? "border-s-2 -ms-[18px] border-emerald-500 ps-4 font-semibold text-emerald-700" : "text-gray-600 hover:text-emerald-600")}>
                    {item.title}
                  </button>
                ))}
              </nav>
              <button onClick={() => window.print()} className="mt-8 inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" /></svg>
                {t("legal.printDocument")}
              </button>
            </div>
          </aside>
          <main className="min-w-0 prose prose-emerald max-w-none">{children}</main>
        </div>
      </div>
      <footer className="border-t border-gray-200 bg-white py-8">
        <div className="mx-auto max-w-5xl px-6 text-center text-sm text-gray-500 lg:px-8">
          <p>{t("legal.footerText")}</p>
          <p className="mt-2">© {new Date().getFullYear()} {t("home.nav.brand")}. {t("home.footer.rights")}</p>
        </div>
      </footer>
    </div>
  );
}

export function LegalSection({ id, icon, title, children }: { id: string; icon: ReactNode; title: string; children: ReactNode }): JSX.Element {
  return (
    <section id={id} className="scroll-mt-24 mb-12">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 text-xl">{icon}</div>
        <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">{title}</h2>
      </div>
      <div className="space-y-4 text-gray-700 leading-relaxed">{children}</div>
    </section>
  );
}

export function LegalCallout({ type = "info", title, children }: { type?: "info" | "warning" | "success" | "principle"; title: string; children: ReactNode }): JSX.Element {
  const styles = { info: "bg-blue-50 border-blue-200 text-blue-900", warning: "bg-amber-50 border-amber-200 text-amber-900", success: "bg-emerald-50 border-emerald-200 text-emerald-900", principle: "bg-gradient-to-br from-emerald-50 to-teal-50 border-emerald-300 text-emerald-900" };
  const icons = { info: "ℹ️", warning: "⚠️", success: "✅", principle: "🌿" };
  return (
    <div className={cn("my-6 rounded-xl border-2 p-5", styles[type])}>
      <div className="mb-2 flex items-center gap-2 font-bold"><span className="text-xl">{icons[type]}</span><span>{title}</span></div>
      <div className="text-sm leading-relaxed">{children}</div>
    </div>
  );
}
'''

# ============================================================================
# 2. Terms Page
# ============================================================================
TERMS_CONTENT = '''/**
 * ============================================================================
 *  Terms.tsx — Terms of Service (Human-Centered & Eco-Friendly)
 * ============================================================================
 */
import { LegalLayout, LegalSection, LegalCallout } from "@/components/Legal/LegalLayout";
import { useLanguage } from "@/hooks/useLanguage";

export function Terms(): JSX.Element {
  const { t } = useLanguage();
  const toc = [
    { id: "preamble", title: t("terms.toc.preamble") }, { id: "values", title: t("terms.toc.values") },
    { id: "acceptance", title: t("terms.toc.acceptance") }, { id: "user-rights", title: t("terms.toc.userRights") },
    { id: "user-obligations", title: t("terms.toc.userObligations") }, { id: "platform-commitments", title: t("terms.toc.platformCommitments") },
    { id: "environmental", title: t("terms.toc.environmental") }, { id: "intellectual-property", title: t("terms.toc.intellectualProperty") },
    { id: "liability", title: t("terms.toc.liability") }, { id: "termination", title: t("terms.toc.termination") },
    { id: "dispute-resolution", title: t("terms.toc.disputeResolution") }, { id: "governing-law", title: t("terms.toc.governingLaw") },
    { id: "amendments", title: t("terms.toc.amendments") }, { id: "contact", title: t("terms.toc.contact") },
  ];

  return (
    <LegalLayout title={t("terms.title")} subtitle={t("terms.subtitle")} lastUpdated={t("terms.lastUpdated")} toc={toc}>
      <LegalSection id="preamble" icon="📜" title={t("terms.sections.preamble.title")}>
        <p>{t("terms.sections.preamble.p1")}</p><p>{t("terms.sections.preamble.p2")}</p>
        <LegalCallout type="principle" title={t("terms.sections.preamble.calloutTitle")}>{t("terms.sections.preamble.calloutText")}</LegalCallout>
      </LegalSection>
      <LegalSection id="values" icon="🌍" title={t("terms.sections.values.title")}>
        <p>{t("terms.sections.values.intro")}</p>
        <ul className="list-none space-y-3 ps-0">
          {[{ icon: "🤝", title: t("terms.sections.values.humanDignity"), desc: t("terms.sections.values.humanDignityDesc") },
            { icon: "🌱", title: t("terms.sections.values.ecoStewardship"), desc: t("terms.sections.values.ecoStewardshipDesc") },
            { icon: "⚖️", title: t("terms.sections.values.transparency"), desc: t("terms.sections.values.transparencyDesc") },
            { icon: "🌐", title: t("terms.sections.values.inclusivity"), desc: t("terms.sections.values.inclusivityDesc") }
          ].map((v, i) => <li key={i} className="flex gap-3"><span className="text-xl">{v.icon}</span><div><strong>{v.title}</strong><p className="mt-1 text-sm">{v.desc}</p></div></li>)}
        </ul>
      </LegalSection>
      <LegalSection id="acceptance" icon="✅" title={t("terms.sections.acceptance.title")}>
        <p>{t("terms.sections.acceptance.p1")}</p><p>{t("terms.sections.acceptance.p2")}</p>
      </LegalSection>
      <LegalSection id="user-rights" icon="🛡️" title={t("terms.sections.userRights.title")}>
        <p>{t("terms.sections.userRights.intro")}</p>
        <ol className="list-decimal space-y-2 ps-6">
          <li>{t("terms.sections.userRights.right1")}</li><li>{t("terms.sections.userRights.right2")}</li>
          <li>{t("terms.sections.userRights.right3")}</li><li>{t("terms.sections.userRights.right4")}</li>
          <li>{t("terms.sections.userRights.right5")}</li><li>{t("terms.sections.userRights.right6")}</li>
        </ol>
        <LegalCallout type="info" title={t("terms.sections.userRights.calloutTitle")}>{t("terms.sections.userRights.calloutText")}</LegalCallout>
      </LegalSection>
      <LegalSection id="user-obligations" icon="📋" title={t("terms.sections.userObligations.title")}>
        <p>{t("terms.sections.userObligations.intro")}</p>
        <ul className="list-disc space-y-2 ps-6">
          <li>{t("terms.sections.userObligations.obligation1")}</li><li>{t("terms.sections.userObligations.obligation2")}</li>
          <li>{t("terms.sections.userObligations.obligation3")}</li><li>{t("terms.sections.userObligations.obligation4")}</li>
          <li>{t("terms.sections.userObligations.obligation5")}</li>
        </ul>
      </LegalSection>
      <LegalSection id="platform-commitments" icon="🤝" title={t("terms.sections.platformCommitments.title")}>
        <p>{t("terms.sections.platformCommitments.intro")}</p>
        <ul className="list-disc space-y-2 ps-6">
          <li>{t("terms.sections.platformCommitments.commitment1")}</li><li>{t("terms.sections.platformCommitments.commitment2")}</li>
          <li>{t("terms.sections.platformCommitments.commitment3")}</li><li>{t("terms.sections.platformCommitments.commitment4")}</li>
        </ul>
      </LegalSection>
      <LegalSection id="environmental" icon="🌿" title={t("terms.sections.environmental.title")}>
        <p>{t("terms.sections.environmental.intro")}</p>
        <LegalCallout type="success" title={t("terms.sections.environmental.calloutTitle")}>{t("terms.sections.environmental.calloutText")}</LegalCallout>
        <ul className="list-disc space-y-2 ps-6">
          <li>{t("terms.sections.environmental.commitment1")}</li><li>{t("terms.sections.environmental.commitment2")}</li>
          <li>{t("terms.sections.environmental.commitment3")}</li><li>{t("terms.sections.environmental.commitment4")}</li>
        </ul>
      </LegalSection>
      <LegalSection id="intellectual-property" icon="©️" title={t("terms.sections.intellectualProperty.title")}>
        <p>{t("terms.sections.intellectualProperty.p1")}</p><p>{t("terms.sections.intellectualProperty.p2")}</p>
      </LegalSection>
      <LegalSection id="liability" icon="⚖️" title={t("terms.sections.liability.title")}>
        <p>{t("terms.sections.liability.p1")}</p><p>{t("terms.sections.liability.p2")}</p>
      </LegalSection>
      <LegalSection id="termination" icon="🔒" title={t("terms.sections.termination.title")}>
        <p>{t("terms.sections.termination.p1")}</p><p>{t("terms.sections.termination.p2")}</p>
      </LegalSection>
      <LegalSection id="dispute-resolution" icon="🕊️" title={t("terms.sections.disputeResolution.title")}>
        <p>{t("terms.sections.disputeResolution.p1")}</p>
        <ol className="list-decimal space-y-2 ps-6">
          <li>{t("terms.sections.disputeResolution.step1")}</li><li>{t("terms.sections.disputeResolution.step2")}</li><li>{t("terms.sections.disputeResolution.step3")}</li>
        </ol>
      </LegalSection>
      <LegalSection id="governing-law" icon="🏛️" title={t("terms.sections.governingLaw.title")}>
        <p>{t("terms.sections.governingLaw.p1")}</p>
      </LegalSection>
      <LegalSection id="amendments" icon="📝" title={t("terms.sections.amendments.title")}>
        <p>{t("terms.sections.amendments.p1")}</p>
      </LegalSection>
      <LegalSection id="contact" icon="📧" title={t("terms.sections.contact.title")}>
        <p>{t("terms.sections.contact.p1")}</p>
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
          <p className="font-semibold">{t("terms.sections.contact.emailLabel")}</p>
          <a href="mailto:legal@econojin.com" className="text-emerald-700 hover:underline">legal@econojin.com</a>
          <p className="mt-3 font-semibold">{t("terms.sections.contact.addressLabel")}</p>
          <p className="text-sm">{t("terms.sections.contact.address")}</p>
        </div>
      </LegalSection>
    </LegalLayout>
  );
}
'''

# ============================================================================
# 3. Privacy Page
# ============================================================================
PRIVACY_CONTENT = '''/**
 * ============================================================================
 *  Privacy.tsx — Privacy Policy (GDPR-Compliant & Human Rights-Based)
 * ============================================================================
 */
import { LegalLayout, LegalSection, LegalCallout } from "@/components/Legal/LegalLayout";
import { useLanguage } from "@/hooks/useLanguage";

export function Privacy(): JSX.Element {
  const { t } = useLanguage();
  const toc = [
    { id: "introduction", title: t("privacy.toc.introduction") }, { id: "principles", title: t("privacy.toc.principles") },
    { id: "data-collected", title: t("privacy.toc.dataCollected") }, { id: "legal-basis", title: t("privacy.toc.legalBasis") },
    { id: "your-rights", title: t("privacy.toc.yourRights") }, { id: "security", title: t("privacy.toc.security") },
    { id: "sharing", title: t("privacy.toc.sharing") }, { id: "retention", title: t("privacy.toc.retention") },
    { id: "cookies", title: t("privacy.toc.cookies") }, { id: "children", title: t("privacy.toc.children") },
    { id: "international", title: t("privacy.toc.international") }, { id: "changes", title: t("privacy.toc.changes") },
    { id: "contact", title: t("privacy.toc.contact") },
  ];

  return (
    <LegalLayout title={t("privacy.title")} subtitle={t("privacy.subtitle")} lastUpdated={t("privacy.lastUpdated")} toc={toc}>
      <LegalSection id="introduction" icon="🔐" title={t("privacy.sections.introduction.title")}>
        <p>{t("privacy.sections.introduction.p1")}</p>
        <LegalCallout type="principle" title={t("privacy.sections.introduction.calloutTitle")}>{t("privacy.sections.introduction.calloutText")}</LegalCallout>
      </LegalSection>
      <LegalSection id="principles" icon="⚖️" title={t("privacy.sections.principles.title")}>
        <p>{t("privacy.sections.principles.intro")}</p>
        <ul className="list-none space-y-3 ps-0">
          {[{ icon: "🎯", title: t("privacy.sections.principles.minimization"), desc: t("privacy.sections.principles.minimizationDesc") },
            { icon: "🔍", title: t("privacy.sections.principles.transparency"), desc: t("privacy.sections.principles.transparencyDesc") },
            { icon: "🛡️", title: t("privacy.sections.principles.integrity"), desc: t("privacy.sections.principles.integrityDesc") },
            { icon: "👤", title: t("privacy.sections.principles.accountability"), desc: t("privacy.sections.principles.accountabilityDesc") }
          ].map((p, i) => <li key={i} className="flex gap-3"><span className="text-xl">{p.icon}</span><div><strong>{p.title}</strong><p className="mt-1 text-sm">{p.desc}</p></div></li>)}
        </ul>
      </LegalSection>
      <LegalSection id="data-collected" icon="📊" title={t("privacy.sections.dataCollected.title")}>
        <p>{t("privacy.sections.dataCollected.intro")}</p>
        <h3 className="mt-6 text-lg font-bold text-gray-900">{t("privacy.sections.dataCollected.personalTitle")}</h3>
        <ul className="list-disc space-y-2 ps-6"><li>{t("privacy.sections.dataCollected.personal1")}</li><li>{t("privacy.sections.dataCollected.personal2")}</li><li>{t("privacy.sections.dataCollected.personal3")}</li><li>{t("privacy.sections.dataCollected.personal4")}</li></ul>
        <h3 className="mt-6 text-lg font-bold text-gray-900">{t("privacy.sections.dataCollected.technicalTitle")}</h3>
        <ul className="list-disc space-y-2 ps-6"><li>{t("privacy.sections.dataCollected.technical1")}</li><li>{t("privacy.sections.dataCollected.technical2")}</li><li>{t("privacy.sections.dataCollected.technical3")}</li></ul>
        <h3 className="mt-6 text-lg font-bold text-gray-900">{t("privacy.sections.dataCollected.agriculturalTitle")}</h3>
        <ul className="list-disc space-y-2 ps-6"><li>{t("privacy.sections.dataCollected.agricultural1")}</li><li>{t("privacy.sections.dataCollected.agricultural2")}</li><li>{t("privacy.sections.dataCollected.agricultural3")}</li></ul>
      </LegalSection>
      <LegalSection id="legal-basis" icon="📜" title={t("privacy.sections.legalBasis.title")}>
        <p>{t("privacy.sections.legalBasis.intro")}</p>
        <ul className="list-disc space-y-2 ps-6">
          <li><strong>{t("privacy.sections.legalBasis.consent")}</strong>: {t("privacy.sections.legalBasis.consentDesc")}</li>
          <li><strong>{t("privacy.sections.legalBasis.contract")}</strong>: {t("privacy.sections.legalBasis.contractDesc")}</li>
          <li><strong>{t("privacy.sections.legalBasis.legitimate")}</strong>: {t("privacy.sections.legalBasis.legitimateDesc")}</li>
          <li><strong>{t("privacy.sections.legalBasis.legal")}</strong>: {t("privacy.sections.legalBasis.legalDesc")}</li>
        </ul>
      </LegalSection>
      <LegalSection id="your-rights" icon="🛡️" title={t("privacy.sections.yourRights.title")}>
        <p>{t("privacy.sections.yourRights.intro")}</p>
        <LegalCallout type="success" title={t("privacy.sections.yourRights.calloutTitle")}>{t("privacy.sections.yourRights.calloutText")}</LegalCallout>
        <div className="grid gap-4 sm:grid-cols-2">
          {[{ icon: "👁️", title: t("privacy.sections.yourRights.right1Title"), desc: t("privacy.sections.yourRights.right1Desc") },
            { icon: "✏️", title: t("privacy.sections.yourRights.right2Title"), desc: t("privacy.sections.yourRights.right2Desc") },
            { icon: "🗑️", title: t("privacy.sections.yourRights.right3Title"), desc: t("privacy.sections.yourRights.right3Desc") },
            { icon: "📦", title: t("privacy.sections.yourRights.right4Title"), desc: t("privacy.sections.yourRights.right4Desc") },
            { icon: "🚫", title: t("privacy.sections.yourRights.right5Title"), desc: t("privacy.sections.yourRights.right5Desc") },
            { icon: "⚙️", title: t("privacy.sections.yourRights.right6Title"), desc: t("privacy.sections.yourRights.right6Desc") },
            { icon: "📢", title: t("privacy.sections.yourRights.right7Title"), desc: t("privacy.sections.yourRights.right7Desc") },
            { icon: "🤖", title: t("privacy.sections.yourRights.right8Title"), desc: t("privacy.sections.yourRights.right8Desc") }
          ].map((r, i) => (
            <div key={i} className="rounded-lg border border-gray-200 bg-white p-4">
              <div className="mb-2 flex items-center gap-2"><span className="text-2xl">{r.icon}</span><strong className="text-gray-900">{r.title}</strong></div>
              <p className="text-sm text-gray-600">{r.desc}</p>
            </div>
          ))}
        </div>
      </LegalSection>
      <LegalSection id="security" icon="🔒" title={t("privacy.sections.security.title")}>
        <p>{t("privacy.sections.security.intro")}</p>
        <ul className="list-disc space-y-2 ps-6">
          <li><strong>{t("privacy.sections.security.encryption")}</strong>: {t("privacy.sections.security.encryptionDesc")}</li>
          <li><strong>{t("privacy.sections.security.access")}</strong>: {t("privacy.sections.security.accessDesc")}</li>
          <li><strong>{t("privacy.sections.security.audits")}</strong>: {t("privacy.sections.security.auditsDesc")}</li>
          <li><strong>{t("privacy.sections.security.breach")}</strong>: {t("privacy.sections.security.breachDesc")}</li>
        </ul>
      </LegalSection>
      <LegalSection id="sharing" icon="🤝" title={t("privacy.sections.sharing.title")}>
        <p>{t("privacy.sections.sharing.intro")}</p>
        <LegalCallout type="warning" title={t("privacy.sections.sharing.calloutTitle")}>{t("privacy.sections.sharing.calloutText")}</LegalCallout>
        <ul className="list-disc space-y-2 ps-6"><li>{t("privacy.sections.sharing.scenario1")}</li><li>{t("privacy.sections.sharing.scenario2")}</li><li>{t("privacy.sections.sharing.scenario3")}</li></ul>
      </LegalSection>
      <LegalSection id="retention" icon="⏱️" title={t("privacy.sections.retention.title")}>
        <p>{t("privacy.sections.retention.intro")}</p>
        <div className="overflow-hidden rounded-lg border border-gray-200">
          <table className="w-full text-sm">
            <thead className="bg-gray-50"><tr><th className="px-4 py-3 text-start font-semibold text-gray-900">{t("privacy.sections.retention.table.type")}</th><th className="px-4 py-3 text-start font-semibold text-gray-900">{t("privacy.sections.retention.table.period")}</th></tr></thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              <tr><td className="px-4 py-3">{t("privacy.sections.retention.table.account")}</td><td className="px-4 py-3">{t("privacy.sections.retention.table.accountPeriod")}</td></tr>
              <tr><td className="px-4 py-3">{t("privacy.sections.retention.table.logs")}</td><td className="px-4 py-3">{t("privacy.sections.retention.table.logsPeriod")}</td></tr>
              <tr><td className="px-4 py-3">{t("privacy.sections.retention.table.backups")}</td><td className="px-4 py-3">{t("privacy.sections.retention.table.backupsPeriod")}</td></tr>
            </tbody>
          </table>
        </div>
      </LegalSection>
      <LegalSection id="cookies" icon="🍪" title={t("privacy.sections.cookies.title")}>
        <p>{t("privacy.sections.cookies.intro")}</p>
        <ul className="list-disc space-y-2 ps-6">
          <li><strong>{t("privacy.sections.cookies.essential")}</strong>: {t("privacy.sections.cookies.essentialDesc")}</li>
          <li><strong>{t("privacy.sections.cookies.analytics")}</strong>: {t("privacy.sections.cookies.analyticsDesc")}</li>
          <li><strong>{t("privacy.sections.cookies.preferences")}</strong>: {t("privacy.sections.cookies.preferencesDesc")}</li>
        </ul>
      </LegalSection>
      <LegalSection id="children" icon="👶" title={t("privacy.sections.children.title")}>
        <p>{t("privacy.sections.children.intro")}</p>
      </LegalSection>
      <LegalSection id="international" icon="🌍" title={t("privacy.sections.international.title")}>
        <p>{t("privacy.sections.international.intro")}</p>
      </LegalSection>
      <LegalSection id="changes" icon="📝" title={t("privacy.sections.changes.title")}>
        <p>{t("privacy.sections.changes.intro")}</p>
      </LegalSection>
      <LegalSection id="contact" icon="📧" title={t("privacy.sections.contact.title")}>
        <p>{t("privacy.sections.contact.intro")}</p>
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
          <p className="font-semibold">{t("privacy.sections.contact.dpoLabel")}</p>
          <a href="mailto:privacy@econojin.com" className="text-emerald-700 hover:underline">privacy@econojin.com</a>
          <p className="mt-3 font-semibold">{t("privacy.sections.contact.responseLabel")}</p>
          <p className="text-sm">{t("privacy.sections.contact.responseTime")}</p>
        </div>
      </LegalSection>
    </LegalLayout>
  );
}
'''

# ============================================================================
# 4. Translation Keys
# ============================================================================
def get_legal_translations() -> Dict[str, Any]:
    return {
        "legal": {
            "backToHome": "بازگشت به صفحه اصلی",
            "lastUpdated": "آخرین به‌روزرسانی",
            "compliantWith": "منطبق با",
            "tableOfContents": "فهرست مطالب",
            "printDocument": "چاپ سند",
            "footerText": "این سند بر اساس اصول حقوق بشر، حفاظت از محیط زیست و استانداردهای بین‌المللی تدوین شده است.",
        },
        "terms": {
            "title": "قوانین و مقررات استفاده",
            "subtitle": "این توافق‌نامه، چارچوب حقوقی و اخلاقی استفاده از پلتفرم اکو نوژین را تعیین می‌کند. با ثبت‌نام، شما این شرایط را با آگاهی کامل می‌پذیرید.",
            "lastUpdated": "۲۴ تیر ۱۴۰۵",
            "toc": { "preamble": "مقدمه", "values": "ارزش‌های بنیادین", "acceptance": "پذیرش شرایط", "userRights": "حقوق کاربر", "userObligations": "تعهدات کاربر", "platformCommitments": "تعهدات پلتفرم", "environmental": "تعهدات زیست‌محیطی", "intellectualProperty": "مالکیت فکری", "liability": "محدودیت مسئولیت", "termination": "فسخ حساب", "disputeResolution": "حل اختلاف", "governingLaw": "قانون حاکم", "amendments": "تغییرات", "contact": "تماس با ما" },
            "sections": {
                "preamble": { "title": "مقدمه", "p1": "به پلتفرم اکو نوژین خوش آمدید. ما معتقدیم که فناوری باید در خدمت انسان و طبیعت باشد، نه در تضاد با آن. این قوانین با الهام از اعلامیه جهانی حقوق بشر، توافق پاریس درباره تغییرات اقلیمی و اهداف توسعه پایدار سازمان ملل متحد تدوین شده‌اند.", "p2": "اکو نوژین یک پلتفرم جامع برای کشاورزی هوشمند، مدیریت منابع آب، حفاظت از محیط زیست و اقتصاد پایدار است. هدف ما توانمندسازی کشاورزان، پژوهشگران، مدیران و جوامع محلی برای ایجاد آینده‌ای پایدارتر است.", "calloutTitle": "تعهد ما به کرامت انسانی", "calloutText": "ما به این باور پایبندیم که هر انسانی، فارغ از نژاد، جنسیت، مذهب، ملیت یا وضعیت اقتصادی، حق دسترسی برابر به اطلاعات، فناوری و فرصت‌های رشد دارد. اکو نوژین هرگز ابزاری برای تبعیض، استثمار یا آسیب به انسان یا طبیعت نخواهد بود." },
                "values": { "title": "ارزش‌های بنیادین", "intro": "تمام فعالیت‌های اکو نوژین بر چهار ارزش بنیادین استوار است:", "humanDignity": "کرامت انسانی", "humanDignityDesc": "احترام به حقوق، حریم خصوصی و کرامت هر کاربر به عنوان یک اصل غیرقابل مذاکره.", "ecoStewardship": "مسئولیت زیست‌محیطی", "ecoStewardshipDesc": "تعهد به حفاظت از تنوع زیستی، کاهش ردپای کربنی و ترویج کشاورزی پایدار.", "transparency": "شفافیت و صداقت", "transparencyDesc": "ارتباط روشن، صادقانه و به‌موقع با کاربران درباره تمام جنبه‌های پلتفرم.", "inclusivity": "فراگیری و برابری", "inclusivityDesc": "دسترسی برابر برای همه، با طراحی جهانی و پشتیبانی چندزبانه." },
                "acceptance": { "title": "پذیرش شرایط", "p1": "با ایجاد حساب کاربری یا استفاده از هر بخش از پلتفرم اکو نوژین، شما اعلام می‌کنید که این قوانین را به دقت خوانده‌اید، درک کرده‌اید و با آن‌ها موافقت می‌کنید. اگر با هر بخشی از این شرایط موافق نیستید، لطفاً از پلتفرم استفاده نکنید.", "p2": "این توافق‌نامه بین شما (به عنوان «کاربر») و اکو نوژین (به عنوان «پلتفرم») منعقد می‌شود و بر تمام تعاملات شما با سرویس‌های ما اعمال می‌گردد." },
                "userRights": { "title": "حقوق کاربر", "intro": "به عنوان کاربر اکو نوژین، شما از حقوق زیر برخوردارید:", "right1": "حق دسترسی به سرویس‌ها بدون هیچ‌گونه تبعیض", "right2": "حق حریم خصوصی کامل و کنترل بر داده‌های شخصی", "right3": "حق دریافت اطلاعات شفاف درباره نحوه استفاده از داده‌هایتان", "right4": "حق درخواست حذف کامل حساب و داده‌ها (حق فراموش شدن)", "right5": "حق انتقال داده‌هایتان به سرویس دیگر (قابلیت جابجایی)", "right6": "حق اعتراض به تصمیمات خودکار گرفته شده توسط هوش مصنوعی", "calloutTitle": "حقوق شما، تعهد ما", "calloutText": "ما این حقوق را نه به عنوان یک لطف، بلکه به عنوان یک وظیفه اخلاقی و قانونی می‌شناسیم. هرگونه نقض این حقوق، تخلف از این توافق‌نامه محسوب می‌شود." },
                "userObligations": { "title": "تعهدات کاربر", "intro": "برای حفظ محیطی امن و سازنده، شما متعهد می‌شوید:", "obligation1": "اطلاعات دقیق و واقعی ارائه دهید", "obligation2": "از پلتفرم برای اهداف قانونی و اخلاقی استفاده کنید", "obligation3": "به حقوق سایر کاربران و مالکیت فکری احترام بگذارید", "obligation4": "از انتشار محتوای توهین‌آمیز، تبعیض‌آمیز یا مخرب خودداری کنید", "obligation5": "در حفاظت از حساب کاربری خود کوشا باشید" },
                "platformCommitments": { "title": "تعهدات پلتفرم", "intro": "اکو نوژین متعهد می‌شود:", "commitment1": "داده‌های شما را با بالاترین استانداردهای امنیتی محافظت کند", "commitment2": "پلتفرم را در دسترس، پایدار و به‌روز نگه دارد", "commitment3": "به تمام درخواست‌های شما درباره داده‌ها ظرف ۳۰ روز پاسخ دهد", "commitment4": "در صورت نقض داده، ظرف ۷۲ ساعت به شما اطلاع دهد" },
                "environmental": { "title": "تعهدات زیست‌محیطی", "intro": "اکو نوژین به عنوان یک پلتفرم دوستدار محیط زیست، متعهد می‌شود:", "calloutTitle": "تعهد ما به زمین", "calloutText": "ما باور داریم که حفاظت از محیط زیست یک وظیفه نسل‌ساز است. هر تصمیمی که در اکو نوژین گرفته می‌شود، با در نظر گرفتن تأثیر آن بر هفت نسل آینده ارزیابی می‌گردد.", "commitment1": "کاهش ردپای کربنی سرورها و زیرساخت‌ها", "commitment2": "استفاده از انرژی‌های تجدیدپذیر در دیتاسنترها", "commitment3": "ترویج کشاورزی پایدار و حفاظت از تنوع زیستی", "commitment4": "گزارش‌دهی سالانه درباره تأثیرات زیست‌محیطی" },
                "intellectualProperty": { "title": "مالکیت فکری", "p1": "تمام محتوای اصلی، کدها، الگوریتم‌ها و طراحی‌های موجود در اکو نوژین تحت حمایت قوانین مالکیت فکری بین‌المللی قرار دارند. شما حق استفاده شخصی و غیرتجاری از این محتوا را دارید، اما هرگونه کپی‌برداری، توزیع یا استفاده تجاری بدون اجازه کتبی ممنوع است.", "p2": "محتوایی که شما در پلتفرم بارگذاری می‌کنید (مانند داده‌های مزرعه، گزارش‌ها و شبیه‌سازی‌ها) متعلق به شما باقی می‌ماند. شما به اکو نوژین مجوز محدودی برای پردازش این داده‌ها به منظور ارائه سرویس می‌دهید." },
                "liability": { "title": "محدودیت مسئولیت", "p1": "اکو نوژین با حسن نیت و بر اساس بهترین شیوه‌های صنعت ارائه می‌شود. با این حال، ما نمی‌توانیم تضمین کنیم که سرویس بدون وقفه، خطا یا نقص امنیتی باشد. در محدوده مجاز قانونی، مسئولیت ما به حداکثر مبلغی که شما در ۱۲ ماه گذشته پرداخته‌اید محدود می‌شود.", "p2": "نتایج شبیه‌سازی‌ها و توصیه‌های هوش مصنوعی صرفاً جنبه مشورتی دارند و نباید به عنوان جایگزین مشاوره تخصصی انسانی در نظر گرفته شوند. تصمیمات نهایی بر عهده کاربر است." },
                "termination": { "title": "فسخ حساب", "p1": "شما می‌توانید در هر زمان و بدون دلیل، حساب کاربری خود را حذف کنید. تمام داده‌های شما ظرف ۳۰ روز به طور کامل و غیرقابل بازیابی حذف خواهند شد.", "p2": "اکو نوژین حق دارد در صورت نقض جدی این قوانین، فعالیت‌های غیرقانونی یا تهدید امنیت پلتفرم، حساب کاربری را به طور موقت یا دائم مسدود کند. در چنین مواردی، به شما اطلاع داده خواهد شد و حق اعتراض خواهید داشت." },
                "disputeResolution": { "title": "حل اختلاف", "p1": "در صورت بروز هرگونه اختلاف، ما به حل مسالمت‌آمیز از طریق مراحل زیر متعهد هستیم:", "step1": "مذاکره مستقیم: تلاش برای حل اختلاف از طریق گفتگوی سازنده ظرف ۳۰ روز", "step2": "میانجی‌گری: در صورت عدم موفقیت، ارجاع به میانجی مستقل و بی‌طرف", "step3": "داوری: به عنوان آخرین راه‌حل، ارجاع به داوری معتبر بین‌المللی" },
                "governingLaw": { "title": "قانون حاکم", "p1": "این توافق‌نامه بر اساس قوانین جمهوری اسلامی ایران و با رعایت اصول حقوق بین‌الملل تفسیر و اجرا می‌شود. هرگونه اختلاف که از طریق مذاکره حل نشود، در صلاحیت دادگاه‌های معتبر ایران خواهد بود." },
                "amendments": { "title": "تغییرات در قوانین", "p1": "اکو نوژین حق دارد این قوانین را به‌روزرسانی کند. تغییرات مهم حداقل ۳۰ روز قبل از اجرا از طریق ایمیل و اعلان در پلتفرم به شما اطلاع داده می‌شوند. استفاده مستمر شما پس از تاریخ اجرا، به معنای پذیرش تغییرات است." },
                "contact": { "title": "تماس با ما", "p1": "برای هرگونه سوال، نگرانی یا درخواست درباره این قوانین، می‌توانید از طریق راه‌های زیر با ما در تماس باشید:", "emailLabel": "ایمیل تیم حقوقی:", "addressLabel": "آدرس:", "address": "تهران، ایران | اکو نوژین، دپارتمان حقوقی" }
            }
        },
        "privacy": {
            "title": "سیاست حفظ حریم خصوصی",
            "subtitle": "حریم خصوصی شما یک حق بنیادین انسانی است، نه یک امتیاز. این سیاست توضیح می‌دهد که ما چگونه از این حق محافظت می‌کنیم.",
            "lastUpdated": "۲۴ تیر ۱۴۰۵",
            "toc": { "introduction": "مقدمه", "principles": "اصول بنیادین", "dataCollected": "داده‌های جمع‌آوری شده", "legalBasis": "مبنای قانونی پردازش", "yourRights": "حقوق شما", "security": "امنیت داده‌ها", "sharing": "اشتراک‌گذاری داده‌ها", "retention": "مدت نگهداری", "cookies": "کوکی‌ها", "children": "حقوق کودکان", "international": "انتقال بین‌المللی", "changes": "تغییرات در سیاست", "contact": "تماس با ما" },
            "sections": {
                "introduction": { "title": "مقدمه و دامنه", "p1": "در اکو نوژین، ما حریم خصوصی را به عنوان یکی از حقوق بنیادین انسانی می‌شناسیم، همان‌طور که در ماده ۱۲ اعلامیه جهانی حقوق بشر آمده است: «هیچ‌کس نباید در معرض مداخلات خودسرانه در حریم خصوصی، خانواده، خانه یا مکاتبات خود قرار گیرد.»", "calloutTitle": "تعهد ما به حریم خصوصی شما", "calloutText": "ما هرگز داده‌های شما را نمی‌فروشیم، بدون رضایت صریح شما به اشخاص ثالث نمی‌دهیم و تنها داده‌هایی را جمع‌آوری می‌کنیم که واقعاً برای ارائه سرویس ضروری باشند. شفافیت کامل، اصل غیرقابل مذاکره ماست." },
                "principles": { "title": "اصول بنیادین حفاظت از داده", "intro": "سیاست ما بر اساس اصول GDPR و استانداردهای بین‌المللی ISO 27001 تدوین شده است:", "minimization": "حداقل‌سازی داده", "minimizationDesc": "تنها داده‌هایی را جمع‌آوری می‌کنیم که برای ارائه سرویس ضروری باشند.", "transparency": "شفافیت کامل", "transparencyDesc": "دقیقاً به شما می‌گوییم چه داده‌ای، چرا و چگونه پردازش می‌شود.", "integrity": "یکپارچگی و محرمانگی", "integrityDesc": "از رمزنگاری پیشرفته و کنترل‌های دسترسی سخت‌گیرانه استفاده می‌کنیم.", "accountability": "پاسخگویی", "accountabilityDesc": "ما مسئول تمام داده‌هایی هستیم که پردازش می‌کنیم." },
                "dataCollected": { "title": "داده‌های جمع‌آوری شده", "intro": "ما سه نوع داده را پردازش می‌کنیم:", "personalTitle": "داده‌های شخصی", "personal1": "نام و نام خانوادگی", "personal2": "آدرس ایمیل", "personal3": "نقش شما در پلتفرم (کشاورز، پژوهشگر، مدیر و غیره)", "personal4": "تاریخچه فعالیت‌ها در پلتفرم", "technicalTitle": "داده‌های فنی", "technical1": "آدرس IP (برای امنیت و جلوگیری از سوءاستفاده)", "technical2": "نوع مرورگر و دستگاه", "technical3": "گزارش‌های خطا برای بهبود سرویس", "agriculturalTitle": "داده‌های کشاورزی (اختیاری)", "agricultural1": "اطلاعات مزرعه (موقعیت، مساحت، نوع محصول)", "agricultural2": "نتایج شبیه‌سازی‌ها", "agricultural3": "گزارش‌های محیط زیستی" },
                "legalBasis": { "title": "مبنای قانونی پردازش", "intro": "ما داده‌های شما را تنها بر اساس یکی از مبنای‌های قانونی زیر پردازش می‌کنیم:", "consent": "رضایت صریح", "consentDesc": "برای فعالیت‌هایی مانند ارسال خبرنامه یا پردازش داده‌های حساس", "contract": "اجرای قرارداد", "contractDesc": "برای ارائه سرویس‌هایی که به آن‌ها مشترک شده‌اید", "legitimate": "منافع مشروع", "legitimateDesc": "برای بهبود سرویس و امنیت، با رعایت حقوق شما", "legal": "الزامات قانونی", "legalDesc": "برای رعایت قوانین و مقررات لازم‌الاجرا" },
                "yourRights": { "title": "حقوق شما به عنوان کاربر", "intro": "بر اساس GDPR و قوانین حقوق بشر، شما از حقوق زیر برخوردارید:", "calloutTitle": "حقوق شما، قدرت شما", "calloutText": "این حقوق را می‌توانید در هر زمان و بدون هیچ هزینه‌ای از طریق پنل کاربری خود یا با تماس با تیم حریم خصوصی ما اعمال کنید.", "right1Title": "حق دسترسی", "right1Desc": "دریافت کپی از تمام داده‌های شخصی شما", "right2Title": "حق اصلاح", "right2Desc": "درخواست اصلاح داده‌های نادرست یا ناقص", "right3Title": "حق فراموش شدن", "right3Desc": "درخواست حذف کامل و غیرقابل بازیابی داده‌ها", "right4Title": "حق انتقال داده", "right4Desc": "دریافت داده‌ها در فرمت قابل خواندن توسط ماشین", "right5Title": "حق اعتراض", "right5Desc": "اعتراض به پردازش داده‌ها در شرایط خاص", "right6Title": "حق محدودسازی", "right6Desc": "درخواست توقف موقت پردازش داده‌ها", "right7Title": "حق اطلاع‌رسانی نقض", "right7Desc": "دریافت اطلاع فوری در صورت نقض داده‌های شما", "right8Title": "حق عدم تصمیم‌گیری خودکار", "right8Desc": "درخواست بررسی انسانی تصمیمات گرفته شده توسط AI" },
                "security": { "title": "امنیت داده‌ها", "intro": "ما از چندین لایه امنیتی برای محافظت از داده‌های شما استفاده می‌کنیم:", "encryption": "رمزنگاری", "encryptionDesc": "تمام داده‌ها در حال انتقال (TLS 1.3) و در حالت استراحت (AES-256) رمزنگاری می‌شوند.", "access": "کنترل دسترسی", "accessDesc": "فقط کارکنان مجاز با اصل «حداقل امتیاز» به داده‌ها دسترسی دارند.", "audits": "ممیزی‌های منظم", "auditsDesc": "ممیزی‌های امنیتی سالانه توسط شرکت‌های مستقل و معتبر.", "breach": "پاسخ به نقض", "breachDesc": "در صورت نقض داده، ظرف ۷۲ ساعت به شما و مراجع قانونی اطلاع می‌دهیم." },
                "sharing": { "title": "اشتراک‌گذاری داده‌ها", "intro": "ما داده‌های شما را تنها در شرایط زیر به اشتراک می‌گذاریم:", "calloutTitle": "اصل عدم فروش", "calloutText": "ما هرگز، تحت هیچ شرایطی، داده‌های شخصی شما را به اشخاص ثالث برای اهداف بازاریابی یا تجاری نمی‌فروشیم. این یک تعهد غیرقابل تغییر است.", "scenario1": "با رضایت صریح و آگاهانه شما", "scenario2": "برای رعایت الزامات قانونی (مانند حکم دادگاه)", "scenario3": "با ارائه‌دهندگان خدمات مورد اعتماد (مانند سرویس‌های ابری) تحت قراردادهای محرمانگی" },
                "retention": { "title": "مدت نگهداری داده‌ها", "intro": "ما داده‌ها را تنها به اندازه ضرورت نگهداری می‌کنیم:", "table": { "type": "نوع داده", "period": "مدت نگهداری", "account": "داده‌های حساب کاربری", "accountPeriod": "تا زمان حذف حساب + ۳۰ روز", "logs": "گزارش‌های فعالیت", "logsPeriod": "۱۲ ماه", "backups": "پشتیبان‌گیری‌ها", "backupsPeriod": "۹۰ روز" } },
                "cookies": { "title": "کوکی‌ها و فناوری‌های مشابه", "intro": "ما از کوکی‌ها برای بهبود تجربه کاربری استفاده می‌کنیم:", "essential": "کوکی‌های ضروری", "essentialDesc": "برای عملکرد صحیح پلتفرم (مانند احراز هویت)", "analytics": "کوکی‌های تحلیلی", "analyticsDesc": "برای درک نحوه استفاده از پلتفرم (با امکان غیرفعال‌سازی)", "preferences": "کوکی‌های ترجیحات", "preferencesDesc": "برای ذخیره تنظیمات شما (مانند زبان و تم)" },
                "children": { "title": "حقوق کودکان", "intro": "اکو نوژین برای افراد زیر ۱۶ سال طراحی نشده است. ما به طور عامدانه داده‌های کودکان را بدون تأیید والدین یا سرپرست قانونی جمع‌آوری نمی‌کنیم. در صورت اطلاع از جمع‌آوری چنین داده‌هایی، بلافاصله آن‌ها را حذف خواهیم کرد." },
                "international": { "title": "انتقال بین‌المللی داده‌ها", "intro": "در صورت انتقال داده‌های شما به خارج از کشور محل سکونتتان، ما اطمینان حاصل می‌کنیم که کشور مقصد دارای سطح حفاظت کافی است یا از مکانیسم‌های قانونی مانند قراردادهای استاندارد اتحادیه اروپا استفاده می‌کنیم." },
                "changes": { "title": "تغییرات در سیاست حریم خصوصی", "intro": "ما ممکن است این سیاست را به‌روزرسانی کنیم. تغییرات مهم از طریق ایمیل و اعلان در پلتفرم حداقل ۳۰ روز قبل از اجرا اطلاع‌رسانی می‌شوند. استفاده مستمر شما پس از تاریخ اجرا، به معنای پذیرش تغییرات است." },
                "contact": { "title": "تماس با مسئول حفاظت از داده", "intro": "برای هر سوال، درخواست یا شکایت درباره حریم خصوصی، می‌توانید با مسئول حفاظت از داده (DPO) ما تماس بگیرید:", "dpoLabel": "ایمیل مسئول حفاظت از داده:", "responseLabel": "زمان پاسخ‌گویی:", "responseTime": "ما متعهد می‌شویم ظرف ۳۰ روز به تمام درخواست‌ها پاسخ دهیم. در موارد پیچیده، این مدت ممکن است تا ۶۰ روز تمدید شود که به شما اطلاع داده خواهد شد." }
            }
        }
    }

def deep_merge(target: Dict, source: Dict) -> None:
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            deep_merge(target[key], value)
        else:
            target[key] = value

def main():
    print("\n" + "=" * 70)
    print("🏛️  Eco Nojin - Legal Pages Setup (Python UTF-8 Safe)")
    print("=" * 70)

    LEGAL_LAYOUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    TERMS_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("\n💾 Creating backups...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    for path in [LEGAL_LAYOUT_PATH, TERMS_PATH, PRIVACY_PATH, FA_JSON_PATH]:
        if path.exists():
            backup = path.with_suffix(path.suffix + f".backup_{timestamp}")
            try:
                shutil.copy2(path, backup)
                print(f"   ✅ {path.name} → {backup.name}")
            except Exception as e:
                print(f"   ⚠️  Backup failed for {path.name}: {e}")

    print("\n📝 Writing TypeScript files...")
    LEGAL_LAYOUT_PATH.write_text(LEGAL_LAYOUT_CONTENT, encoding="utf-8")
    print(f"   ✅ Created: {LEGAL_LAYOUT_PATH.relative_to(PROJECT_ROOT)}")
    
    TERMS_PATH.write_text(TERMS_CONTENT, encoding="utf-8")
    print(f"   ✅ Created: {TERMS_PATH.relative_to(PROJECT_ROOT)}")
    
    PRIVACY_PATH.write_text(PRIVACY_CONTENT, encoding="utf-8")
    print(f"   ✅ Created: {PRIVACY_PATH.relative_to(PROJECT_ROOT)}")

    print("\n🌐 Updating fa.json translations...")
    if not FA_JSON_PATH.exists():
        print(f"   ❌ fa.json not found at: {FA_JSON_PATH}")
        existing_translations = {}
    else:
        try:
            with open(FA_JSON_PATH, "r", encoding="utf-8") as f:
                existing_translations = json.load(f)
        except Exception as e:
            print(f"   ⚠️  Failed to read existing fa.json: {e}")
            existing_translations = {}

    deep_merge(existing_translations, get_legal_translations())

    with open(FA_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(existing_translations, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ Updated: {FA_JSON_PATH.relative_to(PROJECT_ROOT)}")

    print("\n" + "=" * 70)
    print("✅ Setup completed successfully!")
    print("=" * 70)
    print("\n📌 Next steps:")
    print("   1. Restart dev server: cd apps/web && pnpm dev")
    print("   2. Visit: http://localhost:5173/terms")
    print("   3. Visit: http://localhost:5173/privacy")

if __name__ == "__main__":
    main()