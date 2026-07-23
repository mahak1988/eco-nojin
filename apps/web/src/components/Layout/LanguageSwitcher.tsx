// apps/web/src/components/Layout/LanguageSwitcher.tsx
import { useState, useRef, useEffect } from "react";
import { ChevronDown, Check } from "lucide-react";
import { useLang, LANGS } from "../eco/i18n";

export function LanguageSwitcher() {
  const { lang, setLang } = useLang();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const current = LANGS.find((l) => l.code === lang) ?? LANGS[0];

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        aria-haspopup="listbox"
        className="flex items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--surface-raised)] px-3 py-2 text-sm font-bold text-[var(--text-2)] transition-colors hover:bg-stone-100"
      >
        <span className="text-base">{current.flag}</span>
        <span className="hidden sm:inline">{current.nativeName}</span>
        <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div
          role="listbox"
          className="absolute end-0 top-full z-50 mt-1 w-56 rounded-xl border border-[var(--border)] bg-[var(--surface-raised)] p-1 shadow-lg"
          style={{ animation: "fade-up .2s var(--ease-out)" }}
        >
          {LANGS.map((l) => (
            <button
              key={l.code}
              role="option"
              aria-selected={lang === l.code}
              onClick={() => { setLang(l.code); setOpen(false); }}
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                lang === l.code
                  ? "bg-green-50 text-green-700"
                  : "text-[var(--text-2)] hover:bg-stone-50"
              }`}
            >
              <span className="text-lg">{l.flag}</span>
              <span className="flex-1 text-start font-bold">{l.nativeName}</span>
              <span className="text-xs text-[var(--text-3)]">{l.name}</span>
              {lang === l.code && <Check className="h-4 w-4 text-green-600" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
