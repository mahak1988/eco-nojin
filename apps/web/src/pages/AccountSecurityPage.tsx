import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { Shield, KeyRound, Smartphone, Monitor, CheckCircle2 } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { tExtra } from "../components/eco/i18n_extras";

export default function AccountSecurityPage() {
  const { lang } = useLang();
  const tx = (k: string) => tExtra(lang, k);
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [saved, setSaved] = useState(false);

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (next.length < 8 || next !== confirm) return;
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
    setCurrent("");
    setNext("");
    setConfirm("");
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-700 text-white shadow-lg shadow-emerald-500/25">
            <Shield className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{tx("sec_title")}</h1>
            <p className="text-sm text-stone-500">{tx("sec_sub")}</p>
          </div>
        </div>
        <Link to="/account" className="text-sm font-bold text-emerald-700">
          {tx("sec_back")}
        </Link>
      </div>

      <form
        onSubmit={onSubmit}
        className="space-y-4 rounded-3xl border border-stone-200/80 bg-white p-6 shadow-sm"
      >
        <h2 className="flex items-center gap-2 font-display text-lg text-stone-800">
          <KeyRound className="h-5 w-5 text-emerald-600" />
          {tx("sec_password")}
        </h2>
        {saved && (
          <div className="flex items-center gap-2 rounded-xl bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-800">
            <CheckCircle2 className="h-4 w-4" /> OK
          </div>
        )}
        {(
          [
            ["sec_current", current, setCurrent],
            ["sec_new", next, setNext],
            ["sec_confirm", confirm, setConfirm],
          ] as const
        ).map(([key, val, set]) => (
          <label key={key} className="block text-sm">
            <span className="font-medium text-stone-600">{tx(key)}</span>
            <input
              type="password"
              value={val}
              onChange={(e) => set(e.target.value)}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
            />
          </label>
        ))}
        <button
          type="submit"
          className="w-full rounded-xl bg-emerald-600 py-2.5 text-sm font-bold text-white hover:bg-emerald-700"
        >
          {tx("sec_save")}
        </button>
      </form>

      <div className="rounded-3xl border border-stone-200/80 bg-white p-6 shadow-sm">
        <h2 className="mb-4 flex items-center gap-2 font-display text-lg">
          <Monitor className="h-5 w-5 text-stone-500" />
          {tx("sec_sessions")}
        </h2>
        <div className="flex items-center justify-between rounded-2xl bg-stone-50 px-4 py-3">
          <div>
            <p className="font-bold text-stone-800">{tx("sec_this_device")}</p>
            <p className="text-xs text-stone-500">Web · local</p>
          </div>
          <button type="button" className="text-xs font-bold text-rose-600">
            {tx("sec_revoke")}
          </button>
        </div>
      </div>

      <div className="rounded-3xl border border-dashed border-stone-300 bg-gradient-to-br from-stone-50 to-white p-6">
        <h2 className="flex items-center gap-2 font-display text-lg">
          <Smartphone className="h-5 w-5 text-violet-600" />
          {tx("sec_2fa")}
        </h2>
        <p className="mt-2 text-sm text-stone-500">{tx("sec_2fa_desc")}</p>
        <span className="mt-3 inline-block rounded-full bg-stone-200 px-3 py-1 text-xs font-bold text-stone-600">
          {tx("sec_2fa_off")}
        </span>
      </div>
    </div>
  );
}
