const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'
const REQUEST_TIMEOUT_MS = 600000

export async function postJson<T>(path: string, data: unknown): Promise<T> {
  const resp = await request(path, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data),
  })
  return resp.json()
}

export async function getJson<T>(path: string): Promise<T> {
  const resp = await request(path)
  return resp.json()
}

async function request(path: string, init?: RequestInit) {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  try {
    const resp = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
    })

    if (!resp.ok) {
      throw new Error(await getErrorMessage(resp))
    }

    return resp
  } catch (error) {
    throw normalizeRequestError(error, path)
  } finally {
    window.clearTimeout(timeout)
  }
}

function normalizeRequestError(error: unknown, path: string) {
  if (error instanceof DOMException && error.name === 'AbortError') {
    return new Error(
      [
        '请求超时：模型分析文章用时过长，后端在 10 分钟内没有返回结果。',
        '可以稍后重试，或换用 DeepSeek V4 Flash；如果文章很长，也可以先删掉无关附录后再体检。',
      ].join('\n'),
    )
  }

  if (error instanceof TypeError) {
    return new Error(
      [
        `无法连接后端接口：${API_BASE}${path}`,
        '常见原因：后端服务没有启动、端口不是 8000、VITE_API_BASE 配错，或浏览器被代理/安全策略拦截。',
        '本地启动后端：cd backend，然后运行 .\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --port 8000',
      ].join('\n'),
    )
  }

  if (error instanceof Error) {
    return error
  }

  return new Error('请求失败：发生未知网络错误。')
}

async function getErrorMessage(resp: Response) {
  const text = await resp.text()
  if (!text) return `请求失败：HTTP ${resp.status} ${resp.statusText}`

  try {
    const data = JSON.parse(text)
    const message = typeof data.detail === 'string'
      ? data.detail
      : Array.isArray(data.detail)
        ? data.detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join('；')
        : ''

    const lines = [
      message || `请求失败：HTTP ${resp.status} ${resp.statusText}`,
      data.hint,
      data.code ? `错误代码：${data.code}` : '',
    ].filter(Boolean)

    return lines.join('\n')
  } catch {
    return `请求失败：HTTP ${resp.status} ${resp.statusText}\n${text}`
  }
}
