import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { Eye, EyeOff, Loader2, Lock, Mail } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";

export function LoginForm({ onSuccess }: { onSuccess?: () => void }) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      onSuccess?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form
      onSubmit={onSubmit}
      className="w-full space-y-5 rounded-3xl border border-stone-200/80 bg-white/95 p-7 shadow-xl shadow-emerald-900/5 backdrop-blur"
    >
      <div>
        <h1 className="font-display text-2xl text-slate-900">Welcome back</h1>
        <p className="mt-1 text-sm text-slate-500">Sign in to manage farms, courses, and insights.</p>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>
      )}

      <label className="block text-sm">
        <span className="font-medium text-slate-600">Email</span>
        <div className="relative mt-1">
          <Mail className="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-xl border border-stone-200 py-2.5 ps-10 pe-3 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
            placeholder="you@example.com"
          />
        </div>
      </label>

      <label className="block text-sm">
        <span className="font-medium text-slate-600">Password</span>
        <div className="relative mt-1">
          <Lock className="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
          <input
            type={showPw ? "text" : "password"}
            required
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-xl border border-stone-200 py-2.5 ps-10 pe-10 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
          />
          <button
            type="button"
            onClick={() => setShowPw((v) => !v)}
            className="absolute end-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-600"
            aria-label={showPw ? "Hide password" : "Show password"}
          >
            {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
      </label>

      <button
        type="submit"
        disabled={loading}
        className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 py-3 text-sm font-bold text-white shadow-lg shadow-emerald-600/25 hover:from-emerald-700 hover:to-teal-700 disabled:opacity-60"
      >
        {loading && <Loader2 className="h-4 w-4 animate-spin" />}
        {loading ? "Signing in…" : "Sign in"}
      </button>

      <p className="text-center text-sm text-slate-600">
        New here?{" "}
        <Link to="/register" className="font-bold text-emerald-700 hover:underline">
          Create an account
        </Link>
      </p>
    </form>
  );
}
