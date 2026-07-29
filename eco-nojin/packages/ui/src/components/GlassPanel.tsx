import type { ReactNode } from "react";

export function GlassPanel({ children, className = "", hover = false }: {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}) {
  return (
    <div className={[
      "backdrop-blur-xl bg-white/[.06] dark:bg-white/[.04]",
      "border border-white/[.08] dark:border-white/[.06]",
      "rounded-2xl",
      hover ? "transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-black/10" : "",
      className,
    ].filter(Boolean).join(" ")}>
      {children}
    </div>
  );
}
