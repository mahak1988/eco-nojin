/**
 * ════════════════════════════════════════════════════════
 *  EcoButton — دکمه‌های سبز/عسلی Econojin
 *  Wrapper دور shadcn Button با variantهای اختصاصی
 * ═══════════════════════════════════════════════════════
 */

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Slot } from "radix-ui";

const ecoVariants = {
  primary: "btn-eco text-sm md:text-base h-auto py-2.5 md:py-3 px-5 md:px-7",
  outline: "btn-eco-outline text-sm md:text-base h-auto py-2.5 md:py-3 px-5 md:px-7",
  ghost: "btn-eco-ghost text-sm md:text-base h-auto py-2 md:py-2.5 px-4",
  earth: "btn-earth text-sm md:text-base h-auto py-2.5 md:py-3 px-5 md:px-7",
  hero: "btn-eco text-base md:text-lg h-auto py-3.5 md:py-4 px-8 md:px-10 rounded-xl shadow-eco-lg hover:shadow-eco-xl",
} as const;

export interface EcoButtonProps extends React.ComponentProps<"button"> {
  variant?: keyof typeof ecoVariants;
  asChild?: boolean;
  className?: string;
}

export function EcoButton({
  variant = "primary",
  className,
  children,
  ...props
}: EcoButtonProps) {
  return (
    <Button
      className={cn(ecoVariants[variant], "group/eco-btn", className)}
      {...props}
    >
      {children}
    </Button>
  );
}
