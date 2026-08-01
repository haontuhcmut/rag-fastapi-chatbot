import { Navigate, useLocation } from 'react-router-dom'
import { ReactNode, useEffect, useState } from 'react'
import { api } from '../api/client'
import { getApiPrefixSync } from '../api/config'

export default function RequireAdmin({ children }: { children: ReactNode }) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
  const location = useLocation()
  const [status, setStatus] = useState<'loading' | 'allowed' | 'denied'>('loading')

  useEffect(() => {
    let active = true
    async function check() {
      if (!token) {
        setStatus('denied')
        return
      }
      try {
        const prefix = getApiPrefixSync()
        const { data } = await api.get(`${prefix}/oauth/me`)
        const role = data?.role || 'user'
        if (!active) return
        setStatus(role === 'admin' ? 'allowed' : 'denied')
      } catch {
        if (!active) return
        setStatus('denied')
      }
    }
    check()
    return () => { active = false }
  }, [token])

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }
  if (status === 'loading') {
    return (
      <div className="h-full grid place-items-center bg-neutral-950">
        <div className="text-center space-y-4">
          <div className="h-8 w-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-neutral-300">Checking permissions…</p>
        </div>
      </div>
    )
  }
  if (status === 'denied') {
    return <Navigate to="/" replace />
  }
  return <>{children}</>
}