import { InputHTMLAttributes, forwardRef } from 'react'

type Props = InputHTMLAttributes<HTMLInputElement>

const Input = forwardRef<HTMLInputElement, Props>(function InputBase({ className = '', ...props }, ref) {
  return (
    <input
      ref={ref}
      className={`w-full rounded-lg bg-[var(--surface)] border border-[var(--border)] px-4 py-2.5 text-sm placeholder:text-[color:var(--muted)] focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-colors text-[var(--text)] disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      {...props}
    />
  )
})

export default Input


