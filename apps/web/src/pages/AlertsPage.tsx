// apps/web/src/pages/AlertsPage.tsx
import { useMemo, useState } from "react";
import { Bell, CheckCheck, Inbox } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { AnimatedCounter } from "../components/eco/AnimatedCounter";
import { AlertItem } from "../components/alerts/AlertItem";
import { ALERT_STR, levelText, type AlertLang } from "../components/alerts/alertsI18n";
import { MOCK_ALERTS, countAlerts, type Alert, type AlertLevel } from "../components/alerts/alertsData";

const STAT = {
  critical: { text: "text-red-700", bg: "bg-red-50" },
  warning: { text: "text-amber-700", bg: "bg-amber-50" },
  info: { text: "text-blue-700", bg: "bg-blue-50" },
  unread: { text: "text-green-700", bg: "bg-green-50" },
} as const;

type Filter = "all" | AlertLevel;
const FILTERS: Filter[] = ["all", "critical", "warning", "info", "success"];

export default function AlertsPage() {
  const { lang } = useLang();
  const s = ALERT_STR[lang as AlertLang];

  const [alerts, setAlerts] = useState<Alert[]>(MOCK_ALERTS);
  const [filter, setFilter] = useState<Filter>("all");

  // آمار derived از دادهٔ واقعی (رفع باگ اعداد hardcoded)
  const counts = useMemo(() => countAlerts(alerts), [alerts]);
  const filtered = useMemo(
    () => (filter === "all" ? alerts : alerts.filter((a) => a.level === filter)),
    [alerts, filter]
  );

  const toggleRead = (id: string) =>
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, read: !a.read } : a)));
  const dismiss = (id: string) => setAlerts((prev) => prev.filter((a) => a.id !== id));
  const markAllRead = () => setAlerts((prev) => prev.map((a) => ({ ...a, read: true })));

  const statCards = [
    { key: "critical", label: s.statCritical, value: counts.critical, ...STAT.critical },
    { key: "warning", label: s.statWarning, value: counts.warning, ...STAT.warning },
    { key: "info", label: s.statInfo, value: counts.info, ...STAT.info },
    { key: "unread", label: s.statUnread, value: counts.unread, ...STAT.unread },
  ];

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      {/* header */}
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15">
              <Bell className="h-5 w-5 text-green-700" />
            </div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <button
            onClick={markAllRead}
            disabled={counts.unread === 0}
            className="inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-4 py-2 text-sm font-bold text-stone-700 transition-colors hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <CheckCheck className="h-4 w-4" />
            {s.markAllRead}
          </button>
        </div>
      </SectionReveal>

      {/* stats (derived) */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {statCards.map((c, i) => (
          <SectionReveal key={c.key} delay={i * 70}>
            <div className={`rounded-2xl border border-stone-200/80 p-4 shadow-sm ${c.bg}`}>
              <p className="text-sm font-medium text-stone-600">{c.label}</p>
              <p className={`mt-1 font-display text-3xl font-black tabular-nums ${c.text}`}>
                <AnimatedCounter end={c.value} />
              </p>
            </div>
          </SectionReveal>
        ))}
      </div>

      {/* filters */}
      <SectionReveal delay={120}>
        <div className="flex flex-wrap gap-2">
          {FILTERS.map((f) => {
            const active = filter === f;
            const label = f === "all" ? s.filterAll : levelText(s, f);
            return (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`rounded-full px-4 py-2 text-sm font-bold transition-all ${
                  active
                    ? "bg-green-600 text-white shadow-sm"
                    : "border border-stone-200 bg-white text-stone-600 hover:bg-stone-50"
                }`}
              >
                {label}
              </button>
            );
          })}
        </div>
      </SectionReveal>

      {/* list */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <SectionReveal>
            <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
              <Inbox className="h-10 w-10 text-stone-300" />
              <p className="text-stone-500">{s.empty}</p>
            </div>
          </SectionReveal>
        ) : (
          filtered.map((a, i) => (
            <SectionReveal key={a.id} delay={Math.min(i * 60, 300)}>
              <AlertItem
                alert={a}
                strings={s}
                lang={lang as AlertLang}
                onToggleRead={toggleRead}
                onDismiss={dismiss}
              />
            </SectionReveal>
          ))
        )}
      </div>
    </div>
  );
}