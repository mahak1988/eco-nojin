"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AdminSystemPage() {
  const [data, setData] = useState<unknown>(null);

  useEffect(() => {
    fetch(`${API}/api/v1/health`).then((r) => r.json()).then(setData);
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">سلامت سیستم</h1>
      <pre className="bg-slate-900 border border-slate-700 rounded-lg p-4 text-sm overflow-auto">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}
