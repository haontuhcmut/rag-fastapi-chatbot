import { useEffect, useMemo, useState } from 'react'
import { api } from '../../api/client'
import { getApiPrefixSync } from '../../api/config'

type KnowledgeBase = { id: string; name: string }
type DocumentItem = { id: string; file_name: string; knowledge_base_id: string; status?: string }
type ChunkItem = { id: string; document_id: string }

export default function Embeddings() {
  const prefix = useMemo(() => getApiPrefixSync(), [])
  const [kbs, setKbs] = useState<KnowledgeBase[]>([])
  const [kbId, setKbId] = useState('')
  const [docs, setDocs] = useState<DocumentItem[]>([])
  const [chunkCounts, setChunkCounts] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const normalizePage = <T,>(data: any): T[] => Array.isArray(data?.items) ? data.items : (Array.isArray(data) ? data : [])

  async function loadKbs() {
    try {
      const { data } = await api.get(`${prefix}/kb/`)
      const items = normalizePage<KnowledgeBase>(data)
      setKbs(items)
      if (!kbId && items[0]?.id) setKbId(items[0].id)
    } catch {
      setError('Failed to load knowledge bases')
    }
  }

  async function loadDocs() {
    setLoading(true)
    setError(null)
    try {
      const { data } = await api.get(`${prefix}/document/`)
      const items = normalizePage<DocumentItem>(data)
      setDocs(items)
    } catch {
      setError('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  async function loadChunkCountFor(docId: string) {
    try {
      const { data } = await api.get(`${prefix}/chunking/${docId}`, { params: { page: 1, size: 1 } })
      const items = normalizePage<ChunkItem>(data)
      const count = typeof data?.total === 'number' ? data.total : items.length
      setChunkCounts(prev => ({ ...prev, [docId]: count }))
    } catch {
      // ignore count errors
    }
  }

  useEffect(() => { loadKbs(); loadDocs() }, [])
  useEffect(() => {
    docs.forEach(d => loadChunkCountFor(d.id))
  }, [docs])

  async function startEmbedding(docId: string) {
    try {
      await api.post(`${prefix}/embedding/`, null, { params: { document_id: docId } })
      // Reload docs to reflect status
      await loadDocs()
    } catch (e: any) {
      const msg = e?.response?.data?.detail || 'Failed to start embedding'
      setError(typeof msg === 'string' ? msg : 'Failed to start embedding')
    }
  }

  const docsByKb = docs.filter(d => !kbId || d.knowledge_base_id === kbId)

  return (
    <div className="p-4 text-[var(--text)]">
      <h2 className="text-lg font-semibold">Embeddings</h2>
      <p className="text-[color:var(--muted)] text-sm mt-1">Embed documents after chunking; shows chunk count and status.</p>
      <div className="mt-4">
        <select value={kbId} onChange={e => setKbId(e.target.value)} className="bg-[var(--surface)] border border-[var(--border)] rounded px-3 py-2 text-[var(--text)]">
          {kbs.map(k => <option key={k.id} value={k.id}>{k.name}</option>)}
        </select>
      </div>
      {error && <p className="mt-3 text-red-600 dark:text-red-400 text-sm">{error}</p>}

      <div className="mt-6">
        {loading ? (
          <p className="text-[color:var(--muted)]">Loading…</p>
        ) : docsByKb.length === 0 ? (
          <p className="text-[color:var(--muted)]">No documents for this KB.</p>
        ) : (
          <ul className="divide-y divide-[var(--border)]">
            {docsByKb.map(d => (
              <li key={d.id} className="py-3 flex items-center justify-between gap-3">
                <div className="flex-1">
                  <p className="text-[var(--text)] text-sm">{d.file_name}</p>
                  <p className="text-[color:var(--muted)] text-xs">
                    Status: {d.status || 'unknown'} · Chunks: {chunkCounts[d.id] ?? 0}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={() => startEmbedding(d.id)} className="px-2.5 py-1.5 rounded bg-emerald-600 text-white text-sm hover:bg-emerald-500">Embed</button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}