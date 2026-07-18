/**
 * ============================================================================
 *  Card — flexible surface container (shadcn-style)
 * ============================================================================
 *
 *  Composable parts:  <Card><CardHeader><CardTitle/><CardDescription/>
 *                     <CardAction/></CardHeader><CardContent/><CardFooter/></Card>
 *
 *  Uses Tailwind logical properties so it flips automatically with RTL/LTR.
 * ============================================================================
 */

import * as React from "react";

import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Root Card
// ---------------------------------------------------------------------------

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { interactive?: boolean }
>(({ className, interactive = false, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-2xl border border-gray-200 bg-white text-gray-900 shadow-sm dark:border-gray-800 dark:bg-gray-900 dark:text-gray-100",
      interactive &&
        "transition duration-200 hover:-translate-y-1 hover:border-emerald-200 hover:shadow-md",
      className,
    )}
    {...props}
  />
));
Card.displayName = "Card";

// ---------------------------------------------------------------------------
// Header / Title / Description / Action
// ---------------------------------------------------------------------------

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-row items-center justify-between gap-3 p-6", className)}
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "flex items-center gap-2 text-base font-semibold leading-none tracking-tight",
      className,
    )}
    {...props}
  />
));
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-gray-500 dark:text-gray-400", className)}
    {...props}
  />
));
CardDescription.displayName = "CardDescription";

// ---------------------------------------------------------------------------
// Content / Footer
// ---------------------------------------------------------------------------

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
));
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center gap-2 p-6 pt-0", className)}
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
};
