import { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { postAuth, setAccessToken, setRefreshToken } from '../api/client'
import BrandMark from '../components/icons/BrandMark'
import EyeIcon from '../components/icons/Eye'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    // Check if we have a success message from verification redirect
    if (location.state?.message) {
      setSuccessMessage(location.state.message)
      // Clear the state to prevent showing the message again on refresh
      navigate(location.pathname, { replace: true, state: {} })
    }
  }, [location, navigate])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      // Try both versioned and root auth endpoints
      const { data } = await postAuth('/oauth/login', { email, password })
      const access = data?.access_token ?? data?.accessToken ?? ''
      const refresh = data?.refresh_token ?? data?.refreshToken ?? ''
      setAccessToken(access)
      setRefreshToken(refresh)
      navigate('/')
    } catch (err: any) {
      const status = err?.response?.status
      const payload = err?.response?.data
      // Backend returns { message, error_code } for errors
      if (status === 401) {
        setError(payload?.message || 'Incorrect email or password')
      } else {
        // Fallback to any message/detail provided, else generic
        setError(payload?.message || payload?.detail || 'Login failed. Please check your credentials.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-full grid place-items-center bg-[var(--bg)] p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-3">
          <div className="flex justify-center">
            <div className="h-12 w-12 rounded-lg bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center shadow-sm">
              <BrandMark size={28}/>
            </div>
          </div>
          <h1 className="text-2xl font-bold text-[var(--text)]"> FPT Chatbot Login</h1>
          <p className="text-[color:var(--muted)] text-sm">Please sign in to continue and connect with your intelligent assistant.</p>
        </div>
        <form onSubmit={onSubmit} className="w-full grid gap-4 p-8 rounded-xl border border-[var(--border)] bg-[var(--surface)] backdrop-blur-sm shadow-xl">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[color:var(--muted)] mb-1.5">
                Email
              </label>
              <Input 
                type="email"
                placeholder="Enter your email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
                disabled={loading}
              />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-sm font-medium text-[color:var(--muted)]">
                  Password
                </label>
                <Link 
                  to="/forgot-password" 
                  className="text-xs text-[color:var(--accent)] hover:opacity-80 transition-colors"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <Input 
                  type={showPassword ? 'text' : 'password'} 
                  placeholder="Enter your password" 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={loading}
                  className="pr-20"
                  aria-describedby="password-visibility-toggle"
                />
                <button
                  id="password-visibility-toggle"
                  type="button"
                  onClick={() => setShowPassword(v => !v)}
                  disabled={loading}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-md bg-transparent text-[color:var(--muted)] hover:text-[var(--text)] hover:bg-[var(--surface)]"
                  aria-pressed={showPassword}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  <EyeIcon open={showPassword} size={18} />
                </button>
              </div>
            </div>
          </div>
          {successMessage && (
            <div className="text-sm text-green-600 bg-green-100/40 px-4 py-3 rounded-lg border border-green-200/60 dark:text-green-400 dark:bg-green-900/20 dark:border-green-800/50">
              {successMessage}
            </div>
          )}
          {error && (
            <div className="text-sm text-red-600 bg-red-100/40 px-4 py-3 rounded-lg border border-red-200/60 dark:text-red-400 dark:bg-red-900/20 dark:border-red-800/50">
              {error}
            </div>
          )}
          <Button 
            type="submit" 
            className="w-full py-2.5 font-medium bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50"
            disabled={loading || !email.trim() || !password.trim()}
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </Button>
          <div className="text-center text-sm text-neutral-400">
            Don't have an account?{' '}
            <Link to="/signup" className="text-[color:var(--accent)] hover:opacity-80 font-medium transition-colors">
              Sign up
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}



