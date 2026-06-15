"use client";

import * as React from "react";
import Link from "next/link";

type KpiCardProps = {
  label: string;
  value: string;
  unit?: string;
  trend?: "up" | "down" | "stable";
  subtitle?: string;
  href?: string;
};

function KpiCard({ label, value, unit, trend, subtitle, href }: KpiCardProps) {
  const trendColor =
    trend === "up"
      ? "text-emerald-400"
      : trend === "down"
      ? "text-rose-400"
      : "text-slate-300";

  const trendIcon =
    trend === "up" ? "▲" : trend === "down" ? "▼" : "●";

  const content = (
    <div className="relative overflow-hidden rounded-2xl border border-white/5 bg-slate-950/70 px-4 py-3 shadow-[0_18px_45px_rgba(15,23,42,0.9)] transition-transform duration-150 hover:-translate-y-0.5 hover:border-emerald-400/40 hover:shadow-[0_24px_60px_rgba(16,185,129,0.45)]">
      <div className="absolute inset-0 pointer-events-none bg-gradient-to-br from-emerald-500/5 via-emerald-400/0 to-cyan-400/10" />
      <div className="relative flex flex-col gap-1">
        <div className="text-[11px] uppercase tracking-[0.18em] text-slate-400">
          {label}
        </div>
        <div className="flex items-baseline gap-1">
          <div className="text-2xl font-semibold text-slate-50">
            {value}
          </div>
          {unit && (
            <span className="text-xs text-slate-400">{unit}</span>
          )}
        </div>
        {subtitle && (
          <div className="text-[11px] text-slate-400 line-clamp-2">
            {subtitle}
          </div>
        )}
        {trend && (
          <div className={`mt-1 flex items-center gap-1 text-[11px] ${trendColor}`}>
            <span className="text-[10px]">{trendIcon}</span>
            <span>
              {trend === "up"
                ? "Improving vs last period"
                : trend === "down"
                ? "Worse vs last period"
                : "Stable trend"}
            </span>
          </div>
        )}
      </div>
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="block focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400/70 rounded-2xl">
        {content}
      </Link>
    );
  }

  return content;
}

type SectionCardProps = {
  title: string;
  description?: string;
  children: React.ReactNode;
  accent?: "emerald" | "cyan" | "amber" | "rose";
  actionLabel?: string;
  actionHref?: string;
};

function SectionCard({
  title,
  description,
  children,
  accent = "emerald",
  actionLabel,
  actionHref,
}: SectionCardProps) {
  const accentColor =
    accent === "emerald"
      ? "from-emerald-500/12 to-emerald-400/0"
      : accent === "cyan"
      ? "from-cyan-500/12 to-cyan-400/0"
      : accent === "amber"
      ? "from-amber-400/18 to-amber-300/0"
      : "from-rose-500/14 to-rose-400/0";

  return (
    <section className="relative overflow-hidden rounded-3xl border border-white/5 bg-slate-950/80 px-4 py-4 shadow-[0_24px_60px_rgba(15,23,42,0.95)] md:px-5 md:py-5">
      <div
        className={`pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b ${accentColor}`}
      />
      <div className="relative space-y-4">
        <header className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold tracking-wide text-slate-50">
              {title}
            </h2>
            {description && (
              <p className="mt-1 max-w-xl text-xs text-slate-400">
                {description}
              </p>
            )}
          </div>
          {actionHref && actionLabel && (
            <Link
              href={actionHref}
              className="inline-flex items-center gap-1 rounded-full border border-white/12 bg-slate-950/80 px-3 py-1.5 text-[11px] text-slate-200 hover:border-emerald-400/60 hover:bg-emerald-500/10 hover:text-emerald-50 transition-colors"
            >
              <span>{actionLabel}</span>
              <span className="text-[10px]">↗</span>
            </Link>
          )}
        </header>
        <div>{children}</div>
      </div>
    </section>
  );
}

type WaterPoint = { label: string; netWater: number };

function WaterMiniChart({ data }: { data: WaterPoint[] }) {
  if (!data.length) return null;

  const max = Math.max(...data.map((d) => d.netWater), 0);
  const min = Math.min(...data.map((d) => d.netWater), 0);
  const range = max - min || 1;
  const width = 260;
  const height = 80;
  const stepX = width / Math.max(data.length - 1, 1);

  const points = data
    .map((d, idx) => {
      const x = idx * stepX;
      const norm = (d.netWater - min) / range;
      const y = height - norm * (height - 10) - 5;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg
      width="100%"
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className="mt-4 rounded-xl border border-white/5 bg-gradient-to-tr from-emerald-500/10 via-slate-900 to-cyan-500/10"
    >
      <polyline
        fill="none"
        stroke="url(#waterStroke)"
        strokeWidth="2"
        points={points}
      />
      <defs>
        <linearGradient id="waterStroke" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#22c55e" />
          <stop offset="100%" stopColor="#22d3ee" />
        </linearGradient>
      </defs>
    </svg>
  );
}

export default function DashboardPage() {
  const [selectedPilot, setSelectedPilot] = React.useState<"nozhin" | "central" | "corridor">(
    "nozhin"
  );
  const [refreshKey, setRefreshKey] = React.useState(0);

  const mockGlobalKpis = [
    {
      label: "Active projects",
      value: selectedPilot === "nozhin" ? "23" : selectedPilot === "central" ? "15" : "9",
      unit: "",
      trend: "up" as const,
      subtitle: "Total landscape & farm pilots currently monitored",
      href: "/farmers",
    },
    {
      label: "Avg soil–water health score",
      value: selectedPilot === "nozhin" ? "78" : selectedPilot === "central" ? "71" : "83",
      unit: "/ 100",
      trend: "up" as const,
      subtitle: "Composite index from LDN, NDVI, water balance and erosion",
      href: "/water-soil",
    },
    {
      label: "Total carbon credits",
      value: selectedPilot === "nozhin" ? "12.4k" : selectedPilot === "central" ? "9.2k" : "6.8k",
      unit: "tCO₂e",
      trend: "up" as const,
      subtitle: "Verified or modeled mitigation potential across pilots",
      href: "/mrv",
    },
    {
      label: "Data consistency score",
      value: selectedPilot === "nozhin" ? "91" : selectedPilot === "central" ? "87" : "93",
      unit: "/ 100",
      trend: "stable" as const,
      subtitle: "Aggregate QA/QC metric across sensors, models and satellite data",
      href: "/verification",
    },
  ];

  const mockRecentAnalyses = [
    {
      id: "AN-2045",
      region: "Nozhin watershed",
      crop: "Pistachio",
      score: 82,
      status: "Healthy",
      verification: "Pass",
      date: "2026-06-12",
    },
    {
      id: "AN-2041",
      region: "Central plateau pilot",
      crop: "Wheat",
      score: 73,
      status: "Watch",
      verification: "Review",
      date: "2026-06-10",
    },
    {
      id: "AN-2038",
      region: "Eco corridor pilot",
      crop: "Almond",
      score: 65,
      status: "Stress",
      verification: "Flagged",
      date: "2026-06-09",
    },
  ];

  const mockAlerts = [
    {
      id: "AL-938",
      severity: "High",
      message: "Critical soil moisture deficit in pistachio plot #12.",
      timestamp: "2h ago",
    },
    {
      id: "AL-936",
      severity: "Medium",
      message: "Drought index SPI below -1.5 for Central plateau pilot.",
      timestamp: "6h ago",
    },
    {
      id: "AL-931",
      severity: "Low",
      message: "NDVI trend slightly decreasing for wheat fields.",
      timestamp: "Yesterday",
    },
  ];

  const mockStoreItems = [
    {
      name: "Full Soil–Water Health Assessment",
      description: "Integrated analysis of soil, water balance, NDVI, RUSLE and LDN indicators for one pilot site.",
      price: "89",
      currency: "USD",
    },
    {
      name: "Seasonal Climate & Drought Outlook",
      description: "Scenario-based drought and climate risk briefing for the next 3–6 months.",
      price: "59",
      currency: "USD",
    },
    {
      name: "MRV & Carbon Readiness Scan",
      description: "High-level MRV and carbon-market readiness assessment for one landscape program.",
      price: "149",
      currency: "USD",
    },
  ];

  const waterSeries: WaterPoint[] =
    selectedPilot === "nozhin"
      ? [
          { label: "M1", netWater: 4 },
          { label: "M2", netWater: 2 },
          { label: "M3", netWater: 1 },
          { label: "M4", netWater: 3 },
          { label: "M5", netWater: 5 },
        ]
      : selectedPilot === "central"
      ? [
          { label: "M1", netWater: -1 },
          { label: "M2", netWater: -2 },
          { label: "M3", netWater: 0 },
          { label: "M4", netWater: 1 },
          { label: "M5", netWater: -0.5 },
        ]
      : [
          { label: "M1", netWater: 2 },
          { label: "M2", netWater: 3 },
          { label: "M3", netWater: 3.5 },
          { label: "M4", netWater: 4 },
          { label: "M5", netWater: 4.5 },
        ];

  function handlePilotChange(pilot: "nozhin" | "central" | "corridor") {
    setSelectedPilot(pilot);
    setRefreshKey((k) => k + 1);
  }

  return (
    <div className="space-y-6">
      {/* Intro + pilot switcher */}
      <div className="flex flex-col gap-3 pb-1 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-lg font-semibold tracking-tight text-slate-50 md:text-xl">
            Integrated Landscape Intelligence
          </h1>
          <p className="mt-1 max-w-2xl text-xs text-slate-400">
            This console fuses hydrology, soil, remote sensing, MRV and economics into a single,
            decision-ready view for arid and semi-arid production landscapes.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-[11px] text-slate-300">
          <span className="rounded-full border border-emerald-400/40 bg-emerald-500/10 px-3 py-1 text-emerald-200">
            Live · Pilot: {selectedPilot === "nozhin" ? "HydroMa Nojin" : selectedPilot === "central" ? "Central plateau" : "Eco corridor"}
          </span>
          <div className="inline-flex gap-1 rounded-full border border-white/12 bg-slate-950/80 p-1">
            <PilotChip
              label="Nojin"
              active={selectedPilot === "nozhin"}
              onClick={() => handlePilotChange("nozhin")}
            />
            <PilotChip
              label="Central plateau"
              active={selectedPilot === "central"}
              onClick={() => handlePilotChange("central")}
            />
            <PilotChip
              label="Eco corridor"
              active={selectedPilot === "corridor"}
              onClick={() => handlePilotChange("corridor")}
            />
          </div>
          <button
            onClick={() => setRefreshKey((k) => k + 1)}
            className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-slate-900/80 px-3 py-1 text-[11px] hover:bg-slate-800"
          >
            <span className="text-[10px]">⟳</span>
            Refresh snapshot
          </button>
        </div>
      </div>

      {/* Global KPI row */}
      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
        {mockGlobalKpis.map((kpi) => (
          <KpiCard
            key={kpi.label + refreshKey}
            label={kpi.label}
            value={kpi.value}
            unit={kpi.unit}
            trend={kpi.trend}
            subtitle={kpi.subtitle}
            href={kpi.href}
          />
        ))}
      </div>

      {/* Main grid sections */}
      <div className="grid gap-4 lg:grid-cols-3">
        {/* Water & Soil Health */}
        <div className="space-y-4 lg:col-span-2">
          <SectionCard
            title="Water & Soil Health"
            description="Composite view of soil moisture, water balance, erosion risk and land degradation neutrality for priority pilots."
            accent="emerald"
            actionLabel="Open Water & Soil module"
            actionHref="/water-soil"
          >
            <div className="grid gap-3 md:grid-cols-3">
              {/* Chart block */}
              <div className="col-span-2 rounded-2xl border border-white/5 bg-slate-950/70 p-4">
                <div className="flex items-center justify-between gap-2">
                  <div>
                    <div className="text-xs font-medium text-slate-200">
                      Water balance signal
                    </div>
                    <div className="text-[11px] text-slate-400">
                      Net water dynamics for last 5 periods (mock chart per pilot)
                    </div>
                  </div>
                  <span className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-[11px] text-emerald-200">
                    /water/balance · /soil-water/comprehensive (future)
                  </span>
                </div>
                <WaterMiniChart data={waterSeries} />
              </div>
              <div className="space-y-3">
                <div className="rounded-2xl border border-white/5 bg-slate-950/70 p-3">
                  <div className="text-[11px] uppercase tracking-[0.18em] text-slate-500">
                    LDN status
                  </div>
                  <div className="mt-1 text-sm font-semibold text-slate-50">
                    {selectedPilot === "central" ? "At risk" : "On track"}
                  </div>
                  <p className="mt-1 text-[11px] text-slate-400">
                    Based on LDNResult, NDVIResult and RUSLEResult for key pilot sites.
                  </p>
                  <Link
                    href="/water-soil"
                    className="mt-2 inline-flex items-center gap-1 text-[11px] text-emerald-200 hover:text-emerald-100"
                  >
                    View indicators
                    <span className="text-[10px]">↗</span>
                  </Link>
                </div>
                <div className="rounded-2xl border border-white/5 bg-slate-950/70 p-3">
                  <div className="text-[11px] uppercase tracking-[0.18em] text-slate-500">
                    Latest integrated analysis
                  </div>
                  <div className="mt-1 text-xs text-slate-200">
                    {selectedPilot === "corridor" ? "88 / 100 – Healthy" : "82 / 100 – Healthy"}
                  </div>
                  <p className="mt-1 text-[11px] text-slate-400">
                    From ComprehensiveAnalysisResponse combining water, soil, drought and carbon metrics.
                  </p>
                  <Link
                    href="/water-soil"
                    className="mt-2 inline-flex items-center gap-1 text-[11px] text-cyan-200 hover:text-cyan-100"
                  >
                    Open full report
                    <span className="text-[10px]">↗</span>
                  </Link>
                </div>
              </div>
            </div>

            <div className="mt-4">
              <div className="mb-2 flex items-center justify-between text-[11px] text-slate-400">
                <span>Recent soil–water analyses</span>
                <Link
                  href="/water-soil"
                  className="rounded-full border border-white/10 bg-slate-900/70 px-3 py-1 hover:bg-slate-800 text-slate-100"
                >
                  Browse all analyses
                </Link>
              </div>
              <div className="overflow-hidden rounded-2xl border border-white/5 bg-slate-950/70">
                <table className="min-w-full border-separate border-spacing-0 text-xs">
                  <thead className="bg-slate-900/80 text-slate-300">
                    <tr>
                      <th className="px-3 py-2 text-left font-medium">ID</th>
                      <th className="px-3 py-2 text-left font-medium">Region</th>
                      <th className="px-3 py-2 text-left font-medium">Crop</th>
                      <th className="px-3 py-2 text-left font-medium">Score</th>
                      <th className="px-3 py-2 text-left font-medium">Status</th>
                      <th className="px-3 py-2 text-left font-medium">Verification</th>
                      <th className="px-3 py-2 text-left font-medium">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockRecentAnalyses.map((a, idx) => (
                      <tr
                        key={a.id}
                        className={
                          idx % 2 === 0
                            ? "bg-slate-950/60"
                            : "bg-slate-900/40"
                        }
                      >
                        <td className="px-3 py-2 text-slate-200">{a.id}</td>
                        <td className="px-3 py-2 text-slate-300">{a.region}</td>
                        <td className="px-3 py-2 text-slate-300">{a.crop}</td>
                        <td className="px-3 py-2 text-slate-200">{a.score}</td>
                        <td className="px-3 py-2 text-slate-200">{a.status}</td>
                        <td className="px-3 py-2 text-slate-200">{a.verification}</td>
                        <td className="px-3 py-2 text-slate-400">{a.date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </SectionCard>
        </div>

        {/* Climate, MRV, IoT & Store */}
        <div className="space-y-4">
          <SectionCard
            title="Climate, Drought & MRV"
            description="High-level signal on drought stress, satellite thermal anomalies, MRV and carbon economics."
            accent="cyan"
            actionLabel="Open Climate & MRV module"
            actionHref="/drought"
          >
            <div className="space-y-3">
              <div className="rounded-2xl border border-white/5 bg-slate-950/70 p-3">
                <div className="flex items-center justify-between gap-2">
                  <div>
                    <div className="text-[11px] uppercase tracking-[0.18em] text-slate-500">
                      Drought index (SPI / SPEI)
                    </div>
                    <div className="mt-1 text-sm text-slate-50">
                      {selectedPilot === "central" ? "Severe stress" : "Moderate stress"}
                    </div>
                    <p className="mt-1 text-[11px] text-slate-400">
                      From DroughtResult and DroughtIndexBase computed over CHIRPS/ERA5 time series.
                    </p>
                  </div>
                  <div className="h-12 w-12 rounded-full bg-gradient-to-tr from-amber-400/80 to-rose-500/80 text-slate-950 flex items-center justify-center text-xs font-semibold">
                    {selectedPilot === "central" ? "SPI -1.9" : "SPI -1.4"}
                  </div>
                </div>
                <Link
                  href="/drought"
                  className="mt-2 inline-flex items-center gap-1 text-[11px] text-cyan-200 hover:text-cyan-100"
                >
                  Explore drought scenarios
                  <span className="text-[10px]">↗</span>
                </Link>
              </div>

              <div className="rounded-2xl border border-white/5 bg-slate-950/70 p-3">
                <div className="flex items-center justify-between gap-2">
                  <div>
                    <div className="text-[11px] uppercase tracking-[0.18em] text-slate-500">
                      Satellite thermal monitor
                    </div>
                    <div className="mt-1 text-sm text-slate-50">
                      Heat stress pockets detected in Nojin pistachio belt
                    </div>
                    <p className="mt-1 text-[11px] text-slate-400">
                      This will visualize free satellite land surface temperature layers for your pilots.
                    </p>
                  </div>
                  <Link
                    href="/sat-thermal"
                    className="rounded-full border border-emerald-400/50 bg-emerald-500/10 px-3 py-1 text-[11px] text-emerald-100 hover:bg-emerald-500/20"
                  >
                    Open thermal map
                  </Link>
                </div>
              </div>

              <div className="rounded-2xl border border-white/5 bg-slate-950/70 p-3">
                <div className="text-[11px] uppercase tracking-[0.18em] text-slate-500">
                  MRV & carbon economics
                </div>
                <div className="mt-1 text-sm text-slate-50">
                  12.4k tCO₂e · indicative value 248k USD
                </div>
                <p className="mt-1 text-[11px] text-slate-400">
                  Based on CarbonCreditResponse and EconomicIndicatorResponse linked to active projects.
                </p>
                <Link
                  href="/mrv"
                  className="mt-2 inline-flex items-center gap-1 text-[11px] text-emerald-200 hover:text-emerald-100"
                >
                  Open MRV workspace
                  <span className="text-[10px]">↗</span>
                </Link>
              </div>
            </div>
          </SectionCard>

          <SectionCard
            title="IoT alerts & advisory"
            description="Near-real-time signal from sensors, thresholds and advisory rules."
            accent="amber"
            actionLabel="Open IoT module"
            actionHref="/iot"
          >
            <div className="space-y-2 text-xs">
              {mockAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className="rounded-2xl border border-white/5 bg-slate-950/80 px-3 py-2.5"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span
                          className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium ${
                            alert.severity === "High"
                              ? "bg-rose-500/15 text-rose-200 border border-rose-400/40"
                              : alert.severity === "Medium"
                              ? "bg-amber-400/15 text-amber-100 border border-amber-300/40"
                              : "bg-emerald-500/15 text-emerald-100 border border-emerald-400/40"
                          }`}
                        >
                          {alert.severity} alert
                        </span>
                        <span className="text-[10px] text-slate-500">
                          {alert.id} · {alert.timestamp}
                        </span>
                      </div>
                      <p className="mt-1 text-[11px] text-slate-200">
                        {alert.message}
                      </p>
                    </div>
                    <button className="rounded-full border border-white/10 bg-slate-900/80 px-2 py-1 text-[10px] text-slate-200 hover:bg-slate-800">
                      Acknowledge
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard
            title="Eco services & marketplace"
            description="Curated services built on top of the EcoNojin scientific core."
            accent="rose"
            actionLabel="Open Store"
            actionHref="/store"
          >
            <div className="space-y-2 text-xs">
              {mockStoreItems.map((item) => (
                <div
                  key={item.name}
                  className="rounded-2xl border border-white/5 bg-slate-950/85 px-3 py-2.5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="text-[11px] font-medium text-slate-50">
                        {item.name}
                      </div>
                      <p className="mt-1 text-[11px] text-slate-400">
                        {item.description}
                      </p>
                    </div>
                    <div className="text-right text-[11px]">
                      <div className="font-semibold text-emerald-300">
                        {item.price} {item.currency}
                      </div>
                      <button className="mt-1 rounded-full border border-emerald-400/50 bg-emerald-500/10 px-2 py-0.5 text-[10px] text-emerald-100 hover:bg-emerald-500/20">
                        View details
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  );
}

type PilotChipProps = {
  label: string;
  active: boolean;
  onClick: () => void;
};

function PilotChip({ label, active, onClick }: PilotChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={
        "rounded-full px-3 py-1 text-[11px] transition-colors " +
        (active
          ? "bg-emerald-500/20 text-emerald-100 border border-emerald-400/60"
          : "bg-slate-950/70 text-slate-300 border border-white/10 hover:bg-slate-900 hover:text-emerald-50")
      }
    >
      {label}
    </button>
  );
}
