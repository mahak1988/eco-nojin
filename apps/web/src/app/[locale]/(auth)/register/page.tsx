"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { authService } from "@/lib/api";
import { setSession } from "@/lib/auth";
import { useAppStore } from "@/store/useAppStore";

export default function RegisterPage() {
  const router = useRouter();
  const loginStore = useAppStore((s) => s.login);
  const [fid, setFid] = useState("");
  const [phone, setPhone] = useState("+989");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await authService.login(fid, phone, name);
      const user = { fid: res.farmer_id, name, phone };
      setSession(res.access_token, user);
      loginStore(res.access_token, user);
      router.push("/");
    } catch (err: unknown) {
      setError("ثبت‌نام ناموفق — مقادیر را بررسی کنید");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-slate-950">
      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md"
      >
        <h1 className="text-3xl font-bold mb-2">ثبت‌نام</h1>
        <p className="text-slate-400 mb-8">ایجاد حساب کشاورز در اکو نوژین</p>
        <form
          onSubmit={handleSubmit}
          className="space-y-4 p-6 rounded-2xl border border-slate-800 bg-slate-900/60"
        >
          {error && <p className="text-sm text-rose-400">{error}</p>}
          <FormField id="fid" label="شناسه" value={fid} onChange={(e) => setFid(e.target.value)} required />
          <FormField id="phone" label="موبایل" value={phone} onChange={(e) => setPhone(e.target.value)} required />
          <FormField id="name" label="نام" value={name} onChange={(e) => setName(e.target.value)} required />
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "..." : "ایجاد حساب"}
          </Button>
        </form>
        <p className="text-center mt-6 text-sm text-slate-500">
          <Link href="/login" className="text-sky-400">
            ورود
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
