/**
 * ═════════════════════════════════
 *  HeroSection ℓ هوروی Full-Bleed Econojin
 *  الهال از: Benjamin Hardman
 * ═════════════════════════════════
 */

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export interface HeroSectionProps {
  image?: string;
  video?: string;
  overlay?: "dark" | "light" | "medium";
  title: string;
  subtitle?: string;
  height?: "screen" | "large" | "medium";
  align?: "center" | "start" | "end";
  children?: React.ReactNode;
  className?: string;
}

const overlayMap = {
  dark:   "bg-gradient-to-b from-black/60 via-black/30 to-transparent",
  medium: "bg-gradient-to-b from-black/40 via-black/20 to-transparent",
  light:  "bg-gradient-to-b from-eco-50/80 via-eco-50/40 to-transparent",
};

const heightMap = {
  screen: "h-screen min-h-[600px]",
  large:  "h-[80vh] min-h-[500px]",
  medium: "h-[60vh] min-h-[400px]",
};

export function HeroSection({
  image,
  video,
  overlay = "dark",
  title,
  subtitle,
  height = "screen",
  align = "center",
  children,
  className,
}: HeroSectionProps) {
  return (
    <section
      className={cn(
        "relative overflow-hidden flex items-center",
        heightMap[height],
        overlay === "light" ? "text-eco-900" : "text-white",
        className
      )}
    >
      {video ? (
        <video autoPlay muted loop playsInline className="absolute inset-0 h-full w-full object-cover">
          <source src={video} type="video/mp4" />
        </video>
      ) : image ? (
        <img src={image} alt="" className="absolute inset-0 h-full w-full object-cover" loading="eager" />
      ) : (
        <div className="absolute inset-0 bg-eco-gradient" />
      )}
      <div className={cn("absolute inset-0 z-10", overlayMap[overlay])} />
      <div className="container-main relative z-20 w-full">
        <div className={cn("max-w-3xl", align === "center" && "mx-auto text-center", align === "end" && "ms-auto text-end")}>
          <motion.h1 initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, ease: "easeOut" }} className="font-display text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold leading-[1.1] text-balance">{title}</motion.h1>
          {subtitle && (<motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.2, ease: "easeOut" }} className={cn("mt-4 md:mt-6 text-lg md:text-xll leading-relaxed", overlay === "light" ? "text-eco-700" : "text-white/80")}>{subtitle}</motion.p>)}
          {children && (<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.4, ease: "easeOut" }} className="mt-8 md:mt-10 flex flex-wrap gap-4">{children}</motion.div>)}
        </div>
      </div>
      {height === "screen" && (<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.5 }} className="absolute bottom-8 start-1/2 z-20 -translate-x-1/2"><div className="flex flex-col items-center gap-2 text-white/60"><span className="text-xs font-medium tracking-widest uppercase">Scroll</span><motion.div animate={{ y: [0, 8, 0] }} transition={{ repeat: Infinity, duration: 2 }}><svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" /></svg></motion.div></div></motion.div>)}
    </section>
  );
}