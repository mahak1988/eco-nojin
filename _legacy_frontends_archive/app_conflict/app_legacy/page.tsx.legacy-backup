import Link from 'next/link'

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto flex min-h-screen max-w-6xl flex-col items-center justify-center px-6 py-20 text-center">
        <h1 className="text-5xl font-semibold tracking-tight sm:text-6xl">
          Multi-tenant SaaS Dashboard
        </h1>
        <p className="mt-6 max-w-2xl text-lg text-slate-300">
          A modern composable web application built with Next.js, Supabase, Strapi, and Tailwind CSS.
        </p>
        <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Link href="/login" className="rounded-full bg-sky-500 px-6 py-3 text-sm font-semibold text-white transition hover:bg-sky-400">
            Login
          </Link>
          <Link href="/register" className="rounded-full border border-slate-600 px-6 py-3 text-sm font-semibold text-slate-100 transition hover:border-slate-400">
            Register
          </Link>
        </div>
      </section>
    </main>
  )
}
