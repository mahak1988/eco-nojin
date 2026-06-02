// frontend/src/components/LanguageSwitcher.tsx
"use client"

export type Language = "en" | "ar" | "fa"

const supportedLngs: Language[] = ["en", "ar", "fa"]
const languageNames: Record<Language, string> = {
  en: "English",
  ar: "العربية",
  fa: "فارسی",
}
const rtlLngs: Language[] = ["ar", "fa"]

export default function LanguageSwitcher() {
  const currentLang: Language =
    typeof document !== "undefined"
      ? ((document.documentElement.lang as Language) ?? "en")
      : "en"

  const changeLang = (lng: Language) => {
    document.documentElement.dir = rtlLngs.includes(lng) ? "rtl" : "ltr"
    document.documentElement.lang = lng
  }

  return (
    <select
      aria-label="Language"
      value={currentLang}
      onChange={(e) => changeLang(e.target.value as Language)}
      className="px-3 py-1 border rounded bg-white text-sm"
    >
      {supportedLngs.map((lng: Language) => (
        <option key={lng} value={lng}>
          {languageNames[lng]}
        </option>
      ))}
    </select>
  )
}
