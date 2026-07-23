import { Outlet } from 'react-router-dom'
import AdminSidebar from './AdminSidebar'

export default function Layout() {
  return (
    <div className="min-h-screen bg-background flex">
      <AdminSidebar />
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  )
}