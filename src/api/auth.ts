import request from '@/utils/request'

export type AuthOut = {
  user_id: number
  access_token: string
  token_type: string
}

export const login = (payload: { username: string; password: string }) =>
  request.post('/auth/login', payload) as Promise<AuthOut>

export const register = (payload: { username: string; password: string; phone?: string }) =>
  request.post('/auth/register', payload) as Promise<AuthOut>
