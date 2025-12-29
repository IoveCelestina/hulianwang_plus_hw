import request from '@/utils/request'

export type OrderCreateItemIn = {
  dish_id: number
  quantity: number
  selected_specs: Record<string, any>
}

export type OrderCreateIn = {
  address_id: number
  note?: string | null
  items: OrderCreateItemIn[]
}

export type OrderCreateOut = {
  order_id: number
  status: string
  total_amount: number
}

export type OrderListItem = { id: number; status: string; total_amount: number; created_at?: string | null }
export type OrderListOut = { items: OrderListItem[]; total: number }

export type OrderItemOut = {
  id: number
  dish_id: number
  dish_name: string
  quantity: number
  price_snapshot: number
  selected_specs: Record<string, any>
}

export type OrderDetailOut = {
  id: number
  status: string
  total_amount: number
  note?: string | null
  created_at?: string | null
  address_snapshot: Record<string, any>
  items: OrderItemOut[]
}

export const createOrder = (payload: OrderCreateIn) => request.post('/orders', payload) as Promise<OrderCreateOut>
export const listOrders = () => request.get('/orders') as Promise<OrderListOut>
export const getOrderDetail = (id: number) => request.get(`/orders/${id}`) as Promise<OrderDetailOut>
export const payOrder = (id: number) => request.post(`/orders/${id}/pay`)
export const completeOrder = (id: number) => request.post(`/orders/${id}/complete`)
