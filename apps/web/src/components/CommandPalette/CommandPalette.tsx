/**
 * ============================================================================
 *  CommandPalette — global search & quick actions (Ctrl+K)
 * ============================================================================
 *
 *  Inspired by:
 *   - Vercel cmdk
 *   - Linear command palette
 *   - Raycast
 * ============================================================================
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { useAuth } from "@/hooks/useAuth";
import { AVAILABLE_LANGUAGES } from "@/lib/i18n-utils";
import { SIMULATORS } from "@/simulators/registry";
import { SATELLITES } from "@/satellites/registry";
import { SCENARIOS } from "@/scenarios/registry";
import { cn } from "@/lib/utils";
import type { SupportedLanguage } from "@/i18n";

interface CommandItem {
  id: string;
  label: string;
  hint?: string;
  icon: string;
  action: () => void;
  category: "navigate" | "simulator" | "satellite" | "scenario" | "language" | "auth";
}

export interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CommandPalette({ isOpen, onClose }: CommandPaletteProps): JSX.Element | null {
  const { t, language, changeLanguage } = useLanguage();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [activeIdx, setActiveIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input when opening
  useEffect(() => {
    if (isOpen) {
      setQuery("");
      setActiveIdx(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  // Build commands
  const commands = useMemo<CommandItem[]>(() => {
    const navCommands: CommandItem[] = [
      { id: "nav-dashboard", label: t("nav.dashboard"), icon: "📊", category: "navigate", action: () => { navigate("/dashboard"); onClose(); } },
      { id: "nav-documents", label: t("nav.documents"), icon: "📄", category: "navigate", action: () => { navigate("/documents"); onClose(); } },
      { id: "nav-carbon", label: t("nav.carbon"), icon: "🏭", category: "navigate", action: () => { navigate("/carbon"); onClose(); } },
      { id: "nav-watersheds", label: t("nav.watersheds"), icon: "💧", category: "navigate", action: () => { navigate("/hydrology/watersheds"); onClose(); } },
      { id: "nav-soil", label: t("nav.soil"), icon: "🌱", category: "navigate", action: () => { navigate("/soil"); onClose(); } },
      { id: "nav-profile", label: t("user.myProfile"), icon: "👤", category: "navigate", action: () => { navigate("/profile"); onClose(); } },
      { id: "nav-alerts", label: t("alerts.title"), icon: "🔔", category: "navigate", action: () => { navigate("/alerts"); onClose(); } },
    ];

    const simCommands: CommandItem[] = SIMULATORS.map((sim) => ({
      id: `sim-${sim.id}`,
      label: t(sim.nameKey),
      hint: t(sim.descriptionKey),
      icon: sim.icon,
      category: "simulator" as const,
      action: () => { navigate(`/simulators/${sim.id}`); onClose(); },
    }));

    const satCommands: CommandItem[] = SATELLITES.map((sat) => ({
      id: `sat-${sat.id}`,
      label: sat.name,
      hint: sat.agency,
      icon: sat.icon,
      category: "satellite" as const,
      action: () => { navigate("/satellites"); onClose(); },
    }));

    const scenCommands: CommandItem[] = SCENARIOS.map((scn) => ({
      id: `scn-${scn.id}`,
      label: t(scn.nameKey),
      hint: t(scn.descriptionKey),
      icon: scn.icon,
      category: "scenario" as const,
      action: () => { navigate("/scenarios"); onClose(); },
    }));

    const langCommands: CommandItem[] = AVAILABLE_LANGUAGES.map((meta) => ({
      id: `lang-${meta.code}`,
      label: `${meta.flag} ${meta.nativeName}`,
      hint: meta.englishName,
      icon: "🌐",
      category: "language" as const,
      action: () => { changeLanguage(meta.code as SupportedLanguage); onClose(); },
    }));

    const authCommands: CommandItem[] = [
      {
        id: "auth-logout",
        label: t("user.logout"),
        icon: "🚪",
        category: "auth",
        action: async () => { await logout(); navigate("/login"); onClose(); },
      },
    ];

    return [...navCommands, ...simCommands, ...satCommands, ...scenCommands, ...langCommands, ...authCommands];
  }, [t, navigate, onClose, changeLanguage, logout]);

  // Filter by query (fuzzy: contains all chars in order)
  const filtered = useMemo(() => {
    if (!query.trim()) return commands;
    const q = query.toLowerCase();
    return commands.filter((c) =>
      c.label.toLowerCase().includes(q) ||
      c.hint?.toLowerCase().includes(q) ||
      c.category.includes(q)
    );
  }, [commands, query]);

  // Reset active index when filter changes
  useEffect(() => {
    setActiveIdx(0);
  }, [query]);

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen) return;
    function handleKey(event: KeyboardEvent): void {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        setActiveIdx((i) => Math.min(i + 1, filtered.length - 1));
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        setActiveIdx((i) => Math.max(i - 1, 0));
      } else if (event.key === "Enter") {
        event.preventDefault();
        const cmd = filtered[activeIdx];
        if (cmd) cmd.action();
      }
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [isOpen, filtered, activeIdx]);

  if (!isOpen) return null;

  const categoryLabels: Record<CommandItem["category"], string> = {
    navigate: t("commandPalette.navigate"),
    simulator: t("simulators.title"),
    satellite: t("satellites.title"),
    scenario: t("scenarios.title"),
    language: t("common.language"),
    auth: t("user.login"),
  };

  // Group filtered commands by category
  const grouped = filtered.reduce<Record<string, CommandItem[]>>((acc, cmd) => {
    (acc[cmd.category] ??= []).push(cmd);
    return acc;
  }, {});

  let runningIdx = 0;

  return (
    <div className="fixed inset-0 z-[100] flex items-start justify-center bg-black/50 pt-[10vh] backdrop-blur-sm" onClick={onClose}>
      <div
        dir={language === "fa" || language === "ar" ? "rtl" : "ltr"}
        className="w-full max-w-xl overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search input */}
        <div className="flex items-center gap-3 border-b border-gray-100 px-4 py-3">
          <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("commandPalette.placeholder")}
            className="flex-1 bg-transparent text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none"
          />
          <kbd className="rounded border border-gray-200 bg-gray-50 px-1.5 py-0.5 text-xs text-gray-500">ESC</kbd>
        </div>

        {/* Results */}
        <div className="max-h-[60vh] overflow-y-auto p-2">
          {filtered.length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-gray-500">
              {t("commandPalette.noResults")}
            </div>
          ) : (
            Object.entries(grouped).map(([cat, items]) => (
              <div key={cat} className="mb-2">
                <p className="px-3 py-1 text-xs font-semibold uppercase tracking-wider text-gray-400">
                  {categoryLabels[cat as CommandItem["category"]]}
                </p>
                {items.map((cmd) => {
                  const idx = runningIdx++;
                  return (
                    <button
                      key={cmd.id}
                      type="button"
                      onMouseEnter={() => setActiveIdx(idx)}
                      onClick={() => cmd.action()}
                      className={cn(
                        "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-start transition",
                        idx === activeIdx ? "bg-emerald-50" : "hover:bg-gray-50",
                      )}
                    >
                      <span className="text-xl" aria-hidden="true">{cmd.icon}</span>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-gray-900">{cmd.label}</p>
                        {cmd.hint && <p className="truncate text-xs text-gray-500">{cmd.hint}</p>}
                      </div>
                    </button>
                  );
                })}
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-gray-100 px-4 py-2 text-xs text-gray-400">
          <span>{t("commandPalette.footerHint")}</span>
          <span>{filtered.length} {t("commandPalette.results")}</span>
        </div>
      </div>
    </div>
  );
}
