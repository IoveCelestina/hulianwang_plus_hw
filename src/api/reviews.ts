import request from '@/utils/request'

export type ReviewOut = {
  id: number
  dish_id: number
  rating: number
  content?: string | null
  created_at?: string
  user?: { id: number; username?: string } | null
}

export function getDishReviews(dishId: number) {
  return request.get(`/reviews/dish/${dishId}`) as Promise<ReviewOut[]>
}

export function createReview(payload: { dish_id: number; rating: number; content?: string }) {
  return request.post('/reviews', payload) as Promise<ReviewOut>
}
