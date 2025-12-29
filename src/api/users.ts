import request from '@/utils/request'

export type UserMe = {
  id: number
  username: string
  phone?: string | null
  role: 'user' | 'admin'
}

export type UserPreferences = {
  explicit_tags: string[]
  dietary_restrictions: string[]
  implicit_profile?: Record<string, any>
}

export const getMe = () => request.get('/users/me') as Promise<UserMe>
export const getPreferences = () => request.get('/users/preferences') as Promise<UserPreferences>
export const updatePreferences = (payload: Partial<UserPreferences>) =>
  request.put('/users/preferences', payload) as Promise<UserPreferences>
