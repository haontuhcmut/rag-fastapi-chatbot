import { useEffect, useMemo, useState } from 'react'
import { api } from '../../api/client'
import { getApiPrefixSync } from '../../api/config'

type ChunkItem = {
  id: string
  username: string
  document_id: string
  content: string
  created_at?: string
}

type KnowledgeBase = { id: string; name: string }
type DocumentItem = { id: string; file_name: string; knowledge_base_id: string; status?: string }

export default function Chunks() {
  const prefix = useMemo(() => getApiPrefixSync(), [])
  const [kbs, setKbs] = useState<KnowledgeBase[]>([])
  const [kbId, setKbId] = useState('')
  const [docs, setDocs] = useState<DocumentItem[]>([])
  const [docId, setDocId] = useState('')
  const [chunks, setChunks] = useState<ChunkItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [size, setSize] = useState(20)
  const [total, setTotal] = useState(0)
  const [pages, setPages] = useState(0)
  const [query, setQuery] = useState('')
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})
  const [busyDoc, setBusyDoc] = useState<string | null>(null)
  const [busyAction, setBusyAction] = useState<'chunk' | 'embed' | null>(null)

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
    try {
      const { data } = await api.get(`${prefix}/document/`)
      const items = normalizePage<DocumentItem>(data)
      setDocs(items)
      const firstDoc = items.find(d => !kbId || d.knowledge_base_id === kbId)
      if (!docId && firstDoc?.id) setDocId(firstDoc.id)
    } catch {
      setError('Failed to load documents')
    }
  }

  async function loadChunks(targetDocId?: string, targetPage: number = page) {
    setLoading(true)
    setError(null)
    setInfo(null)
    try {
      const url = targetDocId ? `${prefix}/chunking/${targetDocId}` : `${prefix}/chunking/`
      const { data } = await api.get(url, { params: { page: targetPage, size } })
      const items = normalizePage<ChunkItem>(data)
      setChunks(items)
      // read pagination meta if present
      const meta = {
        total: Number(data?.total ?? items.length),
        page: Number(data?.page ?? targetPage),
        size: Number(data?.size ?? size),
        pages: Number(data?.pages ?? Math.ceil((Number(data?.total ?? items.length)) / (Number(data?.size ?? size) || 1)))
      }
      setTotal(meta.total)
      setPage(meta.page)
      setSize(meta.size)
      setPages(meta.pages)
    } catch {
      setError('Failed to load chunks')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadKbs(); loadDocs(); loadChunks(undefined, 1) }, [])
  useEffect(() => {
    if (docId) loadChunks(docId, 1); else loadChunks(undefined, 1)
  }, [docId])

  function refresh() {
    if (docId) loadChunks(docId, page); else loadChunks(undefined, page)
  }

  async function chunkSelected() {
    if (!docId) return
    setBusyDoc(docId); setBusyAction('chunk')
    setError(null); setInfo(null)
    try {
      await api.post(`${prefix}/chunking/`, null, { params: { document_id: docId } })
      setInfo('Chunking started')
      // After starting chunking, refresh chunks and documents
      await loadChunks(docId, 1)
      await loadDocs()
    } catch {
      setError('Failed to start chunking')
    } finally {
      setBusyDoc(null); setBusyAction(null)
    }
  }

  async function embedSelected() {
    if (!docId) return
    setBusyDoc(docId); setBusyAction('embed')
    setError(null); setInfo(null)
    // pre-check chunks available
    const count = total
    if (!count || count === 0) {
      setError('Chunk the document before embedding')
      setBusyDoc(null); setBusyAction(null)
      return
    }
    try {
      await api.post(`${prefix}/embedding/`, null, { params: { document_id: docId } })
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

  return (
    <div className="p-4 text-[var(--text)]">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Chunks</h2>
        <div className="flex items-center gap-2">
          <button onClick={refresh} className="px-2.5 py-1.5 rounded border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] text-sm hover:opacity-90">Refresh</button>
          <select value={size} onChange={e => { setSize(Number(e.target.value)); loadChunks(docId || undefined, 1) }} className="bg-[var(--surface)] border border-[var(--border)] rounded px-2 py-1 text-[var(--text)] text-sm">
            {[10,20,50,100].map(s => <option key={s} value={s}>{s}/page</option>)}
          </select>
          <button onClick={chunkSelected} disabled={!docId || busyDoc === docId || busyAction === 'embed'} className="px-2.5 py-1.5 rounded border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] text-sm hover:opacity-90 disabled:opacity-50">
            {busyDoc === docId && busyAction === 'chunk' ? 'Chunking…' : 'Chunk'}
          </button>
          <button onClick={embedSelected} disabled={!docId || total === 0 || busyDoc === docId || busyAction === 'chunk'} className="px-2.5 py-1.5 rounded bg-emerald-600 text-white text-sm hover:bg-emerald-500 disabled:opacity-50">
            {busyDoc === docId && busyAction === 'embed' ? 'Embedding…' : 'Embed'}
          </button>
        </div>
      </div>
      <div className="mt-4 grid gap-2 sm:grid-cols-3">
        <select value={kbId} onChange={e => setKbId(e.target.value)} className="bg-[var(--surface)] border border-[var(--border)] rounded px-3 py-2 text-[var(--text)]">
          {kbs.map(k => <option key={k.id} value={k.id}>{k.name}</option>)}
        </select>
        <select value={docId} onChange={e => setDocId(e.target.value)} className="bg-[var(--surface)] border border-[var(--border)] rounded px-3 py-2 text-[var(--text)] sm:col-span-2">
          {docsByKb.map(d => <option key={d.id} value={d.id}>{d.file_name}</option>)}
        </select>
        <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Filter chunks by text" className="sm:col-span-3 bg-[var(--surface)] border border-[var(--border)] rounded px-3 py-2 text-[var(--text)]" />
      </div>
      {error && <p className="mt-3 text-red-600 dark:text-red-400 text-sm">{error}</p>}
      {info && <p className="mt-3 text-emerald-600 dark:text-emerald-400 text-sm">{info}</p>}

      <div className="mt-6">
        {loading ? (
          <p className="text-[color:var(--muted)]">Loading…</p>
        ) : chunks.length === 0 ? (
          <p className="text-[color:var(--muted)]">No chunks found.</p>
        ) : (
          <>
            <div className="text-xs text-[color:var(--muted)] mb-2">Page {page} of {pages} · Showing {chunks.length} of {total}</div>
            <ul className="divide-y divide-[var(--border)]">
              {chunks
                .filter(c => !query || c.content.toLowerCase().includes(query.toLowerCase()))
                .map(c => {
                  const isExpanded = !!expanded[c.id]
                  const preview = c.content.length > 600 && !isExpanded ? c.content.slice(0, 600) + '…' : c.content
                  return (
                    <li key={c.id} className="py-3">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1">
                          <p className="text-xs text-[color:var(--muted)] mb-1">Doc: {c.document_id}</p>
                          <p className="text-[var(--text)] text-sm whitespace-pre-wrap">
                            {preview}
                          </p>
                          <div className="mt-1 flex items-center gap-2">
                            <button onClick={() => { navigator.clipboard.writeText(c.content); setInfo('Copied chunk') }} className="px-2 py-1 rounded border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] text-xs hover:opacity-90">Copy</button>
                            {c.content.length > 600 && (
                              <button onClick={() => setExpanded(prev => ({ ...prev, [c.id]: !prev[c.id] }))} className="px-2 py-1 rounded border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] text-xs hover:opacity-90">
                                {isExpanded ? 'Show less' : 'Show more'}
                              </button>
                            )}
                          </div>
                        </div>
                        <div className="shrink-0 text-right">
                          <p className="text-xs text-[color:var(--muted)]">By {c.username}</p>
                          {c.created_at && <p className="text-xs text-[color:var(--muted)]">{new Date(c.created_at).toLocaleString()}</p>}
                        </div>
                      </div>
                    </li>
                  )
                })}
            </ul>
            <div className="mt-4 flex items-center justify-between">
              <div className="text-xs text-[color:var(--muted)]">Total chunks: {total}</div>
              <div className="flex items-center gap-2">
                <button disabled={page <= 1} onClick={() => loadChunks(docId || undefined, 1)} className="px-2 py-1 rounded border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] text-xs hover:opacity-90 disabled:opacity-50">First</button>
                <button disabled={page <= 1} onClick={() => loadChunks(docId || undefined, page - 1)} className="px-2 py-1 rounded border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] text-xs hover:opacity-90 disabled:opacity-50">Prev</button>
                <span className="text-xs text-[color:var(--muted)]">{page}/{pages}</span>
                <button disabled={page >= pages} onClick={() => loadChunks(docId || undefined, page + 1)} className="px-2 py-1 rounded border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] text-xs hover:opacity-90 disabled:opacity-50">Next</button>
                <button disabled={page >= pages} onClick={() => loadChunks(docId || undefined, pages)} className="px-2 py-1 rounded border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] text-xs hover:opacity-90 disabled:opacity-50">Last</button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}