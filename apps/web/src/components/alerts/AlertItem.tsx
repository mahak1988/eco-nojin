// apps/web/src/components/alerts/AlertItem.tsx
import { XCircle, AlertTriangle, Info, CheckCircle2, X, Check, Circle } from "lucide-react";
import type { Alert } from "./alertsData";
import { alertText, timeAgo, type AlertStrings, type AlertLang } from "./alertsI18n";

const LEVEL = {
  critical: { icon: XCircle, text: "text-red-700", bg: "bg-red-50", ring: "ring-red-600/15", bar: "bg-red-600" },
  warning: { icon: AlertTriangle, text: "text-amber-700", bg: "bg-amber-50", ring: "ring-amber-600/15", bar: "bg-amber-500" },
  info: { icon: Info, text: "text-blue-700", bg: "bg-blue-50", ring: "ring-blue-600/15", bar: "bg-blue-600" },
  success: { icon: CheckCircle2, text: "text-green-700", bg: "bg-green-50", ring: "ring-green-600/15", bar: "bg-green-600" },
} as const;

interface Props {
  alert: Alert;
  strings: AlertStrings;
  lang: AlertLang;
  onToggleRead: (id: string) => void;
  onDismiss: (id: string) => void;
}

export function AlertItem({ alert, strings: s, lang, onToggleRead, onDismiss }: Props) {
  const cfg = LEVEL[alert.level];
  const Icon = cfg.icon;

  return (
    <div
      className={`group relative overflow-hidden rounded-2xl border bg-white p-4 shadow-sm transition-all hover:shadow-md ${
        alert.read ? "border-stone-200/80" : "border-green-300 bg-green-50/20"
      }`}
    >
      {/* نوار رنگی سطح — RTL-safe */}
      <span className={`absolute inset-y-0 start-0 w-1 ${cfg.bar}`} />

      <div className="flex items-start gap-3 ps-2">
        <div className={`grid h-9 w-9 shrink-0 place-items-center rounded-full ring-1 ${cfg.bg} ${cfg.text} ${cfg.ring}`}>
          <Icon className="h-4 w-4" />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="font-bold text-stone-800">{alertText(s, alert.titleKey)}</h3>
              {!alert.read && (
                <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${cfg.bg} ${cfg.text}`}>{s.unreadBadge}</span>
              )}
            </div>
            <span className="shrink-0 text-xs text-stone-500">{timeAgo(alert.timestamp, lang)}</span>
          </div>

          <p className="mt-1 text-sm text-stone-600">{alertText(s, alert.messageKey)}</p>

          {/* اکشن‌ها: در موبایل همیشه، در دسکتاپ با hover */}
          <div className="mt-2 flex items-center gap-4 opacity-100 transition-opacity lg:opacity-0 lg:group-hover:opacity-100">
            <button
              onClick={() => onToggleRead(alert.id)}
              className="inline-flex items-center gap-1 text-xs font-bold text-blue-700 transition-colors hover:text-blue-800"
            >
              {alert.read ? <Circle className="h-3.5 w-3.5" /> : <Check className="h-3.5 w-3.5" />}
              {alert.read ? s.markUnread : s.markRead}
            </button>
            <button
              onClick={() => onDismiss(alert.id)}
              className="inline-flex items-center gap-1 text-xs font-bold text-red-700 transition-colors hover:text-red-800"
            >
              <X className="h-3.5 w-3.5" />
              {s.dismiss}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}