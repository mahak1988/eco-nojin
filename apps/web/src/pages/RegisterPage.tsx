import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Leaf, Loader2 } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { LanguageSwitcher } from "../components/Layout/LanguageSwitcher";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register(email, password, fullName || undefined);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative flex min-h-screen flex-col bg-gradient-to-b from-emerald-50/80 via-white to-amber-50/40">
      <div className="flex items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2 font-display text-lg font-bold text-slate-800">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white">
            <Leaf className="h-5 w-5" />
          </span>
          EcoNojin
        </Link>
        <LanguageSwitcher />
      </div>
      <div className="flex flex-1 items-center justify-center p-6">
        <form
          onSubmit={onSubmit}
          className="w-full max-w-md space-y-4 rounded-2xl border border-stone-200 bg-white p-6 shadow-sm"
        >
          <h1 className="font-display text-2xl text-stone-800">Create account</h1>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <label className="block text-sm">
            <span className="text-stone-600">Full name</span>
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2"
            />
          </label>
          <label className="block text-sm">
            <span className="text-stone-600">Email</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2"
            />
          </label>
          <label className="block text-sm">
            <span className="text-stone-600">Password</span>
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2"
            />
          </label>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 py-2.5 text-sm font-bold text-white hover:bg-emerald-700 disabled:opacity-60"
          >
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
            {loading ? "Creating…" : "Register"}
          </button>
          <p className="text-center text-sm text-stone-600">
            Already have an account?{" "}
            <Link to="/login" className="font-bold text-emerald-700 hover:underline">
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
