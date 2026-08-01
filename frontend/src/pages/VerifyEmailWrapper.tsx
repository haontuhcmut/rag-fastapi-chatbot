import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

export default function VerifyEmailWrapper() {
  const { version, token } = useParams<{ version: string; token: string }>()
  const navigate = useNavigate()

  useEffect(() => {
    // Extract token from versioned URL and redirect to simple verify route
    if (token) {
      navigate(`/verify/${token}`, { replace: true })
    } else {
      // If no token, redirect to login
      navigate('/login', { replace: true })
    }
  }, [version, token, navigate])

  // Show loading while redirecting
  return (
    <div className="h-full grid place-items-center bg-neutral-950">
      <div className="text-center space-y-4">
        <div className="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-neutral-300">Redirecting...</p>
      </div>
    </div>
  )
}

