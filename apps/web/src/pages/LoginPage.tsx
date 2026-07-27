import { Link, useNavigate, useLocation } from "react-router-dom";
import { Leaf, ShieldCheck } from "lucide-react";
import { LoginForm } from "../features/auth/LoginForm";
import { LanguageSwitcher } from "../components/Layout/LanguageSwitcher";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from || "/farms";

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#f4f7f2]">
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(900px 500px at 90% -10%, rgba(16,185,129,.16), transparent 55%), radial-gradient(600px 360px at 0% 100%, rgba(245,158,11,.1), transparent 50%)",
        }}
      />
      <div className="relative z-10 mx-auto flex min-h-screen max-w-5xl flex-col px-4 py-6 sm:px-6">
        <div className="mb-8 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-display text-lg font-bold text-slate-800">
            <span className="grid h-10 w-10 place-items-center rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/25">
              <Leaf className="h-5 w-5" />
            </span>
            EcoNojin
          </Link>
          <LanguageSwitcher />
        </div>

        <div className="grid flex-1 items-center gap-12 lg:grid-cols-2">
          <div className="hidden lg:block">
            <p className="mb-3 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white/80 px-3 py-1 text-xs font-bold text-emerald-700">
              <ShieldCheck className="h-3.5 w-3.5" />
              HttpOnly session · RS-ready JWT
            </p>
            <h1 className="font-display text-4xl leading-tight text-slate-900">
              Your fields,
              <span className="block text-emerald-600">one secure dashboard.</span>
            </h1>
            <p className="mt-4 max-w-md text-slate-600">
              Access farms, education, and accounting with cookie-based auth designed for the browser.
            </p>
          </div>
          <div className="mx-auto w-full max-w-md">
            <LoginForm onSuccess={() => navigate(from, { replace: true })} />
            <p className="mt-4 text-center">
              <Link to="/" className="text-xs font-medium text-stone-500 hover:text-stone-800">
                ← Back to home
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
