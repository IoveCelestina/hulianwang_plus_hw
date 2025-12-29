<template>
  <div class="page">
    <div class="page-head">
      <div class="hgroup">
        <div class="h1">结算</div>
        <div class="h2">选择地址，确认订单信息</div>
      </div>
      <el-button class="btn" @click="backToCart">返回购物车</el-button>
    </div>

    <div class="grid">
      <!-- 左：地址与备注 -->
      <el-card class="panel" shadow="never">
        <div class="section-title">收货地址</div>

        <div v-loading="addrLoading" class="addr-box">
          <div v-if="addresses.length === 0 && !addrLoading" class="empty">
            <div class="empty-title">还没有收货地址</div>
            <div class="empty-sub">添加一个地址，便于下单</div>
            <el-button class="btn-primary" @click="openDrawer()">新增地址</el-button>
          </div>

          <el-radio-group v-else v-model="selectedAddressId" class="addr-list">
            <div v-for="a in addresses" :key="a.id" class="addr-item" :data-active="a.id === selectedAddressId">
              <el-radio :label="a.id">
                <div class="addr-main">
                  <div class="row1">
                    <span class="name">{{ a.contact_name }}</span>
                    <span class="phone">{{ a.phone }}</span>
                    <span v-if="a.is_default" class="pill">默认</span>
                  </div>
                  <div class="row2">{{ a.address_line }}</div>
                </div>
              </el-radio>

              <div class="addr-actions">
                <el-button class="link" text :disabled="a.is_default" @click="setDefault(a.id)">设为默认</el-button>
              </div>
            </div>
          </el-radio-group>

          <div class="addr-footer" v-if="addresses.length > 0">
            <el-button class="btn" @click="openDrawer()">新增地址</el-button>
          </div>
        </div>

        <div class="section-title mt">订单备注</div>
        <el-input
          v-model="note"
          type="textarea"
          :rows="4"
          maxlength="200"
          show-word-limit
          placeholder="例如：不要香菜 / 少盐 / 到门口电话联系…"
        />
      </el-card>

      <!-- 右：订单明细 -->
      <el-card class="panel" shadow="never">
        <div class="section-title">订单明细</div>

        <div v-loading="cart.loading" class="items">
          <div v-if="cart.items.length === 0 && !cart.loading" class="empty">
            <div class="empty-title">购物车为空</div>
            <div class="empty-sub">请先添加菜品再结算</div>
            <el-button class="btn-primary" @click="goDishes">去点餐</el-button>
          </div>

          <div v-else class="item" v-for="it in cart.items" :key="it.id">
            <div class="line1">
              <div class="name">{{ it.dish_name }}</div>
              <div class="money">¥ {{ it.subtotal.toFixed(0) }}</div>
            </div>
            <div class="line2">
              <span class="muted">单价 ¥ {{ it.price.toFixed(0) }} · 数量 {{ it.quantity }}</span>
            </div>
            <div class="line3" v-if="formatSpecs(it.selected_specs) !== '无'">
              <span class="muted">规格：{{ formatSpecs(it.selected_specs) }}</span>
            </div>
          </div>
        </div>

        <div class="sum">
          <div class="label">合计</div>
          <div class="total">¥ {{Number(cart.totalAmount ?? 0).toFixed(2) }}</div>
        </div>

        <div class="pay">
          <el-button class="btn" @click="goDishes">继续加购</el-button>
          <el-button
            class="btn-primary"
            :loading="submitting"
            :disabled="cart.items.length === 0"
            @click="submitOrder"
          >
            提交订单
          </el-button>
        </div>

        <div class="tip">下单后可在订单详情中支付并完成订单</div>
      </el-card>
    </div>

    <!-- 新增地址 Drawer -->
    <el-drawer v-model="drawerVisible" title="新增地址" size="420px" class="pro-drawer">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="联系人" prop="contact_name">
          <el-input v-model="form.contact_name" placeholder="例如：张三" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="例如：13800000000" />
        </el-form-item>
        <el-form-item label="详细地址" prop="address_line">
          <el-input v-model="form.address_line" type="textarea" :rows="3" placeholder="例如：XX市XX区XX路XX号XX室" />
        </el-form-item>
        <el-form-item>
          <el-switch v-model="form.is_default" active-text="设为默认地址" />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="drawer-footer">
          <el-button class="btn" @click="drawerVisible=false">取消</el-button>
          <el-button class="btn-primary" :loading="savingAddr" @click="saveAddress">保存</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- 下单成功 Dialog -->
    <el-dialog v-model="successVisible" title="下单成功" width="520px" class="pro-dialog">
      <div class="success">
        <div class="ok">✅ 订单已创建</div>
        <div class="meta">
          <div>订单号：<b>#{{ createdOrderId }}</b></div>
          <div>金额：<b>¥ {{ createdTotal.toFixed(0) }}</b></div>
        </div>
      </div>
      <template #footer>
        <el-button class="btn" @click="goDishes">返回菜单</el-button>
        <el-button class="btn-primary" @click="goOrderDetail">查看订单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useCartStore } from '@/stores/cart'
import { createOrder } from '@/api/orders'
import { listAddresses, createAddress, setDefaultAddress, type AddressOut } from '@/api/addresses'

const cart = useCartStore()

const addrLoading = ref(false)
const addresses = ref<AddressOut[]>([])
const selectedAddressId = ref<number | null>(null)
const note = ref('')

const submitting = ref(false)

const successVisible = ref(false)
const createdOrderId = ref<number | null>(null)
const createdTotal = ref(0)

onMounted(async () => {
  await cart.refresh()

  await loadAddresses()
})

async function loadAddresses() {
  addrLoading.value = true
  try {
    addresses.value = await listAddresses()
    // 默认优先
    const def = addresses.value.find((a) => a.is_default)
    selectedAddressId.value = def?.id ?? addresses.value[0]?.id ?? null
  } finally {
    addrLoading.value = false
  }
}

async function setDefault(id: number) {
  await setDefaultAddress(id)
  ElMessage.success('已设为默认地址')
  await loadAddresses()
}

function formatSpecs(specs: any) {
  if (!specs || Object.keys(specs).length === 0) return '无'
  return Object.entries(specs).map(([k, v]) => `${k}:${v}`).join('，')
}

function backToCart() {
  window.location.href = '/cart'
}
function goDishes() {
  window.location.href = '/dishes'
}
function goOrderDetail() {
  if (createdOrderId.value) window.location.href = `/orders/${createdOrderId.value}`
}

async function submitOrder() {
  if (cart.items.length === 0) {
    ElMessage.warning('购物车为空')
    return
  }
  if (!selectedAddressId.value) {
    ElMessage.warning('请选择收货地址')
    return
  }

  submitting.value = true
  try {
    const payload = {
      address_id: selectedAddressId.value,
      note: note.value?.trim() || null,
      items: cart.items.map((it) => ({
        dish_id: it.dish_id,
        quantity: it.quantity,
        selected_specs: it.selected_specs || {},
      })),
    }

    const res = await createOrder(payload)
    createdOrderId.value = res.order_id
    createdTotal.value = res.total_amount || cart.totalAmount

    // 清空购物车（后端无 bulk clear）
    await cart.clearAll()

    successVisible.value = true
  } finally {
    submitting.value = false
  }
}

/** Drawer：新增地址 */
const drawerVisible = ref(false)
const savingAddr = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  contact_name: '',
  phone: '',
  address_line: '',
  is_default: true,
})

const rules: FormRules = {
  contact_name: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  address_line: [{ required: true, message: '请输入详细地址', trigger: 'blur' }],
}

function openDrawer() {
  drawerVisible.value = true
  form.contact_name = ''
  form.phone = ''
  form.address_line = ''
  form.is_default = addresses.value.length === 0 ? true : false
}

async function saveAddress() {
  if (!formRef.value) return
  await formRef.value.validate(async (ok) => {
    if (!ok) return
    savingAddr.value = true
    try {
      await createAddress({ ...form })
      ElMessage.success('地址已保存')
      drawerVisible.value = false
      await loadAddresses()
    } finally {
      savingAddr.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.page { padding: 18px; max-width: 1200px; margin: 0 auto; }
.page-head {
  display: flex; align-items: flex-end; justify-content: space-between; gap: 14px; margin-bottom: 14px;
}
.hgroup .h1 { font-size: 22px; font-weight: 950; }
.hgroup .h2 { margin-top: 6px; color: var(--app-muted); font-size: 13px; }

.grid { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 12px; }
@media (max-width: 980px) { .grid { grid-template-columns: 1fr; } }

.panel {
  border-radius: 12px;
  border: 1px solid var(--app-border);
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(10px);
}

.section-title { font-weight: 950; font-size: 15px; margin-bottom: 10px; }
.mt { margin-top: 16px; }

.addr-list { display: flex; flex-direction: column; gap: 10px; width: 100%; }
.addr-item {
  display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;
  padding: 12px; border-radius: 12px; border: 1px solid var(--app-border); background: #fff;
}
.addr-item[data-active='true'] { border-color: rgba(79,70,229,.35); box-shadow: 0 16px 40px rgba(17,24,39,.06); }
.addr-main .row1 { display: flex; gap: 10px; align-items: center; }
.name { font-weight: 950; }
.phone { color: var(--app-muted); font-weight: 700; font-size: 12px; }
.pill {
  padding: 4px 8px; border-radius: 999px; font-size: 12px; font-weight: 800;
  background: rgba(79,70,229,.12); border: 1px solid rgba(79,70,229,.2); color: var(--app-primary);
}
.addr-main .row2 { margin-top: 6px; color: #334155; font-size: 12px; }
.addr-actions { margin-left: auto; }
.link { font-weight: 900; }

.items { display: flex; flex-direction: column; gap: 10px; }
.item { padding: 12px; border-radius: 12px; border: 1px solid var(--app-border); background: #fff; }
.line1 { display: flex; justify-content: space-between; gap: 10px; }
.line1 .name { font-weight: 950; }
.money { font-weight: 950; color: var(--app-primary); }
.muted { color: var(--app-muted); font-size: 12px; }

.sum {
  margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--app-border);
  display: flex; justify-content: space-between; align-items: baseline;
}
.sum .label { color: var(--app-muted); font-weight: 800; }
.sum .total { font-size: 20px; font-weight: 950; color: var(--app-primary); }

.pay { margin-top: 12px; display: flex; justify-content: flex-end; gap: 10px; }
.tip { margin-top: 10px; font-size: 12px; color: var(--app-muted); }

.btn { border-radius: 10px; border: 1px solid var(--app-border); }
.btn-primary {
  border-radius: 10px;
  border: 1px solid rgba(99, 102, 241, 0.25);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.95), rgba(109, 40, 217, 0.95));
  color: #fff;
}

.empty { padding: 34px 0; text-align: center; }
.empty-title { font-size: 16px; font-weight: 950; }
.empty-sub { margin-top: 6px; color: var(--app-muted); }

.drawer-footer { display: flex; justify-content: flex-end; gap: 10px; }
.pro-dialog :deep(.el-dialog) { border-radius: 14px; }
.pro-drawer :deep(.el-drawer) { border-radius: 14px 0 0 14px; }

.success .ok { font-weight: 950; font-size: 16px; }
.success .meta { margin-top: 10px; color: #334155; display: grid; gap: 6px; }
</style>
