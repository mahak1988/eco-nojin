"use client";

import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

interface Feature {
  icon: LucideIcon;
  title: string;
  description: string;
}

interface Stat {
  value: string;
  label: string;
}

interface AuthWelcomePanelProps {
  badge: string;
  title: string;
  subtitle: string;
  description: string;
  features: Feature[];
  stats?: Stat[];
  accentGradient: string;
}

export function AuthWelcomePanel({
  badge,
  title,
  subtitle,
  description,
  features,
  stats,
  accentGradient,
}: AuthWelcomePanelProps) {
  return (
    <div className="hidden lg:flex relative flex-col justify-between p-12 overflow-hidden">
      {/* ================================================================== */}
      {/* 🌿 Ambient Background - Nature Distilled */}
      {/* ================================================================== */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-[#0a0a0c] via-[#0f1419] to-[#0a0a0c]" />
        <div
          className="absolute inset-0 opacity-60"
          style={{
            backgroundImage: accentGradient,
          }}
        />
        {/* Noise texture */}
        <div
          className="absolute inset-0 opacity-[0.03] mix-blend-overlay"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
          }}
        />
      </div>

      {/* Decorative orbs */}
      <div className="absolute top-20 right-20 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-20 left-20 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />

      {/* ================================================================== */}
      {/* 📝 Content */}
      {/* ================================================================== */}
      <div className="relative z-10">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.05] backdrop-blur-xl border border-white/10 rounded-full text-xs font-medium text-zinc-300 mb-8"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          {badge}
        </motion.div>

        {/* Title */}
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-4xl xl:text-5xl font-black text-white mb-4 tracking-tight leading-tight"
        >
          {title}
        </motion.h2>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-xl text-emerald-300 font-medium mb-6"
        >
          {subtitle}
        </motion.p>

        {/* Description */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-base text-zinc-400 leading-relaxed max-w-md"
        >
          {description}
        </motion.p>
      </div>

      {/* ================================================================== */}
      {/* ✨ Features List */}
      {/* ================================================================== */}
      <div className="relative z-10 space-y-4 my-10">
        {features.map((feature, idx) => {
          const Icon = feature.icon;
          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 + idx * 0.1 }}
              className="flex items-start gap-4 p-4 bg-white/[0.03] backdrop-blur-xl border border-white/5 rounded-2xl hover:bg-white/[0.05] hover:border-white/10 transition-all group"
            >
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/10 border border-emerald-500/20 group-hover:scale-110 transition-transform">
                <Icon className="h-5 w-5 text-emerald-400" />
              </div>
              <div className="flex-1">
                <h4 className="text-sm font-bold text-white mb-1">{feature.title}</h4>
                <p className="text-xs text-zinc-400 leading-relaxed">{feature.description}</p>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* ================================================================== */}
      {/* 📊 Stats */}
      {/* ================================================================== */}
      {stats && stats.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1 }}
          className="relative z-10 grid grid-cols-3 gap-4 pt-8 border-t border-white/10"
        >
          {stats.map((stat, idx) => (
            <div key={idx} className="text-center">
              <div className="text-2xl font-black text-white tabular-nums mb-1">
                {stat.value}
              </div>
              <div className="text-xs text-zinc-500">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      )}
    </div>
  );
}