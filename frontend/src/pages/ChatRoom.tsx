import { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import rehypeHighlight from 'rehype-highlight'
import { getApiPrefixSync } from '../api/config'
import { api } from '../api/client'
import BrandMark from '../components/icons/BrandMark'
import Textarea from '../components/ui/Textarea'
// Button import removed: not used in ChatRoom

export default function ChatRoom() {
  const { chatId } = useParams()
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const abortRef = useRef<AbortController | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const mountedRef = useRef(true)
  const cancelRequestedRef = useRef(false)
  const timeoutRef = useRef<number | null>(null)
  // Throttle UI updates while streaming to avoid excessive re-renders
  const flushTimerRef = useRef<number | null>(null)
  const bufferedRef = useRef<string>('')
  const GENERATION_TIMEOUT_MS = 360000 // auto-stop after 6mins waiting (before Cloudflare timeout)
  const progressKey = chatId ? `chat_progress:${chatId}` : ''

  function getProgress(id: string | undefined) {
    if (!id) return null
    try {
      const raw = localStorage.getItem(`chat_progress:${id}`)
      if (!raw) return null
      const data = JSON.parse(raw)
      if (typeof data !== 'object' || !data) return null
      return {
        inProgress: !!data.inProgress,
        question: String(data.question || ''),
        partial: String(data.partial || ''),
        updatedAt: Number(data.updatedAt || Date.now()),
      }
    } catch {
      return null
    }
  }

  function setProgress(id: string | undefined, payload: { inProgress: boolean; question: string; partial: string }) {
    if (!id) return
    try {
      localStorage.setItem(`chat_progress:${id}`, JSON.stringify({ ...payload, updatedAt: Date.now() }))
      try {
        window.dispatchEvent(
          new CustomEvent('chat-progress', { detail: { chatId: id, inProgress: payload.inProgress, partial: payload.partial } })
        )
      } catch {}
    } catch {}
  }

  function clearProgress(id: string | undefined) {
    if (!id) return
    try { localStorage.removeItem(`chat_progress:${id}`) } catch {}
    try {
      window.dispatchEvent(new CustomEvent('chat-progress', { detail: { chatId: id, inProgress: false, partial: '' } }))
    } catch {}
  }

  useEffect(() => {
    mountedRef.current = true
    return () => {
      // Mark unmounted to avoid state updates; do NOT abort so backend can finish
      mountedRef.current = false
    }
  }, [])

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }, [question])

  // Load existing history when chatId changes, and cancel any ongoing stream
  useEffect(() => {
    if (!chatId) return
    // Do not abort previous stream when switching chats; allow it to finish server-side
    setIsLoading(false)

    ;(async () => {
      try {
        const prefix = getApiPrefixSync()
        const { data } = await api.get<{ items: { content: string; role: string; created_at: string }[] }>(
          `${prefix}/message/${encodeURIComponent(chatId)}`
        )
        const items = Array.isArray(data?.items) ? data.items : []
        // Sort by created_at ascending to preserve conversation order
        const sorted = items.slice().sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
        const mapped = sorted.map((m) => ({ role: m.role === 'bot' ? 'assistant' as const : 'user' as const, content: m.content }))
        setMessages(mapped)
        // Merge any locally persisted partial assistant content if generation is still ongoing
        const prog = getProgress(chatId)
        // If we already have a saved assistant message, clear stale progress indicator
        const hasAssistant = mapped.some((m) => m.role === 'assistant' && m.content && m.content.trim())
        if (hasAssistant) {
          clearProgress(chatId)
        } else if (prog && prog.inProgress && prog.partial) {
          setMessages((prev) => {
            const copy = [...prev]
            if (copy.length > 0 && copy[copy.length - 1].role === 'assistant') {
              copy[copy.length - 1] = { role: 'assistant', content: prog.partial }
            } else {
              copy.push({ role: 'assistant', content: prog.partial })
            }
            return copy
          })
        }
      } catch (e) {
        // If history fails to load, show empty state but avoid throwing
        setMessages([])
      }
    })()
  }, [chatId])

  async function ask() {
    if (!chatId || !question.trim() || isLoading) return
    const userQuestion = question.trim()
    // If this is the first message of the chat, derive and store a title
    if (messages.length === 0) {
      const raw = userQuestion.replace(/\s+/g, ' ').trim()
      const title = raw.length > 60 ? raw.slice(0, 57) + '…' : raw
      try {
        localStorage.setItem(`chat_title:${chatId}`, title)
      } catch {}
      // Notify other UI (e.g., sidebar) to refresh its chat list
      try {
        window.dispatchEvent(new CustomEvent('chat-updated', { detail: { chatId, title } }))
      } catch {}
    }
    setQuestion('')
    if (mountedRef.current) {
      setIsLoading(true)
      // Add assistant placeholder immediately so pre-stream errors aren't silent
      setMessages((prev) => [...prev, { role: 'user', content: userQuestion }, { role: 'assistant', content: '' }])
    }
    // Initialize local progress storage
    setProgress(chatId, { inProgress: true, question: userQuestion, partial: '' })
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller

    // Best-effort: cancel any previous server-side generation for this chat
    try {
      const prefix = getApiPrefixSync()
      await api.post(`${prefix}/c/${encodeURIComponent(chatId)}/cancel`)
      // Brief pause to let backend finish canceling previous run
      await new Promise((resolve) => setTimeout(resolve, 150))
    } catch (_) {
      // Ignore failures; proceed with the new request
    }

    // Start auto-timeout to cancel if generation takes too long
    if (timeoutRef.current) {
      try { clearTimeout(timeoutRef.current) } catch {}
      timeoutRef.current = null
    }
    timeoutRef.current = window.setTimeout(() => {
      if (!mountedRef.current) return
      // Stop the generation and inform the user
      stopGenerating()
      setMessages((prev) => {
        const copy = [...prev]
        // If the last message is assistant and empty/partial, replace it with busy message
        if (copy.length > 0 && copy[copy.length - 1].role === 'assistant') {
          copy[copy.length - 1] = { role: 'assistant', content: 'Server is busy. Please try again later.' }
        } else {
          copy.push({ role: 'assistant', content: 'Server is busy. Please try again later.' })
        }
        return copy
      })
    }, GENERATION_TIMEOUT_MS)

    const token = localStorage.getItem('access_token')
    const prefix = getApiPrefixSync()
    const url = `${prefix}/c/${encodeURIComponent(chatId)}?question=${encodeURIComponent(userQuestion)}`
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          Authorization: token ? `Bearer ${token}` : '',
        },
        signal: controller.signal,
      })
      if (!res.ok || !res.body) {
        throw new Error('Request failed')
      }
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let acc = ''
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        // Buffer chunks and flush at a small interval to reduce render cost
        bufferedRef.current += chunk
        if (!flushTimerRef.current) {
          flushTimerRef.current = window.setTimeout(() => {
            flushTimerRef.current = null
            acc += bufferedRef.current
            bufferedRef.current = ''
            if (mountedRef.current) {
              setMessages((prev) => {
                const copy = [...prev]
                copy[copy.length - 1] = { role: 'assistant', content: acc }
                return copy
              })
            }
            // Persist partial content for continuity across navigation
            setProgress(chatId, { inProgress: true, question: userQuestion, partial: acc })
          }, 60)
        }
      }
      // Final flush to ensure any remaining buffered content is rendered
      if (bufferedRef.current) {
        acc += bufferedRef.current
        bufferedRef.current = ''
        if (mountedRef.current) {
          setMessages((prev) => {
            const copy = [...prev]
            copy[copy.length - 1] = { role: 'assistant', content: acc }
            return copy
          })
        }
        setProgress(chatId, { inProgress: true, question: userQuestion, partial: acc })
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        if (mountedRef.current) {
          setMessages((prev) => {
            const copy = [...prev]
            if (copy.length > 0 && copy[copy.length - 1].role === 'assistant' && !copy[copy.length - 1].content) {
              copy[copy.length - 1] = { role: 'assistant', content: 'Sorry, an error occurred. Please try again.' }
            }
            return copy
          })
        }
        // Ensure backend generation stops if the client encountered an error
        try {
          controller.abort()
        } catch {}
        try {
          await api.post(`${prefix}/c/${encodeURIComponent(chatId)}/cancel`)
        } catch {}
      }
    } finally {
      // Clear timeout regardless of outcome
      if (timeoutRef.current) {
        try { clearTimeout(timeoutRef.current) } catch {}
        timeoutRef.current = null
      }
      if (flushTimerRef.current) {
        try { clearTimeout(flushTimerRef.current) } catch {}
        flushTimerRef.current = null
        bufferedRef.current = ''
      }
      if (mountedRef.current) setIsLoading(false)
      // Clear local progress on completion or abort
      clearProgress(chatId)
      cancelRequestedRef.current = false
    }
  }

  function stopGenerating() {
    if (!chatId) return
    cancelRequestedRef.current = true
    // Immediately clear UI indicator and stop
    clearProgress(chatId)
    abortRef.current?.abort()
    if (mountedRef.current) setIsLoading(false)
    // Request server-side cancellation to stop background generation
    ;(async () => {
      try {
        const prefix = getApiPrefixSync()
        await api.post(`${prefix}/c/${encodeURIComponent(chatId)}/cancel`)
      } catch (_) {
        // Best-effort; ignore failures
      }
    })()
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      ask()
    }
  }

  return (
    <div className="h-full flex flex-col bg-[var(--bg)] text-[var(--text)]">
      {/* Messages area - ChatGPT-like centered layout */}
      <div className="flex-1 overflow-y-auto scroll-smooth">
        <div className="mx-auto w-full max-w-none sm:max-w-xl md:max-w-2xl lg:max-w-3xl xl:max-w-4xl px-3 md:px-4 py-4 md:py-6">
          {messages.length === 0 && (
            <div className="h-full flex items-center justify-center min-h-[40vh]">
              <div className="text-center space-y-6 max-w-xl">
                <h1 className="text-4xl font-semibold mb-2">How can I help you today?</h1>
              </div>
            </div>
          )}
          
          {/* Messages */}
          {messages.map((m, i) => (
            <div 
              key={i} 
              className={`group mb-3 md:mb-4 animate-in fade-in ${m.role === 'user' ? 'flex justify-end' : 'flex justify-start'}`}
              style={{ animationDelay: `${i * 30}ms` }}
            >
              <div className={`flex gap-3 md:gap-4 w-full ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {/* Avatar */}
                <div className={`h-8 w-8 rounded-sm flex-shrink-0 flex items-center justify-center ${
                  m.role === 'user'
                    ? 'bg-[var(--surface)] border border-[var(--border)]'
                    : 'bg-[var(--surface)] border border-[var(--border)]'
                }`}>
                  {m.role === 'user' ? (
                    <span className="font-semibold text-sm text-[var(--text)]">U</span>
                  ) : (
                    <BrandMark size={20} />
                  )}
                </div>
                
                {/* Message content */}
                <div className={`flex-1 min-w-0 ${m.role === 'user' ? 'text-right' : 'text-left'}`}>
                  <div className="inline-block text-base leading-6 break-words max-w-full">
                    {m.role === 'assistant' ? (
                      <div className="rounded-2xl px-3.5 py-2.5 bg-[var(--surface)] border border-[var(--border)] shadow-sm">
                        <ReactMarkdown 
                          rehypePlugins={[rehypeHighlight]}
                          className="markdown-content"
                          components={{
                            p: ({node, ...props}) => <p className="mb-2 leading-6" {...props} />,
                            ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-2" {...props} />,
                            ol: ({node, ...props}) => <ol className="list-decimal pl-5 mb-2" {...props} />,
                            li: ({node, ...props}) => <li className="mb-0.5" {...props} />,
                            h1: ({node, ...props}) => <h1 className="text-lg font-semibold mt-3 mb-2" {...props} />,
                            h2: ({node, ...props}) => <h2 className="text-base font-semibold mt-3 mb-2" {...props} />,
                            h3: ({node, ...props}) => <h3 className="text-base font-medium mt-3 mb-2" {...props} />,
                            pre: ({node, ...props}) => <pre className="my-3" {...props} />,
                            code: ({node, className, ...props}) => (
                              <code className={"bg-black/5 px-1.5 py-0.5 rounded " + (className || '')} {...props} />
                            ),
                            a: ({node, ...props}) => <a className="text-[color:var(--accent)] border-b border-[color:var(--accent)]/30 hover:border-[color:var(--accent)]" {...props} />,
                          }}
                        >
                          {formatAssistantContent(m.content)}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <div className="inline-block rounded-2xl px-3.5 py-2.5 bg-[var(--surface)] border border-[var(--border)] text-left shadow-sm">{m.content}</div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start gap-4 mb-4 animate-in fade-in">
              <div className="h-8 w-8 rounded-sm bg-[var(--surface)] border border-[var(--border)] flex-shrink-0 flex items-center justify-center">
                <BrandMark size={20} />
              </div>
              <div className="flex items-center gap-1.5 pt-1">
                <div className="h-2 w-2 rounded-full bg-neutral-400 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="h-2 w-2 rounded-full bg-neutral-400 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="h-2 w-2 rounded-full bg-neutral-400 animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area - ChatGPT-like */}
      <div className="border-t border-[var(--border)] bg-[var(--bg)]">
        <div className="mx-auto w-full max-w-none sm:max-w-xl md:max-w-2xl lg:max-w-3xl px-3 md:px-4 py-4">
          <div className="relative flex items-end gap-2">
            <div className="flex-1 relative">
              <Textarea
                ref={textareaRef}
                rows={1}
                className="resize-none min-h-[52px] max-h-[200px] pr-12 py-3.5 text-base bg-[var(--surface)] border-[var(--border)] focus:bg-[var(--surface)] rounded-2xl"
                placeholder="Message ChatBot..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
              />
              {isLoading && (
                <button
                  onClick={stopGenerating}
                  className="absolute right-3 bottom-3 p-1.5 rounded-lg hover:opacity-80 transition-colors"
                  title="Stop generating"
                  aria-label="Stop generating"
                >
                  <svg className="w-5 h-5 text-[color:var(--muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                  </svg>
                </button>
              )}
            </div>
            <button
              onClick={ask}
              disabled={isLoading || !question.trim()}
              className="h-[52px] w-[52px] rounded-lg bg-[var(--surface)] border border-[var(--border)] disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center shrink-0 hover:opacity-90"
              title="Send message"
            >
              {isLoading ? (
                <div className="h-5 w-5 border-2 border-[color:var(--muted)] border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <svg className="w-5 h-5 text-[var(--text)]" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                </svg>
              )}
            </button>
          </div>
          <p className="text-xs text-[color:var(--muted)] text-center mt-2">
            Chatbot can make mistakes. Check important info.
          </p>
        </div>
      </div>
    </div>
  )
}

  // Normalize assistant content to avoid excessive blank lines/spacing
  function formatAssistantContent(content: string): string {
    return content
      .replace(/\s+$/g, '') // trim trailing whitespace
      .replace(/\n{3,}/g, '\n\n') // collapse 3+ newlines to 2
  }


