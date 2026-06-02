import { Slot } from '@radix-ui/react-slot'
import * as React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline'
  asChild?: boolean
}

export function Button({
  variant = 'primary',
  asChild = false,
  className = '',
  ...props
}: ButtonProps) {
  const Component = asChild ? Slot : 'button'
  const base = 'inline-flex items-center justify-center rounded-full px-5 py-2 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400'
  const variantClasses =
    variant === 'secondary'
      ? 'bg-slate-800 text-slate-100 hover:bg-slate-700'
      : variant === 'outline'
      ? 'border border-slate-700 bg-transparent text-slate-100 hover:bg-slate-950/80'
      : 'bg-sky-600 text-white hover:bg-sky-500'

  return <Component className={`${base} ${variantClasses} ${className}`} {...props} />
}
