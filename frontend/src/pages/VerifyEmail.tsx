import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { api } from '../api/client'
import { getApiPrefixSync } from '../api/config'
import Button from '../components/ui/Button'

export default function VerifyEmail() {
  const { token } = useParams<{ token: string }>()
  const navigate = useNavigate()
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState<string>('')

  useEffect(() => {
    async function verifyEmail() {
      if (!token) {
        setStatus('error')
        setMessage('Verification token is missing')
        return
      }

      try {
        const prefix = getApiPrefixSync()
        // Token is already URL-safe, don't double-encode
        const response = await api.get(`${prefix}/oauth/verify/${token}`)

        if (response.status === 200) {
          setStatus('success')
          // Backend returns {"message": "Account verified successfully"}
          setMessage(response.data?.message || 'Account verified successfully')
          
          // Redirect to login after 3 seconds
          setTimeout(() => {
            navigate('/login', {
              state: {
                message: 'Email verified successfully! You can now sign in.'
              }
            })
          }, 3000)
        }
      } catch (err: any) {
        setStatus('error')
        const errorData = err?.response?.data
        
        // Backend error responses:
        // - {"message": "Error occurred during verification"} from service
        // - {"message": "User not found", "error_code": "user_not_found"} from UseNotFound exception
        // - FastAPI validation errors as array in detail
        if (errorData?.message) {
          setMessage(errorData.message)
        } else if (errorData?.detail) {
          if (Array.isArray(errorData.detail)) {
            setMessage(errorData.detail[0]?.msg || 'Verification failed')
          } else if (typeof errorData.detail === 'string') {
            setMessage(errorData.detail)
          } else if (errorData.detail?.message) {
            setMessage(errorData.detail.message)
          } else {
            setMessage('Email verification failed. The link may be invalid or expired.')
          }
        } else {
          setMessage('Email verification failed. The link may be invalid or expired.')
        }
      }
    }

    verifyEmail()
  }, [token, navigate])

  return (
    <div className="h-full grid place-items-center bg-gradient-to-br from-neutral-950 via-neutral-900 to-neutral-950 p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <div className="text-4xl mb-4">{status === 'success' ? '✅' : status === 'error' ? '❌' : '⏳'}</div>
          <h1 className="text-2xl font-bold text-neutral-100">Email Verification</h1>
        </div>

        {status === 'loading' && (
          <div className="text-center space-y-4 p-8 rounded-xl border border-neutral-800 bg-neutral-900/50 backdrop-blur-sm shadow-xl">
            <div className="flex items-center justify-center">
              <div className="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p className="text-neutral-300">Verifying your email...</p>
          </div>
        )}

        {status === 'success' && (
          <div className="text-center space-y-4 p-8 rounded-xl border border-green-800/50 bg-green-900/20 backdrop-blur-sm shadow-xl">
            <h2 className="text-xl font-bold text-green-400">Email Verified Successfully!</h2>
            <p className="text-neutral-300">{message}</p>
            <div className="pt-4 space-y-3">
              <p className="text-sm text-neutral-400">
                Redirecting to login page in a few seconds...
              </p>
              <div className="flex flex-col gap-2">
                <Button
                  onClick={() => navigate('/login', {
                    state: {
                      message: 'Email verified successfully! You can now sign in.'
                    }
                  })}
                  className="w-full py-2.5 font-medium bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Go to Login
                </Button>
                <Link
                  to="/login"
                  className="text-sm text-[color:var(--accent)] hover:opacity-80 transition-colors"
                >
                  Or click here to sign in
                </Link>
              </div>
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="text-center space-y-4 p-8 rounded-xl border border-red-200/60 bg-red-100/40 backdrop-blur-sm shadow-xl dark:border-red-800/50 dark:bg-red-900/20">
            <h2 className="text-xl font-bold text-red-600 dark:text-red-400">Verification Failed</h2>
            <p className="text-[color:var(--muted)]">{message}</p>
            <div className="pt-4 space-y-3">
              <div className="flex flex-col gap-2">
                <Button
                  onClick={() => navigate('/login')}
                  className="w-full py-2.5 font-medium bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Go to Login
                </Button>
                <Link
                  to="/signup"
                  className="text-sm text-[color:var(--accent)] hover:opacity-80 transition-colors"
                >
                  Sign up for a new account
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

