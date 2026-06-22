"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function BackButton({
  fallbackHref = "/models",
  className = "",
  label = "بازگشت",
}: {
  fallbackHref?: string;
  className?: string;
  label?: string;
}) {
  const router = useRouter();

  return (
    <button
      type="button"
      onClick={() => router.back()}
      className={`inline-flex items-center gap-2 text-sm text-emerald-400 hover:text-emerald-300 transition-colors ${className}`}
      aria-label={label}
    >
      <ArrowRight className="w-4 h-4 rotate-180" />
      <span>{label}</span>
    </button>
  );
}
