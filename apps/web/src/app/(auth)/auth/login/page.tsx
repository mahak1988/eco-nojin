"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { loginSchema, type LoginInput } from "@/lib/validation/auth.schema";
import { useAuth } from "@/lib/api/hooks/useAuth";
import { motion } from "framer-motion";

export default function LoginPage() {
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
  });

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      toast.success("ورود موفقیت‌آمیز!");
      window.location.href = "/dashboard";
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  const onSubmit = (data: LoginInput) => {
    loginMutation.mutate(data);
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-6">
      {/* Ambient Background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div className="absolute inset-0 opacity-40" style={{
          backgroundImage: `
            radial-gradient(at 20% 20%, rgba(16, 185, 129, 0.2) 0px, transparent 50%),
            radial-gradient(at 80% 80%, rgba(59, 130, 246, 0.15) 0px, transparent 50%)
          `
        }} />
      </div>

      {/* Login Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md bg-white/[0.03] backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-2xl"
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl font-black text-white mb-2">ورود به اکو نوژین</h1>
          <p className="text-zinc-400">به خانواده احیای زمین بپیوندید</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Farmer ID */}
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">
              شناسه کشاورز
            </label>
            <input
              {...register("fid")}
              placeholder="F001"
              className="w-full px-4 py-3 bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 transition-all"
            />
            {errors.fid && (
              <p className="mt-2 text-sm text-rose-400">{errors.fid.message}</p>
            )}
          </div>

          {/* Phone */}
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">
              شماره تلفن
            </label>
            <input
              {...register("phone")}
              placeholder="+989123456789"
              className="w-full px-4 py-3 bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 transition-all"
            />
            {errors.phone && (
              <p className="mt-2 text-sm text-rose-400">{errors.phone.message}</p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-4 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 rounded-xl font-bold text-white transition-all shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:shadow-[0_0_40px_rgba(16,185,129,0.5)] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                در حال ورود...
              </span>
            ) : (
              "ورود"
            )}
          </button>
        </form>
      </motion.div>
    </div>
  );
}