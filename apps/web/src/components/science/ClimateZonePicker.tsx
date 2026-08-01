import { useEffect, useState } from "react";
import { Globe2, Loader2 } from "lucide-react";
import { getClimateZones, applyClimateZonePackage, type ClimateZone } from "../../lib/apiServices";

const STORAGE_KEY = "econojin_climate_zone_id";

export function readStoredClimateZoneId(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

export function storeClimateZoneId(id: string) {
  try {
    localStorage.setItem(STORAGE_KEY, id);
  } catch {
    /* ignore */
  }
}

type Props = {
  value?: string | null;
  onChange?: (zone: ClimateZone | null) => void;
  compact?: boolean;
  className?: string;
};

export function ClimateZonePicker({ value, onChange, compact, className }: Props) {
  const [zones, setZones] = useState<ClimateZone[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string | null>(value ?? readStoredClimateZoneId());
  const [note, setNote] = useState<string>("");

  useEffect(() => {
    void (async () => {
      setLoading(true);
      const res = await getClimateZones();
      const list = (res.data?.zones as ClimateZone[]) || [];
      setZones(list);
      setNote(String(res.data?.note_fa || res.data?.note_en || ""));
      setLoading(false);
      if (!selected && list.length) {
        const first = list[0].id;
        setSelected(first);
        storeClimateZoneId(first);
        onChange?.(list[0]);
      } else if (selected) {
        const z = list.find((x) => x.id === selected) || null;
        onChange?.(z);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (value != null && value !== selected) setSelected(value);
  }, [value, selected]);

  function pick(id: string) {
    setSelected(id);
    storeClimateZoneId(id);
    const z = zones.find((x) => x.id === id) || null;
    onChange?.(z);
    // Climate package: default models + risk triggers on decision support / monitors
    void applyClimateZonePackage(id);
  }

  const current = zones.find((z) => z.id === selected) || null;

  if (loading) {
    return (
      <div className={`flex items-center gap-2 text-sm text-stone-500 ${className || ""}`}>
        <Loader2 className="h-4 w-4 animate-spin" /> بارگذاری اقلیم‌ها…
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className || ""}`}>
      <div className="flex items-center gap-2 text-sm font-bold text-stone-700">
        <Globe2 className="h-4 w-4 text-emerald-600" />
        اقلیم منظر (انتخاب کاربر — بدون نام مکان محلی)
      </div>
      {note && <p className="text-xs text-stone-500">{note}</p>}
      <div className={`grid gap-2 ${compact ? "sm:grid-cols-2" : "sm:grid-cols-2 lg:grid-cols-4"}`}>
        {zones.map((z) => {
          const active = z.id === selected;
          return (
            <button
              key={z.id}
              type="button"
              onClick={() => pick(z.id)}
              className={`rounded-2xl border p-3 text-right transition ${
                active
                  ? "border-emerald-500 bg-emerald-50 ring-2 ring-emerald-400/40"
                  : "border-stone-200 bg-white hover:border-emerald-300"
              }`}
            >
              <div className="text-sm font-bold text-stone-800">{z.label_fa || z.label_en}</div>
              <div className="mt-0.5 text-[11px] text-stone-500">{z.label_en}</div>
              {z.koppen_hint && (
                <div className="mt-1 font-mono text-[10px] text-emerald-700">{z.koppen_hint}</div>
              )}
            </button>
          );
        })}
      </div>
      {current && !compact && (
        <div className="rounded-xl border border-stone-100 bg-stone-50/80 p-3 text-xs text-stone-600">
          <div className="font-semibold text-stone-800">مدل‌های پیشنهادی</div>
          <p className="mt-1">{(current.default_models || []).join(" · ") || "—"}</p>
          <div className="mt-2 font-semibold text-stone-800">تریگر ریسک</div>
          <p className="mt-1">{(current.risk_triggers || []).join(" · ") || "—"}</p>
          <div className="mt-2 font-semibold text-stone-800">پکیج‌های اولویت</div>
          <p className="mt-1">{(current.priority_packages || []).join(" · ") || "—"}</p>
        </div>
      )}
    </div>
  );
}

export default ClimateZonePicker;
