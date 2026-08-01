import { useEffect, useMemo, useState } from 'react'
import { api } from '../../api/client'
import { getApiPrefixSync } from '../../api/config'

type KnowledgeBase = {
  id: string
  name: string
  description?: string | null
  created_at?: string
}

export default function KnowledgeBases() {
  const [items, setItems] = useState<KnowledgeBase[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [form, setForm] = useState({ name: '', description: '' })

  const prefix = useMemo(() => getApiPrefixSync(), [])

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const { data } = await api.get(`${prefix}/kb/`)
      const records = Array.isArray(data?.items) ? data.items : (Array.isArray(data) ? data : [])
      setItems(records)
    } catch (e) {
      setError('Failed to load knowledge bases')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  async function createKb() {
    if (!form.name.trim()) return
    try {
      await api.post(`${prefix}/kb/`, { name: form.name.trim(), description: form.description || undefined })
      setForm({ name: '', description: '' })
      await load()
    } catch {
      setError('Failed to create knowledge base')
    }
  }

  async function updateKb(kb: KnowledgeBase) {
    try {
      await api.put(`${prefix}/kb/${kb.id}`, { name: kb.name, description: kb.description || '' })
      await load()
    } catch {
      setError('Failed to update knowledge base')
    }
  }

  async function deleteKb(id: string) {
    try {
      await api.delete(`${prefix}/kb/${id}`)
      await load()
    } catch {
      setError('Failed to delete knowledge base')
    }
  }

  return (
    <div className="p-4 text-[var(--text)]">
      <h2 className="text-lg font-semibold">Knowledge Bases</h2>
      <div className="mt-4 grid gap-2">
        <input
          value={form.name}
          onChange={e => setForm(s => ({ ...s, name: e.target.value }))}
          placeholder="Name"
          className="bg-[var(--surface)] border border-[var(--border)] rounded px-3 py-2 text-[var(--text)]"
        />
        <textarea
          value={form.description}
          onChange={e => setForm(s => ({ ...s, description: e.target.value }))}
          placeholder="Description (optional)"
          className="bg-[var(--surface)] border border-[var(--border)] rounded px-3 py-2 text-[var(--text)]"
        />
        <div>
          <button onClick={createKb} className="px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-sm">Create</button>
        </div>
      </div>

      {error && <p className="mt-3 text-red-600 dark:text-red-400 text-sm">{error}</p>}

      <div className="mt-6">
        {loading ? (
          <p className="text-[color:var(--muted)]">Loading…</p>
        ) : items.length === 0 ? (
          <p className="text-[color:var(--muted)]">No knowledge bases yet.</p>
        ) : (
          <ul className="divide-y divide-[var(--border)]">
            {items.map(kb => (
              <li key={kb.id} className="py-3 flex items-start justify-between gap-3">
                <div className="flex-1">
                  <input
                    className="w-full bg-[var(--surface)] border border-[var(--border)] rounded px-3 py-1.5 text-[var(--text)]"
                    value={kb.name}
                    onChange={e => setItems(prev => prev.map(it => it.id === kb.id ? { ...it, name: e.target.value } : it))}
                  />
                  <textarea
                    className="mt-2 w-full bg-[var(--surface)] border border-[var(--border)] rounded px-3 py-1.5 text-[var(--text)]"
                    value={kb.description || ''}
                    onChange={e => setItems(prev => prev.map(it => it.id === kb.id ? { ...it, description: e.target.value } : it))}
                  />
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={() => updateKb(kb)} className="px-2.5 py-1.5 rounded bg-[var(--surface)] text-[var(--text)] text-sm border border-[var(--border)] hover:opacity-90">Save</button>
                  <button onClick={() => deleteKb(kb.id)} className="px-2.5 py-1.5 rounded bg-red-600 text-white text-sm hover:bg-red-500">Delete</button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}