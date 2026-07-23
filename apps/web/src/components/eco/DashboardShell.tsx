import type { ReactNode } from "react";
import { SectionReveal } from "./SectionReveal";
import { AnimatedCounter } from "./AnimatedCounter";
import { GlassPanel } from "./GlassPanel";

export interface StatConfig { label: string; value: number; suffix?: string;
  decimals?: number; icon: string; trend?: { value: number; up: boolean }; }
export interface DashboardConfig { title: string; subtitle: string; icon: string;
  stats: StatConfig[]; quickActions: { label: string; icon: string }[]; }

export function DashboardShell({ config, children }:
  { config: DashboardConfig; children?: ReactNode }) {
  return (
    <div className="min-h-screen p-4 sm:p-6 lg:p-8 space-y-6">
      <SectionReveal>
        <div className="flex items-center gap-4">
          <span className="text-3xl">{config.icon}</span>
          <div><h1 className="text-2xl font-black">{config.title}</h1>
            <p className="text-sm text-[var(--text-3)] font-light">{config.subtitle}</p></div>
        </div>
      </SectionReveal>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {config.stats.map((s, i) => (
          <SectionReveal key={s.label} delay={i * 80}>
            <GlassPanel hover className="p-5">
              <div className="flex items-start justify-between mb-3">
                <span className="text-xl">{s.icon}</span>
                {s.trend && (
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full
                    ${s.trend.up ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}`}>
                    {s.trend.up ? "↑" : "↓"} {s.trend.value}٪</span>)}
              </div>
              <div className="text-2xl font-black tabular-nums mb-1">
                <AnimatedCounter end={s.value} suffix={s.suffix ?? ""} decimals={s.decimals ?? 0} /></div>
              <p className="text-xs text-[var(--text-3)]">{s.label}</p>
            </GlassPanel>
          </SectionReveal>
        ))}
      </div>
      <SectionReveal delay={200}>
        <div className="flex flex-wrap gap-3">
          {config.quickActions.map((a) => (
            <button key={a.label} className="inline-flex items-center gap-2 px-4 py-2 rounded-[var(--r-md)]
              border border-[var(--border-subtle)] text-sm text-[var(--text-2)]
              hover:border-brand-500/40 hover:text-brand-400 hover:bg-brand-500/5 transition-all duration-200">
              <span>{a.icon}</span> {a.label}</button>
          ))}
        </div>
      </SectionReveal>
      <SectionReveal delay={300}>{children}</SectionReveal>
    </div>
  );
}
