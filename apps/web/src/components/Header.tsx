import { useTranslation } from 'react-i18next'
import LanguageSwitcher from './LanguageSwitcher'

export default function Header() {
  const { t } = useTranslation()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center justify-between px-6">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-eco-600 flex items-center justify-center">
            <span className="text-white font-bold text-sm">E</span>
          </div>
          <span className="font-bold text-xl text-eco-700 dark:text-eco-400">
            {t('app.name')}
          </span>
        </div>
        <div className="flex items-center gap-4">
          <LanguageSwitcher />
        </div>
      </div>
    </header>
  )
}