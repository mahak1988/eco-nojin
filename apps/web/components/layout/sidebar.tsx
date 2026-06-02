import Link from 'next/link'

interface Profile {
  id?: string
  email?: string
  tenants?: Array<{ name: string }>
}

export function Sidebar({ profile }: { profile?: Profile }) {
  return (
    <aside className="w-72 border-r border-slate-200/5 bg-slate-950/95 p-6 text-slate-100">
      <div className="mb-10">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Workspace</p>
        <h2 className="mt-2 text-2xl font-semibold">Econojin</h2>
      </div>
      <nav className="space-y-2">
        <Link href="/dashboard" className="block rounded-2xl px-4 py-3 text-sm font-medium text-slate-100 transition hover:bg-slate-800">
          Dashboard
        </Link>
        <Link href="/projects" className="block rounded-2xl px-4 py-3 text-sm font-medium text-slate-100 transition hover:bg-slate-800">
          Projects
        </Link>
        <Link href="/settings" className="block rounded-2xl px-4 py-3 text-sm font-medium text-slate-100 transition hover:bg-slate-800">
          Settings
        </Link>
      </nav>
      <div className="mt-10 rounded-3xl border border-slate-800 bg-slate-950/80 p-4">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Tenant</p>
        <p className="mt-2 font-medium text-white">{profile?.tenants?.[0]?.name ?? 'Primary tenant'}</p>
      </div>
    </aside>
  )
}
