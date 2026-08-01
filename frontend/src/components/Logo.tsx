import { BRAND_NAME } from '../theme/brand'
import BrandMark from './icons/BrandMark'

export default function Logo({ className = '' }: { className?: string }) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <BrandMark size={28} wedge="triple" />
      <span className="text-sm font-semibold text-[var(--text)] flex items-center gap-1">
        {BRAND_NAME}
      </span>
    </div>
  )
}