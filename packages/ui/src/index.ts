import * as React from 'react'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary'
}

export function Button({ variant = 'primary', className = '', ...props }: ButtonProps) {
  const base = 'inline-flex items-center justify-center rounded-full px-5 py-2 text-sm font-semibold transition'
  const variantClasses =
    variant === 'secondary'
      ? 'bg-slate-800 text-slate-100 hover:bg-slate-700'
      : 'bg-sky-600 text-white hover:bg-sky-500'

  return <button className={`${base} ${variantClasses} ${className}`} {...props} />
}
