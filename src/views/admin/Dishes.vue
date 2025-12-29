<template>
  <div class="page">
    <div class="head">
      <div>
        <div class="h1">菜品管理</div>
        <div class="h2">新增/编辑菜品、状态、AI 元数据</div>
      </div>
      <el-button class="btn-primary" @click="openCreate">新增菜品</el-button>
    </div>

    <el-card class="panel" shadow="never" v-loading="loading">
      <el-table :data="list" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="90" />
        <el-table-column prop="name" label="名称" min-width="160" />
        <el-table-column prop="price" label="价格" width="120" />
        <el-table-column prop="status" label="状态" width="120" />
        <el-table-column prop="category_id" label="分类ID" width="120" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button class="btn" size="small" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-drawer v-model="visible" :title="mode==='create' ? '新增菜品' : '编辑菜品'" size="520px" class="pro-drawer">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="分类ID" prop="category_id"><el-input-number v-model="form.category_id" :min="1" /></el-form-item>
        <el-form-item label="价格" prop="price"><el-input-number v-model="form.price" :min="0" /></el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="选择状态">
            <el-option label="在售" value="on_sale" />
            <el-option label="售罄" value="sold_out" />
            <el-option label="下架" value="offline" />
          </el-select>
        </el-form-item>
        <el-form-item label="图片 URL" prop="image_url"><el-input v-model="form.image_url" placeholder="https://..." /></el-form-item>
        <el-form-item label="描述" prop="description"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="AI 元数据（JSON）" prop="ai_metadata">
          <el-input v-model="aiJson" type="textarea" :rows="6" placeholder='{"highlights":["低脂","清淡"]}' />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="drawer-footer">
          <el-button class="btn" @click="visible=false">取消</el-button>
          <el-button class="btn-primary" :loading="saving" @click="save">保存</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { adminCreateDish, adminListDishes, adminUpdateDish, type AdminDish } from '@/api/admin'

const loading = ref(false)
const saving = ref(false)
const list = ref<AdminDish[]>([])

onMounted(load)
async function load() {
  loading.value = true
  try {
    const res = await adminListDishes()
    list.value = res.items || []
  } finally {
    loading.value = false
  }
}

const visible = ref(false)
const mode = ref<'create' | 'edit'>('create')
const editingId = ref<number | null>(null)

const formRef = ref<FormInstance>()
const form = reactive({
  name: '',
  category_id: 1,
  price: 0,
  status: 'on_sale',
  image_url: '',
  description: '',
  ai_metadata: {} as any,
})
const aiJson = ref('')

const rules: FormRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  category_id: [{ required: true, message: '请输入分类ID', trigger: 'change' }],
  price: [{ required: true, message: '请输入价格', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

function openCreate() {
  mode.value = 'create'
  editingId.value = null
  form.name = ''
  form.category_id = 1
  form.price = 0
  form.status = 'on_sale'
  form.image_url = ''
  form.description = ''
  aiJson.value = JSON.stringify({ highlights: [] }, null, 2)
  visible.value = true
}

function openEdit(row: AdminDish) {
  mode.value = 'edit'
  editingId.value = row.id
  form.name = row.name
  form.category_id = row.category_id
  form.price = row.price
  form.status = row.status
  form.image_url = row.image_url || ''
  form.description = row.description || ''
  aiJson.value = JSON.stringify(row.ai_metadata || {}, null, 2)
  visible.value = true
}

async function save() {
  if (!formRef.value) return
  await formRef.value.validate(async (ok) => {
    if (!ok) return
    let meta: any = {}
    try {
      meta = aiJson.value?.trim() ? JSON.parse(aiJson.value) : {}
    } catch {
      ElMessage.error('AI 元数据 JSON 格式错误')
      return
    }

    saving.value = true
    try {
      const payload = {
        name: form.name,
        category_id: form.category_id,
        price: form.price,
        status: form.status,
        image_url: form.image_url || null,
        description: form.description || null,
        ai_metadata: meta,
      } as any

      if (mode.value === 'create') await adminCreateDish(payload)
      else if (editingId.value) await adminUpdateDish(editingId.value, payload)

      ElMessage.success('已保存')
      visible.value = false
      await load()
    } finally {
      saving.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.page { max-width: 1200px; }
.head { display:flex; justify-content:space-between; align-items:flex-end; gap: 14px; margin-bottom: 14px; }
.h1 { font-size: 22px; font-weight: 950; }
.h2 { margin-top: 6px; color: var(--app-muted); font-size: 13px; }
.panel { border-radius: 12px; border: 1px solid var(--app-border); background: rgba(255,255,255,.78); backdrop-filter: blur(10px); }
.btn { border-radius: 10px; border: 1px solid var(--app-border); font-weight: 900; }
.btn-primary { border-radius:10px; border:1px solid rgba(99,102,241,.25); background: linear-gradient(135deg, rgba(99,102,241,.95), rgba(109,40,217,.95)); color:#fff; font-weight:900; }
.pro-drawer :deep(.el-drawer){ border-radius: 14px 0 0 14px; }
.drawer-footer { display:flex; justify-content:flex-end; gap:10px; }
</style>
