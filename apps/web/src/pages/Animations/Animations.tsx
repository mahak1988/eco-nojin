/**
 * ============================================================================
 *  Animations — gallery of UI animation patterns (i18n-aware)
 * ============================================================================
 */

import { useState, type ReactNode } from "react";

import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Animation card
// ---------------------------------------------------------------------------

interface AnimationCardProps {
  titleKey: string;
  descriptionKey: string;
  className?: string;
  hoverClasses?: string;
  children: ReactNode;
}

function AnimationCard({ titleKey, descriptionKey, className, hoverClasses, children }: AnimationCardProps): JSX.Element {
  const { t, dir } = useLanguage();
  return (
    <article dir={dir} className="overflow-hidden rounded-xl border border-gray-200 bg-white">
      <div className={cn("flex h-40 items-center justify-center bg-gray-50 transition-all duration-300", hoverClasses)}>
        {children}
      </div>
      <div className="p-4">
        <h3 className="text-sm font-semibold text-gray-900">{t(titleKey)}</h3>
        <p className="mt-1 text-xs leading-5 text-gray-600">{t(descriptionKey)}</p>
        {className && (
          <code className="mt-2 block overflow-x-auto rounded-md bg-gray-900 px-2 py-1 text-xs text-emerald-300" dir="ltr">
            {className}
          </code>
        )}
      </div>
    </article>
  );
}

// ---------------------------------------------------------------------------
// Demos
// ---------------------------------------------------------------------------

function SpinnerDemo(): JSX.Element {
  return <div className="flex h-16 w-16 items-center justify-center rounded-full border-4 border-emerald-100 border-t-emerald-600 animate-spin" />;
}
function PulseDemo(): JSX.Element {
  return <div className="h-16 w-16 animate-pulse rounded-xl bg-emerald-400" />;
}
function BounceDemo(): JSX.Element {
  return <div className="flex h-16 w-16 items-center justify-center rounded-full bg-amber-400 text-3xl animate-bounce">🌱</div>;
}
function PingDemo(): JSX.Element {
  return (
    <div className="relative flex h-16 w-16 items-center justify-center">
      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
      <span className="relative inline-flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500 text-white">!</span>
    </div>
  );
}
function HoverScaleDemo(): JSX.Element {
  return (
    <div className="flex h-16 w-16 cursor-pointer items-center justify-center rounded-xl bg-emerald-500 text-2xl text-white transition-transform duration-200 hover:scale-110">
      📦
    </div>
  );
}
function HoverLiftDemo(): JSX.Element {
  const { t } = useLanguage();
  return (
    <div className="flex h-16 w-32 cursor-pointer items-center justify-center rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 text-sm font-medium text-white transition-all duration-200 hover:-translate-y-1 hover:shadow-lg">
      {t("common.save")}
    </div>
  );
}
function FadeInDemo(): JSX.Element {
  const { t } = useLanguage();
  const [visible, setVisible] = useState(true);
  return (
    <div className="flex flex-col items-center gap-2">
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        className="rounded-md bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700"
      >
        {visible ? t("animations.hide") : t("animations.show")}
      </button>
      <div className={cn("flex h-12 w-32 items-center justify-center rounded-lg bg-emerald-500 text-xs font-medium text-white transition-opacity duration-300", visible ? "opacity-100" : "opacity-0")}>
        FadeIn
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function Animations(): JSX.Element {
  const { t, dir } = useLanguage();
  const tips = [
    "animations.usageTips.loading",
    "animations.usageTips.hoverDuration",
    "animations.usageTips.reducedMotion",
    "animations.usageTips.cautionBounce",
  ];

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("animations.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("animations.subtitle")}</p>
      </header>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <AnimationCard titleKey="animations.spinner" descriptionKey="animations.spinnerDesc" className="animate-spin">
          <SpinnerDemo />
        </AnimationCard>
        <AnimationCard titleKey="animations.pulse" descriptionKey="animations.pulseDesc" className="animate-pulse">
          <PulseDemo />
        </AnimationCard>
        <AnimationCard titleKey="animations.bounce" descriptionKey="animations.bounceDesc" className="animate-bounce">
          <BounceDemo />
        </AnimationCard>
        <AnimationCard titleKey="animations.ping" descriptionKey="animations.pingDesc" className="animate-ping">
          <PingDemo />
        </AnimationCard>
        <AnimationCard titleKey="animations.hoverScale" descriptionKey="animations.hoverScaleDesc" hoverClasses="hover:scale-105" className="hover:scale-110 transition-transform">
          <HoverScaleDemo />
        </AnimationCard>
        <AnimationCard titleKey="animations.hoverLift" descriptionKey="animations.hoverLiftDesc" hoverClasses="hover:-translate-y-1 hover:shadow-xl" className="hover:-translate-y-1 hover:shadow-lg transition-all">
          <HoverLiftDemo />
        </AnimationCard>
        <AnimationCard titleKey="animations.fadeIn" descriptionKey="animations.fadeInDesc" className="transition-opacity duration-300">
          <FadeInDemo />
        </AnimationCard>
      </div>

      <section dir={dir} className="mt-10 rounded-2xl border border-emerald-200 bg-emerald-50 p-6">
        <h2 className="text-base font-semibold text-gray-900">{t("animations.usageTipsTitle")}</h2>
        <ul className="mt-3 space-y-2 text-sm leading-6 text-gray-700">
          {tips.map((tipKey) => (
            <li key={tipKey} className="flex gap-2">
              <span className="text-emerald-600">✓</span>
              <span>{t(tipKey)}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
