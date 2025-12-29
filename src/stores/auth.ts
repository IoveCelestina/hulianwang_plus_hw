import { defineStore } from 'pinia'
import request from '@/utils/request'

type AnyObj = Record<string, any>

function pickToken(res: AnyObj): string {
  // 兼容：res.access_token / res.token / res.data.access_token / res.data.token
  const direct = res?.access_token || res?.token
  if (direct) return String(direct)

  const data = res?.data
  const nested = data?.access_token || data?.token
  if (nested) return String(nested)

  return ''
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || '',
    me: null as any,
  }),

  getters: {
    isAuthed: (s) => !!s.token,
  },

  actions: {
    setToken(token: string) {
      this.token = token
      if (token) localStorage.setItem('access_token', token)
      else localStorage.removeItem('access_token')
    },

    logout() {
      this.setToken('')
      this.me = null
    },

    async fetchMe() {
      this.me = await request.get('/users/me')
      return this.me
    },

    async login(payload: { username: string; password: string }) {
      const res = await request.post('/auth/login', payload)
      const token = pickToken(res as AnyObj)
      this.setToken(token)
      if (token) await this.fetchMe()
      return res
    },

    async register(payload: { username: string; password: string; phone?: string }) {
      const res = await request.post('/auth/register', payload)
      const token = pickToken(res as AnyObj)
      this.setToken(token)
      if (token) await this.fetchMe()
      return res
    },
  },
})
