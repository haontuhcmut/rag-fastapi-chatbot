import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom'
import { postAuth } from '../api/client'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'

// Password validation matching backend requirements
function validatePassword(password: string): string[] {
  const errors: string[] = []
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters.')
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('Must contain at least one uppercase letter.')
  }
  if (!/[a-z]/.test(password)) {
    errors.push('Must contain at least one lowercase letter.')
  }
  if (!/\d/.test(password)) {
    errors.push('Must contain at least one digit.')
  }
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Must contain at least one special character.')
  }
  return errors
}

interface PasswordResetProps {
  tokenFromWrapper?: string
}

export default function PasswordReset({ tokenFromWrapper }: PasswordResetProps = {}) {
  const { token: tokenFromRoute } = useParams<{ token: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState<string>('')
  const [errors, setErrors] = useState<{ newPassword?: string; confirmPassword?: string }>({})
  const [passwordErrors, setPasswordErrors] = useState<string[]>([])

  // Use token from wrapper if provided, otherwise from route params
  const token = tokenFromWrapper || tokenFromRoute

  // Debug: Log token on mount
  useEffect(() => {
    console.log('PasswordReset component loaded:', { token, tokenFromWrapper, tokenFromRoute, pathname: location.pathname })
  }, [token, tokenFromWrapper, tokenFromRoute, location])

  // Validate password on change
  useEffect(() => {
    if (newPassword) {
      const validationErrors = validatePassword(newPassword)
      setPasswordErrors(validationErrors)
      setErrors(prev => ({ 
        ...prev, 
        newPassword: validationErrors.length > 0 ? validationErrors[0] : undefined 
      }))
    } else {
      setPasswordErrors([])
      setErrors(prev => ({ ...prev, newPassword: undefined }))
    }
  }, [newPassword])

  // Validate passwords match
  useEffect(() => {
    if (confirmPassword && newPassword !== confirmPassword) {
      setErrors(prev => ({ ...prev, confirmPassword: 'Passwords do not match.' }))
    } else if (confirmPassword) {
      setErrors(prev => ({ ...prev, confirmPassword: undefined }))
    }
  }, [newPassword, confirmPassword])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setStatus('loading')
    setMessage('')
    setErrors({})

    if (!token) {
      setStatus('error')
      setMessage('Reset token is missing')
      return
    }

    // Client-side validation matching backend
    const validationErrors = validatePassword(newPassword)
    if (validationErrors.length > 0) {
      setStatus('error')
      setPasswordErrors(validationErrors)
      setErrors({ newPassword: validationErrors[0] })
      setMessage(validationErrors[0])
      return
    }

    if (newPassword !== confirmPassword) {
      setStatus('error')
      setErrors({ confirmPassword: 'Passwords do not match.' })
      setMessage('Passwords do not match.')
      return
    }

    try {
      const encodedToken = encodeURIComponent(token)
      const response = await postAuth(`/oauth/reset-password-confirm/${encodedToken}`, {
        new_password: newPassword,
        confirm_new_password: confirmPassword,
      })

      if (response.status === 200) {
        setStatus('success')
        setMessage(response.data?.message || 'Password reset successfully')
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login', {
            state: {
              message: 'Password reset successfully! You can now sign in with your new password.'
            }
          })
        }, 3000)
      }
    } catch (err: any) {
      setStatus('error')
      const errorData = err?.response?.data
      
      // Backend error responses:
      // - {"message": "Password reset successfully"} on success
      // - {"message": "Error occurred during password reset."} from service
      // - {"message": "User not found", "error_code": "user_not_found"} from UseNotFound
      // - FastAPI validation errors as array in detail
      if (errorData?.detail) {
        if (Array.isArray(errorData.detail)) {
          // FastAPI validation errors
          const fieldErrors: { [key: string]: string } = {}
          errorData.detail.forEach((item: any) => {
            if (item.loc && item.loc.length > 1) {
              const field = item.loc[item.loc.length - 1]
              const errorMsg = item.msg || 'Validation error'
              if (field === 'new_password' || field === 'confirm_new_password') {
                fieldErrors[field === 'new_password' ? 'newPassword' : 'confirmPassword'] = errorMsg
              }
            }
          })
          setErrors(fieldErrors)
          setMessage(errorData.detail[0]?.msg || 'Validation error')
          
          // Extract password validation errors
          const passwordValidationErrors = errorData.detail
            .filter((item: any) => item.loc?.includes('new_password'))
            .map((item: any) => item.msg)
          if (passwordValidationErrors.length > 0) {
            setPasswordErrors(passwordValidationErrors)
          }
        } else if (typeof errorData.detail === 'string') {
          setMessage(errorData.detail)
        } else if (errorData.detail?.message) {
          setMessage(errorData.detail.message)
        } else {
          setMessage('Failed to reset password')
        }
      } else if (errorData?.message) {
        setMessage(errorData.message)
      } else {
        setMessage(
          err?.message || 
          'Failed to reset password. The link may be invalid or expired.'
        )
      }
    }
  }

  return (
    <div className="h-full grid place-items-center bg-[var(--bg)] p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <div className="text-4xl mb-4">🔒</div>
          <h1 className="text-2xl font-bold text-[var(--text)]">Reset Your Password</h1>
          <p className="text-[color:var(--muted)] text-sm">
            {status === 'success' 
              ? 'Your password has been reset successfully' 
              : 'Enter your new password below'}
          </p>
        </div>

        {status === 'success' ? (
          <div className="text-center space-y-4 p-8 rounded-xl border border-green-200/60 bg-green-100/40 backdrop-blur-sm shadow-xl dark:border-green-800/50 dark:bg-green-900/20">
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-xl font-bold text-green-600 dark:text-green-400">Password Reset Successful!</h2>
            <p className="text-[color:var(--muted)]">{message}</p>
            <div className="pt-4 space-y-3">
              <p className="text-sm text-neutral-400">
                Redirecting to login page in a few seconds...
              </p>
              <div className="flex flex-col gap-2">
                <Button
                  onClick={() => navigate('/login', {
                    state: {
                      message: 'Password reset successfully! You can now sign in with your new password.'
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
        ) : (
          <form onSubmit={onSubmit} className="w-full grid gap-4 p-8 rounded-xl border border-[var(--border)] bg-[var(--surface)] backdrop-blur-sm shadow-xl">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[color:var(--muted)] mb-1.5">
                  New Password
                </label>
                <Input
                  type="password"
                  placeholder="Enter your new password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  autoFocus
                  disabled={status === 'loading'}
                  className={errors.newPassword ? 'border-red-500' : ''}
                />
                {errors.newPassword && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.newPassword}</p>
                )}
                {passwordErrors.length > 0 && !errors.newPassword && (
                  <ul className="mt-1.5 space-y-1 text-xs text-red-600 dark:text-red-400">
                    {passwordErrors.map((error, i) => (
                      <li key={i} className="flex items-start gap-1.5">
                        <span className="text-red-500">•</span>
                        <span>{error}</span>
                      </li>
                    ))}
                  </ul>
                )}
                <p className="mt-1.5 text-xs text-[color:var(--muted)]">
                  Password must be at least 8 characters with uppercase, lowercase, digit, and special character (!@#$%^&*(),.?":{}|&lt;&gt;)
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-[color:var(--muted)] mb-1.5">
                  Confirm New Password
                </label>
                <Input
                  type="password"
                  placeholder="Confirm your new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  disabled={status === 'loading'}
                  className={errors.confirmPassword ? 'border-red-500' : ''}
                />
                {errors.confirmPassword && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.confirmPassword}</p>
                )}
            </div>
          </div>

            {message && (
              <div className={`text-sm px-4 py-3 rounded-lg border ${
                status === 'error' 
                  ? 'text-red-600 bg-red-100/40 border-red-200/60 dark:text-red-400 dark:bg-red-900/20 dark:border-red-800/50' 
                  : 'text-green-600 bg-green-100/40 border-green-200/60 dark:text-green-400 dark:bg-green-900/20 dark:border-green-800/50'
              }`}>
                {message}
              </div>
            )}

            <Button
              type="submit"
              className="w-full py-2.5 font-medium bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50"
              disabled={
                status === 'loading' || 
                !newPassword.trim() || 
                !confirmPassword.trim() ||
                passwordErrors.length > 0 ||
                newPassword !== confirmPassword
              }
            >
              {status === 'loading' ? 'Resetting Password...' : 'Reset Password'}
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

