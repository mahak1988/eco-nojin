"use client";

import { useState } from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import { Leaf, Shield, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FormField } from "@/components/ui/form-field";
import { authService } from "@/lib/api";
import { setSession } from "@/lib/auth";
import { useAppStore } from "@/store/useAppStore";
import { HOME_HERO } from "@/lib/media";
import { useTranslations, useLocale } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { Link } from "@/i18n/navigation";

export default function LoginPage() {
  const router = useRouter();
  const t = useTranslations();
  const locale = useLocale();
  const loginStore = useAppStore((s) => s.login);
  const [step, setStep] = useState<"otp" | "verify">("otp");
  const [fid, setFid] = useState("");
  const [phone, setPhone] = useState("+989");
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [devCode, setDevCode] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const requestOtp = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await authService.requestOtp(phone, fid);
      if (res.dev_code) {
        setDevCode(res.dev_code);
        setCode(res.dev_code);
      }
      setStep("verify");
    } catch {
      setError("ارسال OTP ناموفق");
    } finally {
      setLoading(false);
    }
  };

  const verify = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await authService.verifyOtp(phone, code, fid.trim(), name);
      const user = { fid: res.farmer_id, name: name || res.farmer_id, phone };
      setSession(res.access_token, user);
      loginStore(res.access_token, user);
      const redirect =
        typeof window !== "undefined"
          ? new URLSearchParams(window.location.search).get("redirect") || "/"
          : "/";
      router.push(redirect);
    } catch {
      setError("کد نامعتبر است");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-slate-950">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="relative hidden lg:block"
      >
        <Image src={HOME_HERO.image} alt="" fill className="object-cover" priority />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/70 to-transparent" />
        <div className="absolute bottom-12 right-12 text-white max-w-md">
          <h2 className="text-4xl font-bold">{t("app.title")}</h2>
          <p className="mt-4 text-slate-300">
            {locale === "en" ? "OTP login · JWT · Multi-layer security" : "ورود OTP · JWT · امنیت چندلایه"}
          </p>
          <div className="flex gap-3 mt-6 flex-wrap">
            {[Shield, Leaf, Sparkles].map((Icon, i) => (
              <span
                key={i}
                className="flex items-center gap-2 text-sm bg-white/10 px-3 py-2 rounded-full border border-white/10"
              >
                <Icon className="h-4 w-4 text-emerald-400" />
              </span>
            ))}
          </div>
        </div>
      </motion.div>

      <div className="flex items-center justify-center p-8">
        <div className="w-full max-w-md space-y-6">
          <h1 className="text-3xl font-bold">{t("nav.login")}</h1>
          {error && (
            <Alert variant="danger">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          {step === "otp" ? (
            <div className="space-y-4 p-6 rounded-2xl border border-slate-800 bg-slate-900/50">
              <FormField id="fid" label="FID" value={fid} onChange={(e) => setFid(e.target.value)} required />
              <FormField id="phone" label="موبایل" value={phone} onChange={(e) => setPhone(e.target.value)} required />
              <Button onClick={requestOtp} disabled={loading} className="w-full bg-sky-600">
                {t("otp.request")}
              </Button>
            </div>
          ) : (
            <form onSubmit={verify} className="space-y-4 p-6 rounded-2xl border border-slate-800 bg-slate-900/50">
              {devCode && (
                <p className="text-xs text-amber-400">Dev OTP: {devCode}</p>
              )}
              <FormField id="name" label="نام" value={name} onChange={(e) => setName(e.target.value)} />
              <FormField id="code" label="کد OTP" value={code} onChange={(e) => setCode(e.target.value)} required />
              <Button type="submit" disabled={loading} className="w-full bg-emerald-600">
                {t("otp.verify")}
              </Button>
              <Button type="button" variant="ghost" onClick={() => setStep("otp")} className="w-full">
                بازگشت
              </Button>
            </form>
          )}
          <p className="text-center text-sm text-slate-500">
            <Link href="/register" className="text-sky-400">
              ثبت‌نام
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
