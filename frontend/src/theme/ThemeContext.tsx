import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'

type ThemeMode = 'light' | 'dark'

type ThemeContextValue = {
  mode: ThemeMode
  setMode: (m: ThemeMode) => void
  toggle: () => void
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

function detectInitialMode(): ThemeMode {
  try {
    const stored = localStorage.getItem('theme_mode')
    if (stored === 'light' || stored === 'dark') return stored
  } catch {}
  if (typeof window !== 'undefined') {
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    return prefersDark ? 'dark' : 'light'
  }
  return 'dark'
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<ThemeMode>(detectInitialMode())

  useEffect(() => {
    const html = document.documentElement
    html.classList.remove('theme-light', 'theme-dark')
    html.classList.add(mode === 'dark' ? 'theme-dark' : 'theme-light')
    try { localStorage.setItem('theme_mode', mode) } catch {}
  }, [mode])

  const value = useMemo<ThemeContextValue>(() => ({
    mode,
    setMode,
    toggle: () => setMode((prev) => (prev === 'dark' ? 'light' : 'dark')),
  }), [mode])

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider')
  return ctx
}