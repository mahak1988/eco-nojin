// apps/web/src/pages/inventory/StockInPage.tsx
import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, ArrowDownToLine, Plus, Check } from "lucide-react";
import { motion } from "framer-motion";
import { useLang } from "../../components/eco/i18n";
import AnimatedSection from "../../components/animation/AnimatedSection";

interface StockEntry {
  id: string;
  name: string;
  nameFa: string;
  sku: string;
  quantity: number;
  unit: string;
  supplier: string;
  date: string;
}

export default function StockInPage() {
  const { lang } = useLang();
  const [entries, setEntries] = useState<StockEntry[]>([
    { id: "1", name: "Organic Seeds", nameFa: "بذر ارگانیک", sku: "SED-001", quantity: 500, unit: "kg", supplier: "GreenFarm Co.", date: "2026-08-02" },
    { id: "2", name: "NPK Fertilizer", nameFa: "کود NPK", sku: "FRT-003", quantity: 200, unit: "kg", supplier: "AgriCorp", date: "2026-08-01" },
    { id: "3", name: "Irrigation Pipes", nameFa: "لوله آبیاری", sku: "IRR-010", quantity: 150, unit: "m", supplier: "PipeMaster", date: "2026-07-30" },
  ]);

  const [form, setForm] = useState({ name: "", nameFa: "", sku: "", quantity: "", unit: "kg", supplier: "" });
  const [showForm, setShowForm] = useState(false);

  const handleAdd = () => {
    if (!form.name || !form.quantity) return;
    setEntries((prev) => [
      { id: Date.now().toString(), name: form.name, nameFa: form.nameFa || form.name, sku: form.sku || `STK-${Date.now().toString(36).toUpperCase().slice(-4)}`, quantity: Number(form.quantity), unit: form.unit, supplier: form.supplier, date: new Date().toISOString().split("T")[0] },
      ...prev,
    ]);
    setForm({ name: "", nameFa: "", sku: "", quantity: "", unit: "kg", supplier: "" });
    setShowForm(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-4">
        <Link to="/inventory" className="flex items-center gap-1 text-sm text-stone-500 hover:text-emerald-600 transition-colors">
          <ArrowLeft className="h-4 w-4" />
          {lang === "fa" ? "بازگشت" : "Back"}
        </Link>
        <div className="flex-1" />
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-emerald-700">
          <Plus className="h-4 w-4" />
          {lang === "fa" ? "ثبت ورود" : "Record Entry"}
        </button>
      </div>

      <AnimatedSection>
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg shadow-emerald-500/20">
            <ArrowDownToLine className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-bold text-stone-900 dark:text-stone-100">
              {lang === "fa" ? "ورود کالا" : "Stock In"}
            </h1>
            <p className="text-sm text-stone-500">
              {lang === "fa" ? "ثبت ورود کالا به انبار" : "Record incoming stock"}
            </p>
          </div>
        </div>
      </AnimatedSection>

      {showForm && (
        <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} className="overflow-hidden">
          <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <label className="mb-1 block text-xs font-medium text-stone-500">Name</label>
                <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-400 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-100" />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-stone-500">{lang === "fa" ? "نام فارسی" : "Name (FA)"}</label>
                <input type="text" value={form.nameFa} onChange={(e) => setForm({ ...form, nameFa: e.target.value })} className="w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-400 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-100" />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-stone-500">SKU</label>
                <input type="text" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} className="w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-400 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-100" />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-stone-500">{lang === "fa" ? "تعداد" : "Quantity"}</label>
                <input type="number" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} className="w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-400 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-100" />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-stone-500">{lang === "fa" ? "واحد" : "Unit"}</label>
                <select value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} className="w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-stone-100">
                  <option value="kg">kg</option>
                  <option value="g">g</option>
                  <option value="L">L</option>
                  <option value="m">m</option>
                  <option value="pcs">pcs</option>
                </select>
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-stone-500">{lang === "fa" ? "تامین‌کننده" : "Supplier"}</label>
                <input type="text" value={form.supplier} onChange={(e) => setForm({ ...form, supplier: e.target.value })} className="w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-400 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-100" />
              </div>
            </div>
            <div className="mt-4 flex justify-end gap-2">
              <button onClick={() => setShowForm(false)} className="rounded-xl border border-stone-200 px-4 py-2 text-sm text-stone-600 dark:border-slate-700 dark:text-stone-300">{lang === "fa" ? "انصراف" : "Cancel"}</button>
              <button onClick={handleAdd} className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white hover:bg-emerald-700">
                <Check className="inline h-4 w-4 mr-1" />
                {lang === "fa" ? "ثبت" : "Save"}
              </button>
            </div>
          </div>
        </motion.div>
      )}

      <AnimatedSection>
        <div className="overflow-x-auto rounded-2xl border border-stone-200 bg-white dark:border-slate-700 dark:bg-slate-800">
          <table className="w-full text-sm">
            <thead className="border-b border-stone-100 bg-stone-50 dark:border-slate-700 dark:bg-slate-800">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-stone-500">SKU</th>
                <th className="px-4 py-3 text-left font-medium text-stone-500">{lang === "fa" ? "نام" : "Name"}</th>
                <th className="px-4 py-3 text-right font-medium text-stone-500">{lang === "fa" ? "تعداد" : "Qty"}</th>
                <th className="px-4 py-3 text-left font-medium text-stone-500">{lang === "fa" ? "تامین‌کننده" : "Supplier"}</th>
                <th className="px-4 py-3 text-left font-medium text-stone-500">{lang === "fa" ? "تاریخ" : "Date"}</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((e) => (
                <tr key={e.id} className="border-b border-stone-50 hover:bg-stone-50 dark:border-slate-700 dark:hover:bg-slate-700/50">
                  <td className="px-4 py-3 font-mono text-xs text-stone-400">{e.sku}</td>
                  <td className="px-4 py-3 font-medium text-stone-900 dark:text-stone-100">{lang === "fa" ? e.nameFa : e.name}</td>
                  <td className="px-4 py-3 text-right">{e.quantity.toLocaleString()} {e.unit}</td>
                  <td className="px-4 py-3 text-stone-500">{e.supplier}</td>
                  <td className="px-4 py-3 text-stone-500">{new Date(e.date).toLocaleDateString(lang === "fa" ? "fa-IR" : "en-US")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </AnimatedSection>
    </div>
  );
}
