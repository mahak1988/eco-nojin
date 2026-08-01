import { FormEvent, useMemo, useState } from "react";
import { Package, Plus, Trash2, Minus, AlertTriangle } from "lucide-react";
import {
  readWarehouse,
  writeWarehouse,
  addItem,
  adjustQty,
  removeItem,
  warehouseTotalValue,
  type WarehouseItem,
} from "../lib/warehouseStore";
import { readCurrencySettings, convert, formatMoney } from "../lib/currencyStore";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { RequirePermission } from "../components/rbac/RequirePermission";

export default function InventoryPage() {
  const { lang } = useLang();
  const [items, setItems] = useState<WarehouseItem[]>(() => readWarehouse());
  const [show, setShow] = useState(false);
  const [form, setForm] = useState({
    name: "",
    category: "seed",
    unit: "kg",
    quantity: "0",
    minStock: "0",
    unitCost: "0",
    currency: "IRR",
    npk: "",
  });
  const cur = readCurrencySettings();
  const locale = lang === "fa" ? "fa-IR" : "en-US";
  const primary = cur.primary === "CUSTOM" ? cur.customCode : cur.primary;

  const t = (fa: string, en: string) => (lang === "fa" ? fa : en);

  const total = useMemo(
    () => warehouseTotalValue(items, primary, cur.rates, convert),
    [items, primary, cur.rates]
  );

  const onCreate = (e: FormEvent) => {
    e.preventDefault();
    addItem({
      name: form.name,
      category: form.category,
      unit: form.unit,
      quantity: Number(form.quantity) || 0,
      minStock: Number(form.minStock) || 0,
      unitCost: Number(form.unitCost) || 0,
      currency: form.currency,
      npk: form.npk || undefined,
    });
    setItems(readWarehouse());
    setShow(false);
    setForm({ name: "", category: "seed", unit: "kg", quantity: "0", minStock: "0", unitCost: "0", currency: "IRR", npk: "" });
  };

  const onAdj = (id: string, delta: number) => {
    adjustQty(id, delta);
    setItems(readWarehouse());
  };

  const onDel = (id: string) => {
    removeItem(id);
    setItems(readWarehouse());
  };

  return (
    <RequirePermission perm="inventory.view">
      <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
        <SectionReveal>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="grid h-11 w-11 place-items-center rounded-xl bg-orange-50 ring-1 ring-orange-600/15">
                <Package className="h-5 w-5 text-orange-700" />
              </div>
              <div>
                <h1 className="font-display text-3xl text-stone-800">{t("انبار", "Warehouse")}</h1>
                <p className="text-sm text-stone-500">
                  {t("موجودی محلی + ارز", "Local inventory + currency")} ·{" "}
                  <strong>{formatMoney(total, primary, cur, locale)}</strong>
                </p>
              </div>
            </div>
            <button type="button" onClick={() => setShow((v) => !v)}
              className="inline-flex items-center gap-1 rounded-xl bg-orange-600 px-3 py-2 text-sm font-bold text-white">
              <Plus className="h-4 w-4" /> {t("افزودن", "Add item")}
            </button>
          </div>
        </SectionReveal>

        {show && (
          <form onSubmit={onCreate} className="grid gap-2 rounded-2xl border bg-white p-4 sm:grid-cols-2">
            {([
              ["name", t("نام", "Name")],
              ["category", t("دسته", "Category")],
              ["unit", t("واحد", "Unit")],
              ["quantity", t("تعداد", "Qty")],
              ["minStock", t("حداقل", "Min stock")],
              ["unitCost", t("قیمت واحد", "Unit cost")],
              ["currency", t("ارز", "Currency")],
              ["npk", "NPK"],
            ] as const).map(([k, label]) => (
              <label key={k} className="text-sm font-bold text-stone-700">
                {label}
                <input required={k === "name"} value={form[k]}
                  onChange={(e) => setForm((f) => ({ ...f, [k]: e.target.value }))}
                  className="mt-1 w-full rounded-xl border px-3 py-2 text-sm font-normal" />
              </label>
            ))}
            <button type="submit" className="sm:col-span-2 rounded-xl bg-orange-600 py-2.5 font-bold text-white">
              {t("ذخیره", "Save")}
            </button>
          </form>
        )}

        <div className="overflow-x-auto rounded-2xl border bg-white shadow-sm">
          <table className="w-full text-start text-sm">
            <thead className="border-b bg-stone-50 text-xs uppercase text-stone-500">
              <tr>
                <th className="p-3">{t("نام", "Name")}</th>
                <th className="p-3">{t("دسته", "Cat")}</th>
                <th className="p-3">{t("موجودی", "Stock")}</th>
                <th className="p-3">{t("ارزش", "Value")}</th>
                <th className="p-3" />
              </tr>
            </thead>
            <tbody>
              {items.map((it) => {
                const line = convert(it.quantity * it.unitCost, it.currency || "IRR", primary, cur.rates);
                return (
                  <tr key={it.id} className="border-b last:border-0">
                    <td className="p-3 font-medium">{it.name}</td>
                    <td className="p-3">{it.category}</td>
                    <td className="p-3">
                      <div className="flex items-center gap-1">
                        <button type="button" onClick={() => onAdj(it.id, -1)} className="rounded-lg border p-1 hover:bg-stone-50">
                          <Minus className="h-3.5 w-3.5" />
                        </button>
                        <span className="min-w-[3rem] text-center tabular-nums">{it.quantity} {it.unit}</span>
                        <button type="button" onClick={() => onAdj(it.id, 1)} className="rounded-lg border p-1 hover:bg-stone-50">
                          <Plus className="h-3.5 w-3.5" />
                        </button>
                        {it.quantity <= it.minStock && <AlertTriangle className="ms-1 h-3.5 w-3.5 text-amber-600" />}
                      </div>
                    </td>
                    <td className="p-3 tabular-nums">{formatMoney(line, primary, cur, locale)}</td>
                    <td className="p-3">
                      <button type="button" onClick={() => onDel(it.id)} className="rounded-lg p-1.5 text-rose-600 hover:bg-rose-50">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
              {items.length === 0 && (
                <tr><td colSpan={5} className="p-8 text-center text-stone-400">{t("انبار خالی است", "Warehouse is empty")}</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </RequirePermission>
  );
}
