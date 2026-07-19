import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Leaf, Shield, Sparkles, Waves } from 'lucide-react';

import { Layout } from '@/components/Layout/Layout';
import { TypographicLogo } from '@/components/common/TypographicLogo';
import { useAuth } from '@/hooks/useAuth';
import { useLanguage } from '@/hooks/useLanguage';

export default function Home() {
  const { isAuthenticated } = useAuth();
  const { t, dir } = useLanguage();

  return (
    <Layout>
      <div dir={dir} className="relative min-h-screen bg-white dark:bg-gray-950">
        {/* Hero Section */}
        <section className="relative flex min-h-[80vh] flex-col items-center justify-center px-4 py-20">
          <div className="pointer-events-none absolute inset-0 overflow-hidden">
            <div className="absolute -start-20 top-20 h-72 w-72 rounded-full bg-emerald-400/20 blur-3xl" />
            <div className="absolute bottom-0 end-0 h-96 w-96 rounded-full bg-teal-300/15 blur-3xl" />
          </div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="relative z-10 text-center"
          >
            <TypographicLogo size="xl" className="mx-auto mb-8" />
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white sm:text-5xl">
              {t("common.appTagline") || "EcoNojin"}
            </h1>
            <p className="mt-4 max-w-lg text-lg text-gray-600 dark:text-gray-300">
              {t("home.hero.subtitle") || "پلتفرم جامع محیط‌زیست با همزاد دیجیتال HydroMa Nojin"}
            </p>

            {!isAuthenticated && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="mt-8"
              >
                <Link
                  to="/login"
                  className="inline-block rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-8 py-3.5 text-sm font-semibold text-white shadow-lg shadow-emerald-200 transition hover:from-emerald-700 hover:to-teal-700 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
                >
                  {t("home.hero.cta") || "شروع کنید"}
                </Link>
              </motion.div>
            )}
          </motion.div>

          {/* Features Grid */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="relative mt-16 grid gap-6 sm:grid-cols-3 max-w-3xl"
          >
            {[
              { icon: Sparkles, label: t("home.features.items.ai.title") || "هوش مصنوعی", desc: t("home.features.items.ai.desc") || "تحلیل‌های پیشرفته" },
              { icon: Waves, label: t("home.features.items.gis.title") || "سامانه GIS", desc: t("home.features.items.gis.desc") || "نقشه‌برداری دقیق" },
              { icon: Shield, label: t("home.features.items.alert.title") || "هشداردهنده", desc: t("home.features.items.alert.desc") || "هشدارهای لحظه‌ای" },
            ].map(({ icon: Icon, label, desc }, i) => (
              <div
                key={label}
                className="flex flex-col items-center rounded-2xl border border-gray-100 bg-white/80 p-6 text-center backdrop-blur-sm dark:border-gray-800 dark:bg-gray-900/80"
              >
                <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400">
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white">{label}</h3>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{desc}</p>
              </div>
            ))}
          </motion.div>
        </section>
      </div>
    </Layout>
  );
}
