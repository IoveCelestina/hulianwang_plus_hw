<template>
  <div class="page">
    <div class="page-head">
      <div class="hgroup">
        <div class="h1">我的订单</div>
        <div class="h2">查看状态、支付与完成</div>
      </div>
      <el-button class="btn" @click="goDishes">返回菜单</el-button>
    </div>

    <el-card class="panel" shadow="never" v-loading="loading">
      <div v-if="items.length === 0 && !loading" class="empty">
        <div class="empty-title">暂无订单</div>
        <div class="empty-sub">下单后会显示在这里</div>
        <el-button class="btn-primary" @click="goDishes">去点餐</el-button>
      </div>

      <div v-else class="list">
        <div class="row" v-for="o in items" :key="o.id" @click="open(o.id)">
          <div class="left">
            <div class="id">#{{ o.id }}</div>
            <div class="time">{{ o.created_at || '-' }}</div>
          </div>
          <div class="right">
            <el-tag :type="tagType(o.status)" effect="light">{{ statusText(o.status) }}</el-tag>
            <div class="money">¥ {{ o.total_amount.toFixed(0) }}</div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { listOrders, type OrderListItem } from '@/api/orders'

const loading = ref(false)
const items = ref<OrderListItem[]>([])

onMounted(() => cart.refresh())


function open(id: number) {
  window.location.href = `/orders/${id}`
}
function goDishes() {
  window.location.href = '/dishes'
}
function statusText(s: string) {
  if (s === 'pending') return '待支付'
  if (s === 'paid') return '已支付'
  if (s === 'completed') return '已完成'
  if (s === 'cancelled') return '已取消'
  return s
}
function tagType(s: string) {
  if (s === 'pending') return 'warning'
  if (s === 'paid') return 'success'
  if (s === 'completed') return 'info'
  if (s === 'cancelled') return 'danger'
  return ''
}
</script>

<style scoped lang="scss">
.page { padding: 18px; max-width: 1100px; margin: 0 auto; }
.page-head { display:flex; align-items:flex-end; justify-content:space-between; gap:14px; margin-bottom:14px; }
.hgroup .h1 { font-size:22px; font-weight:950; }
.hgroup .h2 { margin-top:6px; color:var(--app-muted); font-size:13px; }
.panel { border-radius:12px; border:1px solid var(--app-border); background:rgba(255,255,255,.78); backdrop-filter: blur(10px); }
.list { display:flex; flex-direction:column; gap:10px; }
.row {
  display:flex; justify-content:space-between; align-items:center; gap:12px;
  padding:12px; border-radius:12px; border:1px solid var(--app-border); background:#fff;
  cursor:pointer; transition: transform .12s ease, box-shadow .12s ease;
}
.row:hover { transform: translateY(-2px); box-shadow: 0 18px 45px rgba(17,24,39,.08); }
.left .id { font-weight:950; }
.left .time { margin-top:6px; color:var(--app-muted); font-size:12px; }
.right { display:flex; align-items:center; gap:12px; }
.money { font-weight:950; color:var(--app-primary); }
.btn { border-radius:10px; border:1px solid var(--app-border); }
.btn-primary {
  border-radius: 10px; border: 1px solid rgba(99, 102, 241, 0.25);
  background: linear-gradient(135deg, rgba(99,102,241,.95), rgba(109,40,217,.95)); color:#fff;
}
.empty { padding:46px 0; text-align:center; }
.empty-title { font-size:16px; font-weight:950; }
.empty-sub { margin-top:6px; color:var(--app-muted); }
</style>
