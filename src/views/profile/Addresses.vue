<template>
  <div class="page">
    <div class="page-head">
      <div class="hgroup">
        <div class="h1">收货地址</div>
        <div class="h2">管理你的地址（后端暂不支持编辑/删除）</div>
      </div>
      <div class="actions">
        <el-button class="btn" :loading="loading" @click="load">刷新</el-button>
        <el-button class="btn-primary" @click="openDrawer">新增地址</el-button>
      </div>
    </div>

    <el-card class="panel" shadow="never" v-loading="loading">
      <div v-if="list.length === 0 && !loading" class="empty">
        <div class="empty-title">暂无地址</div>
        <div class="empty-sub">添加一个地址，便于下单</div>
        <el-button class="btn-primary" @click="openDrawer">新增地址</el-button>
      </div>

      <div v-else class="grid">
        <div class="addr" v-for="a in list" :key="a.id" :data-default="a.is_default">
          <div class="row1">
            <div class="name">{{ a.contact_name }}</div>
            <div class="phone">{{ a.phone }}</div>
            <div v-if="a.is_default" class="pill">默认</div>
          </div>
          <div class="row2">{{ a.address_line }}</div>

          <div class="row3">
            <el-button class="link" text :disabled="a.is_default" @click="setDefault(a.id)">设为默认</el-button>
          </div>
        </div>
      </div>
    </el-card>

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
          <el-button class="btn-primary" :loading="saving" @click="save">保存</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { listAddresses, createAddress, setDefaultAddress, type AddressOut } from '@/api/addresses'

const loading = ref(false)
const saving = ref(false)
const list = ref<AddressOut[]>([])

onMounted(load)

async function load() {
  loading.value = true
  try {
    list.value = await listAddresses()
  } finally {
    loading.value = false
  }
}

async function setDefault(id: number) {
  await setDefaultAddress(id)
  ElMessage.success('已设为默认地址')
  await load()
}

const drawerVisible = ref(false)
const formRef = ref<FormInstance>()
const form = reactive({ contact_name: '', phone: '', address_line: '', is_default: true })

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
  form.is_default = list.value.length === 0 ? true : false
}

async function save() {
  if (!formRef.value) return
  await formRef.value.validate(async (ok) => {
    if (!ok) return
    saving.value = true
    try {
      await createAddress({ ...form })
      ElMessage.success('已保存')
      drawerVisible.value = false
      await load()
    } finally {
      saving.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.page { padding: 18px; max-width: 1100px; margin: 0 auto; }
.page-head { display:flex; align-items:flex-end; justify-content:space-between; gap:14px; margin-bottom: 14px; }
.hgroup .h1 { font-size: 22px; font-weight: 950; }
.hgroup .h2 { margin-top: 6px; color: var(--app-muted); font-size: 13px; }
.actions { display:flex; gap:10px; align-items:center; }

.panel { border-radius: 12px; border: 1px solid var(--app-border); background: rgba(255,255,255,.78); backdrop-filter: blur(10px); }

.grid { display:grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
@media (max-width: 860px) { .grid { grid-template-columns: 1fr; } }

.addr {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid var(--app-border);
  background: #fff;
}
.addr[data-default='true'] { border-color: rgba(79,70,229,.35); box-shadow: 0 16px 40px rgba(17,24,39,.06); }
.row1 { display:flex; gap:10px; align-items:center; }
.name { font-weight: 950; }
.phone { color: var(--app-muted); font-weight: 800; font-size: 12px; }
.pill {
  margin-left: auto;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
  background: rgba(79,70,229,.12);
  border: 1px solid rgba(79,70,229,.2);
  color: var(--app-primary);
}
.row2 { margin-top: 8px; color:#334155; font-size: 12px; }
.row3 { margin-top: 10px; display:flex; justify-content:flex-end; }
.link { font-weight: 900; }

.btn { border-radius: 10px; border: 1px solid var(--app-border); font-weight: 900; }
.btn-primary {
  border-radius: 10px; border: 1px solid rgba(99,102,241,.25);
  background: linear-gradient(135deg, rgba(99,102,241,.95), rgba(109,40,217,.95)); color:#fff; font-weight: 900;
}
.empty { padding: 46px 0; text-align:center; }
.empty-title { font-size: 16px; font-weight: 950; }
.empty-sub { margin-top: 6px; color: var(--app-muted); }
.pro-drawer :deep(.el-drawer) { border-radius: 14px 0 0 14px; }
.drawer-footer { display:flex; justify-content:flex-end; gap:10px; }
</style>
