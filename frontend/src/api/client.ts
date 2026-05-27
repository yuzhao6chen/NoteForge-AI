const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export async function postJson<T>(path: string, data: unknown): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data),
  })
  if (!resp.ok) {
    throw new Error(await getErrorMessage(resp))
  }
  return resp.json()
}

export async function getJson<T>(path: string): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`)
  if (!resp.ok) {
    throw new Error(await getErrorMessage(resp))
  }
  return resp.json()
}

async function getErrorMessage(resp: Response) {
  const text = await resp.text()
  if (!text) return `Request failed: ${resp.status}`

  try {
    const data = JSON.parse(text)
    if (typeof data.detail === 'string') return data.detail
    if (Array.isArray(data.detail)) {
      return data.detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join('；') || text
    }
  } catch {
    return text
  }

  return text
}
