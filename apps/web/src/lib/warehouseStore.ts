/** Warehouse / inventory — localStorage with seed data. Offline-first. */

export type WarehouseItem = {
  id: string;
  name: string;
  category: string;
  unit: string;
  quantity: number;
  minStock: number;
  unitCost: number;
  currency: string;
  npk?: string;
  notes?: string;
  updatedAt: string;
};

const KEY = "econojin_warehouse_v1";

const SEED: WarehouseItem[] = [
  { id: "w1", name: "بذر گندم دیم", category: "seed", unit: "kg", quantity: 420, minStock: 100, unitCost: 185000, currency: "IRR", npk: "", updatedAt: new Date().toISOString() },
  { id: "w2", name: "کود NPK 20-20-20", category: "fertilizer", unit: "kg", quantity: 85, minStock: 50, unitCost: 320000, currency: "IRR", npk: "20-20-20", updatedAt: new Date().toISOString() },
  { id: "w3", name: "سم علف‌کش", category: "pesticide", unit: "L", quantity: 12, minStock: 5, unitCost: 980000, currency: "IRR", updatedAt: new Date().toISOString() },
  { id: "w4", name: "لوله آبیاری قطره‌ای", category: "equipment", unit: "m", quantity: 1500, minStock: 200, unitCost: 45000, currency: "IRR", updatedAt: new Date().toISOString() },
  { id: "w5", name: "بذر گوجه‌فرنگی", category: "seed", unit: "pack", quantity: 28, minStock: 10, unitCost: 12.5, currency: "USD", updatedAt: new Date().toISOString() },
];

export function readWarehouse(): WarehouseItem[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as WarehouseItem[];
      if (Array.isArray(parsed) && parsed.length) return parsed;
    }
  } catch { /* ignore */ }
  return [...SEED];
}

export function writeWarehouse(items: WarehouseItem[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(items));
  } catch { /* ignore */ }
}

export function addItem(item: Omit<WarehouseItem, "id" | "updatedAt">): WarehouseItem {
  const items = readWarehouse();
  const next: WarehouseItem = {
    ...item,
    id: `w${Date.now()}`,
    updatedAt: new Date().toISOString(),
  };
  items.unshift(next);
  writeWarehouse(items);
  return next;
}

export function updateItem(id: string, patch: Partial<WarehouseItem>): WarehouseItem | null {
  const items = readWarehouse();
  const i = items.findIndex((x) => x.id === id);
  if (i < 0) return null;
  items[i] = { ...items[i], ...patch, updatedAt: new Date().toISOString() };
  writeWarehouse(items);
  return items[i];
}

export function removeItem(id: string): boolean {
  const items = readWarehouse().filter((x) => x.id !== id);
  writeWarehouse(items);
  return true;
}

export function adjustQty(id: string, delta: number): WarehouseItem | null {
  const items = readWarehouse();
  const i = items.findIndex((x) => x.id === id);
  if (i < 0) return null;
  items[i] = {
    ...items[i],
    quantity: Math.max(0, items[i].quantity + delta),
    updatedAt: new Date().toISOString(),
  };
  writeWarehouse(items);
  return items[i];
}

export function warehouseTotalValue(
  items: WarehouseItem[],
  targetCode: string,
  rates: Record<string, number>,
  convert: (amount: number, from: string, to: string, rates: Record<string, number>) => number
): number {
  return items.reduce((sum, it) => {
    const line = it.quantity * it.unitCost;
    return sum + convert(line, it.currency || "IRR", targetCode, rates);
  }, 0);
}
