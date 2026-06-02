"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Calendar,
  CloudSun,
  Wallet,
  Map,
  GraduationCap,
  Brain,
  Leaf,
  Users,
  Sprout,
  ArrowUpRight,
  Play,
  Shield,
} from "lucide-react";
import { MainLayout } from "@/components/layout/main-layout";
import { dashboardService, healthService } from "@/lib/api";
import { HOME_HERO } from "@/lib/media";
import { AnimatedStatCard } from "@/components/ui/AnimatedStatCard";

const modules = [
  { id: "calendar", name: "تقویم", desc: "رویداد و یادآور", icon: Calendar, color: "from-blue-500 to-cyan-400", href: "/calendar" },
  { id: "weather", name: "هواشناسی", desc: "پیش‌بینی دقیق", icon: CloudSun, color: "from-sky-500 to-blue-400", href: "/weather" },
  { id: "accounting", name: "حسابداری", desc: "درآمد و هزینه", icon: Wallet, color: "from-emerald-500 to-green-400", href: "/accounting" },
  { id: "gis", name: "GIS", desc: "تحلیل مکانی", icon: Map, color: "from-violet-500 to-purple-400", href: "/gis" },
  { id: "education", name: "آموزش", desc: "دوره و وبینار", icon: GraduationCap, color: "from-amber-500 to-orange-400", href: "/education" },
  { id: "psychology", name: "سلامت روان", desc: "مشاوره", icon: Brain, color: "from-pink-500 to-rose-400", href: "/psychology" },
  { id: "ecomining", name: "EcoCoin", desc: "پاداش سبز", icon: Leaf, color: "from-lime-500 to-emerald-400", href: "/ecomining" },
  { id: "farmers", name: "کشاورزان", desc: "مدیریت پروفایل", icon: Sprout, color: "from-green-600 to-lime-400", href: "/farmers" },
  { id: "community", name: "جامعه", desc: "شبکه اجتماعی", icon: Users, color: "from-indigo-500 to-blue-400", href: "/community" },
];

export default function DashboardPage() {
  const [stats, setStats] = useState({
    active_users: 0,
    active_modules: 0,
    monthly_growth_percent: 0,
    api_status: "offline",
  });

  useEffect(() => {
    Promise.all([dashboardService.stats(), healthService.check()])
      .then(([dash, health]) => {
        setStats({
          active_users: dash.active_users,
          active_modules: dash.active_modules,
          monthly_growth_percent: dash.monthly_growth_percent,
          api_status: health.status,
        });
      })
      .catch(() => setStats((s) => ({ ...s, api_status: "offline" })));
  }, []);

  return (
    <MainLayout>
      <div className="space-y-10 page-enter">
        <section className="relative overflow-hidden rounded-3xl border border-slate-800 min-h-[320px]">
          <Image src={HOME_HERO.image} alt="" fill className="object-cover" priority />
          <div className="absolute inset-0 bg-gradient-to-l from-slate-950 via-slate-950/90 to-slate-950/40" />
          <div className="relative z-10 p-8 md:p-12 flex flex-col md:flex-row md:items-end justify-between gap-8">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <span className="inline-flex items-center gap-2 text-xs font-medium text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full mb-4">
                <Shield className="h-3.5 w-3.5" />
                امنیت چندلایه · JWT · Rate Limit
              </span>
              <h1 className="text-4xl md:text-5xl font-black text-white text-balance max-w-xl">
                داشبورد اکو نوژین
              </h1>
              <p className="text-slate-400 mt-4 text-lg max-w-lg leading-relaxed">
                تجربه‌ای الهام‌گرفته از پلتفرم‌های جهانی — داده زنده، انیمیشن روان، و
                ماژول‌های یکپارچه.
              </p>
            </motion.div>
            {HOME_HERO.video && (
              <motion.a
                href={HOME_HERO.video}
                target="_blank"
                rel="noopener noreferrer"
                whileHover={{ scale: 1.03 }}
                className="flex items-center gap-3 px-5 py-3 rounded-2xl bg-white/10 backdrop-blur border border-white/15 text-sm shrink-0"
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-sky-500/30">
                  <Play className="h-5 w-5 text-white mr-[-2px]" />
                </span>
                ویدئو: کشاورزی پایدار
              </motion.a>
            )}
          </div>
        </section>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
          <AnimatedStatCard
            title="کاربران"
            value={stats.active_users}
            icon={<Users className="h-5 w-5" />}
            color="#3b82f6"
          />
          <AnimatedStatCard
            title="ماژول‌ها"
            value={stats.active_modules}
            icon={<Leaf className="h-5 w-5" />}
            color="#10b981"
          />
          <AnimatedStatCard
            title="رشد ماهانه"
            value={Math.round(stats.monthly_growth_percent)}
            suffix="٪"
            icon={<CloudSun className="h-5 w-5" />}
            color={stats.api_status === "healthy" ? "#22c55e" : "#f59e0b"}
          />
        </div>

        <div>
          <h2 className="text-xl font-bold text-slate-100 mb-5">ماژول‌ها</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {modules.map((mod, i) => (
              <Link href={mod.href} key={mod.id}>
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04 }}
                  whileHover={{ y: -4 }}
                  className="group h-full p-6 rounded-2xl border border-slate-800 bg-slate-900/40 hover:border-slate-600 hover:bg-slate-800/50 transition-all"
                >
                  <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${mod.color} flex items-center justify-center mb-4`}>
                    <mod.icon className="h-5 w-5 text-white" />
                  </div>
                  <h3 className="font-bold text-slate-100">{mod.name}</h3>
                  <p className="text-sm text-slate-500 mt-1">{mod.desc}</p>
                  <span className="inline-flex items-center text-xs text-slate-500 mt-4 group-hover:text-sky-400">
                    ورود <ArrowUpRight className="h-3.5 w-3.5 mr-1" />
                  </span>
                </motion.div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
