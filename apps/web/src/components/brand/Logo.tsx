import Link from "next/link";
import { cn } from "@/lib/utils";

interface LogoProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  showText?: boolean;
}

export function Logo({ size = "md", className, showText = true }: LogoProps) {
  const dimensions = {
    sm: { width: 140, height: 70, text: "text-base" },
    md: { width: 180, height: 90, text: "text-xl" },
    lg: { width: 240, height: 120, text: "text-2xl" },
  };

  const { width, height, text } = dimensions[size];

  return (
    <Link href="/" className={cn("flex items-center gap-3 group", className)}>
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity duration-500" />
        <svg width={width} height={height} viewBox="0 0 240 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="relative z-10 transition-transform duration-500 group-hover:scale-105">
          <defs>
            <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#047857" />
              <stop offset="50%" stopColor="#10b981" />
              <stop offset="100%" stopColor="#2dd4bf" />
            </linearGradient>
            <linearGradient id="leafGradient1" x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#059669" />
              <stop offset="100%" stopColor="#34d399" />
            </linearGradient>
            <linearGradient id="leafGradient2" x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#0d9488" />
              <stop offset="100%" stopColor="#5eead4" />
            </linearGradient>
          </defs>
          <text x="10" y="75" fontFamily="system-ui, -apple-system, sans-serif" fontSize="52" fontWeight="800" fill="url(#logoGradient)">Eco</text>
          <path d="M 78 62 Q 88 88, 102 58" stroke="url(#logoGradient)" strokeWidth="5" strokeLinecap="round" fill="none" />
          <text x="100" y="75" fontFamily="system-ui, -apple-system, sans-serif" fontSize="52" fontWeight="800" fill="url(#logoGradient)">N</text>
          <path d="M 118 55 Q 120 40, 125 30" stroke="url(#logoGradient)" strokeWidth="3" strokeLinecap="round" fill="none" />
          <path d="M 125 32 Q 115 25, 110 28 Q 105 31, 108 35 Q 111 39, 125 32" fill="url(#leafGradient1)" />
          <path d="M 125 30 Q 138 18, 145 22 Q 152 26, 148 32 Q 144 38, 125 30" fill="url(#leafGradient2)" />
          <text x="148" y="75" fontFamily="system-ui, -apple-system, sans-serif" fontSize="52" fontWeight="700" fill="url(#logoGradient)">ojin</text>
        </svg>
      </div>
      {showText && (
        <div className="flex flex-col leading-none mr-2">
          <span className={cn("font-black text-white tracking-tight", text)}>اکو نوین</span>
          <span className="text-[8px] font-bold text-emerald-400 tracking-[0.3em] mt-1.5 uppercase">ECONOJIN</span>
        </div>
      )}
    </Link>
  );
}
