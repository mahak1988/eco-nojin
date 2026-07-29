// apps/web/src/components/settings/useSettings.ts
// hook تنظیمات: persist در localStorage + اعمال زندهٔ side-effectها.
import { useCallback, useEffect, useState } from "react";
import { type Settings, loadSettings, saveSettings, applyAll, applyTheme } from "./settingsData";

export function useSettings() {
  const [settings, setSettings] = useState<Settings>(loadSettings);

  // اعمال زندهٔ همهٔ side-effectها هنگام هر تغییر
  useEffect(() => { applyAll(settings); }, [settings]);

  // گوش‌دادن به تغییر تم سیستم، فقط وقتی theme === 'system'
  useEffect(() => {
    if (settings.theme !== "system" || typeof window === "undefined") return;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => applyTheme("system");
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, [settings.theme]);

  const update = useCallback((patch: Partial<Settings>) => {
    setSettings((prev) => {
      const next = { ...prev, ...patch };
      saveSettings(next);
      return next;
    });
  }, []);

  const reset = useCallback(() => {
    setSettings((prev) => {
      const next: Settings = {
        ...DEFAULT_IMPORT(),
        notifications: { ...DEFAULT_IMPORT().notifications },
      };
      void prev;
      saveSettings(next);
      return next;
    });
  }, []);

  return { settings, update, reset };
}

// indirection کوچک برای دور زدن import circolar احتمالی و خوانایی
import { DEFAULT_SETTINGS } from "./settingsData";
function DEFAULT_IMPORT(): Settings {
  return { ...DEFAULT_SETTINGS, notifications: { ...DEFAULT_SETTINGS.notifications } };
}