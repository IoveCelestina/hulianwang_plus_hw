<template>
  <div class="page">
    <div class="head">
      <div>
        <div class="h1">口味偏好</div>
        <div class="h2">用于 AI 推荐与个性化排序</div>
      </div>
      <div class="actions">
        <el-button class="btn" :loading="loading" @click="load">刷新</el-button>
        <el-button class="btn-primary" :loading="saving" @click="save">保存</el-button>
      </div>
    </div>

    <el-card class="panel" shadow="never" v-loading="loading">
      <el-form label-position="top">
        <el-form-item label="偏好标签（可输入回车创建）">
          <el-select v-model="tags" multiple filterable allow-create default-first-option placeholder="如：清淡 / 不辣 / 高蛋白">
            <el-option v-for="t in tags" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>

        <el-form-item label="忌口（可输入回车创建）">
          <el-select v-model="restrictions" multiple filterable allow-create default-first-option placeholder="如：香菜 / 花生 / 乳制品">
            <el-option v-for="t in restrictions" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>

        <div v-if="implicit" class="tip">
          <div class="tip-title">隐式画像（只读）</div>
          <pre class="json">{{ implicit }}</pre>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const saving = ref(false)

const tags = ref<string[]>([])
const restrictions = ref<string[]>([])
const implicit = ref('')

onMounted(load)

async function load() {
  loading.value = true
  try {
    const data = await request.get('/users/preferences')
    tags.value = data?.explicit_tags || []
    restrictions.value = data?.dietary_restrictions || []
    implicit.value = data?.implicit_profile ? JSON.stringify(data.implicit_profile, null, 2) : ''
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  try {
    await request.put('/users/preferences', {
      explicit_tags: tags.value,
      dietary_restrictions: restrictions.value,
    })
    ElMessage.success('已保存')
    await load()
  } finally {
    saving.value = false
  }
}
</script>

<style scoped lang="scss">
.page { padding: 18px; max-width: 1100px; margin: 0 auto; }
.head { display:flex; align-items:flex-end; justify-content:space-between; gap: 14px; margin-bottom: 14px; }
.h1 { font-size: 22px; font-weight: 950; }
.h2 { margin-top: 6px; color: var(--app-muted); font-size: 13px; }
.actions { display:flex; gap: 10px; }
.panel { border-radius: 12px; border: 1px solid var(--app-border); background: rgba(255,255,255,.78); backdrop-filter: blur(10px); }
.btn { border-radius: 10px; border: 1px solid var(--app-border); font-weight: 900; }
.btn-primary {
  border-radius: 10px; border: 1px solid rgba(99,102,241,.25);
  background: linear-gradient(135deg, rgba(99,102,241,.95), rgba(109,40,217,.95));
  color:#fff; font-weight: 900;
}
.tip { margin-top: 14px; }
.tip-title { font-weight: 950; margin-bottom: 8px; }
.json { background:#0b1220; color:#e5e7eb; padding:12px; border-radius:12px; overflow:auto; max-height: 260px; font-size: 12px; }
</style>
