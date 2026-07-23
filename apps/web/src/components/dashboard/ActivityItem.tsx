// apps/web/src/components/dashboard/ActivityItem.tsx
import { UserPlus, FolderCheck, CreditCard, ShieldCheck, FileBarChart } from "lucide-react";
import type { Activity, ActivityKind } from "./dashboardData";
import { dashText, timeAgo, type DashboardStrings, type DashLang } from "./dashboardI18n";

const KIND_STYLE: Record<ActivityKind, { icon: typeof UserPlus; bg: string; text: string }> = {
  user: { icon: UserPlus, bg: "bg-green-50", text: "text-green-700" },
  project: { icon: FolderCheck, bg: "bg-blue-50", text: "text-blue-700" },
  payment: { icon: CreditCard, bg: "bg-amber-50", text: "text-amber-700" },
  alert: { icon: ShieldCheck, bg: "bg-rose-50", text: "text-rose-700" },
  report: { icon: FileBarChart, bg: "bg-violet-50", text: "text-violet-700" },
};

interface Props {
  activity: Activity;
  strings: DashboardStrings;
  lang: DashLang;
}

export function ActivityItem({ activity: a, strings: s, lang }: Props) {
  const cfg = KIND_STYLE[a.kind];
  const Icon = cfg.icon;
  return (
    <li className="flex items-center gap-3 rounded-xl px-2 py-2.5 transition-colors hover:bg-stone-50">
      <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-full ${cfg.bg} ${cfg.text}`}>
        <Icon className="h-4 w-4" />
      </span>
      <p className="min-w-0 flex-1 truncate text-sm font-medium text-stone-800">{dashText(s, a.titleKey)}</p>
      <span className="shrink-0 text-xs text-stone-500">{timeAgo(a.timestamp, lang)}</span>
    </li>
  );
}