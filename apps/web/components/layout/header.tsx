import Link from 'next/link'

interface User {
  email?: string
}

interface Profile {
  full_name?: string
}

export function Header({ user, profile }: { user?: User; profile?: Profile }) {
  return (
    <header className="flex items-center justify-between border-b border-slate-200/5 bg-slate-950/95 p-6">
      <div>
        <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Welcome back</p>
        <h1 className="text-2xl font-semibold text-white">{profile?.full_name ?? user?.email ?? 'User'}</h1>
      </div>
      <div className="flex items-center gap-3 text-sm text-slate-300">
        <span>{user?.email ?? 'Not signed in'}</span>
        <Link href="/logout" className="rounded-full border border-slate-700 px-4 py-2 text-slate-200 transition hover:border-slate-500">
          Sign out
        </Link>
      </div>
    </header>
  )
}
