"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AdminModulesPage() {
  const [modules, setModules] = useState<Array<{ id: string; status: string }>>([]);

  useEffect(() => {
    fetch(`${API}/api/v1/modules`)
      .then((r) => r.json())
      .then((d) => setModules(d.modules || []))
      .catch(() => setModules([]));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">ماژول‌های سیستم</h1>
      <ul className="space-y-2">
        {modules.map((m) => (
          <li
            key={m.id}
            className="flex justify-between border border-slate-700 rounded-lg px-4 py-3 bg-slate-900"
          >
            <span>{m.id}</span>
            <span className="text-emerald-400">{m.status}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
