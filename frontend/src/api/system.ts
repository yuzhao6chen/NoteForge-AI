const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'
const HEALTH_TIMEOUT_MS = 2500

export interface HealthStatus {
  status: string
  service: string
}

export function getHealth() {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), HEALTH_TIMEOUT_MS)

  return fetch(`${API_BASE}/api/health`, { signal: controller.signal })
    .then(resp => {
      if (!resp.ok) throw new Error(`Health check failed: ${resp.status}`)
      return resp.json() as Promise<HealthStatus>
    })
    .finally(() => window.clearTimeout(timeout))
}
