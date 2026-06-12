"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { Eye, EyeOff, Lock, KeyRound, ArrowLeft, CheckCircle, Shield, Leaf } from "lucide-react";
import Link from "next/link";
import { z } from "zod";
import { useResetPassword } from "@/lib/api/hooks/useAuth";
import { useRouter } from "next/navigation";
import { AuthWelcomePanel } from "@/components/auth/AuthWelcomePanel";

const resetPasswordSchema = z.object({
  token: z
    .string()
    .min(1, "کد تأیید الزامی است")
    .min(6, "کد باید ۶ رقم باشد")
    .max(6, "کد باید ۶ رقم باشد"),
  newPassword: z
    .string()
    .min(1, "رمز عبور جدید الزامی است")
    .min(8, "رمز عبور باید حداقل ۸ کاراکتر باشد")
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      "رمز باید شامل حروف بزرگ، کوچک و عدد باشد"
    ),
  confirmPassword: z.string().min(1, "تأیید رمز عبور الزامی است"),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "رمز عبور و تأیید آن مطابقت ندارند",
  path: ["confirmPassword"],
});

type ResetPasswordInput = z.infer<typeof resetPasswordSchema>;

export default function ResetPasswordPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const resetPasswordMutation = useResetPassword();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<ResetPasswordInput>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      token: "",
      newPassword: "",
      confirmPassword: "",
    },
  });

  const onSubmit = (data: ResetPasswordInput) => {
    resetPasswordMutation.mutate(
      { token: data.token, newPassword: data.newPassword },
      {
        onSuccess: () => {
          setIsSuccess(true);
          setTimeout(() => {
            router.push("/login");
          }, 3000);
        },
      }
    );
  };

  const passwordValue = watch("newPassword") || "";
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
      icon: Shield,
      title: "امنیت پیشرفته",
      description: "رمز عبور با الگوریتم bcrypt رمزنگاری می‌شود",
    },
    {
      icon: Lock,
      title: "الزامات قوی",
      description: "حداقل ۸ کاراکتر شامل حروف بزرگ، کوچک و عدد",
    },
    {
      icon: KeyRound,
      title: "حفاظت از حساب",
      description: "پس از تغییر، تمام نشست‌های قبلی غیرفعال می‌شوند",
    },
  ];

  return (
    <div className="min-h-screen relative flex">
      {/* Ambient Background */}
      <div className="fixed inset-0 -z-10 pointer-events-none lg:hidden">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div
          className="absolute inset-0 opacity-50"
          style={{
            backgroundImage: `
              radial-gradient(at 30% 30%, rgba(16, 185, 129, 0.2) 0px, transparent 50%),
              radial-gradient(at 70% 70%, rgba(139, 92, 246, 0.15) 0px, transparent 50%)
            `,
          }}
        />
      </div>

      {/* Welcome Panel */}
      <AuthWelcomePanel
        badge="تنظیم رمز جدید"
        title="یک رمز قوی بسازید"
        subtitle="امنیت حساب شما در دستان شماست"
        description="رمز عبور جدید باید حداقل ۸ کاراکتر شامل حروف بزرگ، کوچک و عدد باشد. از رمزهای قابل حدس مانند تاریخ تولد یا شماره تلفن استفاده نکنید."
        features={welcomeFeatures}
        accentGradient={`
          radial-gradient(at 30% 30%, rgba(16, 185, 129, 0.25) 0px, transparent 50%),
          radial-gradient(at 70% 70%, rgba(139, 92, 246, 0.2) 0px, transparent 50%),
          radial-gradient(at 50% 50%, rgba(59, 130, 246, 0.15) 0px, transparent 50%)
        `}
      />

      {/* Form */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
        <motion.div
          initial={{ opacity: 0, y: 30, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="w-full max-w-md relative"
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
              <Leaf className="h-8 w-8 text-white" />
            </div>
          </div>

          {!isSuccess ? (
            <>
              <div className="text-center mb-8">
                <div className="inline-flex p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 mb-4">
                  <KeyRound className="h-8 w-8 text-emerald-400" />
                </div>
                <h1 className="text-3xl font-black text-white mb-2 tracking-tight">
                  تنظیم رمز جدید
                </h1>
                <p className="text-zinc-400 font-light">
                  کد دریافتی و رمز عبور جدید را وارد کنید
                </p>
              </div>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                {/* Token */}
                <div>
                  <label htmlFor="token" className="block text-sm font-medium text-zinc-300 mb-2">
                    کد تأیید ۶ رقمی
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
                      <KeyRound className="h-5 w-5 text-zinc-500" />
                    </div>
                    <input
                      id="token"
                      type="text"
                      {...register("token")}
                      placeholder="۱۲۳۴۵۶"
                      maxLength={6}
                      dir="ltr"
                      autoFocus
                      className="w-full pr-12 pl-4 py-3.5 bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 focus:bg-black/40 transition-all text-center text-2xl font-mono tracking-[0.5em]"
                    />
                  </div>
                  {errors.token && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-2 text-sm text-rose-400"
                    >
                      ⚠️ {errors.token.message}
                    </motion.p>
                  )}
                </div>

                {/* New Password */}
                <div>
                  <label htmlFor="newPassword" className="block text-sm font-medium text-zinc-300 mb-2">
                    رمز عبور جدید
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
                      <Lock className="h-5 w-5 text-zinc-500" />
                    </div>
                    <input
                      id="newPassword"
                      type={showPassword ? "text" : "password"}
                      {...register("newPassword")}
                      placeholder="••••••••"
                      dir="ltr"
                      className="w-full pr-12 pl-12 py-3.5 bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 focus:bg-black/40 transition-all text-left"
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

                  {errors.newPassword && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-2 text-sm text-rose-400"
                    >
                      ⚠️ {errors.newPassword.message}
                    </motion.p>
                  )}
                </div>

                {/* Confirm Password */}
                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-zinc-300 mb-2">
                    تکرار رمز عبور جدید
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
                      className="w-full pr-12 pl-12 py-3.5 bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 focus:bg-black/40 transition-all text-left"
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

                <motion.button
                  type="submit"
                  disabled={isSubmitting || resetPasswordMutation.isPending}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full py-4 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 rounded-xl font-bold text-white transition-all shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:shadow-[0_0_40px_rgba(16,185,129,0.5)] disabled:opacity-50 disabled:cursor-not-allowed mt-6"
                >
                  {isSubmitting || resetPasswordMutation.isPending ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      در حال تغییر رمز...
                    </span>
                  ) : (
                    "تغییر رمز عبور"
                  )}
                </motion.button>
              </form>
            </>
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-8"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", delay: 0.2 }}
                className="inline-flex p-5 rounded-full bg-emerald-500/10 border border-emerald-500/20 mb-6"
              >
                <CheckCircle className="h-12 w-12 text-emerald-400" />
              </motion.div>

              <h2 className="text-2xl font-black text-white mb-3">
                رمز عبور تغییر کرد!
              </h2>
              <p className="text-zinc-400 mb-6 leading-relaxed">
                رمز عبور شما با موفقیت تغییر کرد.
                <br />
                تا چند لحظه دیگر به صفحه ورود هدایت می‌شوید.
              </p>

              <Link
                href="/login"
                className="inline-block px-8 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 rounded-xl font-bold text-white transition-all shadow-[0_0_30px_rgba(16,185,129,0.3)]"
              >
                ورود به حساب
              </Link>
            </motion.div>
          )}

          <div className="mt-8 pt-6 border-t border-white/10 text-center">
            <p className="text-xs text-zinc-500">
              کد دریافت نکردید؟{" "}
              <Link href="/forgot-password" className="text-emerald-400 hover:underline">
                ارسال مجدد
              </Link>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}