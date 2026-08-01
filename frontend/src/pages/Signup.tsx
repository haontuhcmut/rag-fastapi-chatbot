import { useState } from 'react'
import { Link } from 'react-router-dom'
import { postAuth } from '../api/client'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'

export default function Signup() {
  const [form, setForm] = useState({
    email: '',
    username: '',
    first_name: '',
    last_name: '',
    password: '',
    confirm_password: '',
  })
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [passwordErrors, setPasswordErrors] = useState<string[]>([])

  function validatePassword(password: string): string[] {
    const errors: string[] = []
    if (password.length < 8) {
      errors.push('At least 8 characters')
    }
    if (!/[A-Z]/.test(password)) {
      errors.push('One uppercase letter')
    }
    if (!/[a-z]/.test(password)) {
      errors.push('One lowercase letter')
    }
    if (!/\d/.test(password)) {
      errors.push('One digit')
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push('One special character')
    }
    return errors
  }

  function validateForm() {
    // Clear password errors first
    setPasswordErrors([])
    
    // Validate password requirements
    const pwdErrors = validatePassword(form.password)
    if (pwdErrors.length > 0) {
      setPasswordErrors(pwdErrors)
      setError(`Password must contain: ${pwdErrors.join(', ')}`)
      return false
    }

    if (form.password !== form.confirm_password) {
      setError('Passwords do not match')
      return false
    }

    return true
  }

  function handlePasswordChange(value: string) {
    // Limit to 64 characters to match backend max_length
    const limitedValue = value.slice(0, 64)
    setForm((p) => ({ ...p, password: limitedValue }))
    if (limitedValue.length > 0) {
      setPasswordErrors(validatePassword(limitedValue))
    } else {
      setPasswordErrors([])
    }
    // Clear error if password changes
    if (error) setError(null)
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setMessage(null)
    
    if (!validateForm()) return
    
    setLoading(true)
    try {
      await postAuth('/oauth/signup', form)
      setMessage('Account created successfully! Please check your email to verify your account.')
      // Reset form on success
      setForm({
        email: '',
        username: '',
        first_name: '',
        last_name: '',
        password: '',
        confirm_password: '',
      })
      setPasswordErrors([])
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Signup failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const formValid = 
    form.email && 
    form.username && 
    form.first_name && 
    form.last_name && 
    form.password && 
    form.confirm_password &&
    passwordErrors.length === 0 &&
    form.password === form.confirm_password

  return (
    <div className="h-full grid place-items-center bg-[var(--bg)] p-4 overflow-auto">
      <div className="w-full max-w-lg space-y-6 my-8">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold text-[var(--text)]">Create your account</h1>
          <p className="text-[color:var(--muted)] text-sm">Sign up to get started with your chatbot</p>
        </div>
        <form onSubmit={onSubmit} className="w-full grid gap-4 p-8 rounded-xl border border-[var(--border)] bg-[var(--surface)] backdrop-blur-sm shadow-xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-[color:var(--muted)] mb-1.5">
                First Name
              </label>
              <Input 
                placeholder="John" 
                value={form.first_name}
                onChange={(e) => {
                  const value = e.target.value.slice(0, 32)
                  setForm((p) => ({ ...p, first_name: value }))
                }}
                maxLength={32}
                disabled={loading}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[color:var(--muted)] mb-1.5">
                Last Name
              </label>
              <Input 
                placeholder="Doe" 
                value={form.last_name}
                onChange={(e) => {
                  const value = e.target.value.slice(0, 32)
                  setForm((p) => ({ ...p, last_name: value }))
                }}
                maxLength={32}
                disabled={loading}
                required
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-[color:var(--muted)] mb-1.5">
              Username
            </label>
            <Input 
              placeholder="johndoe" 
              value={form.username}
              onChange={(e) => {
                const value = e.target.value.slice(0, 32)
                setForm((p) => ({ ...p, username: value }))
              }}
              maxLength={32}
              required
              disabled={loading}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[color:var(--muted)] mb-1.5">
              Email
            </label>
            <Input 
              type="email"
              placeholder="john@example.com" 
              value={form.email}
              onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
              required
              disabled={loading}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[color:var(--muted)] mb-1.5">
              Password
            </label>
            <Input 
              type="password" 
              placeholder="Min 8 chars: uppercase, lowercase, digit, special char" 
              value={form.password}
              onChange={(e) => handlePasswordChange(e.target.value)}
              maxLength={64}
              required
              disabled={loading}
            />
            {form.password.length > 0 && passwordErrors.length > 0 && (
              <div className="mt-2 space-y-1">
                <p className="text-xs text-[color:var(--muted)] mb-1">Password must contain:</p>
                <ul className="text-xs space-y-0.5 text-red-400">
                  {passwordErrors.map((err, i) => (
                    <li key={i} className="flex items-center gap-1">
                      <span className="text-red-500">✗</span> {err}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {form.password.length > 0 && passwordErrors.length === 0 && (
              <div className="mt-2 text-xs text-green-600 dark:text-green-400 flex items-center gap-1">
                <span>✓</span> Password meets all requirements
              </div>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-[color:var(--muted)] mb-1.5">
              Confirm Password
            </label>
            <Input 
              type="password" 
              placeholder="Re-enter your password" 
              value={form.confirm_password}
              onChange={(e) => {
                setForm((p) => ({ ...p, confirm_password: e.target.value }))
                if (error && error === 'Passwords do not match') setError(null)
              }}
              required
              disabled={loading}
            />
            {form.confirm_password.length > 0 && form.password !== form.confirm_password && (
              <p className="mt-1 text-xs text-red-600 dark:text-red-400">Passwords do not match</p>
            )}
            {form.confirm_password.length > 0 && form.password === form.confirm_password && form.password.length > 0 && (
              <p className="mt-1 text-xs text-green-600 dark:text-green-400">Passwords match</p>
            )}
          </div>
          {error && (
            <div className="text-sm text-red-600 bg-red-100/40 px-4 py-3 rounded-lg border border-red-200/60 dark:text-red-400 dark:bg-red-900/20 dark:border-red-800/50">
              {error}
            </div>
          )}
          {message && (
            <div className="text-sm text-green-600 bg-green-100/40 px-4 py-3 rounded-lg border border-green-200/60 dark:text-green-400 dark:bg-green-900/20 dark:border-green-800/50">
              {message}
            </div>
          )}
          <Button 
            type="submit" 
            className="w-full py-2.5 font-medium bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50"
            disabled={loading || !formValid}
          >
            {loading ? 'Creating account...' : 'Sign up'}
          </Button>
          <div className="text-center text-sm text-[color:var(--muted)]">
            Already have an account?{' '}
            <Link to="/login" className="text-[color:var(--accent)] hover:opacity-80 font-medium transition-colors">
              Sign in
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}


