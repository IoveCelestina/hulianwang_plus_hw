import request from '@/utils/request'

export type AiSessionOut = {
  id: number
  title?: string | null
  created_at?: string
}

export type AiMessageOut = {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at?: string
}

export function listAiSessions() {
  return request.get('/ai/sessions') as Promise<AiSessionOut[]>
}

export function createAiSession(payload?: { title?: string }) {
  return request.post('/ai/sessions', payload || {}) as Promise<AiSessionOut>
}

export function getAiMessages(sessionId: number) {
  return request.get(`/ai/sessions/${sessionId}/messages`) as Promise<AiMessageOut[]>
}

export function postAiMessage(sessionId: number, payload: { content: string }) {
  return request.post(`/ai/sessions/${sessionId}/messages`, payload) as Promise<AiMessageOut[] | any>
}

/**
 * SSE 流式：后端有 /messages:stream
 * 这里用原生 EventSource 做（需要后端支持 token 传 query 或 cookie）。
 * 如果你后端要求 Authorization header，那 EventSource 不支持 header，需要改成 fetch + ReadableStream。
 */
export function streamAiMessage(sessionId: number, content: string) {
  const token = localStorage.getItem('access_token') || ''
  const url = `/api/ai/sessions/${sessionId}/messages:stream?content=${encodeURIComponent(content)}&token=${encodeURIComponent(token)}`
  return new EventSource(url)
}
