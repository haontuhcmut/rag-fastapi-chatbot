import { useEffect, useMemo, useState } from 'react'
import { api } from '../../api/client'
import { getApiPrefixSync } from '../../api/config'

type KnowledgeBase = { id: string; name: string }
type DocumentItem = {
  id: string
  file_name: string
  knowledge_base_id: string
  status?: string
  created_at?: string
}

export default function Documents() {
  const prefix = useMemo(() => getApiPrefixSync(), [])
  const [kbs, setKbs] = useState<KnowledgeBase[]>([])
  const [kbId, setKbId] = useState<string>('')
  const [docs, setDocs] = useState<DocumentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [files, setFiles] = useState<FileList | null>(null)
  const [busyDoc, setBusyDoc] = useState<string | null>(null)
  const [busyAction, setBusyAction] = useState<'chunk' | 'embed' | 'delete' | null>(null)
  const [chunkCounts, setChunkCounts] = useState<Record<string, number>>({})

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
    setInfo(null)
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
      const items = normalizePage<any>(data)
      const count = typeof data?.total === 'number' ? data.total : items.length
      setChunkCounts(prev => ({ ...prev, [docId]: count }))
    } catch {
      // ignore
    }
  }

  useEffect(() => { loadKbs(); loadDocs() }, [])
  useEffect(() => { docs.forEach(d => loadChunkCountFor(d.id)) }, [docs])

  async function upload() {
    if (!kbId || !files || files.length === 0) return
    setError(null)
    setInfo(null)
    const fd = new FormData()
    Array.from(files).forEach(file => fd.append('files', file))
    try {
      await api.post(`${prefix}/document/`, fd, { params: { kb_id: kbId }, headers: { 'Content-Type': 'multipart/form-data' } })
      setFiles(null)
      setInfo('Upload successful')
      await loadDocs()
    } catch (e: any) {
      const msg = e?.response?.data?.detail || 'Failed to upload documents'
      setError(typeof msg === 'string' ? msg : 'Failed to upload documents')
    }
  }

  async function removeDoc(id: string) {
    if (!confirm('Delete this document?')) return
    setBusyDoc(id); setBusyAction('delete')
    setError(null); setInfo(null)
    try {
      await api.delete(`${prefix}/document/${id}`)
      setInfo('Document deleted')
      await loadDocs()
    } catch {
      setError('Failed to delete document')
    } finally {
      setBusyDoc(null); setBusyAction(null)
    }
  }

  async function chunkDoc(id: string) {
    setBusyDoc(id); setBusyAction('chunk')
    setError(null); setInfo(null)
    try {
      await api.post(`${prefix}/chunking/`, null, { params: { document_id: id } })
      setInfo('Chunking started')
      await loadDocs()
      await loadChunkCountFor(id)
    } catch {
      setError('Failed to start chunking')
    } finally {
      setBusyDoc(null); setBusyAction(null)
    }
  }

  async function processDoc(id: string) {
    setBusyDoc(id); setBusyAction('chunk')
    setError(null); setInfo(null)
    try {
      await api.post(`${prefix}/chunking/`, null, { params: { document_id: id } })
      setInfo('Chunking started')
      await loadDocs()
      await loadChunkCountFor(id)
    } catch {
      setError('Failed to start chunking')
      setBusyDoc(null); setBusyAction(null)
      return
    }
    const countAfter = chunkCounts[id] ?? 0
    if (countAfter > 0) {
      try {
        setBusyAction('embed')
        await api.post(`${prefix}/embedding/`, null, { params: { document_id: id } })
        setInfo('Embedding started')
        await loadDocs()
      } catch (e: any) {
        const msg = e?.response?.data?.detail || 'Failed to start embedding'
        setError(typeof msg === 'string' ? msg : 'Failed to start embedding')
      }
    } else {
      setInfo('Chunking queued; start embedding once chunks are ready')
    }
    setBusyDoc(null); setBusyAction(null)
  }

  async function embedDoc(id: string) {
    setBusyDoc(id); setBusyAction('embed')
    setError(null); setInfo(null)
    // Pre-check chunks
    const count = chunkCounts[id] ?? 0
    if (count === 0) {
      setError('Chunk the document before embedding');
      setBusyDoc(null); setBusyAction(null); return
    }
    try {
      await api.post(`${prefix}/embedding/`, null, { params: { document_id: id } })
      setInfo('Embedding started')
      await loadDocs()
    } catch (e: any) {
      const msg = e?.response?.data?.detail || 'Failed to start embedding'
      setError(typeof msg === 'string' ? msg : 'Failed to start embedding')
    } finally {
      setBusyDoc(null); setBusyAction(null)
    }
  }

  const docsByKb = docs.filter(d => !kbId || d.knowledge_base_id === kbId)

  const statusBadge = (status?: string) => {
    const s = (status || 'pending').toLowerCase()
    const cls = s === 'chunking' ? 'bg-amber-500/20 text-amber-700 dark:text-amber-300 border-amber-500/30' :
                 s === 'embedding' ? 'bg-blue-500/20 text-blue-700 dark:text-blue-300 border-blue-500/30' :
                 'bg-[var(--surface)] text-[color:var(--muted)] border-[var(--border)]'
    const label = s.charAt(0).toUpperCase() + s.slice(1)
    return <span className={`inline-block text-xs px-2 py-0.5 rounded border ${cls}`}>{label}</span>
  }

  return (
    <div className="p-4 text-[var(--text)]">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Documents</h2>
        <button onClick={loadDocs} className="px-2.5 py-1.5 rounded border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] text-sm hover:opacity-90">Refresh</button>
      </div>
      <p className="text-[color:var(--muted)] text-sm mt-1">Use Process to start chunking; embedding activates once chunks exist.</p>
      <div className="mt-4 grid gap-2 sm:grid-cols-3">
        <select value={kbId} onChange={e => setKbId(e.target.value)} className="bg-[var(--surface)] border border-[var(--border)] rounded px-3 py-2 text-[var(--text)]">
          {kbs.map(k => <option key={k.id} value={k.id}>{k.name}</option>)}
        </select>
        <input type="file" multiple onChange={e => setFiles(e.target.files)} className="bg-[var(--surface)] border border-[var(--border)] rounded px-3 py-2 text-[var(--text)] sm:col-span-2" />
        <div>
          <button onClick={upload} disabled={!files || files.length === 0} className="px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm">Upload</button>
        </div>
      </div>
      {error && <p className="mt-3 text-red-600 dark:text-red-400 text-sm">{error}</p>}
      {info && <p className="mt-3 text-emerald-600 dark:text-emerald-400 text-sm">{info}</p>}

      <div className="mt-6">
        {loading ? (
          <p className="text-[color:var(--muted)]">Loading…</p>
        ) : docsByKb.length === 0 ? (
          <p className="text-[color:var(--muted)]">No documents for this KB.</p>
        ) : (
          <ul className="divide-y divide-[var(--border)]">
            {docsByKb.map(d => {
              const s = (d.status || 'pending').toLowerCase()
              const isChunking = s === 'chunking'
              const isEmbedding = s === 'embedding'
              const isBusy = busyDoc === d.id
              const count = chunkCounts[d.id] ?? 0
              return (
                <li key={d.id} className="py-3">
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-[var(--text)] text-sm truncate">{d.file_name}</p>
                      <div className="flex items-center gap-2 text-xs text-[color:var(--muted)] mt-0.5">
                        {statusBadge(d.status)}
                        <span>Chunks: {count}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => chunkDoc(d.id)} disabled={isBusy || isChunking || isEmbedding} className="px-2.5 py-1.5 rounded border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] text-sm hover:opacity-90 disabled:opacity-50">
                        {isBusy && busyAction === 'chunk' ? 'Chunking…' : 'Chunk'}
                      </button>
                      <button onClick={() => processDoc(d.id)} disabled={isBusy || isEmbedding} className="px-2.5 py-1.5 rounded border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] text-sm hover:opacity-90 disabled:opacity-50">
                        {isBusy && busyAction === 'chunk' ? 'Processing…' : 'Process'}
                      </button>
                      <button onClick={() => embedDoc(d.id)} disabled={isBusy || isEmbedding || count === 0} className="px-2.5 py-1.5 rounded border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] text-sm hover:opacity-90 disabled:opacity-50">
                        {isBusy && busyAction === 'embed' ? 'Embedding…' : 'Embed'}
                      </button>
                      <button onClick={() => removeDoc(d.id)} disabled={isBusy} className="px-2.5 py-1.5 rounded bg-red-600 text-white text-sm hover:bg-red-500 disabled:opacity-50">
                        {isBusy && busyAction === 'delete' ? 'Deleting…' : 'Delete'}
                      </button>
                    </div>
                  </div>
                </li>
              )
            })}
          </ul>
        )}
      </div>
    </div>
  )
}