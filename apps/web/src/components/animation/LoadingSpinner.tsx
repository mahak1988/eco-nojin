import { cn } from "../../lib/cn";

type SpinnerVariant = "default" | "dots" | "pulse" | "ring" | "gradient" | "eco";
type SpinnerSize = "xs" | "sm" | "md" | "lg" | "xl";

const SIZE_MAP: Record<SpinnerSize, string> = {
  xs: "h-4 w-4",
  sm: "h-6 w-6",
  md: "h-10 w-10",
  lg: "h-16 w-16",
  xl: "h-24 w-24",
};

interface Props {
  variant?: SpinnerVariant;
  size?: SpinnerSize;
  className?: string;
  label?: string;
}

function DefaultSpinner({ size, className }: { size: SpinnerSize; className?: string }) {
  return (
    <div
      className={cn(
        SIZE_MAP[size],
        "animate-spin rounded-full border-2 border-stone-200 border-t-emerald-600",
        className
      )}
    />
  );
}

function DotsSpinner({ size, className }: { size: SpinnerSize; className?: string }) {
  const dotSize = size === "xs" ? "h-1.5 w-1.5" : size === "sm" ? "h-2 w-2" : size === "lg" ? "h-4 w-4" : size === "xl" ? "h-5 w-5" : "h-3 w-3";
  return (
    <div className={cn("flex items-center gap-1.5", className)}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={cn(dotSize, "rounded-full bg-emerald-500 animate-bounce-custom")}
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  );
}

function PulseSpinner({ size, className }: { size: SpinnerSize; className?: string }) {
  return (
    <div className={cn(SIZE_MAP[size], "relative", className)}>
      <div className="absolute inset-0 animate-ping rounded-full bg-emerald-400 opacity-25" />
      <div className="relative h-full w-full rounded-full bg-emerald-500" />
    </div>
  );
}

function RingSpinner({ size, className }: { size: SpinnerSize; className?: string }) {
  return (
    <svg
      className={cn(SIZE_MAP[size], "animate-spin", className)}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" opacity="0.2" />
      <path
        d="M12 2a10 10 0 0 1 10 10"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        className="text-emerald-500"
      />
    </svg>
  );
}

function GradientSpinner({ size, className }: { size: SpinnerSize; className?: string }) {
  return (
    <div
      className={cn(
        SIZE_MAP[size],
        "animate-spin rounded-full border-[3px] border-transparent",
        className
      )}
      style={{
        background: "conic-gradient(from 0deg, #10b981, #3b82f6, #8b5cf6, #10b981)",
        WebkitMask: "radial-gradient(farthest-side, transparent calc(100% - 3px), #000 0)",
        mask: "radial-gradient(farthest-side, transparent calc(100% - 3px), #000 0)",
      } as React.CSSProperties}
    />
  );
}

function EcoSpinner({ size, className }: { size: SpinnerSize; className?: string }) {
  return (
    <div className={cn("flex flex-col items-center gap-2", className)}>
      <svg
        className={cn(SIZE_MAP[size], "animate-spin text-emerald-500")}
        viewBox="0 0 24 24"
        fill="none"
      >
        <path
          d="M2 12C2 6.48 6.48 2 12 2s10 4.48 10 10-4.48 10-10 10"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.25"
        />
        <path
          d="M12 2c5.52 0 10 4.48 10 10"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
      <span className="text-xs text-stone-500 font-medium">Econojin</span>
    </div>
  );
}

export default function LoadingSpinner({ variant = "default", size = "md", className, label }: Props) {
  return (
    <div role="status" className="flex flex-col items-center justify-center gap-2">
      {variant === "default" && <DefaultSpinner size={size} className={className} />}
      {variant === "dots" && <DotsSpinner size={size} className={className} />}
      {variant === "pulse" && <PulseSpinner size={size} className={className} />}
      {variant === "ring" && <RingSpinner size={size} className={className} />}
      {variant === "gradient" && <GradientSpinner size={size} className={className} />}
      {variant === "eco" && <EcoSpinner size={size} className={className} />}
      {label && <span className="text-sm text-stone-500">{label}</span>}
      <span className="sr-only">Loading...</span>
    </div>
  );
}
