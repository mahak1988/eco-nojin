import { useState, useRef, useEffect } from "react";
import { Globe, Check } from "lucide-react";
import { useLang, LANGS } from "./i18n";

export function LanguageSwitcher() {
  const { lang, setLang } = useLang();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const active = LANGS.find(l => l.code === lang)!;

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <Globe className="h-4 w-4" />
        <span>{active.nativeName ?? active.code.toUpperCase()}</span>
      </button>
      {isOpen && (
        <div
          className="absolute end-0 mt-1 w-40 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-lg z-50 py-1"
          role="listbox"
        >
          {LANGS.map(l => (
            <button
              key={l.code}
              onClick={() => { setLang(l.code); setIsOpen(false); }}
              className="flex w-full items-center justify-between px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              role="option"
              aria-selected={l.code === lang}
            >
              <span>{l.nativeName ?? l.code.toUpperCase()}</span>
              {l.code === lang && <Check className="h-3.5 w-3.5 text-emerald-600" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
