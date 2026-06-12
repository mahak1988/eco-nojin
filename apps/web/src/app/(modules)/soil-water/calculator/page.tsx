"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Calculator, ArrowRight, Leaf, Droplets, Sprout, TrendingDown } from "lucide-react";
import Link from "next/link";

export default function CalculatorPage() {
  return (
    <div className="min-h-screen relative p-6 lg:p-10">
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div className="absolute inset-0 opacity-50" style={{
          backgroundImage: `radial-gradient(at 30% 30%, rgba(16, 185, 129, 0.15) 0px, transparent 50%)`,
        }} />
      </div>

      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <Link href="/soil-water" className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-emerald-400 mb-4">
            <ArrowRight className="h-4 w-4" /> بازگشت به داشبورد
          </Link>
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600">
              <Calculator className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-white">ماشین‌حساب‌های تخصصی</h1>
              <p className="text-zinc-400 mt-1">محاسبات پیشرفته با ورودی‌های کامل</p>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {[
            { title: "ماشین‌حساب LDN", desc: "محاسبه خنثایی تخریب زمین با پارامترهای کامل", icon: Leaf, color: "emerald", href: "/soil-water" },
            { title: "ماشین‌حساب بیلان آبی", desc: "تحلیل کامل بیلان آب خاک", icon: Droplets, color: "blue", href: "/soil-water" },
            { title: "ماشین‌حساب NDVI/NDWI", desc: "شاخص‌های طیفی پوشش گیاهی و آب", icon: Sprout, color: "green", href: "/soil-water" },
            { title: "ماشین‌حساب RUSLE", desc: "محاسبه فرسایش خاک با ۵ فاکتور", icon: TrendingDown, color: "amber", href: "/soil-water" },
          ].map((item, i) => {
            const Icon = item.icon;
            return (
              <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
                className="p-6 bg-white/[0.03] border border-white/10 rounded-2xl hover:border-emerald-500/30 transition-all">
                <Icon className="h-8 w-8 text-emerald-400 mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
                <p className="text-sm text-zinc-400 mb-4">{item.desc}</p>
                <Link href={item.href} className="inline-flex items-center gap-2 text-sm text-emerald-400 hover:text-emerald-300">
                  باز کردن <ArrowRight className="h-4 w-4" />
                </Link>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
