import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary-600 text-white hover:bg-primary-500",
        secondary: "border-transparent bg-slate-700 text-slate-100 hover:bg-slate-600",
        success: "border-transparent bg-success-500/10 text-success-400 hover:bg-success-500/20",
        warning: "border-transparent bg-warning-500/10 text-warning-400 hover:bg-warning-500/20",
        danger: "border-transparent bg-danger-500/10 text-danger-400 hover:bg-danger-500/20",
        outline: "text-slate-300 border-slate-600",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
