import Button from './ui/Button'

function MicIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} {...props}>
      <rect x="9" y="3" width="6" height="10" rx="3" />
      <path d="M5 10a7 7 0 0 0 14 0M12 17v4M8 21h8" />
    </svg>
  )
}

function ImageIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} {...props}>
      <rect x="3" y="3" width="18" height="18" rx="3" />
      <circle cx="8" cy="8" r="2.5" />
      <path d="M21 15l-4-4-6 6" />
    </svg>
  )
}

function GlobeIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18" />
    </svg>
  )
}

export default function QuickActions() {
  return (
    <div className="space-y-3">
      <div className="glass rounded-2xl border border-[var(--border)] bg-[var(--surface)]/70">
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="flex-1 min-w-0 text-[color:var(--muted)]">Message AI Chat…</div>
          <button className="h-8 w-8 rounded-lg grid place-items-center text-[color:var(--muted)] hover:text-[var(--text)]">
            <MicIcon className="h-4 w-4" />
          </button>
        </div>
        <div className="flex items-center gap-2 px-4 pb-3">
          <Button variant="secondary" className="px-2.5 py-1.5 text-xs"><ImageIcon className="h-4 w-4 mr-1.5" />Create an image</Button>
          <Button variant="secondary" className="px-2.5 py-1.5 text-xs"><GlobeIcon className="h-4 w-4 mr-1.5" />Search the web</Button>
        </div>
      </div>
    </div>
  )
}