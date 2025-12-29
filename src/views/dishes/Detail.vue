<template>
  <div class="page" v-loading="loading">
    <div class="back">
      <el-button class="btn" @click="back">返回</el-button>
      <el-button class="btn" @click="goCart">购物车</el-button>
    </div>

    <div v-if="dish" class="wrap">
      <el-card class="left" shadow="never">
        <div class="hero">
          <img v-if="dish.image_url" :src="dish.image_url" alt="" />
          <div v-else class="ph">No Image</div>
          <div class="status-pill" :data-status="dish.status">{{ statusText(dish.status) }}</div>
        </div>

        <div class="info">
          <div class="title-row">
            <div class="name">{{ dish.name }}</div>
            <div class="price">¥ {{ dish.price.toFixed(0) }}</div>
          </div>

          <div class="desc">{{ dish.description || '—' }}</div>

          <div class="highlights" v-if="dish.ai_metadata?.highlights?.length">
            <el-tag v-for="(t, i) in dish.ai_metadata.highlights.slice(0, 5)" :key="i" class="tag" effect="light">
              {{ t }}
            </el-tag>
          </div>

          <div class="kpis">
            <div class="kpi">销量 {{ dish.sales_count ?? 0 }}</div>
            <div class="kpi">评分 {{ (dish.rating_avg ?? 0).toFixed(1) }}（{{ dish.rating_count ?? 0 }}）</div>
          </div>
        </div>
      </el-card>

      <el-card class="right" shadow="never">
        <div class="section-title">选择规格</div>

        <SpecPicker v-model="specDraft" :specs="dish.specs || []" :required="true" :showDelta="true" />

        <div class="qty">
          <div class="label">数量</div>
          <el-input-number v-model="quantity" :min="1" :max="99" />
        </div>

        <div class="sumline">
          <span class="muted">预计金额</span>
          <b class="money">¥ {{ (dish.price * quantity).toFixed(0) }}</b>
        </div>

        <div class="actions">
          <el-button class="btn" @click="goCart">去购物车</el-button>
          <el-button
            class="btn-primary"
            :disabled="dish.status !== 'on_sale'"
            :loading="adding"
            @click="addToCart"
          >
            加入购物车
          </el-button>
        </div>

        <div class="tip">
          规格加价字段后端已预留；若要“规格加价计入订单总价”，我可以继续把价格链路补齐。
        </div>
      </el-card>
    </div>
  </div>
  <ReviewsPanel v-if="dish" :dishId="dish.id" style="margin-top:14px;" />
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getDishDetail, type DishDetailOut, type DishSpecOut } from '@/api/dishes'
import { useCartStore } from '@/stores/cart'
import SpecPicker from '@/components/SpecPicker/index.vue'
import ReviewsPanel from '@/components/ReviewsPanel.vue'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()

const loading = ref(false)
const adding = ref(false)

const dish = ref<DishDetailOut | null>(null)
const quantity = ref(1)
const specDraft = ref<Record<string, any>>({})

onMounted(async () => {
  const id = Number(route.params.id)
  await load(id)
})

async function load(id: number) {
  loading.value = true
  try {
    dish.value = await getDishDetail(id)
    quantity.value = 1
    specDraft.value = {} // SpecPicker 会自动补齐默认第一项
  } finally {
    loading.value = false
  }
}

function statusText(s: string) {
  if (s === 'on_sale') return '在售'
  if (s === 'sold_out') return '售罄'
  if (s === 'offline') return '下架'
  return s
}

function validateRequiredSpecs(specs: DishSpecOut[], selected: Record<string, any>) {
  for (const s of specs || []) {
    const key = s.spec_name
    const hasOptions = Array.isArray(s.spec_values) && s.spec_values.length > 0
    if (!hasOptions) continue
    const v = selected?.[key]
    if (v === undefined || v === null || v === '') {
      ElMessage.warning(`请选择：${key}`)
      return false
    }
  }
  return true
}

async function addToCart() {
  if (!dish.value) return

  // 校验规格必选
  if (!validateRequiredSpecs(dish.value.specs || [], specDraft.value || {})) return

  adding.value = true
  try {
    await cart.add({
      dish_id: dish.value.id,
      quantity: quantity.value,
      spec_snapshot: specDraft.value || {},
    })
    ElMessage.success('已加入购物车')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.response?.data?.message || '加购失败')
  } finally {
    adding.value = false
  }
}


function back() {
  router.back()
}
function goCart() {
  router.push('/cart')
}
</script>

<style scoped lang="scss">
.page { padding: 18px; max-width: 1200px; margin: 0 auto; }
.back { display:flex; gap:10px; margin-bottom: 12px; }

.wrap { display:grid; grid-template-columns: 1.35fr 1fr; gap: 12px; }
@media (max-width: 980px) { .wrap { grid-template-columns: 1fr; } }

.left, .right {
  border-radius: 12px;
  border: 1px solid var(--app-border);
  background: rgba(255,255,255,.78);
  backdrop-filter: blur(10px);
}

.hero {
  position: relative;
  height: 320px;
  overflow: hidden;
  border-radius: 12px;
  background: #f3f4f6;
}
.hero img { width: 100%; height: 100%; object-fit: cover; }
.ph { height: 100%; display:grid; place-items:center; color:#9ca3af; font-weight: 800; }

.status-pill {
  position:absolute; left:10px; top:10px;
  padding: 6px 10px; border-radius: 999px;
  font-size: 12px; font-weight: 900; color:#fff;
  background: rgba(17,24,39,.75);
}
.status-pill[data-status='on_sale'] { background: rgba(16,185,129,.85); }
.status-pill[data-status='sold_out'] { background: rgba(245,158,11,.85); }
.status-pill[data-status='offline'] { background: rgba(107,114,128,.85); }

.info { padding: 14px 2px 4px; }
.title-row { display:flex; justify-content:space-between; align-items:baseline; gap:10px; }
.name { font-size: 20px; font-weight: 950; }
.price { font-size: 18px; font-weight: 950; color: var(--app-primary); }
.desc { margin-top: 10px; color: var(--app-muted); }

.highlights { margin-top: 12px; display:flex; gap:6px; flex-wrap:wrap; }
.tag { border-radius: 999px; }

.kpis { margin-top: 12px; display:flex; gap: 8px; flex-wrap: wrap; }
.kpi {
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid var(--app-border);
  background: #fff;
  font-size: 12px;
  font-weight: 900;
  color: #374151;
}

.section-title { font-weight: 950; font-size: 15px; margin-bottom: 10px; }
.qty { margin-top: 16px; display:flex; align-items:center; justify-content:space-between; }
.qty .label { font-size: 12px; font-weight: 900; color:#0f172a; }

.sumline {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--app-border);
  display:flex; justify-content:space-between; align-items:baseline;
}
.muted { color: var(--app-muted); font-size: 12px; }
.money { color: var(--app-primary); font-weight: 950; }

.actions { margin-top: 14px; display:flex; justify-content:flex-end; gap: 10px; }
.btn { border-radius: 10px; border: 1px solid var(--app-border); font-weight: 900; }
.btn-primary {
  border-radius: 10px;
  border: 1px solid rgba(99,102,241,.25);
  background: linear-gradient(135deg, rgba(99,102,241,.95), rgba(109,40,217,.95));
  color: #fff;
  font-weight: 900;
}
.tip { margin-top: 12px; font-size: 12px; color: var(--app-muted); line-height: 1.5; }
</style>
