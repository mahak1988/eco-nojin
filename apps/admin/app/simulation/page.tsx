"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AdminSimulationPage() {
  const [out, setOut] = useState("");

  const run = async () => {
    const res = await fetch(`${API}/api/v1/simulation/rothc`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        initial_soc: 45,
        clay_percent: 30,
        mean_temp_c: 14,
        annual_rain_mm: 320,
        years: 3,
      }),
    });
    setOut(JSON.stringify(await res.json(), null, 2));
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">شبیه‌ساز RothC</h1>
      <button onClick={run} className="px-4 py-2 bg-teal-600 rounded-lg mb-4">
        اجرا
      </button>
      <pre className="text-xs bg-slate-900 p-4 rounded-lg overflow-auto">{out}</pre>
    </div>
  );
}
