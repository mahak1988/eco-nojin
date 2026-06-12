"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { FileText, Download, Printer, ArrowRight, FileJson, FileSpreadsheet } from "lucide-react";
import Link from "next/link";
import { useAnalysisHistory } from "@/lib/api/hooks/useSoilWater";

export default function ReportsPage() {
  const { data: history = [] } = useAnalysisHistory();
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const selected = history.find((h) => h.id === selectedId);

  const handlePrint = () => {
    window.print();
  };

  const handleExportJSON = () => {
    if (!selected) return;
    const blob = new Blob([JSON.stringify(selected, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `report-${selected.id}.json`;
    a.click();
  };

  return (
    <div className="min-h-screen relative p-6 lg:p-10">
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
      </div>

      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <Link href="/soil-water" className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-emerald-400 mb-4">
            <ArrowRight className="h-4 w-4" /> بازگشت
          </Link>
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-600">
              <FileText className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-white">گزارش‌های تحلیلی</h1>
              <p className="text-zinc-400 mt-1">{history.length} گزارش ذخیره شده</p>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-2">
            {history.length === 0 ? (
              <div className="p-8 bg-white/[0.03] border border-white/10 rounded-2xl text-center">
                <FileText className="h-12 w-12 text-zinc-600 mx-auto mb-3" />
                <p className="text-zinc-400">هنوز گزارشی ثبت نشده</p>
                <Link href="/soil-water" className="text-sm text-emerald-400 mt-2 inline-block">
                  ایجاد اولین تحلیل
                </Link>
              </div>
            ) : (
              history.map((item) => (
                <button key={item.id} onClick={() => setSelectedId(item.id!)}
                  className={`w-full p-4 rounded-xl border text-right transition-all ${
                    selectedId === item.id
                      ? "bg-emerald-500/10 border-emerald-500/30"
                      : "bg-white/[0.03] border-white/10 hover:bg-white/[0.05]"
                  }`}>
                  <p className="text-sm font-medium text-white">{item.title}</p>
                  <p className="text-xs text-zinc-500 mt-1">
                    {new Date(item.created_at || "").toLocaleDateString("fa-IR")}
                  </p>
                </button>
              ))
            )}
          </div>

          <div className="lg:col-span-2">
            {selected ? (
              <motion.div key={selectedId} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="p-6 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
                  <div>
                    <h2 className="text-xl font-bold text-white">{selected.title}</h2>
                    <p className="text-xs text-zinc-500 mt-1">
                      {new Date(selected.created_at || "").toLocaleString("fa-IR")}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={handlePrint} className="p-2 bg-white/[0.03] border border-white/10 rounded-lg text-zinc-300 hover:bg-white/[0.05]">
                      <Printer className="h-4 w-4" />
                    </button>
                    <button onClick={handleExportJSON} className="p-2 bg-white/[0.03] border border-white/10 rounded-lg text-zinc-300 hover:bg-white/[0.05]">
                      <FileJson className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <div className="space-y-4">
                  {selected.ldn && (
                    <div className="p-4 bg-white/[0.02] rounded-xl">
                      <h3 className="text-sm font-bold text-emerald-400 mb-2">شاخص LDN</h3>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div><span className="text-zinc-500">امتیاز:</span> <span className="text-white font-bold">{selected.ldn.ldn_score.toFixed(2)}</span></div>
                        <div><span className="text-zinc-500">وضعیت:</span> <span className="text-white">{selected.ldn.status}</span></div>
                      </div>
                    </div>
                  )}
                  {selected.ndvi && (
                    <div className="p-4 bg-white/[0.02] rounded-xl">
                      <h3 className="text-sm font-bold text-green-400 mb-2">شاخص NDVI</h3>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div><span className="text-zinc-500">مقدار:</span> <span className="text-white font-bold">{selected.ndvi.ndvi.toFixed(3)}</span></div>
                        <div><span className="text-zinc-500">سلامت:</span> <span className="text-white">{selected.ndvi.vegetation_health}</span></div>
                      </div>
                    </div>
                  )}
                  {selected.rusle && (
                    <div className="p-4 bg-white/[0.02] rounded-xl">
                      <h3 className="text-sm font-bold text-amber-400 mb-2">فرسایش RUSLE</h3>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div><span className="text-zinc-500">اتلاف:</span> <span className="text-white font-bold">{selected.rusle.soil_loss_tons_per_ha.toFixed(2)} t/ha</span></div>
                        <div><span className="text-zinc-500">خطر:</span> <span className="text-white">{selected.rusle.erosion_risk_category}</span></div>
                      </div>
                    </div>
                  )}
                  {selected.carbon && (
                    <div className="p-4 bg-white/[0.02] rounded-xl">
                      <h3 className="text-sm font-bold text-teal-400 mb-2">ترسیب کربن</h3>
                      <div className="text-sm">
                        <span className="text-zinc-500">ذخیره:</span> <span className="text-white font-bold">{selected.carbon.carbon_stock_tons_per_ha.toFixed(2)} t/ha</span>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ) : (
              <div className="p-12 bg-white/[0.03] border border-white/10 rounded-2xl text-center">
                <FileSpreadsheet className="h-16 w-16 text-zinc-600 mx-auto mb-4" />
                <p className="text-zinc-400">یک گزارش را انتخاب کنید</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
