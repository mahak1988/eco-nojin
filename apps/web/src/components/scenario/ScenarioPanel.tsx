/**
 * پنل سناریوهای سازگاری
 */
import { useState } from "react";
import { FlaskConical, Play, Loader2, Zap, Droplets, CloudSun, Sprout, Settings } from "lucide-react";
import { usePresetScenarios, useRunScenario, type PresetScenario } from "../../hooks/useScenarioApi";

const CATEGORY_ICONS: Record<string, any> = {
  irrigation: Droplets,
  climate: CloudSun,
  soil: Sprout,
  management: Settings,
};

const CATEGORY_COLORS: Record<string, string> = {
  irrigation: "border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100",
  climate: "border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-100",
  soil: "border-green-200 bg-green-50 text-green-700 hover:bg-green-100",
  management: "border-purple-200 bg-purple-50 text-purple-700 hover:bg-purple-100",
};

interface ScenarioPanelProps {
  simulatorId: string;
  baseParams: Record<string, any>;
  onScenarioResult: (result: any) => void;
}

export function ScenarioPanel({ simulatorId, baseParams, onScenarioResult }: ScenarioPanelProps) {
  const { data: presetsData, isLoading } = usePresetScenarios(simulatorId);
  const runScenario = useRunScenario();
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  const scenarios = presetsData?.scenarios || [];
  const filtered = activeCategory
    ? scenarios.filter((s) => s.category === activeCategory)
    : scenarios;

  const categories = [...new Set(scenarios.map((s) => s.category))];

  const handleRun = async (scenario: PresetScenario) => {
    const result = await runScenario.mutateAsync({
      scenarioId: `preset_${scenario.id}`,
      overrideParams: { ...baseParams, ...scenario.params },
    });
    onScenarioResult(result);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8 text-stone-400">
        <Loader2 className="h-5 w-5 animate-spin ml-2" />
        در حال بارگذاری سناریوها...
      </div>
    );
  }

  if (scenarios.length === 0) {
    return (
      <div className="text-center py-8 text-stone-400">
        <FlaskConical className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">سناریوی پیش‌فرضی برای این شبیه‌ساز تعریف نشده است</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* فیلتر دسته‌بندی */}
      {categories.length > 1 && (
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setActiveCategory(null)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              !activeCategory
                ? "bg-stone-800 text-white"
                : "bg-stone-100 text-stone-600 hover:bg-stone-200"
            }`}
          >
            همه
          </button>
          {categories.map((cat) => {
            const Icon = CATEGORY_ICONS[cat] || Settings;
            return (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activeCategory === cat
                    ? "bg-stone-800 text-white"
                    : "bg-stone-100 text-stone-600 hover:bg-stone-200"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {cat === "irrigation" ? "آبیاری" :
                 cat === "climate" ? "اقلیم" :
                 cat === "soil" ? "خاک" : "مدیریت"}
              </button>
            );
          })}
        </div>
      )}

      {/* کارت‌های سناریو */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {filtered.map((scenario) => {
          const Icon = CATEGORY_ICONS[scenario.category] || Settings;
          const colorClass = CATEGORY_COLORS[scenario.category] || CATEGORY_COLORS.management;
          const isRunning = runScenario.isPending && runScenario.variables?.scenarioId === `preset_${scenario.id}`;

          return (
            <button
              key={scenario.id}
              onClick={() => handleRun(scenario)}
              disabled={runScenario.isPending}
              className={`group relative flex flex-col items-start gap-2 rounded-xl border p-4 text-right transition-all duration-200 ${colorClass} ${
                runScenario.isPending ? "opacity-60 cursor-wait" : "cursor-pointer hover:shadow-md hover:-translate-y-0.5"
              }`}
            >
              <div className="flex items-center gap-2 w-full">
                <Icon className="h-4 w-4 shrink-0" />
                <span className="text-sm font-bold">{scenario.name}</span>
                {isRunning && <Loader2 className="h-3.5 w-3.5 animate-spin mr-auto" />}
                {!isRunning && (
                  <Play className="h-3.5 w-3.5 mr-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                )}
              </div>
              <p className="text-xs opacity-75 leading-relaxed">{scenario.description}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
