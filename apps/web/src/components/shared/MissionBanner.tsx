"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Heart, Globe, Users, Sparkles, X, ChevronDown } from "lucide-react";

export default function MissionBanner() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  if (isDismissed) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="relative overflow-hidden bg-gradient-to-l from-emerald-900/40 via-green-800/30 to-teal-900/40 border-b border-emerald-500/20"
    >
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 20% 50%, rgba(16, 185, 129, 0.3) 0%, transparent 50%),
                           radial-gradient(circle at 80% 50%, rgba(20, 184, 166, 0.3) 0%, transparent 50%)`
        }} />
      </div>

      <div className="container mx-auto px-6 py-4 relative">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-4 flex-1">
            <motion.div
              animate={{ rotate: [0, 5, -5, 0] }}
              transition={{ duration: 4, repeat: Infinity }}
              className="flex-shrink-0"
            >
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-emerald-500 to-green-600 shadow-lg shadow-emerald-500/30">
                <Heart className="h-5 w-5 text-white" />
              </div>
            </motion.div>
            
            <div className="flex-1 min-w-0">
              <p className="text-sm md:text-base text-emerald-100 font-bold leading-relaxed">
                <span className="text-emerald-400">🌱</span>{" "}
                این پاسخ ما به فقر و نابرابری است:{" "}
                <span className="bg-gradient-to-l from-emerald-300 to-teal-300 bg-clip-text text-transparent font-black">
                  علم را به زبان مردم بیاوریم، نه مردم را به زبان علم مجبور کنیم
                </span>
              </p>
              
              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="mt-3 pt-3 border-t border-emerald-500/20">
                      <p className="text-sm text-slate-300 leading-relaxed mb-3">
                        ما باور داریم که هر کشاورز، هر روستایی، هر انسانی در هر نقطه از جهان،
                        حق دسترسی به علم روز را دارد - حتی بدون سنسور گران‌قیمت، حتی بدون اینترنت پرسرعت.
                      </p>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div className="flex items-center gap-2 text-xs text-slate-300">
                          <Globe className="h-4 w-4 text-emerald-400" />
                          <span>دسترسی جهانی و رایگان</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-slate-300">
                          <Users className="h-4 w-4 text-emerald-400" />
                          <span>علم شهروندی برای همه</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-slate-300">
                          <Sparkles className="h-4 w-4 text-emerald-400" />
                          <span>ابزارهای ساده، نتایج دقیق</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="hidden md:flex items-center gap-1 px-3 py-1.5 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/30 rounded-lg text-xs text-emerald-300 transition-all"
            >
              {isExpanded ? "بستن" : "بیشتر"}
              <ChevronDown className={`h-3 w-3 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
            </button>
            <button
              onClick={() => setIsDismissed(true)}
              className="p-1.5 hover:bg-slate-800/50 rounded-lg text-slate-400 hover:text-slate-200 transition-colors"
              aria-label="بستن"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
