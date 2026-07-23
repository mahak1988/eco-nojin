// apps/web/src/components/account/PreferencesPanel.tsx
import { useState } from "react";
import { Bell } from "lucide-react";
import type { AccountStrings } from "./accountI18n";
import { Toggle } from "./Toggle";

interface Props {
  strings: AccountStrings;
}

export function PreferencesPanel({ strings: s }: Props) {
  const [prefs, setPrefs] = useState({ emailNotif: true, productUpdates: true, weeklyReport: false });

  const rows = [
    { key: "emailNotif" as const, icon: "📧", title: s.emailNotif, desc: s.emailNotifDesc },
    { key: "productUpdates" as const, icon: "✨", title: s.productUpdates, desc: s.productUpdatesDesc },
    { key: "weeklyReport" as const, icon: "📊", title: s.weeklyReport, desc: s.weeklyReportDesc },
  ];

  return (
    <div className="rounded-2xl border border-stone-200/80 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <Bell className="h-5 w-5 text-amber-700" />
        <h3 className="font-display text-xl text-stone-800">{s.preferencesTitle}</h3>
      </div>
      <div className="space-y-3">
        {rows.map((r) => (
          <div key={r.key} className="flex items-center justify-between gap-3 rounded-xl border border-stone-200 p-4">
            <div className="flex items-start gap-3">
              <span className="text-xl">{r.icon}</span>
              <div>
                <p className="font-semibold text-stone-800">{r.title}</p>
                <p className="text-sm text-stone-600">{r.desc}</p>
              </div>
            </div>
            <Toggle checked={prefs[r.key]} onChange={(v) => setPrefs({ ...prefs, [r.key]: v })} ariaLabel={r.title} />
          </div>
        ))}
      </div>
    </div>
  );
}