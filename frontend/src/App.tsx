import { Route, Routes, Navigate, Link, useNavigate, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { api } from './api/client'
import { getApiPrefixSync } from './api/config'
import Login from './pages/Login'
import Signup from './pages/Signup'
import ChatRoom from './pages/ChatRoom'
import VerifyEmail from './pages/VerifyEmail'
import VerifyEmailWrapper from './pages/VerifyEmailWrapper'
import PasswordReset from './pages/PasswordReset'
import PasswordResetWrapper from './pages/PasswordResetWrapper'
import ForgotPassword from './pages/ForgotPassword'
import Sidebar from './components/Sidebar'
import RequireAuth from './auth/RequireAuth'
import RequireAdmin from './auth/RequireAdmin'
import AdminLayout from './pages/admin/AdminLayout'
import KnowledgeBases from './pages/admin/KnowledgeBases'
import Documents from './pages/admin/Documents'
import Chunks from './pages/admin/Chunks'
import Embeddings from './pages/admin/Embeddings'
import ThemeToggle from './components/ThemeToggle'
import Logo from './components/Logo'
import Button from './components/ui/Button'
import HomeHero from './components/HomeHero'
import StartChatCTA from './components/StartChatCTA'

export default function App() {
  const navigate = useNavigate()
  const location = useLocation()
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
  const [role, setRole] = useState<string | null>(null)
  const isAuthPage = location.pathname === '/login' || location.pathname === '/signup' || 
                     location.pathname === '/forgot-password' ||
                     location.pathname.startsWith('/verify/') || 
                     location.pathname.startsWith('/password-reset-confirm/') ||
                     location.pathname.startsWith('/reset-password/') ||
                     /^\/v\d+\/oauth\/verify\//.test(location.pathname) ||
                     /^\/v\d+\/password-reset-confirm/.test(location.pathname) // Match with or without trailing slash

  function handleLogout() {
    localStorage.removeItem('access_token')
    navigate('/login')
  }

  const [isMobileSidebarOpen, setMobileSidebarOpen] = useState(false)

  useEffect(() => {
    let active = true
    async function fetchRole() {
      if (!token) {
        setRole(null)
        return
      }
      try {
        const prefix = getApiPrefixSync()
        const { data } = await api.get(`${prefix}/oauth/me`)
        if (!active) return
        setRole(data?.role || 'user')
      } catch {
        if (!active) return
        setRole(null)
      }
    }
    fetchRole()
    return () => { active = false }
  }, [token])

  if (isAuthPage) {
    return (
      <div className="h-full bg-[var(--bg)] text-[var(--text)] flex flex-col">
        {/* Top bar: show theme toggle even on auth pages */}
        <div className="h-12 border-b border-[var(--border)] bg-[var(--bg)] flex items-center justify-end px-4 shrink-0">
          <ThemeToggle />
        </div>
        <div className="flex-1 min-h-0 overflow-hidden">
          <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/verify/:token" element={<VerifyEmail />} />
          <Route path="/password-reset-confirm/:token" element={<PasswordReset />} />
          <Route path="/reset-password/:token" element={<PasswordReset />} />
          {/* Handle versioned URLs from backend emails */}
          <Route path="/:version/oauth/verify/:token" element={<VerifyEmailWrapper />} />
          <Route path="/:version/password-reset-confirm/:token" element={<PasswordResetWrapper />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-[var(--bg)] text-[var(--text)] flex">
      {/* Sidebar */}
      {token && (
        <>
          {/* Desktop sidebar */}
          <aside className="hidden md:block h-full flex-shrink-0">
            <Sidebar />
          </aside>
          {/* Mobile drawer */}
          {isMobileSidebarOpen && (
            <>
              <div 
                className="fixed inset-0 bg-black/40 z-30"
                onClick={() => setMobileSidebarOpen(false)}
              />
              <div className="fixed inset-y-0 left-0 w-64 z-40 shadow-lg">
                <Sidebar onClose={() => setMobileSidebarOpen(false)} />
              </div>
            </>
          )}
        </>
      )}
      
      {/* Main content */}
      <main className="flex-1 min-w-0 overflow-hidden flex flex-col">
        {/* Top bar with auth/logout */}
        {token && (
          <div className="h-12 border-b border-[var(--border)] bg-[var(--bg)] flex items-center justify-between px-4 shrink-0">
            <div className="flex items-center gap-3">
              {/* Mobile menu */}
              <button
                className="md:hidden p-2 rounded-lg border border-[var(--border)] bg-[var(--surface)] text-[color:var(--muted)] hover:opacity-80"
                onClick={() => setMobileSidebarOpen(true)}
                aria-label="Open menu"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <Link to="/" className="hover:opacity-90 transition-opacity">
                <Logo />
              </Link>
              {/* Admin entry point: only show for admin role */}
              {role === 'admin' && (
                <Link to="/admin/kb" className="text-sm text-[color:var(--muted)] hover:opacity-80">Admin</Link>
              )}
            </div>
            <div className="flex items-center gap-2">
              <ThemeToggle />
              <Button onClick={handleLogout} variant="secondary" className="px-3 py-1.5">
                Sign out
              </Button>
            </div>
          </div>
        )}
        
        <div className="flex-1 min-h-0 overflow-hidden">
          <Routes>
            <Route 
              path="/" 
              element={
                <RequireAuth>
                  <div className="h-full overflow-auto bg-[var(--bg)]">
                    <div className="max-w-4xl mx-auto px-3 md:px-4 py-6 space-y-6">
                      <HomeHero />
                      <StartChatCTA />
                    </div>
                  </div>
                </RequireAuth>
              } 
            />
            <Route path="/c/:chatId" element={<RequireAuth><ChatRoom /></RequireAuth>} />
            {/* Admin routes */}
            <Route path="/admin" element={<RequireAdmin><AdminLayout /></RequireAdmin>}>
              <Route path="kb" element={<KnowledgeBases />} />
              <Route path="documents" element={<Documents />} />
              <Route path="chunks" element={<Chunks />} />
              <Route path="embeddings" element={<Embeddings />} />
              <Route index element={<Navigate to="kb" replace />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}


