"use client";

import { ReactNode } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, LucideIcon } from "lucide-react";
import MissionBanner from "@/components/shared/MissionBanner";
import DataCollectionGuide from "@/components/shared/DataCollectionGuide";

interface ScientificModuleLayoutProps {
  icon: LucideIcon;
  title: string;
  subtitle: string;
  description: string;
  color: string;
  children: ReactNode;
  backHref?: string;
  citizenModuleType?: "hydrology" | "soil" | "rainfall" | "erosion" | "ndvi" | "carbon";
}

export function ScientificModuleLayout({
  icon: Icon,
  title,
  subtitle,
  description,
  color,
  children,
  backHref = "/",
  citizenModuleType
}: ScientificModuleLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-950">
      {/* Mission Banner - در بالای تمام ماژول‌ها */}
      <MissionBanner />
      
      {/* Hero Section مخصوص ماژول */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className={`absolute inset-0 bg-gradient-to-br ${color} opacity-20`} />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Link href={backHref} className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8 text-sm">
              <ArrowRight className="h-4 w-4" />
              بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-8">
              <div className={`p-5 rounded-3xl bg-gradient-to-br ${color} shadow-2xl`}>
                <Icon className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-emerald-400 text-sm font-medium mb-2">{subtitle}</p>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">{title}</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">{description}</p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Content */}
      <section className="container mx-auto px-6 py-12">
        {children}
        
        {/* Citizen Science Guide - در پایین هر ماژول */}
        {citizenModuleType && (
          <div className="mt-16">
            <DataCollectionGuide 
              moduleType={citizenModuleType} 
              moduleName={title} 
            />
          </div>
        )}
      </section>
    </div>
  );
}

// کامپوننت آمار ماژول
interface ModuleStatProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  color: string;
  trend?: string;
}

export function ModuleStat({ label, value, icon: Icon, color, trend }: ModuleStatProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all"
    >
      <div className="flex items-center justify-between mb-4">
        <Icon className="h-8 w-8" style={{ color }} />
        {trend && (
          <span className="text-xs px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded-full">
            {trend}
          </span>
        )}
      </div>
      <p className="text-3xl font-black text-white mb-1">{value}</p>
      <p className="text-sm text-slate-400">{label}</p>
    </motion.div>
  );
}

// کامپوننت کارت اطلاعات
interface InfoCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  color: string;
}

export function InfoCard({ title, description, icon: Icon, color }: InfoCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all"
    >
      <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${color} mb-4`}>
        <Icon className="h-6 w-6 text-white" />
      </div>
      <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
      <p className="text-slate-400 leading-relaxed">{description}</p>
    </motion.div>
  );
}
