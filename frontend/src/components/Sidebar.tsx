import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { api, setAccessToken } from '../api/client'
import { getApiPrefixSync } from '../api/config'

type Chat = {
  id: string
  created_at: string
  updated_at: string
  username?: string
  title?: string
}

type Page<T> = {
  items: T[]
}

export default function Sidebar({ onClose }: { onClose?: () => void }) {
  const [chats, setChats] = useState<Chat[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [isCollapsed, setIsCollapsed] = useState(() => {
    if (typeof window === 'undefined') return false
    return window.innerWidth < 768 // collapse on small screens by default
  })
  const [user, setUser] = useState<{ username?: string; email?: string; role?: string } | null>(null)
  const location = useLocation()
  const navigate = useNavigate()

  function getHiddenChatIds(): string[] {
    try {
      const raw = localStorage.getItem('hidden_chats')
      if (!raw) return []
      const parsed = JSON.parse(raw)
      return Array.isArray(parsed) ? parsed.filter((x) => typeof x === 'string') : []
    } catch {
      return []
    }
  }

  function hideChatId(chatId: string) {
    const current = getHiddenChatIds()
    if (current.includes(chatId)) return
    try {
      localStorage.setItem('hidden_chats', JSON.stringify([...current, chatId]))
    } catch {}
  }

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const prefix = getApiPrefixSync()
      const { data } = await api.get<Page<Chat>>(`${prefix}/chat/`)
      // Sort by updated_at descending (most recent first)
      const sorted = (data.items || []).sort((a, b) => 
        new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      )
      const hidden = getHiddenChatIds()
      const visible = sorted.filter((c) => !hidden.includes(c.id))
      setChats(visible)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to load chats')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const hasToken = typeof window !== 'undefined' && !!localStorage.getItem('access_token')
    if (hasToken) {
      load()
      // Also load current user info for bottom panel
      ;(async () => {
        try {
          const prefix = getApiPrefixSync()
          const { data } = await api.get(`${prefix}/oauth/me`)
          setUser({ username: data?.username, email: data?.email, role: data?.role })
        } catch {
          // noop
        }
      })()
    }
    // Listen for chat updates (e.g., first message sets a title)
    function onChatUpdated() { load() }
    window.addEventListener('chat-updated', onChatUpdated as EventListener)
    return () => {
      window.removeEventListener('chat-updated', onChatUpdated as EventListener)
    }
  }, [location.pathname])

  async function createChat() {
    try {
      const prefix = getApiPrefixSync()
      const { data } = await api.post<Chat>(`${prefix}/chat/`)
      navigate(`/c/${data.id}`)
      await load()
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to create chat')
    }
  }

  function logout() {
    try {
      setAccessToken(null)
      try { localStorage.removeItem('refresh_token') } catch {}
    } catch {}
    navigate('/login')
  }

  async function deleteChat(e: React.MouseEvent, chatId: string) {
    e.preventDefault()
    e.stopPropagation()
    if (!confirm('Are you sure you want to delete this chat?')) return
    
    setDeletingId(chatId)
    try {
      // UI-only delete: hide from local view
      hideChatId(chatId)
      // If currently viewing this chat, navigate home
      if (location.pathname === `/c/${chatId}`) {
        navigate('/')
      }
      // Remove from current state without refetch
      setChats((prev) => prev.filter((c) => c.id !== chatId))
    } finally {
      setDeletingId(null)
    }
  }

  function formatDate(dateString: string) {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  function truncateId(id: string) {
    return id.split('-')[0].slice(0, 8)
  }

  const activeId = location.pathname.startsWith('/c/') ? location.pathname.split('/c/')[1] : ''

  function isChatInProgress(chatId: string): boolean {
    try {
      const raw = localStorage.getItem(`chat_progress:${chatId}`)
      if (!raw) return false
      const data = JSON.parse(raw)
      return !!data?.inProgress
    } catch {
      return false
    }
  }

  const [progressTick, setProgressTick] = useState(0)

  useEffect(() => {
    function onProgressUpdate() {
      setProgressTick((v) => v + 1)
    }
    window.addEventListener('chat-progress', onProgressUpdate as EventListener)
    return () => {
      window.removeEventListener('chat-progress', onProgressUpdate as EventListener)
    }
  }, [])

  function getChatPreview(chatId: string): string {
    // Prefer stored title derived from first user message
    try {
      const t = localStorage.getItem(`chat_title:${chatId}`)
      if (t && t.trim()) return t.trim()
    } catch {}
    return `Chat ${truncateId(chatId)}`
  }

  return (
    <div className={`h-full flex flex-col bg-[var(--surface)] text-[var(--text)] border-r border-[var(--border)] transition-all duration-300 ${isCollapsed ? 'w-12 md:w-16' : 'w-56 md:w-64'}`}>
      {/* Header */}
      <div className="p-3 border-b border-[var(--border)] flex items-center justify-between">
        {!isCollapsed && (
          <button
            onClick={createChat}
            disabled={loading}
            className="flex items-center gap-2 w-full px-3 py-2 rounded-lg transition-colors text-sm border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] hover:opacity-90"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>New chat</span>
          </button>
        )}
        {isCollapsed && (
          <button
            onClick={createChat}
            disabled={loading}
            className="w-8 h-8 rounded-lg transition-colors flex items-center justify-center text-[var(--text)] border border-[var(--border)] bg-[var(--surface)] hover:opacity-90"
            title="New chat"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="ml-2 w-8 h-8 rounded-lg transition-colors flex items-center justify-center text-[color:var(--muted)] hover:opacity-80"
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <svg className={`w-4 h-4 transition-transform ${isCollapsed ? '' : 'rotate-180'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-2 w-8 h-8 rounded-lg transition-colors flex items-center justify-center text-[color:var(--muted)] hover:opacity-80 md:hidden"
            title="Close"
            aria-label="Close"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Chat list */}
      <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-track-transparent">
        {error && !isCollapsed && (
          <div className="text-xs text-red-400 bg-red-900/20 px-3 py-2 m-2 rounded border border-red-800">
            {error}
          </div>
        )}
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="flex gap-1.5">
              <div className="h-2 w-2 rounded-full bg-[color:var(--muted)] animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="h-2 w-2 rounded-full bg-[color:var(--muted)] animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="h-2 w-2 rounded-full bg-[color:var(--muted)] animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        ) : chats.length === 0 ? (
          !isCollapsed && (
            <div className="text-center py-8 px-4">
              <div className="text-sm text-[color:var(--muted)]">No chats yet</div>
            </div>
          )
        ) : (
          <div className="p-2 space-y-1">
            {chats.map((c) => {
              const isActive = c.id === activeId
              const isDeleting = deletingId === c.id
              return (
                <Link
                  key={c.id}
                  to={`/c/${c.id}`}
                  className={`group relative flex items-center gap-2 px-2 py-2 rounded-lg text-sm transition-all ${
                    isActive 
                      ? 'bg-[var(--surface)] text-[var(--text)]' 
                      : 'hover:opacity-80 text-[color:var(--muted)]'
                  } ${isDeleting ? 'opacity-50 pointer-events-none' : ''} ${isCollapsed ? 'justify-center' : ''}`}
                  title={isCollapsed ? getChatPreview(c.id) : ''}
                >
                  {isCollapsed ? (
                    <div className="w-8 h-8 rounded bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center text-xs font-medium text-[color:var(--muted)]">
                      {c.id.slice(0, 1).toUpperCase()}
                    </div>
                  ) : (
                    <>
                      <div className="flex-1 min-w-0">
                        <div className="truncate font-medium text-xs">
                          {getChatPreview(c.id)}
                        </div>
                        <div className="text-xs text-[color:var(--muted)] mt-0.5 truncate">
                          <span className="inline-flex items-center gap-1">
                            {formatDate(c.updated_at)}
                            {isChatInProgress(c.id) && (
                              <span className="inline-flex items-center gap-1 ml-2 text-[color:var(--muted)]">
                                <span className="h-1.5 w-1.5 rounded-full bg-[color:var(--muted)] animate-pulse" />
                                Generating…
                              </span>
                            )}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={(e) => deleteChat(e, c.id)}
                        className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-600/20 text-neutral-400 hover:text-red-400 transition-opacity shrink-0"
                        title="Delete chat"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </>
                  )}
                </Link>
              )
            })}
          </div>
        )}
      </div>

      {/* Bottom user info */}
      <div className="border-t border-[var(--border)] p-3">
        {isCollapsed ? (
          <div className="flex items-center justify-center">
            <div className="w-8 h-8 rounded-full bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center text-xs font-medium text-[color:var(--muted)]">
              {(user?.username || user?.email || 'U').slice(0, 1).toUpperCase()}
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center text-xs font-medium text-[color:var(--muted)]">
              {(user?.username || user?.email || 'U').slice(0, 1).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{user?.username || user?.email || 'User'}</div>
              <div className="text-xs text-[color:var(--muted)] truncate">{user?.role ? user.role : 'Member'}</div>
            </div>
            <button
              onClick={logout}
              className="px-2 py-1 rounded-lg text-xs border border-[var(--border)] bg-[var(--surface)] text-[color:var(--muted)] hover:opacity-80"
              title="Sign out"
            >
              Sign out
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
