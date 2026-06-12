"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import { Play } from "lucide-react";

type Props = {
  title: string;
  subtitle: string;
  imageSrc: string;
  videoSrc?: string;
  accentColor?: string;
};

export function MediaHero({
  title,
  subtitle,
  imageSrc,
  videoSrc,
  accentColor = "#3b82f6",
}: Props) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative overflow-hidden rounded-2xl border border-slate-800/80 min-h-[220px] md:min-h-[280px]"
    >
      <Image
        src={imageSrc}
        alt=""
        fill
        className="object-cover opacity-40"
        priority
        sizes="(max-width: 768px) 100vw, 1200px"
      />
      <div
        className="absolute inset-0 bg-gradient-to-l from-slate-950 via-slate-950/85 to-transparent"
      />
      {videoSrc && (
        <a
          href={videoSrc}
          target="_blank"
          rel="noopener noreferrer"
          className="absolute left-6 bottom-6 flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-sm hover:bg-white/20 transition"
        >
          <Play className="h-4 w-4" style={{ color: accentColor }} />
          تماشای ویدئو معرفی
        </a>
      )}
      <div className="relative z-10 p-8 md:p-10 max-w-2xl">
        <motion.h2
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="text-2xl md:text-4xl font-bold text-white text-balance"
        >
          {title}
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-3 text-slate-300 text-sm md:text-base leading-relaxed"
        >
          {subtitle}
        </motion.p>
      </div>
      <div
        className="absolute top-0 right-0 w-1 h-full opacity-80"
        style={{ background: `linear-gradient(180deg, ${accentColor}, transparent)` }}
      />
    </motion.section>
  );
}
