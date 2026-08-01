import { ButtonHTMLAttributes } from 'react'

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
}

export default function Button({ className = '', variant = 'primary', ...props }: Props) {
  const base = 'inline-flex items-center justify-center rounded-lg text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[var(--bg)] disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]'
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500 shadow-lg shadow-blue-600/20',
    secondary: 'bg-[var(--surface)] hover:opacity-90 text-[var(--text)] focus:ring-neutral-600 border border-[var(--border)]',
    ghost: 'bg-transparent hover:bg-[var(--surface)] text-[color:var(--muted)] focus:ring-neutral-600',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
  } as const
  return (
    <button {...props} className={`${base} ${variants[variant]} ${className}`} />
  )
}


