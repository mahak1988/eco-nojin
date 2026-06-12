"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { Eye, EyeOff, User, Phone, Mail, Lock, Fingerprint, ArrowLeft, Gift, TrendingUp, Users, BookOpen, Shield, Sprout } from "lucide-react";
import Link from "next/link";
import { registerSchema, type RegisterInput } from "@/lib/validation/auth.schema";
import { useRegister } from "@/lib/api/hooks/useAuth";
import { useRouter } from "next/navigation";
import { AuthWelcomePanel } from "@/components/auth/AuthWelcomePanel";

export default function RegisterPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const registerMutation = useRegister();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<RegisterInput>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      fid: "",
      phone: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  const onSubmit = async (data: RegisterInput) => {
    registerMutation.mutate(data, {
      onSuccess: () => {
        setTimeout(() => {
          router.push("/login");
        }, 2000);
      },
    });
  };

  const passwordValue = watch("password") || "";
  const getPasswordStrength = () => {
    let strength = 0;
    if (passwordValue.length >= 8) strength++;
    if (/[a-z]/.test(passwordValue)) strength++;
    if (/[A-Z]/.test(passwordValue)) strength++;
    if (/\d/.test(passwordValue)) strength++;
    if (/[^A-Za-z0-9]/.test(passwordValue)) strength++;
    return strength;
  };

  const passwordStrength = getPasswordStrength();
  const strengthLabels = ["خیلی ضعیف", "ضعیف", "متوسط", "قوی", "خیلی قوی"];
  const strengthColors = ["bg-rose-500", "bg-orange-500", "bg-amber-500", "bg-emerald-500", "bg-emerald-400"];

  const welcomeFeatures = [
    {
      icon: Gift,
      title: "پاداش خوش‌آمدگویی",
      description: "۱۰۰ اکو کوین رایگان به عنوان هدیه ثبت‌نام",
    },
    {
      icon: TrendingUp,
      title: "اکو ماینینگ سبز",
      description: "کسب درآمد با ماینینگ سازگار با محیط زیست",
    },
    {
      icon: BookOpen,
      title: "آکادمی آموزشی",
      description: "دسترسی به بیش از ۲۰۰ دوره تخصصی رایگان",
    },
    {
      icon: Users,
      title: "جامعه کشاورزان",
      description: "ارتباط با هزاران کشاورز و متخصص در سراسر جهان",
    },
  ];

  return (
    <div className="min-h-screen relative flex">
      {/* Ambient Background (موبایل) */}
      <div className="fixed inset-0 -z-10 pointer-events-none lg:hidden">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div
          className="absolute inset-0 opacity-50"
          style={{
            backgroundImage: `
              radial-gradient(at 30% 20%, rgba(16, 185, 129, 0.2) 0px, transparent 50%),
              radial-gradient(at 70% 80%, rgba(59, 130, 246, 0.15) 0px, transparent 50%)
            `,
          }}
        />
      </div>

      {/* Welcome Panel */}
      <AuthWelcomePanel
        badge="عضویت رایگان"
        title="به خانواده اکو نوژین بپیوندید"
        subtitle="آینده‌ای پایدار با هم می‌سازیم"
        description="با ثبت‌نام در اکو نوژین، به جامعه‌ای جهانی از پیشگامان احیای زمین بپیوندید و از مزایای منحصربه‌فرد پلتفرم ما بهره‌مند شوید."
        features={welcomeFeatures}
        accentGradient={`
          radial-gradient(at 20% 30%, rgba(16, 185, 129, 0.25) 0px, transparent 50%),
          radial-gradient(at 80% 70%, rgba(139, 92, 246, 0.2) 0px, transparent 50%),
          radial-gradient(at 50% 50%, rgba(59, 130, 246, 0.15) 0px, transparent 50%)
        `}
      />

      {/* Register Form */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12 overflow-y-auto">
        <motion.div
          initial={{ opacity: 0, y: 30, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="w-full max-w-lg relative my-8"
        >
          {/* Back */}
          <Link
            href="/login"
            className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-emerald-400 transition-colors mb-6"
          >
            <ArrowLeft className="h-4 w-4" />
            بازگشت به ورود
          </Link>

          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-[0_0_40px_rgba(16,185,129,0.3)]">
              <Sprout className="h-8 w-8 text-white" />
            </div>
          </div>

          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-black text-white mb-2 tracking-tight">
              ایجاد حساب کاربری
            </h1>
            <p className="text-zinc-400 font-light">
              در کمتر از ۲ دقیقه ثبت‌نام کنید
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-zinc-300 mb-2">
                نام و نام خانوادگی
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
                  <User className="h-5 w-5 text-zinc-500" />
                </div>
                <input
                  id="name"
                  type="text"
                  {...register("name")}
                  placeholder="علی احمدی"
                  className="w-full pr-12 pl-4 py-3 bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 focus:bg-black/40 transition-all"
                />
              </div>
              {errors.name && (
                <motion.p
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-2 text-sm text-rose-400 flex items-center gap-1"
                >
                  <span>⚠️</span>
                  {errors.name.message}
                </motion.p>
              )}
            </div>

            {/* User ID & Phone */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                    className="w-full pr-12 pl-4 py-3 bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 focus:bg-black/40 transition-all text-left"
                  />
                </div>
                {errors.fid && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-rose-400"
                  >
                    ⚠️ {errors.fid.message}
                  </motion.p>
                )}
              </div>

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
                    className="w-full pr-12 pl-4 py-3 bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 focus:bg-black/40 transition-all text-left"
                  />
                </div>
                {errors.phone && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-rose-400"
                  >
                    ⚠️ {errors.phone.message}
                  </motion.p>
                )}
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-zinc-300 mb-2">
                ایمیل <span className="text-zinc-500 text-xs">(اختیاری)</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
                  <Mail className="h-5 w-5 text-zinc-500" />
                </div>
                <input
                  id="email"
                  type="email"
                  {...register("email")}
                  placeholder="example@email.com"
                  dir="ltr"
                  className="w-full pr-12 pl-4 py-3 bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 focus:bg-black/40 transition-all text-left"
                />
              </div>
              {errors.email && (
                <motion.p
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-2 text-sm text-rose-400"
                >
                  ⚠️ {errors.email.message}
                </motion.p>
              )}
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-zinc-300 mb-2">
                رمز عبور
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
                  <Lock className="h-5 w-5 text-zinc-500" />
                </div>
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  {...register("password")}
                  placeholder="••••••••"
                  dir="ltr"
                  className="w-full pr-12 pl-12 py-3 bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 focus:bg-black/40 transition-all text-left"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 left-0 flex items-center pl-4 text-zinc-500 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>

              {passwordValue && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  className="mt-3"
                >
                  <div className="flex gap-1 mb-1">
                    {[0, 1, 2, 3, 4].map((i) => (
                      <div
                        key={i}
                        className={`h-1 flex-1 rounded-full transition-all ${
                          i < passwordStrength ? strengthColors[passwordStrength - 1] : "bg-white/10"
                        }`}
                      />
                    ))}
                  </div>
                  <p className="text-xs text-zinc-400">
                    قدرت رمز: <span className="text-white font-medium">{strengthLabels[passwordStrength - 1] || "—"}</span>
                  </p>
                </motion.div>
              )}

              {errors.password && (
                <motion.p
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-2 text-sm text-rose-400"
                >
                  ⚠️ {errors.password.message}
                </motion.p>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-zinc-300 mb-2">
                تکرار رمز عبور
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
                  <Lock className="h-5 w-5 text-zinc-500" />
                </div>
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  {...register("confirmPassword")}
                  placeholder="••••••••"
                  dir="ltr"
                  className="w-full pr-12 pl-12 py-3 bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 focus:bg-black/40 transition-all text-left"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 left-0 flex items-center pl-4 text-zinc-500 hover:text-white transition-colors"
                >
                  {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
              {errors.confirmPassword && (
                <motion.p
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-2 text-sm text-rose-400"
                >
                  ⚠️ {errors.confirmPassword.message}
                </motion.p>
              )}
            </div>

            {/* Submit Button */}
            <motion.button
              type="submit"
              disabled={isSubmitting || registerMutation.isPending}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-4 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 rounded-xl font-bold text-white transition-all shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:shadow-[0_0_40px_rgba(16,185,129,0.5)] disabled:opacity-50 disabled:cursor-not-allowed mt-6"
            >
              {isSubmitting || registerMutation.isPending ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  در حال ثبت‌نام...
                </span>
              ) : (
                "ایجاد حساب کاربری"
              )}
            </motion.button>
          </form>

          <div className="mt-6 pt-6 border-t border-white/10 text-center">
            <p className="text-sm text-zinc-400">
              قبلاً ثبت‌نام کرده‌اید؟{" "}
              <Link href="/login" className="text-emerald-400 hover:text-emerald-300 font-medium transition-colors">
                وارد شوید
              </Link>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}