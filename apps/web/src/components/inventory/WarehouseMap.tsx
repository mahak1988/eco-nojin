// apps/web/src/components/inventory/WarehouseMap.tsx
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLang } from "../eco/i18n";

interface Zone {
  id: string;
  name: string;
  nameFa: string;
  x: number;
  y: number;
  w: number;
  h: number;
  color: string;
  occupancy: number; // 0-100
  capacity: string;
  itemCount: number;
}

const ZONES: Zone[] = [
  { id: "A", name: "Seeds Zone", nameFa: "بخش بذر", x: 5, y: 5, w: 30, h: 25, color: "#10b981", occupancy: 65, capacity: "200 kg", itemCount: 42 },
  { id: "B", name: "Fertilizer", nameFa: "کود و سموم", x: 40, y: 5, w: 25, h: 25, color: "#3b82f6", occupancy: 40, capacity: "500 kg", itemCount: 18 },
  { id: "C", name: "Tools", nameFa: "ابزارآلات", x: 70, y: 5, w: 25, h: 25, color: "#8b5cf6", occupancy: 80, capacity: "50 pcs", itemCount: 35 },
  { id: "D", name: "Raw Materials", nameFa: "مواد اولیه", x: 5, y: 35, w: 35, h: 30, color: "#f59e0b", occupancy: 55, capacity: "1000 kg", itemCount: 12 },
  { id: "E", name: "Finished Goods", nameFa: "محصولات", x: 45, y: 35, w: 30, h: 30, color: "#ef4444", occupancy: 25, capacity: "300 pcs", itemCount: 8 },
  { id: "F", name: "Packaging", nameFa: "بسته‌بندی", x: 5, y: 70, w: 25, h: 25, color: "#ec4899", occupancy: 90, capacity: "200 pcs", itemCount: 55 },
  { id: "G", name: "Cold Storage", nameFa: "انبار سرد", x: 35, y: 70, w: 30, h: 25, color: "#14b8a6", occupancy: 45, capacity: "150 kg", itemCount: 22 },
  { id: "H", name: "Spare Parts", nameFa: "قطعات یدکی", x: 70, y: 70, w: 25, h: 25, color: "#6366f1", occupancy: 10, capacity: "100 pcs", itemCount: 7 },
];

interface Props {
  className?: string;
}

export default function WarehouseMap({ className = "" }: Props) {
  const { lang } = useLang();
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <div className={className}>
      <div className="relative rounded-2xl border border-stone-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800 overflow-hidden" style={{ minHeight: 300 }}>
        {/* Grid background */}
        <svg viewBox="0 0 100 100" className="w-full h-[350px]" style={{ maxHeight: "70vh" }}>
          {/* Floor */}
          <rect x={0} y={0} width={100} height={100} fill="#f9fafb" className="dark:fill-slate-900" rx={2} />
          {/* Entrance */}
          <rect x={78} y={45} width={4} height={10} fill="#6b7280" rx={1} />
          {/* Zones */}
          {ZONES.map((zone) => (
            <g key={zone.id}>
              <motion.rect
                x={zone.x}
                y={zone.y}
                width={zone.w}
                height={zone.h}
                rx={3}
                fill={zone.color}
                fillOpacity={0.15}
                stroke={zone.color}
                strokeWidth={selected === zone.id ? 2 : 0.5}
                whileHover={{ fillOpacity: 0.25, scale: 1.02, transformOrigin: `${zone.x + zone.w/2}px ${zone.y + zone.h/2}px` }}
                onClick={() => setSelected(selected === zone.id ? null : zone.id)}
                style={{ cursor: "pointer" }}
              />
              {/* Occupancy bar */}
              <rect
                x={zone.x + 1}
                y={zone.y + zone.h - 5}
                width={zone.w - 2}
                height={3}
                fill="rgba(0,0,0,0.1)"
                rx={1}
              />
              <rect
                x={zone.x + 1}
                y={zone.y + zone.h - 5}
                width={(zone.w - 2) * (zone.occupancy / 100)}
                height={3}
                fill={zone.color}
                rx={1}
              />
              <text
                x={zone.x + zone.w / 2}
                y={zone.y + zone.h / 2 - 4}
                textAnchor="middle"
                fontSize={5}
                fontWeight="bold"
                fill={zone.color}
                style={{ pointerEvents: "none" }}
              >
                {zone.id}
              </text>
              <text
                x={zone.x + zone.w / 2}
                y={zone.y + zone.h / 2 + 4}
                textAnchor="middle"
                fontSize={3.5}
                fill="#6b7280"
                style={{ pointerEvents: "none" }}
              >
                {zone.occupancy}%
              </text>
            </g>
          ))}
        </svg>

        {/* Legend */}
        <div className="mt-3 flex flex-wrap gap-2">
          {ZONES.map((zone) => (
            <motion.button
              key={zone.id}
              whileHover={{ scale: 1.05 }}
              onClick={() => setSelected(selected === zone.id ? null : zone.id)}
              className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-colors ${
                selected === zone.id
                  ? "bg-stone-800 text-white dark:bg-slate-200 dark:text-slate-900"
                  : "bg-stone-100 text-stone-600 dark:bg-slate-700 dark:text-stone-300"
              }`}
            >
              <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: zone.color }} />
              {lang === "fa" ? zone.nameFa : zone.name}
            </motion.button>
          ))}
        </div>

        {/* Detail tooltip */}
        <AnimatePresence>
          {selected && (() => {
            const zone = ZONES.find((z) => z.id === selected)!;
            return (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="mt-4 rounded-xl border border-stone-200 bg-stone-50 p-3 text-sm dark:border-slate-700 dark:bg-slate-800"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-stone-900 dark:text-stone-100">{lang === "fa" ? zone.nameFa : zone.name}</span>
                  <span className="text-emerald-600 dark:text-emerald-400">{zone.itemCount} items</span>
                </div>
                <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-stone-500">
                  <span>{lang === "fa" ? "ظرفیت:" : "Capacity:"} {zone.capacity}</span>
                  <span>{lang === "fa" ? "اشغال:" : "Occupancy:"} {zone.occupancy}%</span>
                </div>
              </motion.div>
            );
          })()}
        </AnimatePresence>
      </div>
    </div>
  );
}
