"use client";

import { useState } from "react";
import type { DailyInput, SimulationRequest, WaterBalance } from "@/api/water";
import { simulateWaterBalance } from "@/api/water";

type Props = {
  scenarios: { id: number; name: string }[];
  soilProfiles: { id: number; name: string }[];
  onResults: (rows: WaterBalance[]) => void;
};

export function SimulationControls({ scenarios, soilProfiles, onResults }: Props) {
  const [scenarioId, setScenarioId] = useState<number | "">("");
  const [soilProfileId, setSoilProfileId] = useState<number | "">("");
  const [rows, setRows] = useState<DailyInput[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addRow = () => {
    setRows((prev) => [
      ...prev,
      {
        date: new Date().toISOString().slice(0, 10),
        precipitation: 0,
        irrigation: 0,
        evapotranspiration: 0,
      },
    ]);
  };

  const updateRow = (index: number, field: keyof DailyInput, value: string) => {
    setRows((prev) =>
      prev.map((row, i) =>
        i === index
          ? {
              ...row,
              [field]:
                field === "date" ? value : value === "" ? null : Number(value),
            }
          : row
      )
    );
  };

  const removeRow = (index: number) => {
    setRows((prev) => prev.filter((_, i) => i !== index));
  };

  const handleRun = async () => {
    if (!scenarioId || !soilProfileId || rows.length === 0) {
      setError("سناریو، پروفایل خاک و حداقل یک ردیف ورودی لازم است.");
      return;
    }
    setError(null);
    setIsRunning(true);
    try {
      const payload: SimulationRequest = {
        scenario_id: Number(scenarioId),
        soil_profile_id: Number(soilProfileId),
        daily_inputs: rows,
      };
      const result = await simulateWaterBalance(payload);
      onResults(result);
    } catch (e: any) {
      setError(e.message ?? "خطا در اجرای شبیه‌سازی");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-4 border rounded-lg p-4 bg-white shadow-sm">
      <div className="flex gap-4 flex-wrap">
        <div>
          <label className="block text-sm font-medium mb-1">سناریو</label>
          <select
            className="border rounded px-2 py-1"
            value={scenarioId}
            onChange={(e) =>
              setScenarioId(e.target.value ? Number(e.target.value) : "")
            }
          >
            <option value="">انتخاب سناریو</option>
            {scenarios.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">پروفایل خاک</label>
          <select
            className="border rounded px-2 py-1"
            value={soilProfileId}
            onChange={(e) =>
              setSoilProfileId(e.target.value ? Number(e.target.value) : "")
            }
          >
            <option value="">انتخاب پروفایل</option>
            {soilProfiles.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <div className="flex justify-between items-center mb-2">
          <span className="font-medium">ورودی روزانه</span>
          <button
            type="button"
            className="text-sm px-2 py-1 border rounded"
            onClick={addRow}
          >
            افزودن روز
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-sm border">
            <thead>
              <tr className="bg-gray-50">
                <th className="border px-2 py-1">تاریخ</th>
                <th className="border px-2 py-1">بارش</th>
                <th className="border px-2 py-1">آبیاری</th>
                <th className="border px-2 py-1">تبخیر-تعرق</th>
                <th className="border px-2 py-1">حذف</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i}>
                  <td className="border px-2 py-1">
                    <input
                      type="date"
                      className="border rounded px-1 py-0.5"
                      value={row.date}
                      onChange={(e) => updateRow(i, "date", e.target.value)}
                    />
                  </td>
                  <td className="border px-2 py-1">
                    <input
                      type="number"
                      className="border rounded px-1 py-0.5 w-24"
                      value={row.precipitation ?? ""}
                      onChange={(e) =>
                        updateRow(i, "precipitation", e.target.value)
                      }
                    />
                  </td>
                  <td className="border px-2 py-1">
                    <input
                      type="number"
                      className="border rounded px-1 py-0.5 w-24"
                      value={row.irrigation ?? ""}
                      onChange={(e) =>
                        updateRow(i, "irrigation", e.target.value)
                      }
                    />
                  </td>
                  <td className="border px-2 py-1">
                    <input
                      type="number"
                      className="border rounded px-1 py-0.5 w-24"
                      value={row.evapotranspiration ?? ""}
                      onChange={(e) =>
                        updateRow(i, "evapotranspiration", e.target.value)
                      }
                    />
                  </td>
                  <td className="border px-2 py-1 text-center">
                    <button
                      type="button"
                      className="text-xs text-red-600"
                      onClick={() => removeRow(i)}
                    >
                      ×
                    </button>
                  </td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td
                    className="border px-2 py-2 text-center text-gray-500"
                    colSpan={5}
                  >
                    هیچ ردیفی تعریف نشده؛ روی «افزودن روز» کلیک کنید.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="button"
        className="px-4 py-2 bg-emerald-600 text-white rounded disabled:opacity-60"
        onClick={handleRun}
        disabled={isRunning}
      >
        {isRunning ? "در حال شبیه‌سازی..." : "اجرای شبیه‌سازی"}
      </button>
    </div>
  );
}