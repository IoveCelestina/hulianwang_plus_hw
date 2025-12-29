import request from '@/utils/request'

export type AdminCategory = { id: number; name: string; sort_order: number }
export type AdminDish = {
  id: number
  category_id: number
  name: string
  description?: string | null
  price: number
  image_url?: string | null
  status: string
  ai_metadata?: Record<string, any>
}
export type AdminOrder = { id: number; status: string; total_amount: number; created_at?: string | null }
export type AdminReview = { id: number; dish_id: number; user_id: number; rating: number; comment?: string | null; created_at?: string | null }

export const adminListCategories = () => request.get('/admin/categories') as Promise<AdminCategory[]>
export const adminCreateCategory = (payload: { name: string; sort_order: number }) =>
  request.post('/admin/categories', payload) as Promise<AdminCategory>

export const adminListDishes = () => request.get('/admin/dishes') as Promise<{ items: AdminDish[]; total: number }>
export const adminCreateDish = (payload: Partial<AdminDish>) => request.post('/admin/dishes', payload) as Promise<AdminDish>
export const adminUpdateDish = (id: number, payload: Partial<AdminDish>) => request.put(`/admin/dishes/${id}`, payload) as Promise<AdminDish>

export const adminListOrders = () => request.get('/admin/orders') as Promise<{ items: AdminOrder[]; total: number }>
export const adminUpdateOrderStatus = (id: number, payload: { status: string }) =>
  request.put(`/admin/orders/${id}/status`, payload)

export const adminListReviews = () => request.get('/admin/reviews') as Promise<{ items: AdminReview[]; total: number }>
