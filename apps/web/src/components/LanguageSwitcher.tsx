import { useTranslation } from 'react-i18next'
import { LANGUAGES, getLanguageDir } from '../i18n'

export default function LanguageSwitcher() {
  const { i18n } = useTranslation()

  const handleChange = (langCode: string) => {
    i18n.changeLanguage(langCode)
    document.documentElement.dir = getLanguageDir(langCode)
    document.documentElement.lang = langCode
  }

  const currentLang = LANGUAGES.find(l => l.code === i18n.language) ?? LANGUAGES[0]

  return (
    <div className="relative group">
      <button className="flex items-center gap-2 px-3 py-2 rounded-lg border bg-card hover:bg-accent transition-colors text-sm">
        <span>{currentLang.flag}</span>
        <span className="hidden sm:inline">{currentLang.nativeName}</span>
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      <div className="absolute left-0 top-full mt-1 w-56 rounded-lg border bg-card shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
        <div className="p-1 max-h-72 overflow-y-auto">
          {LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              onClick={() => handleChange(lang.code)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                i18n.language === lang.code
                  ? 'bg-eco-100 text-eco-800 dark:bg-eco-900 dark:text-eco-200'
                  : 'hover:bg-accent'
              }`}
            >
              <span className="text-lg">{lang.flag}</span>
              <span className="flex-1 text-left">{lang.nativeName}</span>
              <span className="text-xs text-muted-foreground">{lang.name}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}