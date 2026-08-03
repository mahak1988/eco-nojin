// apps/web/src/pages/accounting/ExpenseCategoriesPage.tsx
import { useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Search, Plus, Pencil, Trash2, Tag } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { useLang } from "../../components/eco/i18n";
import AnimatedSection from "../../components/animation/AnimatedSection";
import { cn } from "../../lib/cn";

interface Category {
  id: string;
  name: string;
  nameFa: string;
  color: string;
  budget: number;
  spent: number;
  icon: string;
}

const INITIAL: Category[] = [
  { id: "cat-1", name: "Salaries", nameFa: "حقوق و دستمزد", color: "#10b981", budget: 800_000_000, spent: 650_000_000, icon: "💼" },
  { id: "cat-2", name: "Raw Materials", nameFa: "مواد اولیه", color: "#3b82f6", budget: 600_000_000, spent: 480_000_000, icon: "🏭" },
  { id: "cat-3", name: "Transport", nameFa: "حمل و نقل", color: "#8b5cf6", budget: 350_000_000, spent: 280_000_000, icon: "🚚" },
  { id: "cat-4", name: "Marketing", nameFa: "بازاریابی", color: "#f59e0b", budget: 250_000_000, spent: 190_000_000, icon: "📢" },
  { id: "cat-5", name: "Rent", nameFa: "اجاره", color: "#ef4444", budget: 300_000_000, spent: 300_000_000, icon: "🏢" },
  { id: "cat-6", name: "Utilities", nameFa: "آب و برق و گاز", color: "#ec4899", budget: 120_000_000, spent: 95_000_000, icon: "⚡" },
  { id: "cat-7", name: "Insurance", nameFa: "بیمه", color: "#14b8a6", budget: 180_000_000, spent: 175_000_000, icon: "🛡️" },
  { id: "cat-8", name: "Maintenance", nameFa: "نگهداری و تعمیرات", color: "#6366f1", budget: 150_000_000, spent: 110_000_000, icon: "🔧" },
];

export default function ExpenseCategoriesPage() {
  const { lang } = useLang();
  const [categories, setCategories] = useState<Category[]>(INITIAL);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", nameFa: "", budget: "", color: "#10b981" });

  const filtered = categories.filter((c) => {
    const q = search.toLowerCase();
    return c.name.toLowerCase().includes(q) || c.nameFa.includes(q);
  });

  const totalBudget = categories.reduce((s, c) => s + c.budget, 0);
  const totalSpent = categories.reduce((s, c) => s + c.spent, 0);

  const pieData = categories.map((c) => ({
    name: lang === "fa" ? c.nameFa : c.name,
    value: c.spent / 1_000_000,
    color: c.color,
  }));

  const format = (n: number) =>
    new Intl.NumberFormat(lang === "fa" ? "fa-IR" : "en-US", {
      style: "decimal",
      maximumFractionDigits: 0,
    }).format(n);

  const handleSave = () => {
    if (!form.name.trim()) return;
    const newCat: Category = {
      id: editingId || `cat-${Date.now()}`,
      name: form.name,
      nameFa: form.nameFa || form.name,
      color: form.color,
      budget: Number(form.budget) || 0,
      spent: 0,
      icon: "📋",
    };
    if (editingId) {
      setCategories((prev) => prev.map((c) => c.id === editingId ? { ...c, ...newCat, spent: c.spent } : c));
    } else {
      setCategories((prev) => [...prev, newCat]);
    }
    setShowForm(false);
    setEditingId(null);
    setForm({ name: "", nameFa: "", budget: "", color: "#10b981" });
  };

  const handleEdit = (cat: Category) => {
    setEditingId(cat.id);
    setForm({ name: cat.name, nameFa: cat.nameFa, budget: String(cat.budget), color: cat.color });
    setShowForm(true);
  };

  const handleDelete = (id: string) => {
    setCategories((prev) => prev.filter((c) => c.id !== id));
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-4">
        <Link to="/accounting" className="flex items-center gap-1 text-sm text-stone-500 hover:text-emerald-600 transition-colors">
          <ArrowLeft className="h-4 w-4" />
          {lang === "fa" ? "بازگشت به حسابداری" : "Back to Accounting"}
        </Link>
        <div className="flex-1" />
        <button
          onClick={() => { setEditingId(null); setForm({ name: "", nameFa: "", budget: "", color: "#10b981" }); setShowForm(!showForm); }}
          className="flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-emerald-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          {lang === "fa" ? "دسته‌بندی جدید" : "New Category"}
        </button>
      </div>

      <AnimatedSection>
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-orange-500 to-red-600 shadow-lg shadow-orange-500/20">
            <Tag className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-bold text-stone-900 dark:text-stone-100">
              {lang === "fa" ? "دسته‌بندی هزینه‌ها" : "Expense Categories"}
            </h1>
            <p className="text-sm text-stone-500">
              {lang === "fa" ? "مدیریت بودجه و هزینه‌ها" : "Budget & expense management"}
            </p>
          </div>
        </div>
      </AnimatedSection>

      {/* Add/Edit Form */}
      <AnimatePresence>
        {showForm && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
              <h3 className="mb-4 font-bold text-stone-900 dark:text-stone-100">
                {editingId ? (lang === "fa" ? "ویرایش" : "Edit") : (lang === "fa" ? "دسته‌بندی جدید" : "New Category")}
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-xs font-medium text-stone-500">Name (EN)</label>
                  <input
                    type="text"
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    className="w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-400 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-100"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-stone-500">{lang === "fa" ? "نام (فارسی)" : "Name (FA)"}</label>
                  <input
                    type="text"
                    value={form.nameFa}
                    onChange={(e) => setForm({ ...form, nameFa: e.target.value })}
                    className="w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-400 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-100"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-stone-500">{lang === "fa" ? "بودجه (ریال)" : "Budget (IRR)"}</label>
                  <input
                    type="number"
                    value={form.budget}
                    onChange={(e) => setForm({ ...form, budget: e.target.value })}
                    className="w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-400 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-100"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-stone-500">{lang === "fa" ? "رنگ" : "Color"}</label>
                  <input
                    type="color"
                    value={form.color}
                    onChange={(e) => setForm({ ...form, color: e.target.value })}
                    className="h-10 w-full rounded-xl border border-stone-200 cursor-pointer"
                  />
                </div>
              </div>
              <div className="mt-4 flex justify-end gap-2">
                <button onClick={() => { setShowForm(false); setEditingId(null); }} className="rounded-xl border border-stone-200 px-4 py-2 text-sm text-stone-600 dark:border-slate-700 dark:text-stone-300">
                  {lang === "fa" ? "انصراف" : "Cancel"}
                </button>
                <button onClick={handleSave} className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white hover:bg-emerald-700">
                  {lang === "fa" ? "ذخیره" : "Save"}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Summary Stats */}
      <div className="grid gap-4 sm:grid-cols-2">
        <AnimatedSection animation="slide-in-left">
          <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
            <h3 className="mb-3 font-bold text-stone-900 dark:text-stone-100">{lang === "fa" ? "خلاصه بودجه" : "Budget Summary"}</h3>
            <div className="mt-2 space-y-3">
              {categories.slice(0, 5).map((cat) => {
                const pct = cat.budget > 0 ? Math.min((cat.spent / cat.budget) * 100, 100) : 0;
                return (
                  <div key={cat.id}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-stone-600 dark:text-stone-400">{lang === "fa" ? cat.nameFa : cat.name}</span>
                      <span className="text-stone-500">{pct.toFixed(0)}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-stone-100 dark:bg-slate-700">
                      <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pct}%`, backgroundColor: cat.color }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </AnimatedSection>

        <AnimatedSection animation="slide-in-right">
          <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
            <h3 className="mb-3 font-bold text-stone-900 dark:text-stone-100">{lang === "fa" ? "نمودار هزینه‌ها" : "Expense Chart"}</h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" outerRadius={80} dataKey="value">
                  {pieData.map((d, i) => (
                    <Cell key={i} fill={d.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number) => [`${value.toFixed(1)}M IRR`, ""]}
                  contentStyle={{ borderRadius: "12px", fontSize: "12px" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </AnimatedSection>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={lang === "fa" ? "جستجوی دسته‌بندی..." : "Search categories..."}
          className="w-full rounded-xl border border-stone-200 bg-white py-2.5 pl-10 pr-4 text-sm outline-none focus:ring-2 focus:ring-emerald-400 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-100"
        />
      </div>

      {/* Category Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((cat, i) => (
          <AnimatedSection key={cat.id} delay={i * 0.05}>
            <motion.div
              whileHover={{ y: -3 }}
              className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{cat.icon}</span>
                  <span className="font-bold text-stone-900 dark:text-stone-100">{lang === "fa" ? cat.nameFa : cat.name}</span>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => handleEdit(cat)} className="rounded-lg p-1.5 text-stone-400 hover:bg-stone-100 hover:text-stone-600 dark:hover:bg-slate-700">
                    <Pencil className="h-3.5 w-3.5" />
                  </button>
                  <button onClick={() => handleDelete(cat.id)} className="rounded-lg p-1.5 text-stone-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-900/30">
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
              <div
                className="h-2 rounded-full mb-3"
                style={{ backgroundColor: `${cat.color}20` }}
              >
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${cat.budget > 0 ? Math.min((cat.spent / cat.budget) * 100, 100) : 0}%`,
                    backgroundColor: cat.color,
                  }}
                />
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-stone-500">{lang === "fa" ? "مصرف شده:" : "Spent:"} <span className="font-medium text-stone-700 dark:text-stone-300">{format(cat.spent)}</span></span>
                <span className="text-stone-500">{lang === "fa" ? "بودجه:" : "Budget:"} <span className="font-medium text-stone-700 dark:text-stone-300">{format(cat.budget)}</span></span>
              </div>
            </motion.div>
          </AnimatedSection>
        ))}
      </div>
    </div>
  );
}
