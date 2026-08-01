import { useEffect, useState } from "react";
import { Shield } from "lucide-react";
import {
  ALL_ROLES,
  ROLE_LABELS,
  readDemoRole,
  writeDemoRole,
  type Role,
} from "../../lib/rbacStore";
import { useLang } from "../eco/i18n";

export function RoleSwitcher() {
  const { lang } = useLang();
  const [role, setRole] = useState<Role>(readDemoRole);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onChange = (e: Event) => {
      const d = (e as CustomEvent).detail as Role;
      if (d) setRole(d);
    };
    window.addEventListener("econojin-role-changed", onChange);
    return () => window.removeEventListener("econojin-role-changed", onChange);
  }, []);

  const label = ROLE_LABELS[role]?.[lang as "fa" | "en" | "ar"] ?? role;

  return (
    <div className="fixed bottom-4 end-4 z-[90]">
      {open && (
        <div className="mb-2 overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-xl">
          <p className="border-b bg-stone-50 px-3 py-2 text-[11px] font-bold uppercase tracking-wide text-stone-500">
            {lang === "fa" ? "نقش آزمایشی" : lang === "ar" ? "دور تجريبي" : "Demo role"}
          </p>
          {ALL_ROLES.map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => {
                writeDemoRole(r);
                setRole(r);
                setOpen(false);
              }}
              className={`flex w-full items-center gap-2 px-3 py-2.5 text-start text-sm font-bold transition-colors ${
                r === role ? "bg-green-50 text-green-800" : "text-stone-700 hover:bg-stone-50"
              }`}
            >
              <span
                className={`h-2 w-2 rounded-full ${
                  r === "admin" ? "bg-amber-500" : r === "editor" ? "bg-blue-500" : r === "user" ? "bg-green-500" : "bg-stone-400"
                }`}
              />
              {ROLE_LABELS[r][lang as "fa" | "en" | "ar"] ?? r}
            </button>
          ))}
        </div>
      )}
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="inline-flex items-center gap-2 rounded-full border border-stone-200 bg-white px-3 py-2 text-xs font-bold text-stone-700 shadow-lg ring-1 ring-black/5 hover:bg-stone-50"
        title="Switch demo role to test access"
      >
        <Shield className="h-3.5 w-3.5 text-green-700" />
        {label}
      </button>
    </div>
  );
}
