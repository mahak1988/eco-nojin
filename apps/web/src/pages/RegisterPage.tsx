import { FormEvent, useMemo, useState } from "react";
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
import { useLang, CONTENT } from "../components/eco/i18n";
import { tr, tExtra } from "../components/eco/i18n_extras";

type RoleChoice = "farmer" | "expert" | "viewer";

export default function RegisterPage() {
  const { setSessionFromAuth, login } = useAuth() as ReturnType<typeof useAuth> & {
    setSessionFromAuth?: (t: string, u?: unknown) => void;
  };
  const navigate = useNavigate();
  const { lang } = useLang();
  const c = CONTENT[lang] as unknown as Record<string, unknown>;
  const tx = (key: string) => {
    const a = tr(c, lang, key);
    return a !== key ? a : tExtra(lang, key);
  };

  const roles = useMemo(
    () => [
      { id: "farmer" as RoleChoice, title: tx("role_farmer"), desc: tx("role_farmer_desc"), icon: Sprout },
      { id: "expert" as RoleChoice, title: tx("role_expert"), desc: tx("role_expert_desc"), icon: GraduationCap },
      { id: "viewer" as RoleChoice, title: tx("role_viewer"), desc: tx("role_viewer_desc"), icon: Eye },
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps -- lang drives strings
    [lang],
  );

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState(""); // Kept for UI but not used in API
  const [organization, setOrganization] = useState(""); // Kept for UI but not used in API
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [role, setRole] = useState<RoleChoice>("farmer"); // Kept for UI but not used in API
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [acceptPrivacy, setAcceptPrivacy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (password !== confirm) {
      setError(tx("auth_err_password_match"));
      return;
    }
    if (password.length < 8) {
      setError(tx("auth_err_password_len"));
      return;
    }
    if (!acceptTerms || !acceptPrivacy) {
      setError(tx("auth_err_terms"));
      return;
    }
    setLoading(true);
    try {
      // Call register with only the fields supported by the new API
      await authApi.register({
        email,
        password,
        full_name: fullName || undefined,
        locale: "en-US" // Adding locale as required by the new API
      });
      
      // Then log in to get the token
      const res = await login(email, password);
      const tok = res.access_token || "";
      if (tok && setSessionFromAuth) setSessionFromAuth(tok, res.user);
      navigate("/farms", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : tx("auth_err_register"));
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
            {tx("appName")}
          </Link>
          <LanguageSwitcher />
        </div>

        <div className="grid flex-1 items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="hidden lg:block">
            <p className="mb-3 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white/80 px-3 py-1 text-xs font-bold text-emerald-700">
              <ShieldCheck className="h-3.5 w-3.5" />
              {tx("auth_reg_hero_badge")}
            </p>
            <h1 className="font-display text-4xl leading-tight text-slate-900 xl:text-5xl">
              {tx("auth_reg_hero_t1")}
              <span className="block bg-gradient-to-r from-emerald-600 to-teal-500 bg-clip-text text-transparent">
                {tx("auth_reg_hero_t2")}
              </span>
            </h1>
            <p className="mt-4 max-w-md text-base leading-relaxed text-slate-600">{tx("auth_reg_hero_lede")}</p>
            <ul className="mt-8 space-y-3 text-sm text-slate-700">
              {[tx("auth_reg_bullet1"), tx("auth_reg_bullet2"), tx("auth_reg_bullet3")].map((line) => (
                <li key={line} className="flex items-start gap-2">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
                  {line}
                </li>
              ))}
            </ul>
          </div>

          <form
            onSubmit={onSubmit}
            className="rounded-3xl border border-stone-200/80 bg-white/95 p-6 shadow-xl shadow-emerald-900/5 backdrop-blur sm:p-8"
          >
            <h2 className="font-display text-2xl text-slate-900">{tx("auth_reg_title")}</h2>
            <p className="mt-1 text-sm text-slate-500">{tx("auth_reg_sub")}</p>

            {error && (
              <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
                {error}
              </div>
            )}

            {/* Removed role selection as it's not supported by the new API */}
            
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <label className="block text-sm sm:col-span-2">
                <span className="font-medium text-slate-600">{tx("auth_full_name")}</span>
                <input
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
                />
              </label>
              <label className="block text-sm sm:col-span-2">
                <span className="font-medium text-slate-600">{tx("auth_email")}</span>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
                />
              </label>
              <label className="block text-sm">
                <span className="font-medium text-slate-600">{tx("auth_phone")}</span>
                <input
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
                />
              </label>
              <label className="block text-sm">
                <span className="font-medium text-slate-600">{tx("auth_organization")}</span>
                <input
                  value={organization}
                  onChange={(e) => setOrganization(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
                />
              </label>
              <label className="block text-sm">
                <span className="font-medium text-slate-600">{tx("auth_password")}</span>
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
                <span className="font-medium text-slate-600">{tx("auth_confirm_password")}</span>
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
                  {tx("auth_agree_terms")}{" "}
                  <Link to="/policies" className="font-bold text-emerald-700 hover:underline">
                    {tx("auth_terms")}
                  </Link>
                  {tx("auth_agree_mid") ? ` ${tx("auth_agree_mid")}` : ""}
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
                  {tx("auth_read_privacy")}{" "}
                  <Link to="/policies" className="font-bold text-emerald-700 hover:underline">
                    {tx("auth_privacy")}
                  </Link>
                  {tx("auth_read_privacy_suffix")}
                </span>
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 py-3 text-sm font-bold text-white shadow-lg shadow-emerald-600/25 transition hover:from-emerald-700 hover:to-teal-700 disabled:opacity-60"
            >
              {loading && <Loader2 className="h-4 w-4 animate-spin" />}
              {loading ? tx("auth_creating") : tx("auth_create_btn")}
            </button>

            <p className="mt-4 text-center text-sm text-slate-600">
              {tx("auth_already")}{" "}
              <Link to="/login" className="font-bold text-emerald-700 hover:underline">
                {tx("auth_signin")}
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}