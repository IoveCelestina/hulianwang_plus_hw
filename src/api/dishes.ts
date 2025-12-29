import request from '@/utils/request'

export type Category = { id: number; name: string; sort_order: number }

export type DishListItem = {
  id: number
  name: string
  price: number
  image_url?: string | null
  status: 'on_sale' | 'sold_out' | 'offline' | string
  rating_avg: number
  rating_count: number
  sales_count: number
  ai_highlights: string[]
}

export type DishListOut = { items: DishListItem[]; total: number }

export type DishSpecOut = {
  id: number
  spec_name: string
  spec_values: any[]
}

export type DishDetailOut = {
  id: number
  category_id?: number | null
  name: string
  description?: string | null
  price: number
  image_url?: string | null
  status: string
  rating_avg: number
  rating_count: number
  sales_count: number
  ai_metadata: Record<string, any>
  specs: DishSpecOut[]
}

export const getCategories = () => request.get('/dishes/categories') as Promise<Category[]>
export const getDishes = (params?: { category_id?: number; keyword?: string; status?: string }) =>
  request.get('/dishes', { params }) as Promise<DishListOut>
export const getDishDetail = (id: number) =>
  request.get(`/dishes/${id}`) as Promise<DishDetailOut>
export async function getHomeRecommendations() {
  const res: any = await request.get('/dishes/recommend/home')
  return Array.isArray(res) ? res : (res?.items || res?.data || [])
}
