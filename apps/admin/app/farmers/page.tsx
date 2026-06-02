"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AdminFarmersPage() {
  const [farmers, setFarmers] = useState<Array<{ id: number; name: string }>>([]);

  useEffect(() => {
    fetch(`${API}/api/v1/farmers/?limit=50`)
      .then((r) => r.json())
      .then((d) => setFarmers(d.farmers || []))
      .catch(() => setFarmers([]));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">کشاورزان</h1>
      <table className="w-full text-sm border border-slate-700 rounded-lg overflow-hidden">
        <thead className="bg-slate-800">
          <tr>
            <th className="text-right p-3">شناسه</th>
            <th className="text-right p-3">نام</th>
          </tr>
        </thead>
        <tbody>
          {farmers.map((f) => (
            <tr key={f.id} className="border-t border-slate-800">
              <td className="p-3">{f.id}</td>
              <td className="p-3">{f.name}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
