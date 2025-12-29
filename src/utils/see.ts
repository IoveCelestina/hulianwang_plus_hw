import { useAuthStore } from '@/stores/auth'

export type SseHandler = (json: any) => void

export async function postSse(url: string, body: any, onData: SseHandler, signal?: AbortSignal) {
  const auth = useAuthStore()

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
    },
    body: JSON.stringify(body),
    signal,
  })

  if (!res.ok || !res.body) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `SSE 请求失败：${res.status}`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    // SSE: 以 \n\n 分隔事件；每行可能以 data: 开头
    const parts = buffer.split('\n\n')
    buffer = parts.pop() || ''

    for (const part of parts) {
      const lines = part.split('\n').map((l) => l.trim())
      for (const line of lines) {
        if (!line.startsWith('data:')) continue
        const raw = line.slice(5).trim()
        if (!raw) continue
        try {
          onData(JSON.parse(raw))
        } catch {
          // 忽略非 JSON data
        }
      }
    }
  }
}
