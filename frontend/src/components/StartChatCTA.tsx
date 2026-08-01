import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { getApiPrefixSync } from '../api/config'
import Button from './ui/Button'

export default function StartChatCTA() {
  const navigate = useNavigate()

  async function createChat() {
    try {
      const prefix = getApiPrefixSync()
      const { data } = await api.post<{ id: string }>(`${prefix}/chat/`)
      navigate(`/c/${data.id}`)
    } catch (_) {
      // silently fail
    }
  }

  return (
    <div className="flex justify-center">
      <Button onClick={createChat} className="px-4 py-2">Start a new chat</Button>
    </div>
  )
}