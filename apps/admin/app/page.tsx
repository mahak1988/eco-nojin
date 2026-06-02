"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AdminHome() {
  const [health, setHealth] = useState<Record<string, unknown> | null>(null);
  const [stats, setStats] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    fetch(`${API}/api/v1/health`)
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setHealth({ status: "offline" }));
    fetch(`${API}/api/v1/dashboard/stats`)
      .then((r) => r.json())
      .then(setStats)
      .catch(() => null);
  }, []);

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">داشبورد مدیریت</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">
          <p className="text-slate-400 text-sm">وضعیت API</p>
          <p className="text-2xl font-bold mt-2 text-emerald-400">
            {String(health?.status ?? "نامشخص")}
          </p>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">
          <p className="text-slate-400 text-sm">ماژول‌های آنلاین</p>
          <p className="text-2xl font-bold mt-2">
            {stats?.active_modules != null ? String(stats.active_modules) : "—"}
          </p>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">
          <p className="text-slate-400 text-sm">کاربران (نمونه)</p>
          <p className="text-2xl font-bold mt-2">
            {stats?.active_users != null
              ? Number(stats.active_users).toLocaleString("fa-IR")
              : "—"}
          </p>
        </div>
      </div>
      <pre className="text-xs bg-slate-900 border border-slate-700 rounded-lg p-4 overflow-auto">
        {JSON.stringify({ health, stats }, null, 2)}
      </pre>
    </div>
  );
}
