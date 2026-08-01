import { TextareaHTMLAttributes, forwardRef } from 'react'

type Props = TextareaHTMLAttributes<HTMLTextAreaElement>

const Textarea = forwardRef<HTMLTextAreaElement, Props>(function TextareaBase({ className = '', ...props }, ref) {
  return (
    <textarea
      ref={ref}
      className={`w-full rounded-lg bg-[var(--surface)] border border-[var(--border)] px-4 py-3 text-sm placeholder:text-[color:var(--muted)] focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-colors text-[var(--text)] ${className}`}
      {...props}
    />
  )
})

export default Textarea


