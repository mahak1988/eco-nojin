import { Outlet } from 'react-router-dom'
import AgentSidebar from './AgentSidebar'

export default function Layout() {
  return (
    <div className="min-h-screen bg-background flex">
      <AgentSidebar />
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  )
}