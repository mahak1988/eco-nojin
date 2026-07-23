// apps/web/src/pages/SettingsPage.tsx  (محتوای کامل فایل ۴ بالا)
// apps/web/src/pages/SettingsPage.tsx
// تنظیمات یکپارچه با useLang + تنظیمات کارا (theme/اعلان/دسترس‌پذیری/حریم‌خصوصی).
import { useState, type ComponentType } from "react";
import {
  Globe, Palette, Bell, Accessibility, ShieldCheck, Download, RotateCcw,
  Sun, Moon, Monitor, Check,
} from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { useSettings } from "../components/settings/useSettings";
import { SET_STR, type SetLang } from "../components/settings/settingsI18n";
import { exportUserData, type Theme } from "../components/settings/settingsData";

// نام زبان‌ها به زبان خودشان (ثابت، نه ترجمه)
const LANGS: { code: SetLang; label: string }[] = [
  { code: "fa", label: "فارسی" },
  { code: "en", label: "English" },
  { code: "ar", label: "العربية" },
];

export default function SettingsPage() {
  const { lang, setLang } = useLang();
  const s = SET_STR[lang as SetLang];
  const { settings, update, reset } = useSettings();

  const [exported, setExported] = useState(false);
  const [confirmReset, setConfirmReset] = useState(false);
  const [resetDone, setResetDone] = useState(false);

  const doExport = () => {
    exportUserData(settings);
    setExported(true);
    setTimeout(() => setExported(false), 1800);
  };
  const doReset = () => {
    if (!confirmReset) { setConfirmReset(true); setTimeout(() => setConfirmReset(false), 2500); return; }
    reset();
    setConfirmReset(false);
    setResetDone(true);
    setTimeout(() => setResetDone(false), 1800);
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6 p-5 sm:p-8">
      <header>
        <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
        <p className="mt-1 text-stone-600">{s.subtitle}</p>
      </header>

      {/* ── Language ── */}
      <Section icon={Globe} title={s.section_language} desc={s.language_desc}>
        <div className="grid grid-cols-3 gap-2">
          {LANGS.map((l) => {
            const active = lang === l.code;
            return (
              <button key={l.code} onClick={() => setLang(l.code)} aria-pressed={active}
                className={`rounded-xl border px-3 py-3 text-sm font-bold transition-all hover:-translate-y-0.5 ${
                  active ? "border-green-500 bg-green-50 text-green-700 ring-1 ring-green-600/20" : "border-stone-200 bg-white text-stone-700 hover:bg-stone-50"
                }`}>
                {l.label}
              </button>
            );
          })}
        </div>
      </Section>

      {/* ── Appearance ── */}
      <Section icon={Palette} title={s.section_appearance} desc={s.appearance_desc}>
        <div className="grid grid-cols-3 gap-2">
          <ThemeOption value="light" current={settings.theme} icon={Sun} label={s.theme_light} desc={s.theme_light_desc}
            onSelect={(v) => update({ theme: v })} preview={<Preview kind="light" />} />
          <ThemeOption value="dark" current={settings.theme} icon={Moon} label={s.theme_dark} desc={s.theme_dark_desc}
            onSelect={(v) => update({ theme: v })} preview={<Preview kind="dark" />} />
          <ThemeOption value="system" current={settings.theme} icon={Monitor} label={s.theme_system} desc={s.theme_system_desc}
            onSelect={(v) => update({ theme: v })} preview={<Preview kind="system" />} />
        </div>
      </Section>

      {/* ── Notifications ── */}
      <Section icon={Bell} title={s.section_notifications} desc={s.notifications_desc}>
        <div className="space-y-2">
          <ToggleRow label={s.notif_email} desc={s.notif_email_desc} checked={settings.notifications.email}
            onChange={(v) => update({ notifications: { ...settings.notifications, email: v } })} />
          <ToggleRow label={s.notif_product} desc={s.notif_product_desc} checked={settings.notifications.product}
            onChange={(v) => update({ notifications: { ...settings.notifications, product: v } })} />
          <ToggleRow label={s.notif_weekly} desc={s.notif_weekly_desc} checked={settings.notifications.weekly}
            onChange={(v) => update({ notifications: { ...settings.notifications, weekly: v } })} />
        </div>
      </Section>

      {/* ── Accessibility ── */}
      <Section icon={Accessibility} title={s.section_accessibility} desc={s.accessibility_desc}>
        <div className="space-y-2">
          <ToggleRow label={s.a11y_reduce_motion} desc={s.a11y_reduce_motion_desc} checked={settings.reduceMotion}
            onChange={(v) => update({ reduceMotion: v })} />
          <ToggleRow label={s.a11y_larger_text} desc={s.a11y_larger_text_desc} checked={settings.largerText}
            onChange={(v) => update({ largerText: v })} />
        </div>
      </Section>

      {/* ── Privacy & Data ── */}
      <Section icon={ShieldCheck} title={s.section_privacy} desc={s.privacy_desc}>
        <ToggleRow label={s.privacy_analytics} desc={s.privacy_analytics_desc} checked={settings.analytics}
          onChange={(v) => update({ analytics: v })} />

        <div className="mt-3 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-stone-200 bg-stone-50 p-3">
          <div className="min-w-0">
            <p className="text-sm font-bold text-stone-800">{s.export_data}</p>
            <p className="text-xs text-stone-500">{s.export_data_desc}</p>
          </div>
          <button onClick={doExport}
            className={`inline-flex shrink-0 items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs font-bold transition-colors ${
              exported ? "bg-green-50 text-green-700" : "bg-white text-stone-700 ring-1 ring-stone-200 hover:bg-stone-100"
            }`}>
            {exported ? <Check className="h-3.5 w-3.5" /> : <Download className="h-3.5 w-3.5" />}
            {exported ? s.exported : s.export_data}
          </button>
        </div>

        <div className="mt-3 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-red-200 bg-red-50/60 p-3">
          <div className="min-w-0">
            <p className="text-sm font-bold text-red-800">{s.reset_settings}</p>
            <p className="text-xs text-red-700/80">{s.reset_settings_desc}</p>
          </div>
          <button onClick={doReset}
            className={`inline-flex shrink-0 items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs font-bold transition-colors ${
              resetDone ? "bg-green-600 text-white" : confirmReset ? "bg-red-600 text-white" : "bg-white text-red-700 ring-1 ring-red-200 hover:bg-red-100"
            }`}>
            {resetDone ? <Check className="h-3.5 w-3.5" /> : <RotateCcw className="h-3.5 w-3.5" />}
            {resetDone ? s.reset_done : confirmReset ? s.reset_confirm : s.reset_settings}
          </button>
        </div>
      </Section>
    </div>
  );
}

/* ── بخش (کارت) ── */
function Section({ icon: Icon, title, desc, children }: {
  icon: ComponentType<{ className?: string }>; title: string; desc: string; children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm sm:p-6">
      <div className="mb-4 flex items-start gap-3">
        <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-green-50 text-green-700 ring-1 ring-green-600/15">
          <Icon className="h-4 w-4" />
        </span>
        <div>
          <h2 className="font-display text-lg text-stone-800">{title}</h2>
          <p className="text-sm text-stone-500">{desc}</p>
        </div>
      </div>
      {children}
    </section>
  );
}

/* ── سطر toggle (RTL-safe) ── */
function ToggleRow({ label, desc, checked, onChange }: {
  label: string; desc: string; checked: boolean; onChange: (v: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-stone-200 bg-white p-3">
      <div className="min-w-0">
        <p className="text-sm font-bold text-stone-800">{label}</p>
        <p className="text-xs text-stone-500">{desc}</p>
      </div>
      <button role="switch" aria-checked={checked} aria-label={label} onClick={() => onChange(!checked)}
        className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-green-500/40 ${
          checked ? "bg-green-600" : "bg-stone-300"
        }`}>
        <span className="absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-all duration-300"
          style={{ insetInlineStart: checked ? "calc(100% - 1.375rem)" : "0.125rem" }} />
      </button>
    </div>
  );
}

/* ── گزینهٔ theme با mini-preview ── */
function ThemeOption({ value, current, icon: Icon, label, desc, onSelect, preview }: {
  value: Theme; current: Theme; icon: ComponentType<{ className?: string }>;
  label: string; desc: string; onSelect: (v: Theme) => void; preview: React.ReactNode;
}) {
  const active = current === value;
  return (
    <button onClick={() => onSelect(value)} aria-pressed={active}
      className={`flex flex-col gap-2 rounded-xl border p-3 text-start transition-all hover:-translate-y-0.5 ${
        active ? "border-green-500 bg-green-50/60 ring-1 ring-green-600/20" : "border-stone-200 bg-white hover:bg-stone-50"
      }`}>
      {preview}
      <span className="flex items-center gap-1.5">
        <Icon className={`h-4 w-4 ${active ? "text-green-700" : "text-stone-500"}`} />
        <span className={`text-sm font-bold ${active ? "text-green-700" : "text-stone-800"}`}>{label}</span>
      </span>
      <span className="text-[11px] leading-snug text-stone-500">{desc}</span>
    </button>
  );
}

/* ── mini-preview رنگ‌ها ── */
function Preview({ kind }: { kind: "light" | "dark" | "system" }) {
  const light = (
    <span className="flex h-9 w-full overflow-hidden rounded-md ring-1 ring-black/5">
      <span className="flex-1 bg-white" /><span className="w-1/3 bg-stone-800" />
    </span>
  );
  const dark = (
    <span className="flex h-9 w-full overflow-hidden rounded-md ring-1 ring-black/10">
      <span className="flex-1 bg-stone-900" /><span className="w-1/3 bg-stone-100" />
    </span>
  );
  if (kind === "system") {
    return (
      <span className="flex h-9 w-full overflow-hidden rounded-md ring-1 ring-black/10">
        <span className="flex flex-1"><span className="flex-1 bg-white" /><span className="w-1/2 bg-stone-800" /></span>
        <span className="flex flex-1"><span className="flex-1 bg-stone-900" /><span className="w-1/2 bg-stone-100" /></span>
      </span>
    );
  }
  return kind === "light" ? light : dark;
}