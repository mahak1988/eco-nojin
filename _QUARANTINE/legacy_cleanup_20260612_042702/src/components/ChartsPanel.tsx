import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from "recharts";
import { useAnalysisStore } from "../store/useAnalysisStore";
import { useMemo } from "react";
import { ProfitDataPoint } from "../types";

export default function ChartsPanel() {
  // حالا مستقیماً داده‌های پردازش شده را می‌گیریم
  const { ndviData, results } = useAnalysisStore();

  // محاسبه سود (منطق بیزینس در کامپوننت باقی ماند اما تایپ شد)
  const profitData: ProfitDataPoint[] = useMemo(() => {
    const { area, yieldPerHa, pricePerTon, waterCost, laborCost } = results;
    const revenue = area * yieldPerHa * pricePerTon;
    const operationalCost = area * 800000; // هزینه ثابت عملیات
    const totalCost = waterCost + laborCost + operationalCost;
    const netProfit = revenue - totalCost;

    return [
      { item: "درآمد", value: revenue, color: "#10b981" },
      { item: "هزینه آب", value: waterCost, color: "#3b82f6" },
      { item: "هزینه کارگر", value: laborCost, color: "#f59e0b" },
      { item: "سود خالص", value: netProfit, color: netProfit > 0 ? "#10b981" : "#ef4444" },
    ];
  }, [results]);

  // حالت خالی
  if (ndviData.length === 0) {
    return (
      <div className="bg-slate-800 rounded-xl p-6 h-[320px] flex flex-col items-center justify-center text-slate-400 border border-slate-700 shadow-inner">
        <span className="text-4xl mb-2">📊</span>
        <p>پس از اجرای اولین تحلیل، نمودارها اینجا نمایش داده می‌شوند.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* نمودار NDVI */}
      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700 shadow-lg">
        <h4 className="font-bold mb-4 text-sky-300 flex items-center gap-2">
          <span>📈</span> روند شاخص NDVI
        </h4>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={ndviData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
            <YAxis domain={[0, 1]} stroke="#94a3b8" fontSize={12} />
            <Tooltip 
              contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "8px" }}
              labelStyle={{ color: "#fff" }}
            />
            <Line 
              type="monotone" 
              dataKey="ndvi" 
              stroke="#38bdf8" 
              strokeWidth={3} 
              dot={{ r: 4, fill: "#38bdf8" }} 
              activeDot={{ r: 6 }} 
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* نمودار اقتصادی */}
      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700 shadow-lg">
        <h4 className="font-bold mb-4 text-green-300 flex items-center gap-2">
          <span>💰</span> تحلیل اقتصادی (تومان)
        </h4>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={profitData} layout="vertical" margin={{ left: 20, right: 30 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
            <XAxis 
              type="number" 
              stroke="#94a3b8" 
              tickFormatter={(v) => `${(v / 1000000).toFixed(1)}M`} 
              fontSize={12}
            />
            <YAxis 
              dataKey="item" 
              type="category" 
              stroke="#94a3b8" 
              width={80} 
              fontSize={12}
            />
            <Tooltip 
              formatter={(value: number) => `${value.toLocaleString()} تومان`}
              contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "8px" }}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
              {/* ✅ اصلاح صحیح رنگ‌دهی میله‌ها با Cell */}
              {profitData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}