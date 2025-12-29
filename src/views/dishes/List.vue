<template>
  <div class="page">
    <div class="page-head">
      <div class="hgroup">
        <div class="h1">今日菜单</div>
        <div class="h2">分类浏览 · 关键词搜索 · 一键加购</div>
      </div>

      <div class="filters">
        <el-input
          v-model="keyword"
          placeholder="搜索菜品名称…"
          clearable
          class="search"
          @keyup.enter="load"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select v-model="status" placeholder="状态" class="status" clearable @change="load">
          <el-option label="在售" value="on_sale" />
          <el-option label="售罄" value="sold_out" />
          <el-option label="下架" value="offline" />
        </el-select>

        <el-button class="btn" :loading="loading" @click="load">刷新</el-button>
      </div>
    </div>

    <!-- AI 推荐 -->
    <el-card class="panel" shadow="never" style="margin-bottom: 12px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
        <div style="font-weight:950;">为你推荐</div>
        <el-button class="btn" :loading="recLoading" @click="loadRecs">换一批</el-button>
      </div>

      <div v-loading="recLoading" style="display:flex;gap:10px;overflow:auto;padding-bottom:4px;">
        <div
          v-for="r in recs"
          :key="r.id"
          style="min-width:220px;border:1px solid var(--app-border);border-radius:12px;padding:10px;background:#fff;cursor:pointer;"
          @click="goDetail(r.id)"
        >
          <div style="font-weight:900;">{{ r.name }}</div>
          <div style="margin-top:6px;color:var(--app-muted);font-size:12px;min-height:16px;">
            {{ (r.ai_highlights && r.ai_highlights[0]) || r.description || '—' }}
          </div>
          <div style="margin-top:8px;font-weight:950;color:var(--app-primary);">
            ¥ {{ Number(r.price || 0).toFixed(0) }}
          </div>
        </div>

        <div v-if="!recLoading && recs.length === 0" style="color:var(--app-muted);font-size:12px;">
          暂无推荐
        </div>
      </div>
    </el-card>

    <!-- 菜品列表 -->
    <el-card class="panel" shadow="never">
      <div class="tabs-row">
        <el-segmented v-model="activeCategoryId" :options="categoryOptions" @change="load" />
        <div class="right">
          <div class="total">共 {{ total }} 项</div>
        </div>
      </div>

      <div v-loading="loading" class="grid">
        <div v-if="!loading && dishes.length === 0" class="empty">
          <div class="empty-title">没有找到相关菜品</div>
          <div class="empty-sub">换个关键词或切换分类试试</div>
          <el-button class="btn-primary" @click="reset">重置筛选</el-button>
        </div>

        <div v-for="d in dishes" :key="d.id" class="card" @click="goDetail(d.id)">
          <div class="thumb">
            <img v-if="d.image_url" :src="d.image_url" alt="" />
            <div v-else class="ph">No Image</div>
            <div class="status-pill" :data-status="d.status">{{ statusText(d.status) }}</div>
          </div>

          <div class="body">
            <div class="top">
              <div class="name">{{ d.name }}</div>
              <div class="price">¥ {{ d.price.toFixed(0) }}</div>
            </div>

            <div class="highlights" v-if="d.ai_highlights?.length">
              <el-tag
                v-for="(t, idx) in d.ai_highlights.slice(0, 3)"
                :key="idx"
                class="tag"
                effect="light"
              >
                {{ t }}
              </el-tag>
            </div>
            <div v-else class="desc muted">—</div>

            <div class="meta">
              <div class="mitem">销量 {{ d.sales_count ?? 0 }}</div>
              <div class="mitem">评分 {{ (d.rating_avg ?? 0).toFixed(1) }}（{{ d.rating_count ?? 0 }}）</div>
            </div>

            <div class="actions" @click.stop>
              <el-button class="btn" @click.stop.prevent="goDetail(d.id)">查看</el-button>
              <el-button
                class="btn-primary"
                :disabled="d.status !== 'on_sale'"
                :loading="addingId === d.id"
                @click.stop.prevent="openAddDrawer(d.id)"
              >
                加购
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 加购 Drawer -->
    <el-drawer
      v-model="addDrawerVisible"
      title="加入购物车"
      size="420px"
      class="pro-drawer"
      :append-to-body="true"
      :modal-append-to-body="true"
      destroy-on-close
    >
      <div class="drawer-wrap">
        <div v-loading="drawerLoading" class="drawer-body">
          <div v-if="drawerDish" class="dish-mini">
            <div class="mini-left">
              <div class="mini-name">{{ drawerDish.name }}</div>
              <div class="mini-sub">
                <span class="pill" :data-status="drawerDish.status">{{ statusText(drawerDish.status) }}</span>
                <span class="money">¥ {{ drawerDish.price.toFixed(0) }}</span>
              </div>
            </div>
          </div>

          <div class="section-title">选择规格</div>
          <SpecPicker v-model="specDraft" :specs="drawerSpecs" :required="true" :showDelta="true" />

          <div class="qty">
            <div class="label">数量</div>
            <el-input-number v-model="quantity" :min="1" :max="99" />
          </div>

          <div class="sumline">
            <span class="muted">预计金额</span>
            <b class="money">¥ {{ estAmount.toFixed(0) }}</b>
          </div>

          <div class="drawer-tip">
            规格加价字段后端已预留；若你后续要做“规格加价计入总价”，我可以把前端与后端一起补齐。
          </div>
        </div>

        <div class="drawer-footer">
          <el-button class="btn" @click="addDrawerVisible = false">取消</el-button>
          <el-button class="btn-primary" :loading="drawerSaving" @click="confirmAdd">
            加入购物车
          </el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import SpecPicker from '@/components/SpecPicker/index.vue'
import { useCartStore } from '@/stores/cart'

import {
  getCategories,
  getDishes,
  getDishDetail,
  getHomeRecommendations, // ✅ 你要确保 api/dishes.ts 里有这个函数
  type DishListItem,
  type DishDetailOut,
  type DishSpecOut,
} from '@/api/dishes'

const router = useRouter()
const cart = useCartStore()

/** ===== 列表筛选 ===== */
const loading = ref(false)
const addingId = ref<number | null>(null)

const categories = ref<{ id: number; name: string }[]>([])
const activeCategoryId = ref<number | 'all'>('all')
const keyword = ref('')
const status = ref<string>('')

const dishes = ref<DishListItem[]>([])
const total = ref(0)

const categoryOptions = computed(() => [
  { label: '全部', value: 'all' },
  ...categories.value.map((c) => ({ label: c.name, value: c.id })),
])

function statusText(s: string) {
  if (s === 'on_sale') return '在售'
  if (s === 'sold_out') return '售罄'
  if (s === 'offline') return '下架'
  return s
}

async function loadCategories() {
  const res = await getCategories()
  categories.value = (res || []).map((c: any) => ({ id: Number(c.id), name: c.name }))
}

async function load() {
  loading.value = true
  try {
    const category_id = activeCategoryId.value === 'all' ? undefined : Number(activeCategoryId.value)
    const res: any = await getDishes({
      category_id,
      keyword: keyword.value || undefined,
      status: status.value || undefined,
    } as any)

    if (Array.isArray(res)) {
      dishes.value = res as any
      total.value = res.length
    } else {
      dishes.value = (res.items || res.data || []) as any
      total.value = Number(res.total ?? dishes.value.length)
    }
  } finally {
    loading.value = false
  }
}

function reset() {
  activeCategoryId.value = 'all'
  keyword.value = ''
  status.value = ''
  load()
}

function goDetail(id: number) {
  router.push(`/dishes/${id}`)
}

/** ===== AI 推荐 ===== */
const recLoading = ref(false)
const recs = ref<any[]>([])

async function loadRecs() {
  recLoading.value = true
  try {
    const res: any = await getHomeRecommendations()
    recs.value = Array.isArray(res) ? res : (res?.items || [])
    console.log('recommend/home =>', recs.value)
  } catch (e) {
    console.error(e)
    ElMessage.error('获取推荐失败')
  } finally {
    recLoading.value = false
  }
}

/** ===== Drawer 加购 ===== */
const addDrawerVisible = ref(false)
const drawerLoading = ref(false)
const drawerSaving = ref(false)

const drawerDishId = ref<number | null>(null)
const drawerDish = ref<DishDetailOut | null>(null)
const drawerSpecs = ref<DishSpecOut[]>([])
const quantity = ref(1)
const specDraft = ref<Record<string, any>>({})

const estAmount = computed(() => {
  const p = drawerDish.value?.price ?? 0
  return Number(p) * Number(quantity.value || 1)
})

async function openAddDrawer(dishId: number) {
  addingId.value = dishId
  try {
    addDrawerVisible.value = true
    drawerDishId.value = dishId
    quantity.value = 1
    specDraft.value = {}
    drawerDish.value = null
    drawerSpecs.value = []

    drawerLoading.value = true
    const detail = await getDishDetail(dishId)
    drawerDish.value = detail
    drawerSpecs.value = detail.specs || []
  } catch (e) {
    ElMessage.error('加载菜品详情失败')
    addDrawerVisible.value = false
  } finally {
    drawerLoading.value = false
    addingId.value = null
  }
}

function validateRequiredSpecs(specs: DishSpecOut[], selected: Record<string, any>) {
  for (const s of specs || []) {
    const key = s.spec_name
    const hasOptions = Array.isArray(s.spec_values) && s.spec_values.length > 0
    if (!hasOptions) continue
    const v = selected?.[key]
    if (v === undefined || v === null || v === '') return false
  }
  return true
}

async function confirmAdd() {
  console.log('confirmAdd clicked') // ✅ 必须能打印

  if (!drawerDishId.value) return ElMessage.error('dishId 缺失')
  if (!drawerDish.value) return ElMessage.error('菜品未加载完成')

  const ok = validateRequiredSpecs(drawerSpecs.value, specDraft.value || {})
  if (!ok) return ElMessage.warning('请先选择完整规格')

  drawerSaving.value = true
  try {
    await cart.add({
      dish_id: drawerDishId.value,
      quantity: quantity.value ?? 1,
      spec_snapshot: specDraft.value || {},
    })
    ElMessage.success('已加入购物车')
    addDrawerVisible.value = false
  } catch (e) {
    console.error(e)
    ElMessage.error('加入购物车失败')
  } finally {
    drawerSaving.value = false
  }
}

/** ✅ 只保留一个 onMounted（顶层） */
onMounted(async () => {
  await loadCategories()
  await load()
  await loadRecs()
})
</script>

<style scoped lang="scss">
.page { padding: 18px; max-width: 1200px; margin: 0 auto; }

.page-head { display:flex; align-items:flex-end; justify-content:space-between; gap:14px; margin-bottom:14px; }
.hgroup .h1 { font-size:22px; font-weight:950; }
.hgroup .h2 { margin-top:6px; color:var(--app-muted); font-size:13px; }

.filters { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
.search { width: 260px; }
.status { width: 120px; }

.panel { border-radius: 12px; border: 1px solid var(--app-border); background: rgba(255,255,255,.78); backdrop-filter: blur(10px); }

.tabs-row { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom: 12px; }

.grid { display:grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
@media (max-width: 960px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 640px) { .grid { grid-template-columns: repeat(1, minmax(0, 1fr)); } }

.card { border: 1px solid var(--app-border); background: #fff; border-radius: 12px; overflow:hidden; cursor: pointer; transition: transform .12s ease; }
.card:hover { transform: translateY(-1px); }

.thumb { position: relative; height: 150px; background: #f3f4f6; }
.thumb img { width:100%; height:100%; object-fit:cover; display:block; }
.ph { height:100%; display:flex; align-items:center; justify-content:center; color:#9ca3af; font-weight:800; }

.status-pill { position:absolute; left:10px; top:10px; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 900; color: #fff; background: #10b981; }
.status-pill[data-status="sold_out"] { background: #f59e0b; }
.status-pill[data-status="offline"] { background: #6b7280; }

.body { padding: 12px; }
.top { display:flex; justify-content:space-between; align-items:baseline; gap:10px; }
.name { font-weight: 950; font-size: 15px; }
.price { font-weight: 950; color: var(--app-primary); }

.highlights { margin-top: 8px; display:flex; gap:6px; flex-wrap:wrap; }
.tag { font-weight: 900; }
.desc { margin-top: 8px; min-height: 20px; }
.muted { color: var(--app-muted); }

.meta { margin-top: 10px; display:flex; gap:12px; color: var(--app-muted); font-size: 12px; }
.actions { margin-top: 12px; display:flex; gap:10px; justify-content:flex-end; }

.btn { border-radius: 10px; border: 1px solid var(--app-border); }
.btn-primary { border-radius: 10px; border: 1px solid rgba(99, 102, 241, 0.25); background: linear-gradient(135deg, rgba(99,102,241,.95), rgba(109,40,217,.95)); color: #fff; }

.empty { padding: 46px 0; text-align:center; grid-column: 1 / -1; }
.empty-title { font-size: 16px; font-weight: 950; }
.empty-sub { margin-top: 6px; color: var(--app-muted); }

.drawer-wrap { display:flex; flex-direction:column; height: 100%; }
.drawer-body { flex: 1; padding-bottom: 12px; }
.drawer-footer { padding: 12px 0; display:flex; justify-content:flex-end; gap:12px; border-top: 1px solid var(--app-border); background: #fff; }

.section-title { margin: 12px 0 8px; font-weight: 950; }
.qty { margin-top: 12px; display:flex; align-items:center; justify-content:space-between; gap:12px; }
.sumline { margin-top: 12px; display:flex; justify-content:space-between; align-items:center; }
.sumline .money { color: var(--app-primary); }
.drawer-tip { margin-top: 10px; color: var(--app-muted); font-size: 12px; line-height: 1.5; }
</style>
