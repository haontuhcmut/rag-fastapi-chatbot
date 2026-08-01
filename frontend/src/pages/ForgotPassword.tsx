import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { postAuth } from '../api/client'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState<string>('')
  const navigate = useNavigate()

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setStatus('loading')
    setMessage('')

    try {
      const response = await postAuth('/oauth/reset-password-request', { email })
      
      if (response.status === 200) {
        setStatus('success')
        setMessage(
          response.data?.message || 
          'If an account exists with this email, you will receive password reset instructions.'
        )
      }
    } catch (err: any) {
      setStatus('error')
      // Don't reveal if email exists or not for security
      setMessage(
        'If an account exists with this email, you will receive password reset instructions.'
      )
    }
  }

  return (
    <div className="h-full grid place-items-center bg-[var(--bg)] p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <div className="text-4xl mb-4">🔑</div>
          <h1 className="text-2xl font-bold text-[var(--text)]">Reset Your Password</h1>
          <p className="text-[color:var(--muted)] text-sm">
            Enter your email address and we'll send you a link to reset your password
          </p>
        </div>

        {status === 'success' ? (
          <div className="w-full grid gap-4 p-8 rounded-xl border border-green-200/60 bg-green-100/40 backdrop-blur-sm shadow-xl dark:border-green-800/50 dark:bg-green-900/20">
            <div className="text-center space-y-4">
              <div className="text-6xl mb-4">✅</div>
              <h2 className="text-xl font-bold text-green-600 dark:text-green-400">Email Sent!</h2>
              <p className="text-[color:var(--muted)]">{message}</p>
              <div className="pt-4 space-y-3">
                <Button
                  onClick={() => navigate('/login')}
                  className="w-full py-2.5 font-medium bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Back to Login
                </Button>
                <Link
                  to="/login"
                  className="block text-sm text-[color:var(--accent)] hover:opacity-80 transition-colors text-center"
                >
                  Return to sign in
                </Link>
              </div>
            </div>
          </div>
        ) : (
          <form onSubmit={onSubmit} className="w-full grid gap-4 p-8 rounded-xl border border-[var(--border)] bg-[var(--surface)] backdrop-blur-sm shadow-xl">
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
                disabled={status === 'loading'}
              />
            </div>

            {status === 'error' && message && (
              <div className="text-sm text-amber-600 bg-amber-100/40 px-4 py-3 rounded-lg border border-amber-200/60 dark:text-amber-400 dark:bg-amber-900/20 dark:border-amber-800/50">
                {message}
              </div>
            )}

            <Button
              type="submit"
              className="w-full py-2.5 font-medium bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50"
              disabled={status === 'loading' || !email.trim()}
            >
              {status === 'loading' ? 'Sending...' : 'Send Reset Link'}
            </Button>

            <div className="text-center text-sm text-[color:var(--muted)]">
              Remember your password?{' '}
              <Link to="/login" className="text-[color:var(--accent)] hover:opacity-80 font-medium transition-colors">
                Sign in
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}

