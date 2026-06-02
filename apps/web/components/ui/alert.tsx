import * as React from 'react'

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'destructive'
}

export function Alert({
  variant = 'default',
  className = '',
  ...props
}: AlertProps) {
  const variantStyles =
    variant === 'destructive'
      ? 'border-red-500/40 bg-red-500/10 text-red-100'
      : 'border-slate-700/80 bg-slate-800/80 text-slate-100'

  return (
    <div className={`rounded-2xl border p-4 ${variantStyles} ${className}`} {...props} />
  )
}

export function AlertDescription({ className = '', ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={`text-sm text-slate-200 ${className}`} {...props} />
}
