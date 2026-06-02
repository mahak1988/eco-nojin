"use client";

import { useCallback, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MainLayout } from "@/components/layout/main-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ChartCard } from "@/components/ui/ChartCard";
import { DataTable } from "@/components/ui/DataTable";
import { AnimatedStatCard } from "@/components/ui/AnimatedStatCard";
import { MediaHero } from "@/components/ui/media-hero";
import {
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  TrendingUp,
  AlertTriangle,
  Sparkles,
  LayoutGrid,
} from "lucide-react";
import { useModuleData } from "@/hooks/useModuleData";
import type { ModuleDefinition } from "@/lib/modules";
import { MODULE_MEDIA } from "@/lib/media";
import { api } from "@/lib/api";

export type ModuleDashboardData = {
  stats: { title: string; value: number | string }[];
  rows: Record<string, unknown>[];
  chartData?: Record<string, unknown>[];
  raw?: unknown;
};

type Props = {
  config: ModuleDefinition;
  fetchData?: () => Promise<ModuleDashboardData>;
  children?: React.ReactNode;
  onNew?: () => void;
};

async function defaultFetch(config: ModuleDefinition): Promise<ModuleDashboardData> {
  const res = await api.get<Record<string, unknown>>(`${config.apiBase}/`);
  const items = (res.items as Record<string, unknown>[]) || [];
  const total = (res.total as number) ?? items.length;
  return {
    stats: [
      { title: "مجموع", value: total },
      { title: "نمایش", value: items.length },
      { title: "فعال", value: items.length },
      { title: "API", value: 1 },
    ],
    rows: items,
    chartData: items,
    raw: res,
  };
}

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.06 } },
};

const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0 },
};

export function ModuleDashboard({ config, fetchData, children, onNew }: Props) {
  const [searchQuery, setSearchQuery] = useState("");
  const Icon = config.icon;
  const media = MODULE_MEDIA[config.id];

  const loader = useCallback(
    () => (fetchData ? fetchData() : defaultFetch(config)),
    [config, fetchData]
  );

  const { data, loading, error, reload } = useModuleData(loader, {
    stats: [],
    rows: [],
    chartData: [],
  });

  const filteredRows = useMemo(() => {
    if (!searchQuery.trim()) return data.rows;
    const q = searchQuery.toLowerCase();
    return data.rows.filter((row) =>
      Object.values(row).some((v) => String(v).toLowerCase().includes(q))
    );
  }, [data.rows, searchQuery]);

  const columns =
    config.tableKeys?.map((c) => ({
      key: c.key,
      title: c.title,
      sortable: true,
    })) ||
    (filteredRows[0]
      ? Object.keys(filteredRows[0]).slice(0, 5).map((k) => ({
          key: k,
          title: k,
          sortable: true,
        }))
      : []);

  return (
    <MainLayout>
      <motion.div variants={container} initial="hidden" animate="show" className="space-y-8 page-enter">
        <motion.div variants={item}>
          <MediaHero
            title={config.title}
            subtitle={config.description}
            imageSrc={media.image}
            videoSrc={media.video}
            accentColor={config.color}
          />
        </motion.div>

        <motion.div
          variants={item}
          className="flex flex-col lg:flex-row lg:items-center justify-between gap-4"
        >
          <div className="flex items-center gap-3">
            <div
              className="p-2.5 rounded-xl border border-slate-700/80 bg-slate-900/60"
              style={{ color: config.color }}
            >
              <Icon className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-slate-100">پنل عملیاتی</h2>
              <p className="text-xs text-slate-500">داده زنده از API · امنیت JWT</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              className="border-slate-700"
              onClick={() => reload()}
            >
              <RefreshCw className={`h-4 w-4 ml-2 ${loading ? "animate-spin" : ""}`} />
              بروزرسانی
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="border-slate-700"
              onClick={() => {
                const blob = new Blob([JSON.stringify(data.rows, null, 2)], {
                  type: "application/json",
                });
                const a = document.createElement("a");
                a.href = URL.createObjectURL(blob);
                a.download = `${config.id}-export.json`;
                a.click();
              }}
            >
              <Download className="h-4 w-4 ml-2" /> خروجی
            </Button>
            <Button
              size="sm"
              style={{ backgroundColor: config.color }}
              onClick={onNew}
            >
              <Plus className="h-4 w-4 ml-2" /> جدید
            </Button>
          </div>
        </motion.div>

        <AnimatePresence>
          {error && (
            <motion.p
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0 }}
              className="text-sm text-rose-300 bg-rose-500/10 border border-rose-500/30 rounded-xl px-4 py-3"
            >
              {error}
              {!String(error).includes("401") && (
                <span className="block text-xs mt-1 text-slate-400">
                  سرور API را روی پورت ۸۰۰۰ اجرا کنید
                </span>
              )}
            </motion.p>
          )}
        </AnimatePresence>

        {children && <motion.div variants={item}>{children}</motion.div>}

        <motion.div variants={item} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {data.stats.map((stat, i) => (
            <AnimatedStatCard
              key={i}
              title={stat.title}
              value={typeof stat.value === "number" ? stat.value : parseInt(String(stat.value), 10) || 0}
              icon={
                i === 0 ? (
                  <Icon className="h-5 w-5" />
                ) : i === 1 ? (
                  <TrendingUp className="h-5 w-5" />
                ) : (
                  <LayoutGrid className="h-5 w-5" />
                )
              }
              color={config.color}
            />
          ))}
        </motion.div>

        <motion.div variants={item} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <Input
              className="pr-10 bg-slate-950/50 border-slate-800 h-11"
              placeholder="جستجو در جدول..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Button variant="secondary" className="bg-slate-800 border-slate-700 h-11">
            <Filter className="h-4 w-4 ml-2" /> فیلتر پیشرفته
          </Button>
        </motion.div>

        {(data.chartData?.length ?? 0) > 0 && (
          <motion.div variants={item}>
            <ChartCard
              title={`تحلیل ${config.title}`}
              icon={<Sparkles className="h-5 w-5" />}
              data={data.chartData || []}
              chartType="bar"
              xKey={config.tableKeys?.[0]?.key || Object.keys(data.chartData![0] || {})[0] || "id"}
              yKey={config.tableKeys?.[1]?.key || Object.keys(data.chartData![0] || {})[1] || "name"}
              colors={[config.color, "#10b981", "#f59e0b"]}
              loading={loading}
            />
          </motion.div>
        )}

        <motion.div variants={item}>
          <Card className="border-slate-800/80 bg-slate-900/30 backdrop-blur-md overflow-hidden">
            <CardHeader className="border-b border-slate-800/60 bg-slate-900/50">
              <CardTitle className="flex items-center gap-2 text-slate-100">
                <AlertTriangle className="h-4 w-4 text-amber-400/80" />
                جدول داده‌ها
                <span className="text-xs font-normal text-slate-500 mr-auto">
                  {filteredRows.length} ردیف
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <DataTable
                data={filteredRows}
                columns={columns}
                emptyMessage="داده‌ای یافت نشد — اتصال API را بررسی کنید"
              />
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </MainLayout>
  );
}
