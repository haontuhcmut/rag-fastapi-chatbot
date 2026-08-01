import { Navigate, useLocation } from 'react-router-dom'
import { ReactNode } from 'react'

export default function RequireAuth({ children }: { children: ReactNode }) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
  const location = useLocation()
  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }
  return <>{children}</>
}


