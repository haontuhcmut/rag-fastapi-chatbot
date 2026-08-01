type Props = {
  open?: boolean
  size?: number
  className?: string
}

export default function EyeIcon({ open = false, size = 18, className = '' }: Props) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
      focusable="false"
    >
      {open ? (
        // Eye (visible)
        <>
          <path
            d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12Z"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinejoin="round"
          />
          <circle cx="12" cy="12" r="3.25" fill="none" stroke="currentColor" strokeWidth="1.75" />
        </>
      ) : (
        // Eye off (hidden)
        <>
          <path
            d="M1 12s4-7 11-7c2.2 0 4.1.6 5.7 1.5M23 12s-4 7-11 7c-2.2 0-4.1-.6-5.7-1.5"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinejoin="round"
          />
          <circle cx="12" cy="12" r="3.25" fill="none" stroke="currentColor" strokeWidth="1.75" />
          <path d="M4 4l16 16" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
        </>
      )}
    </svg>
  )
}