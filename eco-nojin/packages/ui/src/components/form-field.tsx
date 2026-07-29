"use client";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

type Props = {
  id: string;
  label: string;
  hint?: string;
  error?: string;
  className?: string;
} & React.InputHTMLAttributes<HTMLInputElement>;

export function FormField({ id, label, hint, error, className, ...props }: Props) {
  return (
    <div className={cn("space-y-1.5", className)}>
      <Label htmlFor={id} className="text-slate-300">
        {label}
      </Label>
      <Input
        id={id}
        className={cn(
          "bg-slate-950/60 border-slate-700 focus:border-sky-500/50 focus:ring-sky-500/20 transition-all",
          error && "border-rose-500/50"
        )}
        {...props}
      />
      {hint && !error && <p className="text-xs text-slate-500">{hint}</p>}
      {error && <p className="text-xs text-rose-400">{error}</p>}
    </div>
  );
}
