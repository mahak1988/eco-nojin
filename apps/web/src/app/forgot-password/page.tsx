"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { Phone, ArrowLeft, KeyRound, CheckCircle, Shield, HelpCircle, Clock, Leaf } from "lucide-react";
import Link from "next/link";
import { forgotPasswordSchema, type ForgotPasswordInput } from "@/lib/validation/auth.schema";
import { useForgotPassword } from "@/lib/api/hooks/useAuth";
import { useRouter } from "next/navigation";
import { AuthWelcomePanel } from "@/components/auth/AuthWelcomePanel";

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [sentPhone, setSentPhone] = useState("");
  const forgotPasswordMutation = useForgotPassword();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordInput>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      phone: "",
    },
  });

  const onSubmit = (data: ForgotPasswordInput) => {
    forgotPasswordMutation.mutate(data, {
      onSuccess: () => {
        setSentPhone(data.phone);
        setIsSubmitted(true);
      },
    });
  };

  const welcomeFeatures = [
    {
      icon: Shield,
      title: "امنیت کامل",
      description: "کد بازیابی فقط به شماره ثبت‌شده شما ارسال می‌شود",
    },
    {
      icon: Clock,
      title: "اعتبار ۱۰ دقیقه‌ای",
      description: "کد ارسالی تا ۱۰ دقیقه معتبر است",
    },
    {
      icon: HelpCircle,
      title: "پشتیبانی ۲۴/۷",
      description: "در صورت مشکل، تیم پشتیبانی در کنار شماست",
    },
  ];

  return (
    <div className="min-h-screen relative flex">
      <div className="fixed inset-0 -z-10 pointer-events-none lg:hidden">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div
          className="absolute inset-0 opacity-50"
          style={{
            backgroundImage: "radial-gradient(at 20% 30%, rgba(245, 158, 11, 0.2) 0px, transparent 50%), radial-gradient(at 80% 70%, rgba(16, 185, 129, 0.15) 0px, transparent 50%)",
          }}
        />
      </div>

      <AuthWelcomePanel
        badge="بازیابی امن حساب"
        title="نگران نباشید!"
        subtitle="بازگشت به حساب در چند قدم ساده"
        description="فراموشی رمز عبور اتفاق رایجی است. ما با ارسال کد تأیید به شماره تلفن شما، فرآیند بازیابی را امن و سریع انجام می‌دهیم."
        features={welcomeFeatures}
        accentGradient="radial-gradient(at 20% 30%, rgba(245, 158, 11, 0.2) 0px, transparent 50%), radial-gradient(at 80% 70%, rgba(16, 185, 129, 0.2) 0px, transparent 50%), radial-gradient(at 50% 50%, rgba(59, 130, 246, 0.15) 0px, transparent 50%)"
      />

      <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
        <motion.div
          initial={{ opacity: 0, y: 30, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="w-full max-w-md relative"
        >
          <Link
            href="/login"
            className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-emerald-400 transition-colors mb-6"
          >
            <ArrowLeft className="h-4 w-4" />
            بازگشت به ورود
          </Link>

          <div className="flex justify-center mb-6">
            <div className="p-4 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 shadow-[0_0_40px_rgba(245,158,11,0.3)]">
              <Leaf className="h-8 w-8 text-white" />
            </div>
          </div>

          {!isSubmitted ? (
            <>
              <div className="text-center mb-8">
                <div className="inline-flex p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 mb-4">
                  <KeyRound className="h-8 w-8 text-amber-400" />
                </div>
                <h1 className="text-3xl font-black text-white mb-2 tracking-tight">
                  فراموشی رمز عبور
                </h1>
                <p className="text-zinc-400 font-light">
                  شماره تلفن ثبت‌شده خود را وارد کنید
                </p>
              </div>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
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
                      autoFocus
                      className="w-full pr-12 pl-4 py-3.5 bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-amber-500/50 focus:ring-2 focus:ring-amber-500/20 focus:bg-black/40 transition-all text-left"
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

                <div className="p-4 bg-amber-500/5 border border-amber-500/20 rounded-xl">
                  <p className="text-sm text-amber-200/80 leading-relaxed">
                    کد بازیابی از طریق پیامک به شماره شما ارسال خواهد شد. این کد تا ۱۰ دقیقه معتبر است.
                  </p>
                </div>

                <motion.button
                  type="submit"
                  disabled={isSubmitting || forgotPasswordMutation.isPending}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full py-4 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 rounded-xl font-bold text-white transition-all shadow-[0_0_30px_rgba(245,158,11,0.3)] hover:shadow-[0_0_40px_rgba(245,158,11,0.5)] disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting || forgotPasswordMutation.isPending ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      در حال ارسال کد...
                    </span>
                  ) : (
                    "ارسال کد بازیابی"
                  )}
                </motion.button>
              </form>
            </>
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-6"
            >
              <div className="inline-flex p-5 rounded-full bg-emerald-500/10 border border-emerald-500/20 mb-6">
                <CheckCircle className="h-12 w-12 text-emerald-400" />
              </div>

              <h2 className="text-2xl font-black text-white mb-3">
                کد ارسال شد!
              </h2>
              <p className="text-zinc-400 mb-6 leading-relaxed">
                کد بازیابی به شماره
                <br />
                <span className="text-white font-bold font-mono" dir="ltr">{sentPhone}</span>
                <br />
                ارسال شد.
              </p>

              <div className="mb-6 p-4 bg-white/[0.03] border border-white/10 rounded-xl">
                <p className="text-sm text-zinc-400 mb-3">کد ۶ رقمی را وارد کنید:</p>
                <div className="flex gap-2 justify-center" dir="ltr">
                  {[0, 1, 2, 3, 4, 5].map((i) => (
                    <input
                      key={i}
                      type="text"
                      maxLength={1}
                      className="w-12 h-14 text-center text-xl font-bold bg-black/30 border border-white/10 rounded-xl text-white focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all"
                    />
                  ))}
                </div>
              </div>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push("/reset-password")}
                className="w-full py-4 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 rounded-xl font-bold text-white transition-all shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:shadow-[0_0_40px_rgba(16,185,129,0.5)]"
              >
                ادامه و تنظیم رمز جدید
              </motion.button>

              <button
                onClick={() => setIsSubmitted(false)}
                className="mt-4 text-sm text-zinc-400 hover:text-emerald-400 transition-colors"
              >
                ارسال مجدد کد
              </button>
            </motion.div>
          )}

          <div className="mt-8 pt-6 border-t border-white/10 text-center">
            <p className="text-xs text-zinc-500">
              مشکلی دارید؟{" "}
              <Link href="/contact" className="text-emerald-400 hover:underline">
                با پشتیبانی تماس بگیرید
              </Link>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
