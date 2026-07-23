/**
 * پنل مقایسهٔ سناریوها
 */
import { useState } from "react";
import { GitCompareArrows, Loader2, BarChart3, Table, Layers } from "lucide-react";
import { useCreateComparison, type ComparisonResult } from "../../hooks/useScenarioApi";

interface ComparisonPanelProps {
  scenarioResults: Array<{
    id: string;
    name: string;
    metrics: Record<string, any>;
  }>;
}

export function ComparisonPanel({ scenarioResults }: ComparisonPanelProps) {
  const createComparison = useCreateComparison();
  const [viewMode, setViewMode] = useState<"table" | "chart">("table");
  const [comparisonResult, setComparisonResult] = useState<ComparisonResult | null>(null);

  if (scenarioResults.length < 2) {
    return (
      <div className="text-center py-8 text-stone-400">
        <GitCompareArrows className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">حداقل ۲ سناریو برای مقایسه اجرا کنید</p>
      </div>
    );
  }

  const handleCompare = async () => {
    const result = await createComparison.mutateAsync({
      name: `مقایسه ${scenarioResults.length} سناریو`,
      scenarioIds: scenarioResults.map((s) => s.id),
      comparisonType: viewMode === "table" ? "table" : "side_by_side",
    });
    setComparisonResult(result);
  };

  // جمع‌آوری تمام متریک‌های یکتا
  const allMetricKeys = [...new Set(
    scenarioResults.flatMap((s) => Object.keys(s.metrics))
  )];

  return (
    <div className="space-y-4">
      {/* کنترل‌ها */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode("table")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              viewMode === "table" ? "bg-stone-800 text-white" : "bg-stone-100 text-stone-600"
            }`}
          >
            <Table className="h-3.5 w-3.5" /> جدولی
          </button>
          <button
            onClick={() => setViewMode("chart")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              viewMode === "chart" ? "bg-stone-800 text-white" : "bg-stone-100 text-stone-600"
            }`}
          >
            <BarChart3 className="h-3.5 w-3.5" /> نموداری
          </button>
        </div>
        <button
          onClick={handleCompare}
          disabled={createComparison.isPending}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50"
        >
          {createComparison.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <GitCompareArrows className="h-4 w-4" />
          )}
          مقایسه کن
        </button>
      </div>

      {/* نمای جدولی */}
      {viewMode === "table" && (
        <div className="overflow-x-auto rounded-xl border border-stone-200">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-stone-50 border-b border-stone-200">
                <th className="px-4 py-3 text-right font-medium text-stone-500">متریک</th>
                {scenarioResults.map((s) => (
                  <th key={s.id} className="px-4 py-3 text-center font-medium text-stone-700">
                    {s.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {allMetricKeys.map((key) => {
                const values = scenarioResults.map((s) => s.metrics[key]);
                const maxVal = Math.max(...values.filter((v) => typeof v === "number"));
                return (
                  <tr key={key} className="border-b border-stone-100 hover:bg-stone-50">
                    <td className="px-4 py-2.5 text-stone-600 font-medium">{key}</td>
                    {scenarioResults.map((s, i) => {
                      const val = s.metrics[key];
                      const isMax = typeof val === "number" && val === maxVal;
                      return (
                        <td
                          key={s.id}
                          className={`px-4 py-2.5 text-center ${
                            isMax ? "font-bold text-emerald-700 bg-emerald-50" : "text-stone-700"
                          }`}
                        >
                          {typeof val === "number" ? val.toFixed(2) : val ?? "—"}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* نمای نموداری */}
      {viewMode === "chart" && (
        <div className="space-y-4">
          {allMetricKeys.slice(0, 4).map((key) => (
            <div key={key} className="rounded-xl border border-stone-200 p-4">
              <h4 className="text-sm font-medium text-stone-600 mb-3">{key}</h4>
              <div className="space-y-2">
                {scenarioResults.map((s) => {
                  const val = s.metrics[key] || 0;
                  const maxVal = Math.max(...scenarioResults.map((r) => r.metrics[key] || 0));
                  const pct = maxVal > 0 ? (val / maxVal) * 100 : 0;
                  return (
                    <div key={s.id} className="flex items-center gap-3">
                      <span className="text-xs text-stone-500 w-24 truncate">{s.name}</span>
                      <div className="flex-1 h-6 bg-stone-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium text-stone-700 w-16 text-left">
                        {typeof val === "number" ? val.toFixed(1) : "—"}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* نتیجهٔ مقایسه */}
      {comparisonResult && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <h4 className="text-sm font-bold text-emerald-800 mb-2">
            ✅ مقایسهٔ «{comparisonResult.name}» ذخیره شد
          </h4>
          <p className="text-xs text-emerald-600">
            {comparisonResult.scenarios.length} سناریو مقایسه شد
          </p>
        </div>
      )}
    </div>
  );
}
