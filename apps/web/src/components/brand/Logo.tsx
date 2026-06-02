"use client";

import { Link } from "@/i18n/navigation";
import { cn } from "@/lib/utils";

type Props = {
  className?: string;
  size?: "sm" | "md" | "lg";
  showTagline?: boolean;
};

const sizes = {
  sm: { mark: 32, title: "text-lg", sub: "text-[10px]" },
  md: { mark: 40, title: "text-xl", sub: "text-xs" },
  lg: { mark: 52, title: "text-3xl", sub: "text-sm" },
};

export function Logo({ className, size = "md", showTagline = true }: Props) {
  const s = sizes[size];
  return (
    <Link href="/" className={cn("inline-flex items-center gap-3 group", className)}>
      <svg
        width={s.mark}
        height={s.mark}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0 drop-shadow-lg group-hover:scale-105 transition-transform"
        aria-hidden
      >
        <defs>
          <linearGradient id="ecoGrad" x1="0" y1="0" x2="64" y2="64">
            <stop offset="0%" stopColor="#38bdf8" />
            <stop offset="50%" stopColor="#34d399" />
            <stop offset="100%" stopColor="#a3e635" />
          </linearGradient>
        </defs>
        <circle cx="32" cy="32" r="30" stroke="url(#ecoGrad)" strokeWidth="2" fill="#0f172a" />
        <path
          d="M32 14 C24 22 20 32 22 42 C28 38 36 38 42 42 C44 32 40 22 32 14Z"
          fill="url(#ecoGrad)"
          opacity="0.9"
        />
        <path
          d="M18 46 Q32 52 46 46"
          stroke="#38bdf8"
          strokeWidth="2"
          fill="none"
          strokeLinecap="round"
        />
        <text
          x="32"
          y="36"
          textAnchor="middle"
          fill="#f8fafc"
          fontSize="14"
          fontWeight="800"
          fontFamily="system-ui, sans-serif"
        >
          E
        </text>
      </svg>
      <div className="flex flex-col leading-none">
        <span
          className={cn(
            "font-black tracking-tight bg-gradient-to-l from-sky-400 via-emerald-400 to-lime-400 bg-clip-text text-transparent",
            s.title
          )}
        >
          Econojin
        </span>
        {showTagline && (
          <span className={cn("text-slate-500 font-medium mt-0.5", s.sub)}>
            اکو · نو · ژین
          </span>
        )}
      </div>
    </Link>
  );
}
