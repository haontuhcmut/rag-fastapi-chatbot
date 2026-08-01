import { Link, Outlet, useLocation } from 'react-router-dom'

export default function AdminLayout() {
  const location = useLocation()
  const isActive = (path: string) => location.pathname === path
  return (
    <div className="h-full flex flex-col bg-[var(--bg)] text-[var(--text)]">
      <div className="h-12 border-b border-[var(--border)] bg-[var(--bg)] flex items-center px-4 gap-4">
        <Link to="/admin/kb" className={`text-sm px-2 py-1.5 rounded ${isActive('/admin/kb') ? 'bg-[var(--surface)] text-[var(--text)]' : 'text-[color:var(--muted)] hover:bg-[var(--surface)]/60'}`}>Knowledge Bases</Link>
        <Link to="/admin/documents" className={`text-sm px-2 py-1.5 rounded ${isActive('/admin/documents') ? 'bg-[var(--surface)] text-[var(--text)]' : 'text-[color:var(--muted)] hover:bg-[var(--surface)]/60'}`}>Documents</Link>
        <Link to="/admin/chunks" className={`text-sm px-2 py-1.5 rounded ${isActive('/admin/chunks') ? 'bg-[var(--surface)] text-[var(--text)]' : 'text-[color:var(--muted)] hover:bg-[var(--surface)]/60'}`}>Chunks</Link>
        <Link to="/admin/embeddings" className={`text-sm px-2 py-1.5 rounded ${isActive('/admin/embeddings') ? 'bg-[var(--surface)] text-[var(--text)]' : 'text-[color:var(--muted)] hover:bg-[var(--surface)]/60'}`}>Embeddings</Link>
      </div>
      <div className="flex-1 min-h-0 overflow-auto">
        <Outlet />
      </div>
    </div>
  )
}