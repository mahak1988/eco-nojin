"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { Eye, EyeOff, Fingerprint, Phone, ArrowLeft, Shield, Zap, Globe, Leaf, Coins, Brain } from "lucide-react";
import Link from "next/link";
import { loginSchema, type LoginInput } from "@/lib/validation/auth.schema";
import { useLogin } from "@/lib/api/hooks/useAuth";
import { AuthWelcomePanel } from "@/components/auth/AuthWelcomePanel";

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const loginMutation = useLogin();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      fid: "",
      phone: "",
    },
  });

  const onSubmit = (data: LoginInput) => {
    loginMutation.mutate(data);
  };

  const welcomeFeatures = [
    {
      icon: Shield,
      title: "احراز هویت امن",
      description: "ورود با رمز یکبار مصرف و رمزنگاری پیشرفته",
    },
    {
      icon: Zap,
      title: "دسترسی سریع",
      description: "دسترسی آنی به تمام ماژول‌ها و داشبورد شخصی",
    },
    {
      icon: Globe,
      title: "پشتیبانی ۲۴/۷",
      description: "تیم پشتیبانی در تمام ساعات شبانه‌روز در کنار شماست",
    },
  ];

  const welcomeStats = [
    { value: "۱۲.۵K+", label: "کاربر فعال" },
    { value: "۱۸", label: "کشور" },
    { value: "۹۸٪", label: "رضایت" },
  ];

  return (
    <div className="min-h-screen relative flex">
      {/* ================================================================== */}
      {/* 🌿 Ambient Background (برای موبایل) */}
      {/* ================================================================== */}
      <div className="fixed inset-0 -z-10 pointer-events-none lg:hidden">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div
          className="absolute inset-0 opacity-50"
          style={{
            backgroundImage: `
              radial-gradient(at 20% 20%, rgba(16, 185, 129, 0.2) 0px, transparent 50%),
              radial-gradient(at 80% 80%, rgba(59, 130, 246, 0.15) 0px, transparent 50%)
            `,
          }}
        />
      </div>

      {/* ================================================================== */}
      {/* 🎨 Welcome Panel (سمت راست در RTL) */}
      {/* ================================================================== */}
      <AuthWelcomePanel
        badge="پلتفرم جامع احیای زمین"
        title="خوش آمدید به اکو نوژین"
        subtitle="ساکن زمین هستیم، احیاگر اکوسیستم"
        description="با ورود به اکو نوژین، به جامعه‌ای از کشاورزان، دانشمندان و فعالان محیط زیست بپیوندید که در حال ساختن آینده‌ای پایدار برای زمین هستند."
        features={welcomeFeatures}
        stats={welcomeStats}
        accentGradient={`
          radial-gradient(at 20% 20%, rgba(16, 185, 129, 0.25) 0px, transparent 50%),
          radial-gradient(at 80% 80%, rgba(59, 130, 246, 0.2) 0px, transparent 50%),
          radial-gradient(at 50% 50%, rgba(139, 92, 246, 0.15) 0px, transparent 50%)
        `}
      />

      {/* ================================================================== */}
      {/* 🔐 Login Form (سمت چپ در RTL) */}
      {/* ================================================================== */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
        <motion.div
          initial={{ opacity: 0, y: 30, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="w-full max-w-md relative"
        >
          {/* Back to Home - فقط در موبایل */}
          <Link
            href="/"
            className="lg:hidden inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-emerald-400 transition-colors mb-6"
          >
            <ArrowLeft className="h-4 w-4" />
            بازگشت به خانه
          </Link>

          {/* Logo */}
          <div className="flex justify-center mb-8">
            <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-[0_0_40px_rgba(16,185,129,0.3)]">
              <Leaf className="h-8 w-8 text-white" />
            </div>
          </div>

          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-black text-white mb-2 tracking-tight">
              ورود به حساب کاربری
            </h1>
            <p className="text-zinc-400 font-light">
              شناسه کاربری و شماره تلفن خود را وارد کنید
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* User ID */}
            <div>
              <label htmlFor="fid" className="block text-sm font-medium text-zinc-300 mb-2">
                شناسه کاربری
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
                  <Fingerprint className="h-5 w-5 text-zinc-500" />
                </div>
                <input
                  id="fid"
                  type="text"
                  {...register("fid")}
                  placeholder="U001"
                  dir="ltr"
                  autoFocus
                  className="w-full pr-12 pl-4 py-3.5 bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 focus:bg-black/40 transition-all text-left"
                />
              </div>
              {errors.fid && (
                <motion.p
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-2 text-sm text-rose-400 flex items-center gap-1"
                >
                  <span>⚠️</span>
                  {errors.fid.message}
                </motion.p>
              )}
            </div>

            {/* Phone */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-zinc-300 mb-2">
                شماره تلفن
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
                  <Phone className="h-5 w-5 text-zinc-500" />
                </div>
                <input
                  id="phone"
                  type="tel"
                  {...register("phone")}
                  placeholder="+989123456789"
                  dir="ltr"
                  className="w-full pr-12 pl-4 py-3.5 bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 focus:bg-black/40 transition-all text-left"
                />
              </div>
              {errors.phone && (
                <motion.p
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-2 text-sm text-rose-400 flex items-center gap-1"
                >
                  <span>⚠️</span>
                  {errors.phone.message}
                </motion.p>
              )}
            </div>

            {/* Submit Button */}
            <motion.button
              type="submit"
              disabled={isSubmitting || loginMutation.isPending}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-4 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 rounded-xl font-bold text-white transition-all shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:shadow-[0_0_40px_rgba(16,185,129,0.5)] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting || loginMutation.isPending ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  در حال ورود...
                </span>
              ) : (
                "ورود به حساب"
              )}
            </motion.button>
          </form>

          {/* Footer Links */}
          <div className="mt-8 pt-6 border-t border-white/10 space-y-4">
            <div className="flex items-center justify-between text-sm">
              <Link
                href="/forgot-password"
                className="text-zinc-400 hover:text-emerald-400 transition-colors"
              >
                فراموشی رمز عبور؟
              </Link>
              <Link
                href="/register"
                className="text-emerald-400 hover:text-emerald-300 font-medium transition-colors"
              >
                ثبت‌نام کنید
              </Link>
            </div>

            <p className="text-center text-xs text-zinc-500">
              با ورود به اکو نوژین، شما با{" "}
              <Link href="/terms" className="text-emerald-400 hover:underline">
                شرایط استفاده
              </Link>{" "}
              و{" "}
              <Link href="/privacy" className="text-emerald-400 hover:underline">
                حریم خصوصی
              </Link>{" "}
              ما موافقت می‌کنید.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}