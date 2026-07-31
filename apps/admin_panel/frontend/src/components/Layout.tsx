import { Outlet } from 'react-router-dom'
import AdminSidebar from './AdminSidebar'
import ThemeSelector from './ThemeSelector'
import { Button } from '@econojin/ui/button'
import { Moon, Sun } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'

export default function Layout() {
  const { theme, setTheme } = useTheme()
  
  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  return (
    <div className="min-h-screen bg-background flex flex-col" dir="rtl">
      <header className="border-b bg-card p-4 flex justify-between items-center sticky top-0 z-10">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold text-foreground">پنل مدیریت اکونوژین</h1>
        </div>
        <div className="flex items-center gap-4">
          <ThemeSelector />
          <Button
            variant="outline"
            size="icon"
            onClick={toggleTheme}
            aria-label={theme === 'light' ? 'تغییر به تم تاریک' : 'تغییر به تم روشن'}
            title={theme === 'light' ? 'تغییر به تم تاریک' : 'تغییر به تم روشن'}
          >
            {theme === 'light' ? (
              <Moon className="h-4 w-4" />
            ) : (
              <Sun className="h-4 w-4" />
            )}
          </Button>
        </div>
      </header>
      
      <div className="flex flex-1 overflow-hidden">
        <AdminSidebar />
        <main className="flex-1 p-6 overflow-auto" tabIndex={-1}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}