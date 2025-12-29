import request from '@/utils/request'

export type CartItemOut = {
  id: number
  dish_id: number
  dish_name: string
  price: number
  quantity: number
  selected_specs: Record<string, any>
}

export type CartOut = {
  items: CartItemOut[]
  total_amount: number
}

export const getCart = () => request.get('/cart') as Promise<CartOut>

export const addCartItem = (payload: { dish_id: number; quantity: number; selected_specs?: Record<string, any> }) =>
  request.post('/cart/items', { ...payload, selected_specs: payload.selected_specs || {} })

export const updateCartItem = (item_id: number, payload: { quantity?: number; selected_specs?: Record<string, any> }) =>
  request.put(`/cart/items/${item_id}`, payload)

export const removeCartItem = (item_id: number) => request.delete(`/cart/items/${item_id}`)
