<template>
  <div class="page">
    <div class="head">
      <el-button class="btn" @click="back">返回</el-button>
      <div class="title">订单详情</div>
    </div>

    <el-card class="panel" shadow="never" v-loading="loading">
      <div v-if="order" class="grid">
        <div class="row"><span class="k">订单号</span><b class="v">#{{ order.id }}</b></div>
        <div class="row"><span class="k">状态</span><b class="v">{{ order.status }}</b></div>
        <div class="row"><span class="k">总金额</span><b class="v money">¥ {{ order.total_amount?.toFixed?.(0) ?? order.total_amount }}</b></div>
        <div class="row"><span class="k">创建时间</span><b class="v">{{ order.created_at || '-' }}</b></div>

        <div class="section">明细</div>
        <el-table :data="order.items || []" border style="width: 100%">
          <el-table-column prop="dish_id" label="菜品ID" width="110" />
          <el-table-column prop="dish_name" label="菜品名" min-width="160" />
          <el-table-column prop="quantity" label="数量" width="90" />
          <el-table-column prop="unit_price" label="单价" width="120" />
          <el-table-column label="规格" min-width="220">
            <template #default="{ row }">
              <span class="muted">{{ formatSpec(row.spec_snapshot) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-else class="empty">
        <div class="empty-title">未找到订单</div>
        <div class="empty-sub">请检查订单是否存在</div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const order = ref<any>(null)

onMounted(() => load())

async function load() {
  loading.value = true
  try {
    const id = Number(route.params.id)
    order.value = await request.get(`/orders/${id}`)
  } finally {
    loading.value = false
  }
}

function back() {
  router.back()
}

function formatSpec(s: any) {
  if (!s) return '-'
  if (typeof s === 'string') return s
  if (typeof s === 'object') return Object.entries(s).map(([k, v]) => `${k}:${v}`).join('，')
  return String(s)
}
</script>

<style scoped lang="scss">
.page { padding: 18px; max-width: 1100px; margin: 0 auto; }
.head { display:flex; align-items:center; gap: 12px; margin-bottom: 12px; }
.title { font-size: 18px; font-weight: 950; }
.panel { border-radius: 12px; border: 1px solid var(--app-border); background: rgba(255,255,255,.78); backdrop-filter: blur(10px); }
.grid { display:flex; flex-direction:column; gap: 10px; }
.row { display:flex; justify-content:space-between; gap: 10px; padding: 10px; border: 1px solid var(--app-border); border-radius: 12px; background:#fff; }
.k { color: var(--app-muted); font-weight: 900; }
.v { font-weight: 950; }
.money { color: var(--app-primary); }
.section { margin-top: 10px; font-weight: 950; }
.muted { color: var(--app-muted); font-size: 12px; }
.btn { border-radius: 10px; border: 1px solid var(--app-border); font-weight: 900; }
.empty { padding: 50px 0; text-align:center; }
.empty-title { font-weight: 950; }
.empty-sub { margin-top: 6px; color: var(--app-muted); }
</style>
