"use client";

import { useCallback, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { MainLayout } from "@/components/layout/main-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ChartCard } from "@/components/ui/ChartCard";
import { DataTable } from "@/components/ui/DataTable";
import { AnimatedStatCard } from "@/components/ui/AnimatedStatCard";
import {
  CloudSun,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  TrendingUp,
  AlertTriangle,
  Sparkles,
} from "lucide-react";
import { weatherService } from "@/lib/api";
import { useModuleData } from "@/hooks/useModuleData";
import { MediaHero } from "@/components/ui/media-hero";
import { MODULE_MEDIA } from "@/lib/media";

type ForecastRow = {
  day: string;
  temp: number;
  rain: number;
};

export default function WeatherPage() {
  const [location, setLocation] = useState("تهران");
  const [searchQuery, setSearchQuery] = useState("");

  const fetchWeather = useCallback(async () => {
    const [forecastRes, alertsRes] = await Promise.all([
      weatherService.getForecast(location, 7) as Promise<{
        forecast: Array<{ day: string; temp_c: number; rain_chance: number }>;
      }>,
      weatherService.getAlerts(location) as Promise<{
        alerts: Array<{ type: string; severity: string; message: string }>;
      }>,
    ]);

    const forecast: ForecastRow[] = forecastRes.forecast.map((f) => ({
      day: f.day,
      temp: f.temp_c,
      rain: f.rain_chance,
    }));

    return { forecast, alerts: alertsRes.alerts };
  }, [location]);

  const { data, loading, error, reload } = useModuleData(fetchWeather, {
    forecast: [] as ForecastRow[],
    alerts: [] as Array<{ type: string; severity: string; message: string }>,
  });

  const filtered = useMemo(() => {
    if (!searchQuery.trim()) return data.forecast;
    return data.forecast.filter((f) =>
      f.day.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [data.forecast, searchQuery]);

  const stats = [
    {
      title: "روزهای پیش‌بینی",
      value: data.forecast.length,
      icon: <CloudSun className="h-5 w-5" />,
      color: "#0ea5e9",
    },
    {
      title: "میانگین دما",
      value: data.forecast.length
        ? Math.round(
            data.forecast.reduce((s, f) => s + f.temp, 0) / data.forecast.length
          )
        : 0,
      icon: <TrendingUp className="h-5 w-5" />,
      color: "#10b981",
    },
    {
      title: "هشدارها",
      value: data.alerts.length,
      icon: <AlertTriangle className="h-5 w-5" />,
      color: "#f59e0b",
    },
    {
      title: "منطقه",
      value: location,
      icon: <CloudSun className="h-5 w-5" />,
      color: "#8b5cf6",
    },
  ];

  const columns = [
    { key: "day", title: "روز", sortable: true },
    { key: "temp", title: "دما (°C)", sortable: true },
    { key: "rain", title: "احتمال بارش %", sortable: true },
  ];

  return (
    <MainLayout>
      <div className="space-y-8 page-enter">
        <MediaHero
          title="هواشناسی کشاورزی"
          subtitle="پیش‌بینی هفت‌روزه و هشدارهای هوشمند — متصل به API"
          imageSrc={MODULE_MEDIA.weather.image}
          videoSrc={MODULE_MEDIA.weather.video}
          accentColor="#0ea5e9"
        />
        <motion.div
          initial={{ opacity: 0, y: -15 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-6 border-b border-slate-800"
        >
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3 text-slate-100">
              <span
                className="p-2 rounded-xl bg-slate-800/50 border border-slate-700"
                style={{ color: "#0ea5e9" }}
              >
                <CloudSun className="h-7 w-7" />
              </span>
              هواشناسی
            </h1>
            <p className="text-slate-400 mt-2 text-sm">
              پیش‌بینی و هشدار — داده از API
            </p>
          </div>
          <div className="flex gap-2.5 flex-wrap">
            <Input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-36 bg-slate-950 border-slate-700"
              placeholder="منطقه"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => reload()}
              className="border-slate-700 text-slate-300"
            >
              <RefreshCw
                className={`h-4 w-4 ml-2 ${loading ? "animate-spin" : ""}`}
              />
              بروزرسانی
            </Button>
          </div>
        </motion.div>

        {error && (
          <p className="text-sm text-rose-400 bg-rose-500/10 border border-rose-500/30 rounded-lg px-4 py-2">
            {error}
          </p>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {stats.map((stat, i) => (
            <AnimatedStatCard key={i} {...stat} />
          ))}
        </div>

        {data.alerts.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {data.alerts.map((a, i) => (
              <Badge key={i} variant="outline" className="border-amber-600/50 text-amber-200">
                {a.message}
              </Badge>
            ))}
          </div>
        )}

        <ChartCard
          title="نمودار دما"
          icon={<CloudSun className="h-5 w-5" />}
          data={filtered}
          chartType="line"
          xKey="day"
          yKey="temp"
          colors={["#0ea5e9"]}
          loading={loading}
        />

        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader className="border-b border-slate-800/50">
            <CardTitle className="text-slate-100 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-sky-400" />
              پیش‌بینی هفت‌روزه
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <DataTable
              data={filtered}
              columns={columns}
              searchKeys={["day"]}
              emptyMessage="داده‌ای دریافت نشد"
            />
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
