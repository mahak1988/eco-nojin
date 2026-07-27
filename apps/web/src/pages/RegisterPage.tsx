import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Leaf,
  Loader2,
  Sprout,
  GraduationCap,
  Eye,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { LanguageSwitcher } from "../components/Layout/LanguageSwitcher";
import { authApi } from "../api/auth.api";

type RoleChoice = "farmer" | "expert" | "viewer";

const ROLES: {
  id: RoleChoice;
  title: string;
  desc: string;
  icon: typeof Sprout;
}[] = [
  {
    id: "farmer",
    title: "Farmer",
    desc: "Manage farms, crops, irrigation & field data",
    icon: Sprout,
  },
  {
    id: "expert",
    title: "Expert",
    desc: "Advise growers, review simulations & content",
    icon: GraduationCap,
  },
  {
    id: "viewer",
    title: "Viewer",
    desc: "Read-only access to dashboards and reports",
    icon: Eye,
  },
];

export default function RegisterPage() {
  const { setSessionFromAuth } = useAuth() as ReturnType<typeof useAuth> & {
    setSessionFromAuth?: (t: string, u?: unknown) => void;
  };
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [organization, setOrganization] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [role, setRole] = useState<RoleChoice>("farmer");
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [acceptPrivacy, setAcceptPrivacy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (password !== confirm) {
      setError("Passwords do not match");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    if (!acceptTerms || !acceptPrivacy) {
      setError("Please accept Terms of Service and Privacy Policy");
      return;
    }
    setLoading(true);
    try {
      const res = await authApi.register({
        email,
        password,
        full_name: fullName || undefined,
        phone: phone || undefined,
        organization: organization || undefined,
        role,
        accept_terms: true,
      });
      const tok = res.access_token || "";
      if (tok && setSessionFromAuth) setSessionFromAuth(tok, res.user);
      navigate("/farms", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#f4f7f2]">
      <div
        className="pointer-events-none absolute inset-0 opacity-90"
        style={{
          background:
            "radial-gradient(900px 500px at 10% -10%, rgba(16,185,129,.18), transparent 55%), radial-gradient(700px 400px at 100% 0%, rgba(245,158,11,.12), transparent 50%)",
        }}
      />
      <div className="relative z-10 mx-auto flex min-h-screen max-w-6xl flex-col px-4 py-6 sm:px-6">
        <div className="mb-6 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-display text-lg font-bold text-slate-800">
            <span className="grid h-10 w-10 place-items-center rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/25">
              <Leaf className="h-5 w-5" />
            </span>
            EcoNojin
          </Link>
          <LanguageSwitcher />
        </div>

        <div className="grid flex-1 items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]">
          {/* Brand panel */}
          <div className="hidden lg:block">
            <p className="mb-3 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white/80 px-3 py-1 text-xs font-bold text-emerald-700">
              <ShieldCheck className="h-3.5 w-3.5" />
              Secure · Sustainable · Local-first
            </p>
            <h1 className="font-display text-4xl leading-tight text-slate-900 xl:text-5xl">
              Grow with data.
              <span className="block bg-gradient-to-r from-emerald-600 to-teal-500 bg-clip-text text-transparent">
                Join the network.
              </span>
            </h1>
            <p className="mt-4 max-w-md text-base leading-relaxed text-slate-600">
              Create your account to manage farms, track water, enroll in courses, and access climate-aware tools built for real fields.
            </p>
            <ul className="mt-8 space-y-3 text-sm text-slate-700">
              {[
                "Farm maps & GeoJSON boundaries",
                "Education tracks for climate-smart agriculture",
                "Role-based access for teams",
              ].map((line) => (
                <li key={line} className="flex items-start gap-2">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
                  {line}
                </li>
              ))}
            </ul>
          </div>

          {/* Form */}
          <form
            onSubmit={onSubmit}
            className="rounded-3xl border border-stone-200/80 bg-white/95 p-6 shadow-xl shadow-emerald-900/5 backdrop-blur sm:p-8"
          >
            <h2 className="font-display text-2xl text-slate-900">Create your account</h2>
            <p className="mt-1 text-sm text-slate-500">Takes less than a minute. Choose your role carefully.</p>

            {error && (
              <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
                {error}
              </div>
            )}

            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              {ROLES.map((r) => {
                const Icon = r.icon;
                const active = role === r.id;
                return (
                  <button
                    key={r.id}
                    type="button"
                    onClick={() => setRole(r.id)}
                    className={`rounded-2xl border p-3 text-start transition-all ${
                      active
                        ? "border-emerald-500 bg-emerald-50 ring-2 ring-emerald-500/20"
                        : "border-stone-200 hover:border-stone-300 hover:bg-stone-50"
                    }`}
                  >
                    <Icon className={`mb-2 h-5 w-5 ${active ? "text-emerald-600" : "text-stone-400"}`} />
                    <p className="text-sm font-bold text-slate-800">{r.title}</p>
                    <p className="mt-0.5 text-[11px] leading-snug text-slate-500">{r.desc}</p>
                  </button>
                );
              })}
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <label className="block text-sm sm:col-span-2">
                <span className="font-medium text-slate-600">Full name</span>
                <input
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Azadeh Karimi"
                  className="mt-1 w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
                />
              </label>
              <label className="block text-sm sm:col-span-2">
                <span className="font-medium text-slate-600">Email</span>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="mt-1 w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
                />
              </label>
              <label className="block text-sm">
                <span className="font-medium text-slate-600">Phone (optional)</span>
                <input
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+98 …"
                  className="mt-1 w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
                />
              </label>
              <label className="block text-sm">
                <span className="font-medium text-slate-600">Organization</span>
                <input
                  value={organization}
                  onChange={(e) => setOrganization(e.target.value)}
                  placeholder="Co-op / company"
                  className="mt-1 w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
                />
              </label>
              <label className="block text-sm">
                <span className="font-medium text-slate-600">Password</span>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
                />
              </label>
              <label className="block text-sm">
                <span className="font-medium text-slate-600">Confirm password</span>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
                />
              </label>
            </div>

            <div className="mt-4 space-y-2 text-sm text-slate-600">
              <label className="flex items-start gap-2">
                <input
                  type="checkbox"
                  checked={acceptTerms}
                  onChange={(e) => setAcceptTerms(e.target.checked)}
                  className="mt-1 rounded border-stone-300 text-emerald-600 focus:ring-emerald-500"
                />
                <span>
                  I agree to the{" "}
                  <Link to="/policies" className="font-bold text-emerald-700 hover:underline">
                    Terms of Service
                  </Link>
                </span>
              </label>
              <label className="flex items-start gap-2">
                <input
                  type="checkbox"
                  checked={acceptPrivacy}
                  onChange={(e) => setAcceptPrivacy(e.target.checked)}
                  className="mt-1 rounded border-stone-300 text-emerald-600 focus:ring-emerald-500"
                />
                <span>
                  I have read the{" "}
                  <Link to="/policies" className="font-bold text-emerald-700 hover:underline">
                    Privacy Policy
                  </Link>
                </span>
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 py-3 text-sm font-bold text-white shadow-lg shadow-emerald-600/25 transition hover:from-emerald-700 hover:to-teal-700 disabled:opacity-60"
            >
              {loading && <Loader2 className="h-4 w-4 animate-spin" />}
              {loading ? "Creating account…" : "Create account"}
            </button>

            <p className="mt-4 text-center text-sm text-slate-600">
              Already registered?{" "}
              <Link to="/login" className="font-bold text-emerald-700 hover:underline">
                Sign in
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
