import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from "recharts";
import { useAnalysisStore } from "../store/useAnalysisStore";
import { useMemo } from "react";

export default function ChartsPanel() {
  const { events, results } = useAnalysisStore();
  const finalEvent = events.find(e => e.event_type === "final");

  // استخراج داده‌های واقعی NDVI از آخرین رویداد نهایی
  const ndviData = useMemo(() => {
    const raw = finalEvent?.data?.tasks?.task_ndvi_analysis?.detailed_data?.gee_ndvi?.ndvi?.values || [];
    const dates = finalEvent?.data?.tasks?.task_ndvi_analysis?.detailed_data?.gee_ndvi?.ndvi?.dates || [];
    return raw.map((v: number, i: number) => ({
      date: dates[i]?.slice(5) || `روز ${i+1}`,
      ndvi: parseFloat(v.toFixed(3))
    }));
  }, [finalEvent]);

  // محاسبه سود بر اساس داده‌های شبیه‌ساز (اگر در فرم وارد شده باشد)
  const profitData = useMemo(() => {
    const area = results.area || 10;
    const yieldPerHa = results.yieldPerHa || 1.35;
    const price = results.pricePerTon || 12000;
    const water = results.waterCost || 1500000;
    const labor = results.laborCost || 2000000;
    const revenue = area * yieldPerHa * price;
    const totalCost = water + labor + (area * 800000);
    return [
      { item: "درآمد", value: revenue, color: "#10b981" },
      { item: "هزینه آب", value: water, color: "#3b82f6" },
      { item: "هزینه نیروی کار", value: labor, color: "#f59e0b" },
      { item: "سود خالص", value: revenue - totalCost, color: (revenue - totalCost) > 0 ? "#10b981" : "#ef4444" },
    ];
  }, [results]);

  if (ndviData.length === 0 && !finalEvent) return (
    <div className="bg-slate-800 rounded-xl p-4 h-[320px] flex items-center justify-center text-slate-500 border border-slate-700">
      پس از اجرای اولین تحلیل، نمودارها نمایش داده می‌شوند.
    </div>
  );

  return (
    <div className="space-y-4">
      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h4 className="font-bold mb-3 text-sky-300">📈 روند شاخص NDVI</h4>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={ndviData.length ? ndviData : [{ date: "در انتظار", ndvi: 0 }]}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="date" stroke="#94a3b8" />
            <YAxis domain={[0, 1]} stroke="#94a3b8" />
            <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "8px" }} />
            <Line type="monotone" dataKey="ndvi" stroke="#38bdf8" strokeWidth={3} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h4 className="font-bold mb-3 text-green-300">💰 تحلیل اقتصادی (تومان)</h4>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={profitData} layout="vertical" margin={{ left: 80 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis type="number" stroke="#94a3b8" tickFormatter={v => `${v.toLocaleString()}`} />
            <YAxis dataKey="item" type="category" stroke="#94a3b8" width={90} />
            <Tooltip formatter={(v: number) => `${v.toLocaleString()} تومان`} contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }} />
            <Bar dataKey="value" fill={(d: any) => d.color} radius={[0, 6, 6, 0]} barSize={20} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}