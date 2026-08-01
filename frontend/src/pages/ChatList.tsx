import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { getApiPrefixSync } from '../api/config'

type Chat = {
  id: string
  created_at: string
  updated_at: string
  username?: string
}

type Page<T> = {
  items: T[]
}

export default function ChatList() {
  const [chats, setChats] = useState<Chat[]>([])
  const [error, setError] = useState<string | null>(null)
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

  useEffect(() => {
    ;(async () => {
      try {
        const prefix = getApiPrefixSync()
        const { data } = await api.get<Page<Chat>>(`${prefix}/chat/`)
        const sorted = (data.items || []).sort((a, b) => 
          new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        )
        const hidden = getHiddenChatIds()
        setChats(sorted.filter((c) => !hidden.includes(c.id)))
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Failed to load chats')
      }
    })()
  }, [])

  async function createChat() {
    try {
      const prefix = getApiPrefixSync()
      const { data } = await api.post<Chat>(`${prefix}/chat/`)
      navigate(`/c/${data.id}`)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to create chat')
    }
  }

  return (
    <div style={{ display: 'grid', gap: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <h2>Chats</h2>
        <button onClick={createChat}>New chat</button>
      </div>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <ul>
        {chats.map((c) => (
          <li key={c.id}>
            <Link to={`/c/${c.id}`}>{c.id}</Link>
          </li>
        ))}
      </ul>
    </div>
  )
}


