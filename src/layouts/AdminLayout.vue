<template>
  <div class="admin-shell">
    <aside class="sider">
      <div class="brand" @click="go('/admin')">
        <div class="logo">AI</div>
        <div>
          <div class="t1">Admin</div>
          <div class="t2">管理控制台</div>
        </div>
      </div>

      <div class="menu">
        <div class="item" :data-active="is('/admin/categories')" @click="go('/admin/categories')">分类管理</div>
        <div class="item" :data-active="is('/admin/dishes')" @click="go('/admin/dishes')">菜品管理</div>
        <div class="item" :data-active="is('/admin/orders')" @click="go('/admin/orders')">订单管理</div>
        <div class="item" :data-active="is('/admin/reviews')" @click="go('/admin/reviews')">评价管理</div>
      </div>

      <div class="bottom">
        <el-button class="btn" @click="go('/dishes')">切换到用户端</el-button>
      </div>
    </aside>

    <div class="main">
      <header class="topbar">
        <div class="left">SaaS Admin Console</div>
        <div class="right">
          <div class="user">{{ auth.me?.username }}</div>
          <el-button class="btn" @click="logout">退出</el-button>
        </div>
      </header>

      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const is = (p: string) => computed(() => route.path.startsWith(p)).value
const go = (p: string) => router.push(p)
function logout() {
  auth.logout()
  router.replace('/login')
}
</script>

<style scoped lang="scss">
.admin-shell { min-height: 100vh; display:flex; background: var(--app-bg); }
.sider {
  width: 260px;
  background: #0b1220;
  color: #e5e7eb;
  padding: 14px;
  display:flex;
  flex-direction:column;
  gap: 12px;
}
.brand { display:flex; gap: 10px; align-items:center; cursor:pointer; user-select:none; }
.logo {
  width: 38px; height: 38px; border-radius: 12px;
  background: linear-gradient(135deg, var(--app-primary), #6d28d9);
  display:grid; place-items:center; font-weight: 900; color:#fff;
}
.t1 { font-weight: 950; }
.t2 { font-size: 12px; opacity:.7; margin-top: 2px; }
.menu { margin-top: 6px; display:flex; flex-direction:column; gap: 8px; }
.item {
  padding: 10px 12px;
  border-radius: 12px;
  cursor:pointer;
  border: 1px solid rgba(255,255,255,.08);
  background: rgba(255,255,255,.04);
  font-weight: 900;
}
.item[data-active='true'] {
  background: rgba(79,70,229,.22);
  border-color: rgba(79,70,229,.40);
}
.bottom { margin-top: auto; }
.btn { border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.06); color:#fff; font-weight: 900; }
.main { flex:1; display:flex; flex-direction:column; }
.topbar {
  height: 64px;
  display:flex; align-items:center; justify-content:space-between;
  padding: 0 18px;
  border-bottom: 1px solid var(--app-border);
  background: rgba(255,255,255,.7);
  backdrop-filter: blur(10px);
}
.content { padding: 18px; }
.right { display:flex; gap: 10px; align-items:center; }
.user { font-weight: 900; color:#0f172a; }
</style>
