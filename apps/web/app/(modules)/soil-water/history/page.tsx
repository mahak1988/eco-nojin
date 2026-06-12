"use client";

import { motion } from "framer-motion";
import { History, Trash2, ArrowRight, Calendar, TrendingUp } from "lucide-react";
import Link from "next/link";
import { useAnalysisHistory, useDeleteAnalysis } from "@/lib/api/hooks/useSoilWater";

export default function HistoryPage() {
  const { data: history = [], refetch } = useAnalysisHistory();
  const deleteM = useDeleteAnalysis();

  const handleDelete = (id: number) => {
    if (confirm("آیا از حذف این تحلیل مطمئن هستید؟")) {
      deleteM.mutate(id, { onSuccess: () => refetch() });
    }
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
            <div className="p-3 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-600">
              <History className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-white">تاریخچه تحلیل‌ها</h1>
              <p className="text-zinc-400 mt-1">{history.length} تحلیل ثبت شده</p>
            </div>
          </div>
        </div>

        {history.length === 0 ? (
          <div className="p-12 bg-white/[0.03] border border-white/10 rounded-2xl text-center">
            <History className="h-16 w-16 text-zinc-600 mx-auto mb-4" />
            <p className="text-zinc-400 mb-2">هنوز تحلیلی ثبت نشده است</p>
            <Link href="/soil-water" className="text-emerald-400 hover:text-emerald-300 text-sm">
              ایجاد اولین تحلیل →
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {history.map((item, i) => (
              <motion.div key={item.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}
                className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl hover:border-white/20 transition-all">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-zinc-500">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(item.created_at || "").toLocaleString("fa-IR")}
                      </span>
                      {item.ldn && (
                        <span className="flex items-center gap-1">
                          <TrendingUp className="h-3 w-3" />
                          LDN: {item.ldn.ldn_score.toFixed(1)}
                        </span>
                      )}
                      {item.ndvi && <span>NDVI: {item.ndvi.ndvi.toFixed(2)}</span>}
                      {item.rusle && <span>فرسایش: {item.rusle.soil_loss_tons_per_ha.toFixed(1)} t/ha</span>}
                    </div>
                  </div>
                  <button onClick={() => handleDelete(item.id!)}
                    className="p-2 text-zinc-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-all">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
