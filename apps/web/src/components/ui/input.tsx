/**
 * ============================================================================
 *  Input / Textarea / Label — form primitives with consistent styling
 * ============================================================================
 *
 *  All fields use Tailwind logical properties (ps/pe/start/end) so they
 *  flip correctly with RTL/LTR. Error state uses rose accent.
 * ============================================================================
 */

import * as React from "react";

import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Input
// ---------------------------------------------------------------------------

export type InputSize = "sm" | "md" | "lg";

const INPUT_SIZE_CLASS: Record<InputSize, string> = {
  sm: "h-8 px-2.5 text-xs",
  md: "h-10 px-3 text-sm",
  lg: "h-12 px-4 text-base",
};

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  invalid?: boolean;
  inputSize?: InputSize;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, invalid = false, inputSize = "md", ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "w-full rounded-lg border bg-white text-gray-900 placeholder:text-gray-400",
        "outline-none transition focus:ring-2 focus:ring-emerald-500/20",
        invalid
          ? "border-rose-400 focus:border-rose-500 focus:ring-rose-500/20"
          : "border-gray-200 focus:border-emerald-500",
        INPUT_SIZE_CLASS[inputSize],
        className,
      )}
      aria-invalid={invalid || undefined}
      {...props}
    />
  ),
);
Input.displayName = "Input";

// ---------------------------------------------------------------------------
// Textarea
// ---------------------------------------------------------------------------

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  invalid?: boolean;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, invalid = false, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(
        "w-full rounded-lg border bg-white px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400",
        "outline-none transition focus:ring-2 focus:ring-emerald-500/20",
        invalid
          ? "border-rose-400 focus:border-rose-500 focus:ring-rose-500/20"
          : "border-gray-200 focus:border-emerald-500",
        className,
      )}
      aria-invalid={invalid || undefined}
      {...props}
    />
  ),
);
Textarea.displayName = "Textarea";

// ---------------------------------------------------------------------------
// Label
// ---------------------------------------------------------------------------

export interface LabelProps
  extends React.LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean;
}

export function Label({
  children,
  required = false,
  className,
  ...props
}: LabelProps): JSX.Element {
  return (
    <label
      className={cn(
        "block text-sm font-medium text-gray-700",
        className,
      )}
      {...props}
    >
      {children}
      {required && <span className="ms-0.5 text-rose-500">*</span>}
    </label>
  );
}

// ---------------------------------------------------------------------------
// FieldError — small helper to render validation messages
// ---------------------------------------------------------------------------

export interface FieldErrorProps {
  children?: React.ReactNode;
  className?: string;
}

export function FieldError({ children, className }: FieldErrorProps): JSX.Element | null {
  if (!children) return null;
  return (
    <p className={cn("mt-1 text-xs text-rose-600", className)} role="alert">
      {children}
    </p>
  );
}

export default Input;
