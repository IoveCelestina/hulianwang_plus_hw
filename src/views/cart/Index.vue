<template>
  <div class="page">
    <div class="page-head">
      <div class="hgroup">
        <div class="h1">购物车</div>
        <div class="h2">确认数量与规格，准备下单</div>
      </div>
      <el-button class="btn" @click="goDishes">继续选购</el-button>
    </div>

    <el-card class="panel" shadow="never" v-loading="cart.loading">
      <div v-if="cart.items.length === 0 && !cart.loading" class="empty">
        <div class="empty-title">你的购物车还是空的</div>
        <div class="empty-sub">去挑选几道喜欢的菜吧</div>
        <el-button class="btn-primary" @click="goDishes">去点餐</el-button>
      </div>

      <div v-else class="list">
        <div v-for="it in cart.items" :key="it.id" class="row">
          <div class="main">
            <div class="title">
              <div class="name">{{ it.name }}</div>
              <div class="price">¥ {{ Number(it.unit_price ?? 0).toFixed(0) }}</div>
            </div>

            <div class="specs">
              <div class="spec-text">
                <span class="k">规格：</span>
                <span class="v">{{ formatSpecs(it.spec_snapshot) }}</span>
              </div>
              <el-button class="link" text @click="openSpecs(it)">修改规格</el-button>
            </div>

            <div class="ops">
              <el-input-number
                v-model="qtyDraft[it.id]"
                :min="1"
                :max="99"
                @change="(v:number) => changeQty(it.id, v)"
              />
              <div class="subtotal">
                小计 ¥ {{ lineSubtotal(it) }}
              </div>
              <el-button class="danger" text @click="remove(it.id)">删除</el-button>
            </div>
          </div>
        </div>

        <div class="footer">
          <div class="sum">
            <span class="label">合计</span>
            <span class="money">¥{{ Number(cart.totalAmount ?? 0).toFixed(2) }}</span>
          </div>
          <el-button class="btn-primary" :disabled="cart.items.length === 0" @click="checkout">
            去结算
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 规格选择 Dialog -->
    <el-dialog v-model="specDialogVisible" title="选择规格" width="560px" class="pro-dialog">
      <div v-loading="specLoading">
        <div class="hint">
          请选择规格组合（当前总价展示按后端 cart.total_amount 为准；规格仅更新购物车项快照）。
        </div>

        <SpecPicker
          v-model="specDraft"
          :specs="specDefs"
          :required="true"
          :showDelta="true"
        />
      </div>

      <template #footer>
        <el-button class="btn" @click="specDialogVisible=false">取消</el-button>
        <el-button class="btn-primary" :loading="specSaving" @click="saveSpecs">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useCartStore, type CartItemVM } from '@/stores/cart'
import { getDishDetail, type DishSpecOut } from '@/api/dishes'
import SpecPicker from '@/components/SpecPicker/index.vue'

const router = useRouter()
const cart = useCartStore()

/** 数量草稿（InputNumber 双向绑定用） */
const qtyDraft = reactive<Record<number, number>>({})

function syncQtyDraft() {
  for (const it of cart.items) qtyDraft[it.id] = it.quantity
}

onMounted(async () => {
  try {
    await cart.refresh()
  } finally {
    syncQtyDraft()
  }
})

function goDishes() {
  router.push('/dishes')
}

function checkout() {
  router.push('/checkout')
}

function formatSpecs(specs: any) {
  if (!specs || typeof specs !== 'object' || Object.keys(specs).length === 0) return '无'
  return Object.entries(specs).map(([k, v]) => `${k}:${v}`).join('，')
}

function lineSubtotal(it: CartItemVM) {
  const q = Number(qtyDraft[it.id] ?? it.quantity ?? 0)
  const p = Number(it.unit_price ?? 0)
  return Number(q * p).toFixed(0)
}

async function changeQty(itemId: number, v: number) {
  try {
    await cart.updateItem(itemId, { quantity: v })
    await cart.refresh()
    syncQtyDraft()
    ElMessage.success('已更新数量')
  } catch (e) {
    ElMessage.error('更新失败，请重试')
  }
}

async function remove(itemId: number) {
  try {
    await cart.removeItem(itemId)
    await cart.refresh()
    syncQtyDraft()
    ElMessage.success('已删除')
  } catch (e) {
    ElMessage.error('删除失败，请重试')
  }
}

/** 规格编辑 */
const specDialogVisible = ref(false)
const specLoading = ref(false)
const specSaving = ref(false)

const specDefs = ref<DishSpecOut[]>([])
const specDraft = ref<Record<string, any>>({})
let currentItem: CartItemVM | null = null

function validateRequiredSpecs(): boolean {
  for (const s of specDefs.value || []) {
    const key = (s as any).spec_name
    const values = (s as any).spec_values
    const hasOptions = Array.isArray(values) && values.length > 0
    if (!hasOptions) continue

    const v = specDraft.value?.[key]
    if (v === undefined || v === null || v === '') {
      ElMessage.warning(`请选择：${key}`)
      return false
    }
  }
  return true
}

async function openSpecs(it: CartItemVM) {
  currentItem = it
  specDialogVisible.value = true
  specLoading.value = true
  try {
    const detail = await getDishDetail(it.dish_id)
    specDefs.value = (detail as any).specs || []
    // 初始：使用购物车项的 spec_snapshot
    specDraft.value = JSON.parse(JSON.stringify(it.spec_snapshot || {}))
  } catch (e) {
    ElMessage.error('加载规格失败')
  } finally {
    specLoading.value = false
  }
}

async function saveSpecs() {
  if (!currentItem) return
  if (!validateRequiredSpecs()) return

  specSaving.value = true
  try {
    await cart.updateItem(currentItem.id, { spec_snapshot: specDraft.value || {} })
    await cart.refresh()
    syncQtyDraft()
    ElMessage.success('已更新规格')
    specDialogVisible.value = false
  } catch (e) {
    ElMessage.error('保存失败，请重试')
  } finally {
    specSaving.value = false
  }
}
</script>

<style scoped lang="scss">
.page { padding: 18px; max-width: 1100px; margin: 0 auto; }
.page-head { display:flex; align-items:flex-end; justify-content:space-between; gap:14px; margin-bottom:14px; }
.hgroup .h1 { font-size:22px; font-weight:950; }
.hgroup .h2 { margin-top:6px; color:var(--app-muted); font-size:13px; }

.panel {
  border-radius: 12px;
  border: 1px solid var(--app-border);
  background: rgba(255,255,255,.78);
  backdrop-filter: blur(10px);
}

.list { display:flex; flex-direction:column; gap:10px; }
.row {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid var(--app-border);
  background: #fff;
}
.title { display:flex; justify-content:space-between; align-items:baseline; gap:10px; }
.name { font-weight: 950; font-size: 15px; }
.price { font-weight: 950; color: var(--app-primary); }

.specs { margin-top: 8px; display:flex; justify-content:space-between; align-items:center; gap:10px; }
.spec-text { font-size: 12px; color: #374151; }
.spec-text .k { color: var(--app-muted); }
.link { font-weight: 900; }

.ops { margin-top: 12px; display:flex; align-items:center; gap:12px; }
.subtotal { margin-left: auto; font-weight: 950; }
.danger { color: #ef4444; font-weight: 950; }

.footer { margin-top: 10px; display:flex; justify-content:flex-end; align-items:center; gap:14px; }
.sum .label { color: var(--app-muted); margin-right: 8px; font-weight: 800; }
.sum .money { font-weight: 950; font-size: 18px; color: var(--app-primary); }

.btn { border-radius: 10px; border: 1px solid var(--app-border); }
.btn-primary {
  border-radius: 10px;
  border: 1px solid rgba(99, 102, 241, 0.25);
  background: linear-gradient(135deg, rgba(99,102,241,.95), rgba(109,40,217,.95));
  color: #fff;
}

.empty { padding: 46px 0; text-align:center; }
.empty-title { font-size: 16px; font-weight: 950; }
.empty-sub { margin-top: 6px; color: var(--app-muted); }

.hint {
  margin-bottom: 12px;
  font-size: 12px;
  color: var(--app-muted);
  line-height: 1.5;
}

.pro-dialog :deep(.el-dialog) { border-radius: 14px; }
</style>
