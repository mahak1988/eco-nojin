/**
 * Pilot NDVI timeseries / VCI / anomaly + farmer participation join.
 */
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Satellite, Users, BookOpen, ChevronRight, RefreshCw } from "lucide-react";
import { SectionReveal } from "../components/eco/SectionReveal";
import { INTL_PILOTS } from "../lib/internationalPilots";
import {
  IMPACT_CATALOG,
  PARTICIPATION_STAGES,
  joinPilot,
  readMembers,
  advanceMemberStage,
  type PilotMember,
} from "../lib/pilotImpact";
import { apiFetch, v1 } from "../api/http";

type BatchPilot = {
  id: string;
  code: string;
  lat: number;
  lon: number;
  count?: number;
  latest_ndvi?: number | null;
  latest_vci?: number | null;
  latest_anomaly?: number | null;
  drought_label?: string | null;
  series?: { date?: string; mean_ndvi?: number; vci?: number; anomaly?: number }[];
  error?: string;
};

export default function PilotNdviPage() {
  const [batch, setBatch] = useState<BatchPilot[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [members, setMembers] = useState<PilotMember[]>(() => readMembers());
  const [joinOpen, setJoinOpen] = useState(false);
  const [form, setForm] = useState({
    pilotId: "dishmok",
    name: "",
    contact: "",
    residencyNote: "",
    canWork: true,
  });

  const load = async () => {
    setLoading(true);
    setErr(null);
    try {
      const res = await apiFetch<{ pilots: BatchPilot[] }>(
        `${v1("/satellite/pilots-ndvi-batch")}?days=90&limit=16`,
        {},
        120_000,
      );
      setBatch(res.pilots || []);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "API offline");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const byId = useMemo(() => {
    const m = new Map(batch.map((b) => [b.id, b]));
    return m;
  }, [batch]);

  const onJoin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !form.contact.trim()) return;
    setMembers(
      joinPilot({
        pilotId: form.pilotId,
        name: form.name,
        contact: form.contact,
        residencyNote: form.residencyNote,
        canWork: form.canWork,
      }),
    );
    setJoinOpen(false);
    setForm({ pilotId: "dishmok", name: "", contact: "", residencyNote: "", canWork: true });
  };

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl text-stone-900">سری زمانی NDVI پایلوت‌ها · VCI · آنومالی</h1>
            <p className="mt-1 max-w-2xl text-sm text-stone-600">
              داده واقعی Planetary Computer (Sentinel-2). VCI نسبت به min/max پنجره؛ آنومالی نسبت به میانگین همان پنجره.
              کشاورز ساکن منطقه: آموزش → عضویت منظر → کار میدانی.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => void load()}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm font-bold"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
              بروزرسانی
            </button>
            <button
              type="button"
              onClick={() => setJoinOpen(true)}
              className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white"
            >
              <Users className="h-4 w-4" /> عضویت در پایلوت
            </button>
            <Link to="/pilots" className="rounded-xl border px-3 py-2 text-sm font-bold">
              کاتالوگ پایلوت‌ها
            </Link>
            <Link to="/danesh-yar" className="inline-flex items-center gap-1 rounded-xl border px-3 py-2 text-sm font-bold">
              <BookOpen className="h-4 w-4" /> آموزش SOP
            </Link>
          </div>
        </div>
      </SectionReveal>

      {err && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
          {err} — API را روی :8000 روشن کنید.
        </div>
      )}

      {/* Participation path */}
      <SectionReveal delay={40}>
        <h2 className="mb-3 font-display text-xl">مسیر مشارکت کشاورز (طبق طرح هیدروما)</h2>
        <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {PARTICIPATION_STAGES.map((st) => (
            <li key={st.id} className="rounded-2xl border border-stone-200 bg-white p-4">
              <div className="text-xs font-bold text-emerald-700">{st.titleFa}</div>
              <p className="mt-1 text-xs leading-relaxed text-stone-600">{st.descFa}</p>
            </li>
          ))}
        </ol>
        <p className="mt-3 text-xs text-stone-500">
          شرط: سکونت/بهره‌برداری در محدوده پایلوت + توانایی کار. ابتدا آموزش (دانش‌یار / FFS)، سپس عضویت پیمان منظر، سپس اجرای میدانی.
        </p>
      </SectionReveal>

      {/* Impact catalog from→to */}
      <SectionReveal delay={60}>
        <h2 className="mb-3 font-display text-xl">شاخص‌های اثر — از کجا به کجا (سال ۳)</h2>
        <div className="overflow-x-auto rounded-2xl border border-stone-200 bg-white">
          <table className="min-w-[720px] w-full text-xs">
            <thead className="bg-stone-50 text-stone-500">
              <tr>
                <th className="px-3 py-2 text-start">شاخص</th>
                <th className="px-3 py-2 text-start">وضع موجود</th>
                <th className="px-3 py-2 text-start">هدف سال ۳</th>
                <th className="px-3 py-2 text-start">روش اندازه‌گیری</th>
              </tr>
            </thead>
            <tbody>
              {IMPACT_CATALOG.map((ind) => (
                <tr key={ind.id} className="border-t border-stone-100">
                  <td className="px-3 py-2 font-bold text-stone-800">{ind.labelFa}</td>
                  <td className="px-3 py-2 text-stone-600">{ind.baseline}</td>
                  <td className="px-3 py-2 font-bold text-emerald-800">
                    {ind.targetYear3} <span className="font-normal text-stone-400">{ind.unit}</span>
                  </td>
                  <td className="px-3 py-2 text-stone-500">{ind.methodFa}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionReveal>

      {/* NDVI batch table */}
      <SectionReveal delay={80}>
        <h2 className="mb-3 flex items-center gap-2 font-display text-xl">
          <Satellite className="h-5 w-5 text-sky-700" />
          جدول NDVI / VCI پایلوت‌ها
        </h2>
        <div className="overflow-x-auto rounded-2xl border border-stone-200 bg-white">
          <table className="min-w-[900px] w-full text-xs">
            <thead className="bg-sky-50 text-sky-900">
              <tr>
                <th className="px-3 py-2 text-start">پایلوت</th>
                <th className="px-3 py-2 text-start">کد</th>
                <th className="px-3 py-2 text-start">NDVI اخیر</th>
                <th className="px-3 py-2 text-start">VCI</th>
                <th className="px-3 py-2 text-start">آنومالی</th>
                <th className="px-3 py-2 text-start">خشکسالی</th>
                <th className="px-3 py-2 text-start">نمودار آنومالی (پنجره)</th>
              </tr>
            </thead>
            <tbody>
              {INTL_PILOTS.map((site) => {
                const b = byId.get(site.id);
                const series = b?.series || [];
                const maxAbs = Math.max(...series.map((s) => Math.abs(s.anomaly ?? 0)), 0.01);
                return (
                  <tr key={site.id} className="border-t border-stone-100 hover:bg-emerald-50/30">
                    <td className="px-3 py-2">
                      {site.icon} {site.nameFa}
                      <div className="text-[10px] text-stone-400">{site.countryFa}</div>
                    </td>
                    <td className="px-3 py-2 font-mono">{site.code}</td>
                    <td className="px-3 py-2 font-mono">
                      {b?.latest_ndvi != null ? b.latest_ndvi.toFixed(3) : b?.error ? "err" : loading ? "…" : "—"}
                    </td>
                    <td className="px-3 py-2 font-mono">
                      {b?.latest_vci != null ? b.latest_vci.toFixed(1) : "—"}
                    </td>
                    <td className="px-3 py-2 font-mono">
                      {b?.latest_anomaly != null
                        ? (b.latest_anomaly >= 0 ? "+" : "") + b.latest_anomaly.toFixed(3)
                        : "—"}
                    </td>
                    <td className="px-3 py-2">{b?.drought_label || "—"}</td>
                    <td className="px-3 py-2">
                      <div className="flex h-8 items-end gap-0.5">
                        {series.map((s, i) => {
                          const a = s.anomaly ?? 0;
                          const h = Math.max(4, (Math.abs(a) / maxAbs) * 28);
                          return (
                            <div
                              key={i}
                              title={`${s.date}: Δ${a}`}
                              className={`w-2 rounded-t ${
                                a >= 0 ? "bg-emerald-500" : "bg-amber-500"
                              }`}
                              style={{ height: h }}
                            />
                          );
                        })}
                        {!series.length && <span className="text-stone-400">—</span>}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="mt-2 text-[11px] text-stone-400">
          API: <code className="font-mono">GET /api/v1/satellite/pilots-ndvi-batch</code> ·{" "}
          <code className="font-mono">/api/v1/satellite/vci?lat=&amp;lon=</code>
        </p>
      </SectionReveal>

      {/* Members */}
      {members.length > 0 && (
        <SectionReveal delay={100}>
          <h2 className="mb-3 font-display text-xl">اعضای ثبت‌شده ({members.length})</h2>
          <ul className="space-y-2">
            {members.slice(0, 20).map((m) => {
              const site = INTL_PILOTS.find((p) => p.id === m.pilotId);
              const st = PARTICIPATION_STAGES.find((s) => s.id === m.stage);
              return (
                <li
                  key={m.id}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm"
                >
                  <div>
                    <strong>{m.name}</strong>
                    <span className="text-stone-500">
                      {" · "}{site?.nameFa || m.pilotId} · {st?.titleFa}
                    </span>
                    <div className="text-[11px] text-stone-400">{m.residencyNote}</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setMembers(advanceMemberStage(m.id))}
                    className="inline-flex items-center gap-1 rounded-lg bg-emerald-50 px-2.5 py-1 text-xs font-bold text-emerald-800"
                  >
                    مرحله بعد <ChevronRight className="h-3.5 w-3.5" />
                  </button>
                </li>
              );
            })}
          </ul>
        </SectionReveal>
      )}

      {joinOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-stone-900/40" onClick={() => setJoinOpen(false)} />
          <form onSubmit={onJoin} className="relative w-full max-w-md space-y-3 rounded-2xl bg-white p-6 shadow-xl">
            <h2 className="font-display text-xl">عضویت در پایلوت هیدروما</h2>
            <p className="text-xs text-stone-500">
              فقط ساکنان/بهره‌برداران منطقه با توانایی کار. پس از ثبت، مرحله «علاقه» فعال می‌شود — سپس آموزش.
            </p>
            <select
              value={form.pilotId}
              onChange={(e) => setForm({ ...form, pilotId: e.target.value })}
              className="w-full rounded-xl border px-3 py-2.5 text-sm"
            >
              {INTL_PILOTS.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.icon} {p.nameFa} ({p.countryFa})
                </option>
              ))}
            </select>
            <input
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="نام"
              className="w-full rounded-xl border px-3 py-2.5 text-sm"
            />
            <input
              required
              value={form.contact}
              onChange={(e) => setForm({ ...form, contact: e.target.value })}
              placeholder="تماس / ایمیل"
              className="w-full rounded-xl border px-3 py-2.5 text-sm"
            />
            <textarea
              required
              value={form.residencyNote}
              onChange={(e) => setForm({ ...form, residencyNote: e.target.value })}
              placeholder="توضیح سکونت یا بهره‌برداری در محدوده پایلوت"
              rows={2}
              className="w-full rounded-xl border px-3 py-2.5 text-sm"
            />
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form.canWork}
                onChange={(e) => setForm({ ...form, canWork: e.target.checked })}
              />
              توانایی مشارکت در کار میدانی را دارم
            </label>
            <div className="flex gap-2">
              <button type="button" onClick={() => setJoinOpen(false)} className="flex-1 rounded-xl border py-2.5 text-sm font-bold">
                انصراف
              </button>
              <button type="submit" className="flex-1 rounded-xl bg-emerald-600 py-2.5 text-sm font-bold text-white">
                ثبت عضویت
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
