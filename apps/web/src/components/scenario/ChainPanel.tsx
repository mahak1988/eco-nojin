/**
 * پنل زنجیره‌سازی مدل‌ها
 */
import { useState } from "react";
import { Link2, Play, Loader2, ArrowDown, CheckCircle2, XCircle, Clock } from "lucide-react";
import { useCreateChain, useRunChain, type ChainResult, type ChainStep } from "../../hooks/useScenarioApi";

interface ChainPanelProps {
  defaultChain?: {
    name: string;
    steps: Array<{
      simulator_id: string;
      params: Record<string, any>;
      input_from?: string;
      output_mapping?: Record<string, string>;
    }>;
  };
}

const SIMULATOR_LABELS: Record<string, string> = {
  climate: "اقلیم",
  aquacrop: "محصول (AquaCrop)",
  dssat: "محصول (DSSAT)",
  cba: "تحلیل اقتصادی (CBA)",
  swat: "آبخیزداری (SWAT)",
  rusle2: "فرسایش خاک (RUSLE2)",
};

export function ChainPanel({ defaultChain }: ChainPanelProps) {
  const createChain = useCreateChain();
  const runChain = useRunChain();
  const [chainId, setChainId] = useState<string | null>(null);
  const [chainResult, setChainResult] = useState<ChainResult | null>(null);

  const chain = defaultChain || {
    name: "زنجیرهٔ اقلیم ← محصول ← اقتصاد",
    steps: [
      {
        simulator_id: "climate",
        params: { scenario: "rcp45", years: 30 },
        output_mapping: { temp_change: "temp_offset" },
      },
      {
        simulator_id: "aquacrop",
        params: { crop: "wheat", total_irrigation: 250 },
        input_from: "climate",
      },
      {
        simulator_id: "cba",
        params: { initial_investment: 1000, annual_cost: 500, discount_rate: 5, years: 10 },
        input_from: "aquacrop",
        output_mapping: { yield_t_ha: "annual_benefit" },
      },
    ],
  };

  const handleCreateAndRun = async () => {
    const created = await createChain.mutateAsync(chain);
    setChainId(created.id);
    const result = await runChain.mutateAsync(created.id);
    setChainResult(result);
  };

  const isRunning = createChain.isPending || runChain.isPending;

  const StepIcon = ({ status }: { status: string }) => {
    if (status === "completed") return <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
    if (status === "failed") return <XCircle className="h-4 w-4 text-red-500" />;
    return <Clock className="h-4 w-4 text-stone-400" />;
  };

  return (
    <div className="space-y-4">
      {/* عنوان و دکمهٔ اجرا */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Link2 className="h-5 w-5 text-stone-500" />
          <h3 className="text-sm font-bold text-stone-700">{chain.name}</h3>
        </div>
        <button
          onClick={handleCreateAndRun}
          disabled={isRunning}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50"
        >
          {isRunning ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          اجرای زنجیره
        </button>
      </div>

      {/* نمایش مراحل */}
      <div className="space-y-0">
        {chain.steps.map((step, i) => {
          const stepResult = chainResult?.steps?.[i];
          return (
            <div key={i}>
              <div className={`flex items-center gap-3 rounded-xl border p-4 ${
                stepResult?.status === "completed" ? "border-emerald-200 bg-emerald-50" :
                stepResult?.status === "failed" ? "border-red-200 bg-red-50" :
                "border-stone-200 bg-white"
              }`}>
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-stone-100 text-xs font-bold text-stone-500">
                  {i + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-stone-700">
                      {SIMULATOR_LABELS[step.simulator_id] || step.simulator_id}
                    </span>
                    {stepResult && <StepIcon status={stepResult.status} />}
                  </div>
                  {step.input_from && (
                    <p className="text-xs text-stone-400 mt-0.5">
                      ← ورودی از: {SIMULATOR_LABELS[step.input_from] || step.input_from}
                    </p>
                  )}
                  {stepResult?.execution_time_ms && (
                    <p className="text-xs text-stone-400 mt-0.5">
                      ⏱ {stepResult.execution_time_ms.toFixed(0)} ms
                    </p>
                  )}
                </div>
                {stepResult?.metrics && Object.keys(stepResult.metrics).length > 0 && (
                  <div className="text-left">
                    {Object.entries(stepResult.metrics).slice(0, 2).map(([k, v]) => (
                      <p key={k} className="text-xs text-stone-500">
                        {k}: <span className="font-medium">{typeof v === "number" ? (v as number).toFixed(2) : v}</span>
                      </p>
                    ))}
                  </div>
                )}
              </div>
              {i < chain.steps.length - 1 && (
                <div className="flex justify-center py-1">
                  <ArrowDown className="h-4 w-4 text-stone-300" />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* نتیجهٔ نهایی */}
      {chainResult && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <h4 className="text-sm font-bold text-emerald-800 mb-2">✅ زنجیره با موفقیت اجرا شد</h4>
          <p className="text-xs text-emerald-600">
            زمان کل: {chainResult.total_execution_time_ms.toFixed(0)} ms |
            مراحل: {chainResult.steps.filter(s => s.status === "completed").length}/{chainResult.steps.length}
          </p>
        </div>
      )}
    </div>
  );
}
