import { FormEvent, useCallback, useEffect, useState } from "react";
import { Package, Loader2, Plus, AlertTriangle } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { tExtra } from "../components/eco/i18n_extras";

interface Item {
  id: number;
  name: string;
  category: string;
  unit: string;
  quantity: number;
  min_stock: number;
  npk?: string | null;
  active_ingredient?: string | null;
  target_pest?: string | null;
  unit_cost?: number | null;
}

export default function InventoryPage() {
  const { lang } = useLang();
  const tx = (k: string) => tExtra(lang, k);
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [show, setShow] = useState(false);
  const [form, setForm] = useState({
    name: "",
    category: "seed",
    unit: "kg",
    quantity: "0",
    min_stock: "0",
    npk: "",
    active_ingredient: "",
    target_pest: "",
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      await fetch("/api/v1/inventory/seed-demo", { method: "POST", credentials: "include" });
      const res = await fetch("/api/v1/inventory/items?page=1&size=100", {
        credentials: "include",
        headers: { Accept: "application/json" },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const j = await res.json();
      setItems(j.data || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : tx("state_error"));
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);

  useEffect(() => {
    void load();
  }, [load]);

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    const res = await fetch("/api/v1/inventory/items", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: form.name,
        category: form.category,
        unit: form.unit,
        quantity: Number(form.quantity),
        min_stock: Number(form.min_stock),
        npk: form.npk || null,
        active_ingredient: form.active_ingredient || null,
        target_pest: form.target_pest || null,
      }),
    });
    if (!res.ok) {
      setError(`HTTP ${res.status}`);
      return;
    }
    setShow(false);
    await load();
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-orange-50">
            <Package className="h-5 w-5 text-orange-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{tx("inv_title")}</h1>
            <p className="text-sm text-stone-500">{tx("inv_sub")}</p>
          </div>
        </div>
        <button type="button" onClick={() => setShow((v) => !v)} className="inline-flex items-center gap-1 rounded-xl bg-orange-600 px-3 py-2 text-sm font-bold text-white">
          <Plus className="h-4 w-4" /> {tx("inv_item")}
        </button>
      </div>
      {error && <div className="rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>}
      {show && (
        <form onSubmit={onCreate} className="grid gap-2 rounded-2xl border bg-white p-4 sm:grid-cols-2">
          {(["name", "category", "unit", "quantity", "min_stock", "npk", "active_ingredient", "target_pest"] as const).map((k) => (
            <label key={k} className="text-sm">
              {k}
              <input
                required={k === "name"}
                value={form[k]}
                onChange={(e) => setForm((f) => ({ ...f, [k]: e.target.value }))}
                className="mt-1 w-full rounded-xl border px-3 py-2"
              />
            </label>
          ))}
          <button type="submit" className="sm:col-span-2 rounded-xl bg-orange-600 py-2 font-bold text-white">
            {tx("inv_save")}
          </button>
        </form>
      )}
      {loading ? (
        <div className="flex justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-orange-600" />
        </div>
      ) : (
        <div className="overflow-x-auto rounded-2xl border bg-white">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-stone-50 text-xs uppercase text-stone-500">
              <tr>
                <th className="p-3">{tx("inv_name")}</th>
                <th className="p-3">{tx("inv_cat")}</th>
                <th className="p-3">{tx("inv_qty")}</th>
                <th className="p-3">{tx("inv_detail")}</th>
              </tr>
            </thead>
            <tbody>
              {items.map((it) => (
                <tr key={it.id} className="border-b last:border-0">
                  <td className="p-3 font-medium">{it.name}</td>
                  <td className="p-3">{it.category}</td>
                  <td className="p-3">
                    {it.quantity} {it.unit}
                    {it.quantity <= it.min_stock && (
                      <AlertTriangle className="ms-1 inline h-3.5 w-3.5 text-amber-600" />
                    )}
                  </td>
                  <td className="p-3 text-xs text-stone-500">
                    {it.npk || it.active_ingredient || it.target_pest || "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
