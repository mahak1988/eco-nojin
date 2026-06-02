"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { MainLayout } from "@/components/layout/main-layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ChartCard } from "@/components/ui/ChartCard";
import { DataTable } from "@/components/ui/DataTable";
import { AnimatedStatCard } from "@/components/ui/AnimatedStatCard";
import { EventForm } from "@/components/calendar/EventForm";
import { Calendar, Search, RefreshCw, TrendingUp, Sparkles } from "lucide-react";
import { useCalendarEvents, useDeleteCalendarEvent } from "@/hooks/useCalendar";
import { MediaHero } from "@/components/ui/media-hero";
import { MODULE_MEDIA } from "@/lib/media";
import { useTranslations } from "next-intl";

export default function CalendarPage() {
  const t = useTranslations();
  const [searchQuery, setSearchQuery] = useState("");
  const [showForm, setShowForm] = useState(false);
  const { data, isLoading, error, refetch } = useCalendarEvents();
  const remove = useDeleteCalendarEvent();

  const rows = useMemo(() => {
    const items = data?.items ?? [];
    return items.map((e) => ({
      id: e.id,
      title: e.title,
      start: new Date(e.start_time).toLocaleString("fa-IR"),
      category: e.category,
    }));
  }, [data]);

  const filtered = useMemo(() => {
    if (!searchQuery.trim()) return rows;
    const q = searchQuery.toLowerCase();
    return rows.filter(
      (r) =>
        r.title.toLowerCase().includes(q) ||
        r.category.toLowerCase().includes(q)
    );
  }, [rows, searchQuery]);

  const columns = [
    { key: "id", title: "شناسه", sortable: true, width: "80px" },
    { key: "title", title: "عنوان", sortable: true },
    { key: "start", title: "زمان", sortable: true },
    {
      key: "category",
      title: "دسته",
      render: (v: string) => (
        <Badge variant="outline" className="border-slate-700">
          {v}
        </Badge>
      ),
    },
    {
      key: "actions",
      title: "",
      render: (_: unknown, row: { id: number }) => (
        <Button
          variant="ghost"
          size="sm"
          className="text-rose-400"
          onClick={() => remove.mutate(row.id)}
        >
          حذف
        </Button>
      ),
    },
  ];

  return (
    <MainLayout>
      <div className="space-y-8 page-enter">
        <MediaHero
          title={t("calendar.title")}
          subtitle="رویدادها با JWT و React Query"
          imageSrc={MODULE_MEDIA.calendar.image}
          accentColor="#3b82f6"
        />

        <div className="flex flex-wrap gap-2 justify-between">
          <Button variant="outline" onClick={() => refetch()} className="border-slate-700">
            <RefreshCw className={`h-4 w-4 ml-2 ${isLoading ? "animate-spin" : ""}`} />
            بروزرسانی
          </Button>
          <Button onClick={() => setShowForm(!showForm)} className="bg-blue-600">
            {t("calendar.new")}
          </Button>
        </div>

        {showForm && (
          <EventForm onSuccess={() => { setShowForm(false); refetch(); }} />
        )}

        {error && (
          <p className="text-rose-400 text-sm">
            خطا در بارگذاری — برای ایجاد رویداد وارد شوید
          </p>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <AnimatedStatCard
            title="کل رویدادها"
            value={data?.total ?? 0}
            icon={<Calendar className="h-5 w-5" />}
            color="#3b82f6"
          />
          <AnimatedStatCard
            title="نمایش"
            value={filtered.length}
            icon={<TrendingUp className="h-5 w-5" />}
            color="#10b981"
          />
          <AnimatedStatCard
            title="API"
            value={error ? 0 : 1}
            icon={<Sparkles className="h-5 w-5" />}
            color="#8b5cf6"
          />
        </div>

        <div className="relative">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <Input
            className="pr-10 border-slate-800"
            placeholder="جستجو..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <ChartCard
          title="رویدادها"
          icon={<Calendar className="h-5 w-5" />}
          data={filtered}
          chartType="bar"
          xKey="start"
          yKey="title"
          loading={isLoading}
        />

        <DataTable data={filtered} columns={columns} emptyMessage="رویدادی نیست" />
      </div>
    </MainLayout>
  );
}
