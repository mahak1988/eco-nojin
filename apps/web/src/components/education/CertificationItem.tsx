// apps/web/src/components/education/CertificationItem.tsx
import { BadgeCheck, Clock, Loader2 } from "lucide-react";
import type { Certification, CertStatusKey } from "./educationData";
import { eduText, certStatusText, fmtDate, type EducationStrings, type EduLang } from "./educationI18n";

const STATUS_STYLE: Record<CertStatusKey, { icon: typeof BadgeCheck; chip: string }> = {
  cert_verified: { icon: BadgeCheck, chip: "bg-green-50 text-green-700" },
  cert_pending: { icon: Clock, chip: "bg-amber-50 text-amber-700" },
  cert_progress: { icon: Loader2, chip: "bg-blue-50 text-blue-700" },
};

interface Props {
  cert: Certification;
  strings: EducationStrings;
  lang: EduLang;
}

export function CertificationItem({ cert, strings: s, lang }: Props) {
  const cfg = STATUS_STYLE[cert.statusKey];
  const Icon = cfg.icon;
  const spinning = cert.statusKey === "cert_progress";

  return (
    <div className="flex items-center gap-3 rounded-xl border border-stone-200 p-4 transition-colors hover:border-green-300 hover:bg-green-50/30">
      <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-amber-50 to-orange-50 text-2xl ring-1 ring-amber-600/10">
        {cert.icon}
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate font-bold text-stone-800">{eduText(s, cert.nameKey)}</p>
        <p className="text-xs text-stone-500">{fmtDate(cert.date, lang)}</p>
      </div>
      <span className={`inline-flex shrink-0 items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold ${cfg.chip}`}>
        <Icon className={`h-3.5 w-3.5 ${spinning ? "animate-spin" : ""}`} />
        {certStatusText(s, cert.statusKey)}
      </span>
    </div>
  );
}