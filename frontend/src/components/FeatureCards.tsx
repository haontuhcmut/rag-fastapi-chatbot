type CardProps = { title: string; desc: string }

function Card({ title, desc }: CardProps) {
  return (
    <div className="glass rounded-xl p-4 text-left bg-[var(--surface)]/70 border border-[var(--border)]">
      <div className="text-sm font-semibold mb-1.5">{title}</div>
      <div className="text-xs text-[color:var(--muted)]">{desc}</div>
    </div>
  )
}

export default function FeatureCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
      <Card title="Testing Templates" desc="Kick off with pre-made scenarios and flows." />
      <Card title="Analytics" desc="Visualize test outcomes and insights quickly." />
      <Card title="Reports" desc="Share concise summaries across your teams." />
    </div>
  )
}