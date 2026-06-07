"use client";

import Link from "next/link";
import { ArrowRight, Monitor } from "lucide-react";

export default function DesktopPage() {
  return (
    <div className="container mx-auto px-6 py-12">
      <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8">
        <ArrowRight className="h-4 w-4" /> بازگشت به خانه
      </Link>
      
      <div className="mb-10">
        <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-slate-500 to-gray-500 mb-4">
          <Monitor className="h-10 w-10 text-white" />
        </div>
        <h1 className="text-4xl font-bold text-white mb-3">میزکار</h1>
        <p className="text-lg text-slate-400">داشبورد شخصی‌سازی‌شده</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map(i => (
          <div key={i} className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all">
            <div className="h-32 bg-gradient-to-br from-slate-500 to-gray-500 rounded-xl mb-4 opacity-20" />
            <h3 className="text-lg font-bold text-white mb-2">پروژه {i}</h3>
            <p className="text-sm text-slate-400 mb-4">توضیحات پروژه میزکار شماره {i}</p>
            <button onClick={() => console.log("Button clicked")}  className="text-emerald-400 hover:text-emerald-300 text-sm font-medium">مشاهده جزئیات ←</button>
          </div>
        ))}
      </div>
    </div>
  );
}