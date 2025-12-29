import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/layouts/AppLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'

const routes: RouteRecordRaw[] = [
  { path: '/login', name: 'Login', component: () => import('@/views/auth/Login.vue'), meta: { public: true } },
  { path: '/register', name: 'Register', component: () => import('@/views/auth/Register.vue'), meta: { public: true } },

  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dishes' },
      { path: '/dishes', name: 'DishList', component: () => import('@/views/dishes/List.vue') },
      { path: '/dishes/:id', name: 'DishDetail', component: () => import('@/views/dishes/Detail.vue') },
      { path: '/cart', name: 'Cart', component: () => import('@/views/cart/Index.vue') },
      { path: '/checkout', name: 'Checkout', component: () => import('@/views/checkout/Index.vue') },
      { path: '/orders', name: 'OrderList', component: () => import('@/views/orders/List.vue') },
      { path: '/orders/:id', name: 'OrderDetail', component: () => import('@/views/orders/Detail.vue') },
      { path: '/profile/preferences', name: 'Preferences', component: () => import('@/views/profile/Preferences.vue') },
      { path: '/profile/addresses', name: 'Addresses', component: () => import('@/views/profile/Addresses.vue') },
      { path: '/ai/chat', name: 'AiChat', component: () => import('@/views/ai/Chat.vue') },
    ],
  },

  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, roles: ['admin'] },
    children: [
      { path: '', redirect: '/admin/categories' },
      { path: 'categories', component: () => import('@/views/admin/Categories.vue') },
      { path: 'dishes', component: () => import('@/views/admin/Dishes.vue') },
      // 你若已按我之前的订单/评价页加入，也可以继续挂：
      // { path: 'orders', component: () => import('@/views/admin/Orders.vue') },
      // { path: 'reviews', component: () => import('@/views/admin/Reviews.vue') },
    ],
  },

  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.public) return true
  if (!auth.token) return { path: '/login', query: { redirect: to.fullPath } }

  if (!auth.meLoaded) {
    try {
      await auth.fetchMe()
    } catch {
      return { path: '/login', query: { redirect: to.fullPath } }
    }
  }

  const roles = (to.meta.roles as string[] | undefined) || []
  if (roles.length && !roles.includes(auth.role)) {
    return { path: '/dishes' }
  }

  return true
})

router.beforeEach((to) => {
  const token = localStorage.getItem('access_token')
  const needAuth = ['/cart', '/checkout', '/orders', '/profile'].some((p) => to.path.startsWith(p))
  if (needAuth && !token) return '/login'
})


export default router
