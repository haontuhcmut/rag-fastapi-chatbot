let cachedPrefix: string | null = null

export async function detectApiPrefix(): Promise<string> {
  if (cachedPrefix) return cachedPrefix
  const fromEnv = (import.meta.env.VITE_API_PREFIX as string) || ''
  const candidates = [
    '/api/v1',
    '/v1',
    '/api',
    fromEnv,
    '',
  ].filter((x, i, arr) => x !== undefined && arr.indexOf(x) === i)

  for (const prefix of candidates) {
    try {
      const res = await fetch(`${prefix}/health`, { method: 'GET' })
      const contentType = res.headers.get('content-type') || ''
      if (res.ok && contentType.includes('application/json')) {
        cachedPrefix = prefix || ''
        sessionStorage.setItem('api_prefix', cachedPrefix)
        return cachedPrefix
      }
    } catch (_) {}
  }
  cachedPrefix = fromEnv || '/api/v1'
  sessionStorage.setItem('api_prefix', cachedPrefix)
  return cachedPrefix
}

export function getApiPrefixSync(): string {
  if (cachedPrefix) return cachedPrefix
  const fromSession = sessionStorage.getItem('api_prefix')
  const fromEnv = (import.meta.env.VITE_API_PREFIX as string) || ''
  cachedPrefix = fromSession || fromEnv || '/api/v1'
  return cachedPrefix
}

