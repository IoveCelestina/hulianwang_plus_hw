<!-- src/layouts/AppLayout.vue -->
<template>
  <div class="app-shell">
    <header class="app-topbar">
      <div class="brand" @click="$router.push('/dishes')">
        <div class="logo">AI</div>
        <div class="title">Smart Ordering</div>
      </div>

      <div class="topbar-actions">
        <el-button class="ghost" :icon="Menu" circle @click="goDishes" />
        <el-badge :value="cart.count" :max="99" class="badge">
          <el-button class="primary-soft" :icon="ShoppingCart" circle @click="goCart" />
        </el-badge>

        <el-dropdown>
          <div class="user-chip">
            <div class="avatar">{{ initials }}</div>
            <div class="meta">
              <div class="name">{{ auth.me?.username || 'User' }}</div>
              <div class="sub">点餐用户</div>
            </div>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { Menu, ShoppingCart } from '@element-plus/icons-vue'

const auth = useAuthStore()
const cart = useCartStore()

const initials = computed(() => (auth.me?.username?.slice(0, 1) || 'U').toUpperCase())

onMounted(async () => {
  // 顶栏角标需要
  await cart.refresh()

})

function goCart() {
  window.location.href = '/cart'
}
function goDishes() {
  window.location.href = '/dishes'
}
function logout() {
  auth.logout()
  window.location.href = '/login'
}
</script>

<style scoped lang="scss">
.app-shell {
  min-height: 100vh;
  background: var(--app-bg);
  color: var(--app-text);
}
.app-topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 18px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--app-border);
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}
.logo {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--app-primary), #6d28d9);
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 800;
}
.title {
  font-weight: 800;
  letter-spacing: 0.3px;
}
.topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.user-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  border-radius: 12px;
  border: 1px solid var(--app-border);
  background: rgba(255, 255, 255, 0.6);
  cursor: pointer;
}
.avatar {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: #111827;
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 700;
}
.meta .name {
  font-size: 13px;
  font-weight: 700;
  line-height: 1.1;
}
.meta .sub {
  font-size: 12px;
  color: var(--app-muted);
}
.badge :deep(.el-badge__content) {
  border: none;
}
.ghost {
  border: 1px solid var(--app-border);
  background: #fff;
}
.primary-soft {
  border: 1px solid rgba(99, 102, 241, 0.25);
  background: rgba(99, 102, 241, 0.12);
}
</style>
