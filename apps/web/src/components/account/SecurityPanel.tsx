// apps/web/src/components/account/SecurityPanel.tsx
import { useState } from "react";
import { Shield, KeyRound, MonitorSmartphone, BellRing, LogOut } from "lucide-react";
import { MOCK_SESSIONS } from "./accountData";
import { localeOf, type AccountStrings, type AccLang } from "./accountI18n";
import { Toggle } from "./Toggle";

interface Props {
  strings: AccountStrings;
  lang: AccLang;
}

export function SecurityPanel({ strings: s, lang }: Props) {
  const [twoFactor, setTwoFactor] = useState(false);
  const [loginAlerts, setLoginAlerts] = useState(true);
  const locale = localeOf(lang);
  const fmtTime = (iso: string) =>
    new Date(iso).toLocaleString(locale, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });

  return (
    <div className="rounded-2xl border border-stone-200/80 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <Shield className="h-5 w-5 text-green-700" />
        <h3 className="font-display text-xl text-stone-800">{s.securityTitle}</h3>
      </div>

      <div className="space-y-3">
        {/* 2FA */}
        <div className="flex items-center justify-between gap-3 rounded-xl border border-stone-200 p-4">
          <div className="flex items-start gap-3">
            <Shield className="mt-0.5 h-5 w-5 shrink-0 text-green-700" />
            <div>
              <p className="font-semibold text-stone-800">{s.twoFactor}</p>
              <p className="text-sm text-stone-600">{s.twoFactorDesc}</p>
            </div>
          </div>
          <div className="flex flex-col items-end gap-1">
            <Toggle checked={twoFactor} onChange={setTwoFactor} ariaLabel={s.twoFactor} />
            <span className={`text-xs font-bold ${twoFactor ? "text-green-700" : "text-stone-500"}`}>
              {twoFactor ? s.enabled : s.disabled}
            </span>
          </div>
        </div>

        {/* Password */}
        <div className="flex items-center justify-between gap-3 rounded-xl border border-stone-200 p-4">
          <div className="flex items-start gap-3">
            <KeyRound className="mt-0.5 h-5 w-5 shrink-0 text-blue-700" />
            <div>
              <p className="font-semibold text-stone-800">{s.password}</p>
              <p className="text-sm text-stone-600">{s.passwordDesc}</p>
            </div>
          </div>
          <button className="shrink-0 rounded-lg border border-stone-200 px-3 py-1.5 text-sm font-bold text-blue-700 transition-colors hover:bg-blue-50">
            {s.changePassword}
          </button>
        </div>

        {/* Login alerts */}
        <div className="flex items-center justify-between gap-3 rounded-xl border border-stone-200 p-4">
          <div className="flex items-start gap-3">
            <BellRing className="mt-0.5 h-5 w-5 shrink-0 text-amber-700" />
            <div>
              <p className="font-semibold text-stone-800">{s.loginAlerts}</p>
              <p className="text-sm text-stone-600">{s.loginAlertsDesc}</p>
            </div>
          </div>
          <Toggle checked={loginAlerts} onChange={setLoginAlerts} ariaLabel={s.loginAlerts} />
        </div>
      </div>

      {/* Sessions */}
      <div className="mt-5 border-t border-stone-100 pt-5">
        <div className="mb-3 flex items-center gap-2">
          <MonitorSmartphone className="h-4 w-4 text-stone-500" />
          <h4 className="text-sm font-bold text-stone-700">{s.activeSessions}</h4>
        </div>
        <div className="space-y-2">
          {MOCK_SESSIONS.map((sess) => (
            <div
              key={sess.id}
              className={`flex items-center justify-between gap-3 rounded-xl border p-3 ${
                sess.current ? "border-green-200 bg-green-50/50" : "border-stone-200"
              }`}
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-stone-800">{sess.device}</p>
                <p className="text-xs text-stone-500">{sess.location} · {fmtTime(sess.lastActive)}</p>
              </div>
              {sess.current && (
                <span className="shrink-0 rounded-full bg-green-100 px-2.5 py-0.5 text-[11px] font-bold text-green-700">
                  {s.thisDevice}
                </span>
              )}
            </div>
          ))}
        </div>
        <button className="mt-3 inline-flex items-center gap-2 text-sm font-bold text-red-700 transition-colors hover:text-red-800">
          <LogOut className="h-4 w-4" />{s.logoutAll}
        </button>
      </div>
    </div>
  );
}