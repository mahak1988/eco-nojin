// apps/web/src/components/inventory/InventoryTable.tsx
import { useState } from "react";
import { motion } from "framer-motion";
import { Search, ArrowUpDown } from "lucide-react";
import { useLang } from "../eco/i18n";
import { cn } from "../../lib/cn";

interface InventoryItem {
  id: string;
  name: string;
  nameFa: string;
  sku: string;
  category: string;
  categoryFa: string;
  quantity: number;
  unit: string;
  minStock: number;
  price: number;
  currency: string;
  status: "in-stock" | "low" | "out";
  lastUpdated: string;
}

interface Props {
  items: InventoryItem[];
  className?: string;
}

export default function InventoryTable({ items, className = "" }: Props) {
  const { lang } = useLang();
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const categories = [...new Set(items.map((i) => i.category))];

  const filtered = items
    .filter((i) => {
      const q = search.toLowerCase();
      return (categoryFilter === "all" || i.category === categoryFilter) &&
        (i.name.toLowerCase().includes(q) || i.nameFa.includes(q) || i.sku.toLowerCase().includes(q));
    })
    .sort((a, b) => {
      const cmp = a.name.localeCompare(b.name);
      return sortDir === "asc" ? cmp : -cmp;
    });

  const format = (n: number) =>
    new Intl.NumberFormat(lang === "fa" ? "fa-IR" : "en-US", {
      style: "decimal",
      maximumFractionDigits: 0,
    }).format(n);

  return (
    <div className={className}>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[180px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={lang === "fa" ? "جستجو..." : "Search..."}
            className="w-full rounded-xl border border-stone-200 bg-white py-2 pl-10 pr-4 text-sm outline-none focus:ring-2 focus:ring-emerald-400 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-100"
          />
        </div>
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm text-stone-600 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-300"
        >
          <option value="all">{lang === "fa" ? "همه" : "All"}</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <button
          onClick={() => setSortDir((d) => (d === "asc" ? "desc" : "asc"))}
          className="rounded-xl border border-stone-200 bg-white px-3 py-2 text-stone-600 hover:bg-stone-50 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-300"
        >
          <ArrowUpDown className="h-4 w-4" />
        </button>
      </div>

      <div className="overflow-x-auto rounded-2xl border border-stone-200 bg-white dark:border-slate-700 dark:bg-slate-800">
        <table className="w-full text-sm">
          <thead className="border-b border-stone-100 bg-stone-50 dark:border-slate-700 dark:bg-slate-800">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-stone-500">SKU</th>
              <th className="px-4 py-3 text-left font-medium text-stone-500">{lang === "fa" ? "نام" : "Name"}</th>
              <th className="px-4 py-3 text-left font-medium text-stone-500">{lang === "fa" ? "دسته" : "Category"}</th>
              <th className="px-4 py-3 text-right font-medium text-stone-500">{lang === "fa" ? "موجودی" : "Qty"}</th>
              <th className="px-4 py-3 text-right font-medium text-stone-500">{lang === "fa" ? "قیمت" : "Price"}</th>
              <th className="px-4 py-3 text-center font-medium text-stone-500">{lang === "fa" ? "وضعیت" : "Status"}</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((item, i) => (
              <motion.tr
                key={item.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.03 }}
                className="border-b border-stone-50 hover:bg-stone-50 dark:border-slate-700 dark:hover:bg-slate-700/50"
              >
                <td className="px-4 py-3 font-mono text-xs text-stone-400">{item.sku}</td>
                <td className="px-4 py-3 font-medium text-stone-900 dark:text-stone-100">
                  {lang === "fa" ? item.nameFa : item.name}
                </td>
                <td className="px-4 py-3 text-stone-500">{lang === "fa" ? item.categoryFa : item.category}</td>
                <td className="px-4 py-3 text-right font-mono text-stone-700 dark:text-stone-300">
                  {item.quantity.toLocaleString()} {item.unit}
                </td>
                <td className="px-4 py-3 text-right font-mono text-stone-700 dark:text-stone-300">
                  {format(item.price)} {item.currency}
                </td>
                <td className="px-4 py-3 text-center">
                  <span className={cn(
                    "inline-flex rounded-full px-2.5 py-0.5 text-xs font-bold",
                    item.status === "in-stock" && "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300",
                    item.status === "low" && "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300",
                    item.status === "out" && "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
                  )}>
                    {item.status === "in-stock" ? (lang === "fa" ? "موجود" : "In Stock") :
                     item.status === "low" ? (lang === "fa" ? "کم" : "Low") :
                     (lang === "fa" ? "ناموجود" : "Out")}
                  </span>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="py-10 text-center text-sm text-stone-400">
            {lang === "fa" ? "هیچ کالایی یافت نشد" : "No items found"}
          </div>
        )}
      </div>
    </div>
  );
}
