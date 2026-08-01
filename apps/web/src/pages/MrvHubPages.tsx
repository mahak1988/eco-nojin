/**
 * MRV hub pages — assurance L1–L3, evidence, verify, satellites, points, EcoCoin link.
 */
import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowLeft, Shield, Satellite, MapPin, FileCheck, Scale, Calculator,
  Layers, BookOpen, Link2, Plus, Check, X, Coins,
} from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { PageAiPanel } from "../components/ai/PageAiPanel";
import {
  LEVEL_POLICY, SATELLITE_CARDS, readPoints, addPoint, readEvidence, addEvidence,
  readClaims, upsertClaim, verifyClaim, issueClaim, readLedger, estimateQuality,
  classifyLevel, type AssuranceLevel, type EvidenceItem,
} from "../lib/mrvStore";
import { readFarms } from "../lib/farmsStore";

function Shell({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mx-auto max-w-4xl space-y-5 p-5 sm:p-8">
      <Link to="/mrv" className="inline-flex items-center gap-1 text-sm font-bold text-stone-500">
        <ArrowLeft className="h-4 w-4" /> MRV
      </Link>
      <h1 className="font-display text-2xl text-stone-800">{title}</h1>
      {children}
    </div>
  );
}

/** /mrv/levels */
export function MrvLevelsPage() {
  const { lang } = useLang();
  return (
    <Shell title={lang === "fa" ? "سطوح اطمینان L1 · L2 · L3" : "Assurance levels L1 · L2 · L3"}>
      <PageAiPanel lang={lang} pageKey="mrv-levels" compact />
      <p className="text-sm text-stone-600">
        Aligned with IPCC-style tiers + hybrid protocols (Verra VM0042, GS SOC, FAO GSOC MRV).
      </p>
      <div className="grid gap-4 sm:grid-cols-3">
        {(["L1", "L2", "L3"] as AssuranceLevel[]).map((lv) => (
          <div key={lv} className={`rounded-2xl border p-5 shadow-sm ${
            lv === "L3" ? "border-emerald-400 bg-emerald-50" : "border-stone-200 bg-white"
          }`}>
            <p className="font-display text-3xl font-black text-emerald-800">{lv}</p>
            <p className="mt-2 text-xs font-bold text-stone-500">{LEVEL_POLICY[lv].sources}</p>
            <p className="mt-2 text-sm leading-relaxed text-stone-700">
              {lang === "fa" ? LEVEL_POLICY[lv].fa : LEVEL_POLICY[lv].en}
            </p>
            <p className="mt-3 text-xs font-bold text-amber-800">Buffer {(LEVEL_POLICY[lv].buffer * 100).toFixed(0)}%</p>
          </div>
        ))}
      </div>
    </Shell>
  );
}

/** /mrv/evidence */
export function MrvEvidencePage() {
  const { lang } = useLang();
  const [list, setList] = useState(() => readEvidence());
  const [type, setType] = useState<EvidenceItem["type"]>("satellite");
  const [label, setLabel] = useState("");
  const [value, setValue] = useState("");
  const q = estimateQuality(list);

  const add = (e: React.FormEvent) => {
    e.preventDefault();
    if (!label.trim()) return;
    addEvidence({ type, label: label.trim(), value: value ? parseFloat(value) : undefined, unit: type === "satellite" ? "ndvi" : undefined, source: type });
    setList(readEvidence());
    setLabel("");
  };

  return (
    <Shell title={lang === "fa" ? "بسته شواهد" : "Evidence package"}>
      <div className="rounded-2xl bg-emerald-600 p-4 text-white">
        <p className="text-xs uppercase opacity-80">Computed</p>
        <p className="text-lg font-bold">{q.level} · Q={q.quality_score} · factor={q.effective_mint_factor}</p>
      </div>
      <ul className="space-y-2">
        {list.map((x) => (
          <li key={x.id} className="rounded-xl border bg-white px-4 py-3 text-sm">
            <span className="font-bold">{x.type}</span> · {x.label} {x.value != null && `· ${x.value} ${x.unit || ""}`}
          </li>
        ))}
      </ul>
      <form onSubmit={add} className="flex flex-wrap gap-2 rounded-2xl border bg-stone-50 p-3">
        <select value={type} onChange={(e) => setType(e.target.value as EvidenceItem["type"])} className="rounded-xl border px-3 py-2 text-sm">
          <option value="satellite">satellite</option>
          <option value="field">field</option>
          <option value="lab">lab</option>
          <option value="model">model</option>
          <option value="document">document</option>
        </select>
        <input value={label} onChange={(e) => setLabel(e.target.value)} placeholder="Label" className="rounded-xl border px-3 py-2 text-sm" />
        <input value={value} onChange={(e) => setValue(e.target.value)} placeholder="Value" className="w-24 rounded-xl border px-3 py-2 text-sm" />
        <button type="submit" className="rounded-xl bg-emerald-600 px-3 py-2 text-xs font-bold text-white"><Plus className="inline h-3.5 w-3.5" /> Add</button>
      </form>
    </Shell>
  );
}

/** /mrv/verify */
export function MrvVerifyPage() {
  const { lang } = useLang();
  const [claims, setClaims] = useState(() => readClaims());
  const refresh = () => setClaims(readClaims());

  return (
    <Shell title={lang === "fa" ? "صف تأیید پایشگر" : "Verifier queue"}>
      <PageAiPanel lang={lang} pageKey="mrv-verify" compact />
      <ul className="space-y-3">
        {claims.map((c) => (
          <li key={c.id} className="rounded-2xl border bg-white p-4 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="font-bold text-stone-800">{c.title}</p>
                <p className="text-xs text-stone-500">{c.level} · {c.status} · {c.measured_tco2e} tCO₂e · {c.issuable_eco} ECO</p>
              </div>
              <div className="flex gap-2">
                {c.status === "under_review" || c.status === "submitted" ? (
                  <>
                    <button type="button" onClick={() => { verifyClaim(c.id, "verifier_demo", true); refresh(); }}
                      className="inline-flex items-center gap-1 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-bold text-white"><Check className="h-3.5 w-3.5" /> Verify</button>
                    <button type="button" onClick={() => { verifyClaim(c.id, "verifier_demo", false); refresh(); }}
                      className="inline-flex items-center gap-1 rounded-lg bg-rose-100 px-3 py-1.5 text-xs font-bold text-rose-800"><X className="h-3.5 w-3.5" /> Reject</button>
                  </>
                ) : null}
                {c.status === "verified" && (
                  <button type="button" onClick={() => { issueClaim(c.id, "treasury_demo"); refresh(); }}
                    className="inline-flex items-center gap-1 rounded-lg bg-violet-600 px-3 py-1.5 text-xs font-bold text-white"><Coins className="h-3.5 w-3.5" /> Issue ECO</button>
                )}
              </div>
            </div>
          </li>
        ))}
      </ul>
    </Shell>
  );
}

/** /mrv/satellites */
export function MrvSatellitesPage() {
  const { lang } = useLang();
  return (
    <Shell title={lang === "fa" ? "کارت‌های ماهواره" : "Satellite cards"}>
      <p className="text-sm text-stone-600">Multi-sensor stack for practice detection & biomass proxies (RegenAg / dMRV style).</p>
      <div className="grid gap-3 sm:grid-cols-2">
        {SATELLITE_CARDS.map((s) => (
          <div key={s.id} className={`rounded-2xl border p-4 ${
            s.priority_mrv ? "border-emerald-300 bg-emerald-50/50" : "border-stone-200 bg-white"
          }`}>
            <div className="flex items-center gap-2">
              <Satellite className="h-5 w-5 text-emerald-700" />
              <h3 className="font-bold">{s.name}</h3>
            </div>
            <p className="mt-1 text-xs text-stone-500">{s.provider} · {s.resolution_m} m · revisit {s.revisit_days}d</p>
            <p className="mt-2 text-xs">{s.indices.join(" · ")}</p>
            <p className="mt-1 text-xs text-stone-600">{s.notes}</p>
            {s.priority_mrv && <span className="mt-2 inline-block rounded-full bg-emerald-600 px-2 py-0.5 text-[10px] font-bold text-white">MRV priority</span>}
          </div>
        ))}
      </div>
      <Link to="/satellite" className="text-sm font-bold text-emerald-700 underline">Open satellite hub →</Link>
    </Shell>
  );
}

/** /mrv/points */
export function MrvPointsPage() {
  const { lang } = useLang();
  const farms = readFarms();
  const [points, setPoints] = useState(() => readPoints());
  const [name, setName] = useState("");
  const [lat, setLat] = useState("34.5");
  const [lon, setLon] = useState("69.2");
  const [farmId, setFarmId] = useState(farms[0]?.id || "");

  const add = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    addPoint({ name: name.trim(), lat: parseFloat(lat), lon: parseFloat(lon), kind: "soil_sample", farmId: farmId || undefined });
    setPoints(readPoints());
    setName("");
  };

  return (
    <Shell title={lang === "fa" ? "نقاط پایش میدانی" : "Field monitoring points"}>
      <p className="text-xs text-stone-500">Register points on farm parcels · link to claims · NDVI sample design</p>
      <ul className="space-y-2">
        {points.map((p) => (
          <li key={p.id} className="flex justify-between rounded-xl border bg-white px-4 py-3 text-sm">
            <span><MapPin className="inline h-3.5 w-3.5 text-emerald-600" /> <strong>{p.name}</strong> · {p.kind} · farm {p.farmId || "—"}</span>
            <span className="font-mono text-xs">{p.lat.toFixed(4)}, {p.lon.toFixed(4)}</span>
          </li>
        ))}
      </ul>
      <form onSubmit={add} className="grid gap-2 rounded-2xl border bg-stone-50 p-3 sm:grid-cols-2">
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Point name" className="rounded-xl border px-3 py-2 text-sm" />
        <select value={farmId} onChange={(e) => setFarmId(e.target.value)} className="rounded-xl border px-3 py-2 text-sm">
          <option value="">No farm</option>
          {farms.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
        </select>
        <input value={lat} onChange={(e) => setLat(e.target.value)} placeholder="Lat" className="rounded-xl border px-3 py-2 text-sm" />
        <input value={lon} onChange={(e) => setLon(e.target.value)} placeholder="Lon" className="rounded-xl border px-3 py-2 text-sm" />
        <button type="submit" className="rounded-xl bg-emerald-600 px-3 py-2 text-xs font-bold text-white sm:col-span-2">Add point</button>
      </form>
      <Link to="/farms" className="text-sm font-bold text-emerald-700 underline">Farms map →</Link>
    </Shell>
  );
}

/** /mrv/claim */
export function MrvClaimPage() {
  const { lang } = useLang();
  const nav = useNavigate();
  const evidence = readEvidence();
  const points = readPoints();
  const q = estimateQuality(evidence);
  const [title, setTitle] = useState("New SOC claim");
  const [v, setV] = useState("40");

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const measured = parseFloat(v) || 0;
    const Fc = 25; // tCO2e pathway default
    const issuable = Math.round(measured * Fc * q.effective_mint_factor);
    const claim = {
      id: `c${Date.now()}`,
      title: title.trim() || "Claim",
      status: "submitted" as const,
      level: q.level,
      measured_tco2e: measured,
      quality_score: q.quality_score,
      permanence_buffer: q.permanence_buffer,
      issuable_eco: issuable,
      evidenceIds: evidence.map((x) => x.id),
      pointIds: points.slice(0, 3).map((p) => p.id),
      methodology: "hydroma_hybrid_v1",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    upsertClaim(claim);
    nav("/mrv/verify");
  };

  return (
    <Shell title={lang === "fa" ? "ثبت ادعا و mint پیش‌نمایش" : "Submit claim · mint preview"}>
      <div className="rounded-2xl border border-violet-200 bg-violet-50 p-4 text-sm">
        Level <strong>{q.level}</strong> · Q={q.quality_score} · buffer {(q.permanence_buffer * 100).toFixed(0)}% · factor={q.effective_mint_factor}
      </div>
      <form onSubmit={submit} className="space-y-3 rounded-2xl border bg-white p-5">
        <input value={title} onChange={(e) => setTitle(e.target.value)} className="w-full rounded-xl border px-3 py-2.5 text-sm" />
        <label className="block text-sm">Measured tCO₂e
          <input type="number" value={v} onChange={(e) => setV(e.target.value)} className="mt-1 w-full rounded-xl border px-3 py-2.5" />
        </label>
        <p className="text-xs text-stone-500">Preview ECO ≈ V × 25 × Q_eff (scarcity applied on-chain later)</p>
        <button type="submit" className="w-full rounded-xl bg-emerald-600 py-3 text-sm font-bold text-white">Submit for verification</button>
      </form>
      <Link to="/mrv/evidence" className="text-sm font-bold text-emerald-700 underline">Build evidence first →</Link>
    </Shell>
  );
}

/** /mrv/methodology */
export function MrvMethodologyPage() {
  const { lang } = useLang();
  const refs = [
    { id: "ipcc", t: "IPCC GHG Inventory Tiers 1–3", d: "Default → country data → measurement-based" },
    { id: "fao", t: "FAO GSOC MRV", d: "Soil organic carbon stock change assessment" },
    { id: "vm42", t: "Verra VM0042", d: "Improved agricultural land management; hybrid measure-model" },
    { id: "gs", t: "Gold Standard SOC Framework", d: "Model and measurement pathways" },
    { id: "car", t: "CAR Soil Enrichment Protocol", d: "US soil enrichment; sampling + model" },
    { id: "icvcm", t: "ICVCM Core Carbon Principles", d: "Integrity label for high-quality credits" },
    { id: "iso", t: "ISO 14064-2 / 14065", d: "Project GHG accounting · VVB accreditation context" },
  ];
  return (
    <Shell title={lang === "fa" ? "استانداردها و متدولوژی" : "Standards & methodology"}>
      <ul className="space-y-2">
        {refs.map((r) => (
          <li key={r.id} className="rounded-xl border bg-white px-4 py-3">
            <p className="font-bold text-stone-800">{r.t}</p>
            <p className="text-xs text-stone-500">{r.d}</p>
          </li>
        ))}
      </ul>
      <p className="text-xs text-stone-500">Hydroma implements internal hybrid dMRV; external registry listing requires separate VVB process.</p>
    </Shell>
  );
}

/** /mrv/ledger */
export function MrvLedgerPage() {
  const { lang } = useLang();
  const events = readLedger();
  return (
    <Shell title={lang === "fa" ? "دفتر رویداد تأیید" : "Verification ledger"}>
      {events.length === 0 ? <p className="text-stone-500">No events yet — verify a claim first.</p> : (
        <ul className="space-y-2">
          {events.map((e) => (
            <li key={e.id} className="rounded-xl border bg-white px-4 py-3 text-sm">
              <strong>{e.action}</strong> · claim {e.claimId} · {e.actor}
              <span className="block text-xs text-stone-400">{new Date(e.at).toLocaleString()}</span>
              {e.note && <span className="text-xs text-stone-600">{e.note}</span>}
            </li>
          ))}
        </ul>
      )}
    </Shell>
  );
}

/** /mrv/calculator */
export function MrvCalculatorPage() {
  const { lang } = useLang();
  const [v, setV] = useState(40);
  const [fc, setFc] = useState(25);
  const [add, setAdd] = useState(1);
  const [leak, setLeak] = useState(0);
  const evidence = readEvidence();
  const q = useMemo(() => estimateQuality(evidence, add, leak), [evidence, add, leak]);
  const issuable = v * fc * q.effective_mint_factor;

  return (
    <Shell title={lang === "fa" ? "ماشین‌حساب Q و mint" : "Q & mint calculator"}>
      <div className="space-y-3 rounded-2xl border bg-white p-5">
        <label className="block text-sm">V measured <input type="number" value={v} onChange={(e) => setV(+e.target.value)} className="mt-1 w-full rounded-xl border px-3 py-2" /></label>
        <label className="block text-sm">Fc credit factor <input type="number" value={fc} onChange={(e) => setFc(+e.target.value)} className="mt-1 w-full rounded-xl border px-3 py-2" /></label>
        <label className="block text-sm">Additionality 0–1 <input type="number" step="0.05" min={0} max={1} value={add} onChange={(e) => setAdd(+e.target.value)} className="mt-1 w-full rounded-xl border px-3 py-2" /></label>
        <label className="block text-sm">Leakage risk 0–0.5 <input type="number" step="0.05" min={0} max={0.5} value={leak} onChange={(e) => setLeak(+e.target.value)} className="mt-1 w-full rounded-xl border px-3 py-2" /></label>
        <div className="rounded-xl bg-emerald-600 p-4 text-white">
          <p className="text-xs opacity-80">{q.level} · Q={q.quality_score} · buffer {(q.permanence_buffer * 100).toFixed(0)}%</p>
          <p className="font-display text-3xl font-black">{issuable.toFixed(2)} ECO</p>
          <p className="text-xs opacity-80">M = V × Fc × Q_eff × R × S (R=S=1 here)</p>
        </div>
      </div>
    </Shell>
  );
}

/** /mrv/buffer */
export function MrvBufferPage() {
  const { lang } = useLang();
  return (
    <Shell title={lang === "fa" ? "بافر ماندگاری" : "Permanence buffer pool"}>
      <p className="text-sm text-stone-600">Inspired by AFOLU non-permanence risk tools — share of credits held against reversal.</p>
      <ul className="mt-3 space-y-2">
        {(["L1", "L2", "L3"] as AssuranceLevel[]).map((lv) => (
          <li key={lv} className="flex justify-between rounded-xl border bg-white px-4 py-3 text-sm">
            <span className="font-bold">{lv}</span>
            <span>{(LEVEL_POLICY[lv].buffer * 100).toFixed(0)}% held</span>
          </li>
        ))}
      </ul>
    </Shell>
  );
}

/** /mrv/farm-link */
export function MrvFarmLinkPage() {
  const { lang } = useLang();
  const farms = readFarms();
  return (
    <Shell title={lang === "fa" ? "اتصال مزرعه ↔ MRV" : "Farm ↔ MRV link"}>
      <ul className="space-y-2">
        {farms.map((f) => (
          <li key={f.id} className="flex flex-wrap items-center justify-between gap-2 rounded-xl border bg-white px-4 py-3 text-sm">
            <span>{f.name} · Hydroma {f.hydromaScore}% · {f.areaHa} ha</span>
            <div className="flex gap-2">
              <Link to={`/farms/${f.id}/monitoring`} className="text-xs font-bold text-emerald-700 underline">Monitor</Link>
              <Link to="/mrv/points" className="text-xs font-bold text-emerald-700 underline">Points</Link>
              <Link to="/mrv/claim" className="text-xs font-bold text-violet-700 underline">Claim</Link>
            </div>
          </li>
        ))}
      </ul>
    </Shell>
  );
}

/** Nav cards for main /mrv enhancement — used if imported */
export function MrvNavGrid() {
  const links = [
    { to: "/mrv/levels", icon: Layers, t: "Levels L1–L3" },
    { to: "/mrv/evidence", icon: FileCheck, t: "Evidence" },
    { to: "/mrv/verify", icon: Scale, t: "Verify" },
    { to: "/mrv/satellites", icon: Satellite, t: "Satellites" },
    { to: "/mrv/points", icon: MapPin, t: "Points" },
    { to: "/mrv/claim", icon: Coins, t: "Claim / mint" },
    { to: "/mrv/methodology", icon: BookOpen, t: "Standards" },
    { to: "/mrv/ledger", icon: Shield, t: "Ledger" },
    { to: "/mrv/calculator", icon: Calculator, t: "Calculator" },
    { to: "/mrv/buffer", icon: Shield, t: "Buffer" },
    { to: "/mrv/farm-link", icon: Link2, t: "Farm link" },
  ];
  return (
    <div className="grid gap-2 sm:grid-cols-3 lg:grid-cols-4">
      {links.map((l) => (
        <Link key={l.to} to={l.to} className="flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-3 py-3 text-sm font-bold hover:border-emerald-300">
          <l.icon className="h-4 w-4 text-emerald-700" /> {l.t}
        </Link>
      ))}
    </div>
  );
}
