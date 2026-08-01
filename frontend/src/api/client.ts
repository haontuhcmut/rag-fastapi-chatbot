import axios from 'axios'
import { getApiPrefixSync } from './config'

const apiBase = import.meta.env.VITE_API_BASE || '' // use dev proxy when empty

export const api = axios.create({
  baseURL: apiBase,
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export function setAccessToken(token: string | null) {
  if (!token) {
    localStorage.removeItem('access_token')
    return
  }
  localStorage.setItem('access_token', token)
}

export function setRefreshToken(token: string | null) {
  if (!token) {
    localStorage.removeItem('refresh_token')
    return
  }
  localStorage.setItem('refresh_token', token)
}

// Token refresh handling
let isRefreshing = false
let pendingSubscribers: Array<(token: string | null) => void> = []

function subscribeTokenRefresh(cb: (token: string | null) => void) {
  pendingSubscribers.push(cb)
}

function onRefreshed(token: string | null) {
  pendingSubscribers.forEach((cb) => cb(token))
  pendingSubscribers = []
}

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) return null
  const prefix = getApiPrefixSync()
  try {
    const res = await axios.get(`${prefix}/oauth/refresh_token`, {
      headers: { Authorization: `Bearer ${refreshToken}` },
      withCredentials: true,
    })
    const newAccess = res.data?.access_token ?? res.data?.accessToken ?? ''
    if (newAccess) {
      setAccessToken(newAccess)
      return newAccess
    }
    return null
  } catch (e) {
    // Clear tokens on hard failure
    try { setAccessToken(null) } catch {}
    try { setRefreshToken(null) } catch {}
    return null
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { response, config } = error || {}
    if (!response) throw error
    // Only handle unauthorized
    if (response.status !== 401) throw error
    const url: string = (config && (config as any).url) || ''
    const isAuthEndpoint = /\/oauth\/(login|signup|reset-password-request|reset-password-confirm|verify)/.test(url)
    // Do not attempt token refresh for auth endpoints like login/signup/reset/verify
    if (isAuthEndpoint) throw error
    // Only attempt refresh if the original request had an Authorization header (i.e., it used the access token)
    const hadAuthHeader = !!(config && config.headers && ((config.headers as any).Authorization || (config.headers as any)['Authorization']))
    if (!hadAuthHeader) throw error
    // Avoid infinite retry loops
    if ((config as any).__isRetry) throw error

    if (!isRefreshing) {
      isRefreshing = true
      const newToken = await refreshAccessToken()
      isRefreshing = false
      onRefreshed(newToken)
      if (!newToken) {
        throw error
      }
    }

    return new Promise((resolve, reject) => {
      subscribeTokenRefresh((token) => {
        if (!token) {
          reject(error)
          return
        }
        const newConfig = {
          ...config,
          headers: { ...(config.headers || {}), Authorization: `Bearer ${token}` },
        }
        ;(newConfig as any).__isRetry = true
        resolve(api(newConfig))
      })
    })
  }
)

// Helpers to call auth endpoints that might be either root-scoped or version-prefixed
export async function postAuth<T = any>(path: string, body: any) {
  const prefix = getApiPrefixSync()
  const candidates = [
    `${prefix}${path.startsWith('/') ? path : `/${path}`}`,
    `${path.startsWith('/') ? path : `/${path}`}`,
  ]
  for (const url of candidates) {
    try {
      // Use raw axios to avoid response interceptor triggering refresh on 401 for auth endpoints
      const res = await axios.post<T>(url, body)
      return res
    } catch (e: any) {
      if (e?.response?.status === 404) continue
      throw e
    }
  }
  // If both 404, throw last error
  throw new Error('Auth endpoint not found at expected prefixes')
}


