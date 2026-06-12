"use client";

import { useState } from "react";
import type { WaterBalance } from "@/api/water";
import { SimulationControls } from "./SimulationControls";

const dummyScenarios = [
  { id: 1, name: "سناریو پایه" },
  { id: 2, name: "سناریو کم‌آبی" },
];

const dummyProfiles = [
  { id: 1, name: "خاک سبک" },
  { id: 2, name: "خاک سنگین" },
];

export default function HydrologyPage() {
  const [results, setResults] = useState<WaterBalance[]>([]);

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-xl font-semibold">ماژول آب و خاک</h1>

      <SimulationControls
        scenarios={dummyScenarios}
        soilProfiles={dummyProfiles}
        onResults={setResults}
      />

      {results.length > 0 && (
        <div className="border rounded-lg p-4 bg-white shadow-sm">
          <h2 className="font-medium mb-2">نتایج شبیه‌سازی (خلاصه)</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm border">
              <thead>
                <tr className="bg-gray-50">
                  <th className="border px-2 py-1">تاریخ</th>
                  <th className="border px-2 py-1">بارش</th>
                  <th className="border px-2 py-1">آبیاری</th>
                  <th className="border px-2 py-1">رواناب</th>
                  <th className="border px-2 py-1">نفوذ عمقی</th>
                  <th className="border px-2 py-1">رطوبت خاک</th>
                  <th className="border px-2 py-1">نسخه مدل</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r) => (
                  <tr key={r.id}>
                    <td className="border px-2 py-1">
                      {new Date(r.date).toLocaleDateString("fa-IR")}
                    </td>
                    <td className="border px-2 py-1 text-right">
                      {r.precipitation ?? "-"}
                    </td>
                    <td className="border px-2 py-1 text-right">
                      {r.irrigation ?? "-"}
                    </td>
                    <td className="border px-2 py-1 text-right">
                      {r.runoff ?? "-"}
                    </td>
                    <td className="border px-2 py-1 text-right">
                      {r.deep_drainage ?? "-"}
                    </td>
                    <td className="border px-2 py-1 text-right">
                      {r.soil_moisture ?? "-"}
                    </td>
                    <td className="border px-2 py-1">{r.model_version}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}