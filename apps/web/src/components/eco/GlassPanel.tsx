import type { ReactNode } from "react";
export function GlassPanel({ children, className = "", hover = false,
  ink = false }: { children: ReactNode; className?: string; hover?: boolean; ink?: boolean }) {
  return (
    <div className={`${ink ? "glass-ink" : "glass"} rounded-[var(--r-lg)] ${hover ? "card-hover" : ""} ${className}`}>
      {children}</div>
  );
}
