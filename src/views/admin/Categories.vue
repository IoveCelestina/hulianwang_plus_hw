<template>
  <div class="page">
    <div class="head">
      <div>
        <div class="h1">分类管理</div>
        <div class="h2">新增分类、排序</div>
      </div>
      <el-button class="btn-primary" @click="open">新增分类</el-button>
    </div>

    <el-card class="panel" shadow="never" v-loading="loading">
      <el-table :data="list" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="90" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="sort_order" label="排序" width="120" />
      </el-table>
    </el-card>

    <el-dialog v-model="visible" title="新增分类" width="520px" class="pro-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="排序" prop="sort_order"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button class="btn" @click="visible=false">取消</el-button>
        <el-button class="btn-primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { adminCreateCategory, adminListCategories, type AdminCategory } from '@/api/admin'

const loading = ref(false)
const saving = ref(false)
const list = ref<AdminCategory[]>([])

onMounted(load)
async function load() {
  loading.value = true
  try {
    list.value = await adminListCategories()
  } finally {
    loading.value = false
  }
}

const visible = ref(false)
const formRef = ref<FormInstance>()
const form = reactive({ name: '', sort_order: 0 })
const rules: FormRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
}

function open() {
  form.name = ''
  form.sort_order = 0
  visible.value = true
}

async function save() {
  if (!formRef.value) return
  await formRef.value.validate(async (ok) => {
    if (!ok) return
    saving.value = true
    try {
      await adminCreateCategory({ name: form.name, sort_order: form.sort_order })
      ElMessage.success('已新增')
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
.pro-dialog :deep(.el-dialog){ border-radius: 14px; }
</style>
