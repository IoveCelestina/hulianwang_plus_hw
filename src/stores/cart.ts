import { defineStore } from 'pinia'
import request from '@/utils/request'

export type CartItemVM = {
  id: number
  dish_id: number
  name: string
  image_url?: string | null
  quantity: number
  unit_price: number
  spec_snapshot?: any
}

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [] as CartItemVM[],
    totalAmount: 0,
    loaded: false,
    loading: false,
  }),

  getters: {
    count: (s) => s.items.reduce((sum, it) => sum + (it.quantity || 0), 0),
    isEmpty: (s) => s.items.length === 0,
  },

  actions: {
    async refresh() {
      this.loading = true
      try {
        const res = (await request.get('/cart')) as any // ✅ GET /api/cart
        this.items = (res.items || []).map((it: any) => ({
          id: Number(it.id),
          dish_id: Number(it.dish_id),
          name: it.dish_name || it.name || `Dish #${it.dish_id}`,
          image_url: it.dish_image_url || it.image_url || null,
          quantity: Number(it.quantity ?? 1),
          unit_price: Number(it.unit_price ?? 0),
          spec_snapshot: it.spec_snapshot || it.spec || {},
        }))
        this.totalAmount = Number(res.total_amount ?? 0) // ✅ total_amount
        this.loaded = true
        return res
      } finally {
        this.loading = false
      }
    },

    async add(payload: { dish_id: number; quantity?: number; spec_snapshot?: any }) {
      await request.post('/cart/items', {
        dish_id: payload.dish_id,
        quantity: payload.quantity ?? 1,
        spec_snapshot: payload.spec_snapshot ?? {},
      })
      await this.refresh()
    },

    async updateItem(itemId: number, payload: { quantity?: number; spec_snapshot?: any }) {
      await request.put(`/cart/items/${itemId}`, payload)
      await this.refresh()
    },

    async removeItem(itemId: number) {
      await request.delete(`/cart/items/${itemId}`)
      await this.refresh()
    },

    clearLocal() {
      this.items = []
      this.totalAmount = 0
      this.loaded = false
    },
  },
})
