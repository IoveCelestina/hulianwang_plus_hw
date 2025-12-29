import request from '@/utils/request'

export type AiSessionOut = { session_id: number }
export type AiMessageIn = { content: string }

export const createSession = () => request.post('/ai/sessions', {}) as Promise<AiSessionOut>
export const sendMessage = (sessionId: number, payload: AiMessageIn) =>
  request.post(`/ai/sessions/${sessionId}/messages`, payload)

export const streamMessageUrl = (sessionId: number) =>
  (import.meta.env.VITE_API_BASE_URL || '/api') + `/ai/sessions/${sessionId}/messages:stream`
