import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { LanguageSwitcher } from "../components/Layout/LanguageSwitcher";
import { useLang, CONTENT } from "../components/eco/i18n";
import { tr, tExtra } from "../components/eco/i18n_extras";

export default function VerifyOtpPage() {
  const { lang } = useLang();
  const c = CONTENT[lang] as unknown as Record<string, unknown>;
  const tx = (key: string) => {
    const a = tr(c, lang, key);
    return a !== key ? a : tExtra(lang, key);
  };
  const [otp, setOtp] = useState("");
  const navigate = useNavigate();

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (otp.length >= 4) navigate("/dashboard");
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-stone-50 p-4">
      <div className="mb-4 flex w-full max-w-md justify-end">
        <LanguageSwitcher />
      </div>
      <form onSubmit={onSubmit} className="w-full max-w-md space-y-4 rounded-3xl border bg-white p-8 shadow-lg">
        <h1 className="font-display text-2xl">{tx("auth_otp_title")}</h1>
        <p className="text-sm text-stone-500">{tx("auth_otp_sub")}</p>
        <input
          value={otp}
          onChange={(e) => setOtp(e.target.value)}
          className="w-full rounded-xl border px-3 py-2.5 tracking-widest"
          placeholder="••••"
        />
        <button type="submit" className="w-full rounded-xl bg-emerald-600 py-2.5 font-bold text-white">
          {tx("auth_otp_verify")}
        </button>
        <Link to="/login" className="block text-center text-sm font-bold text-emerald-700">
          {tx("auth_signin")}
        </Link>
      </form>
    </div>
  );
}
