import { useEffect, useState } from 'react'
import { useParams, useLocation } from 'react-router-dom'
import PasswordReset from './PasswordReset'

export default function PasswordResetWrapper() {
  const { version, token } = useParams<{ version: string; token: string }>()
  const location = useLocation()
  const [extractedToken, setExtractedToken] = useState<string | null>(null)

  useEffect(() => {
    // Extract token from versioned URL
    // Try to get token from params first, if not available, try to extract from pathname
    let resetToken = token
    
    if (!resetToken && location.pathname) {
      // Extract token from pathname if params didn't work
      // Path format: /v1/password-reset-confirm/{token}
      const match = location.pathname.match(/password-reset-confirm\/(.+?)(?:\?|$)/)
      if (match && match[1]) {
        resetToken = match[1]
      }
    }

    if (resetToken && resetToken.trim()) {
      // Decode the token if needed, then set it
      try {
        const decoded = decodeURIComponent(resetToken)
        setExtractedToken(decoded)
      } catch {
        // If decode fails, use original
        setExtractedToken(resetToken)
      }
    }
  }, [version, token, location])

  // If we have a token, render PasswordReset component directly with the token
  // This avoids an extra redirect and shows the UI immediately
  if (extractedToken) {
    // Use React Router's Navigate to pass the token, but we'll render directly
    return <PasswordReset tokenFromWrapper={extractedToken} />
  }

  // Show loading while extracting token
  return (
    <div className="h-full grid place-items-center bg-[var(--bg)]">
      <div className="text-center space-y-4">
        <div className="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-[color:var(--muted)]">Loading password reset form...</p>
      </div>
    </div>
  )
}

