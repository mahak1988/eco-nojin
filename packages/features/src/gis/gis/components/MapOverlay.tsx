import { useState, type ReactNode } from "react";
export function MapPanel({ children, position = "top-right", className = "",
  collapsible = true }: { children: ReactNode;
  position?: "top-right" | "top-left" | "bottom-right" | "bottom-left";
  className?: string; collapsible?: boolean }) {
  const [open, setOpen] = useState(true);
  const pos = { "top-right": "top-4 end-4", "top-left": "top-4 start-4",
    "bottom-right": "bottom-4 end-4", "bottom-left": "bottom-4 start-4" }[position];
  return (
    <div className={`absolute z-[1000] ${pos} ${className}`}>
      <div className="glass rounded-[var(--r-lg)] shadow-[var(--shadow-lg)] overflow-hidden transition-all duration-300"
        style={{ minWidth: open ? 220 : 44 }}>
        {collapsible && (
          <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between px-3 py-2 text-xs font-bold text-[var(--text-3)] hover:text-[var(--text-1)] transition-colors">
            {open && <span>پنل کنترل</span>}<span className="text-base">{open ? "◁" : "▷"}</span></button>)}
        {open && <div className="px-3 pb-3">{children}</div>}
      </div>
    </div>
  );
}
export function LayerControl({ layers, active, onToggle }: {
  layers: { id: string; label: string; icon: string }[]; active: Set<string>; onToggle: (id: string) => void }) {
  return (
    <MapPanel position="bottom-left">
      <div className="space-y-1.5">
        {layers.map((l) => (
          <button key={l.id} onClick={() => onToggle(l.id)}
            className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-[var(--r-sm)] text-sm transition-all duration-200 ${active.has(l.id) ? "bg-brand-500/15 text-brand-400 font-medium" : "text-[var(--text-3)] hover:bg-white/5 hover:text-[var(--text-1)]"}`}>
            <span>{l.icon}</span><span className="flex-1 text-start">{l.label}</span>
            <span className={`w-2 h-2 rounded-full transition-colors ${active.has(l.id) ? "bg-brand-400" : "bg-[var(--text-3)]/30"}`} /></button>
        ))}
      </div>
    </MapPanel>
  );
}
export function MapLegend({ items }: { items: { color: string; label: string }[] }) {
  return (
    <MapPanel position="bottom-right" collapsible={false}>
      <div className="space-y-1.5">
        {items.map((it) => (
          <div key={it.label} className="flex items-center gap-2 text-xs text-[var(--text-2)]">
            <span className="w-3 h-3 rounded-sm flex-shrink-0" style={{ background: it.color }} />{it.label}</div>
        ))}
      </div>
    </MapPanel>
  );
}
