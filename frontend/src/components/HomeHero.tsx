import Logo from './Logo'
import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { getApiPrefixSync } from '../api/config'

function BrandSphere() {
  return (
    <div className="relative mx-auto h-16 w-16 rounded-full overflow-hidden shadow-lg">
      <div className="absolute inset-0 bg-gradient-to-br from-sky-400 via-pink-300 to-amber-300" />
      <div className="absolute inset-0 opacity-60 blur-xl bg-[var(--accent)]" />
    </div>
  )
}

function greeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Good Morning'
  if (h < 18) return 'Good Afternoon'
  return 'Good Evening'
}

export default function HomeHero() {
  const [displayName, setDisplayName] = useState<string>('User')

  useEffect(() => {
    let active = true
    ;(async () => {
      try {
        const prefix = getApiPrefixSync()
        const { data } = await api.get(`${prefix}/oauth/me`)
        const name = data?.username || data?.email || 'User'
        if (active) setDisplayName(name)
      } catch {
        // keep default on error
      }
    })()
    return () => { active = false }
  }, [])

  return (
    <div className="text-center space-y-4">
      <div className="flex justify-center"><BrandSphere /></div>
      <h1 className="text-2xl md:text-3xl font-semibold">{greeting()}, {displayName}.</h1>
      <p className="text-[color:var(--muted)] text-lg">Can I help you with anything?</p>
    </div>
  )
}