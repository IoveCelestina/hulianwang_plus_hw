<template>
  <el-card class="panel" shadow="never">
    <div class="head">
      <div class="title">用户评论</div>
      <el-button class="btn" @click="refresh" :loading="loading">刷新</el-button>
    </div>

    <div class="composer">
      <div class="row">
        <div class="label">评分</div>
        <el-rate v-model="rating" :max="5" />
      </div>
      <el-input
        v-model="content"
        type="textarea"
        :rows="3"
        placeholder="写下你的评价（可选）"
        maxlength="300"
        show-word-limit
      />
      <div class="actions">
        <el-button class="btn-primary" :loading="submitting" @click="submit">发布评论</el-button>
      </div>
    </div>

    <div v-loading="loading" class="list">
      <div v-if="!loading && reviews.length === 0" class="empty">暂无评论</div>

      <div v-for="r in reviews" :key="r.id" class="item">
        <div class="top">
          <div class="who">{{ r.user?.username || '匿名用户' }}</div>
          <el-rate :model-value="r.rating" disabled />
        </div>
        <div class="txt">{{ r.content || '（无文字内容）' }}</div>
        <div class="time" v-if="r.created_at">{{ r.created_at }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createReview, getDishReviews, type ReviewOut } from '@/api/reviews'

const props = defineProps<{ dishId: number }>()

const loading = ref(false)
const submitting = ref(false)
const reviews = ref<ReviewOut[]>([])

const rating = ref(5)
const content = ref('')

async function refresh() {
  loading.value = true
  try {
    reviews.value = await getDishReviews(props.dishId)
  } finally {
    loading.value = false
  }
}

async function submit() {
  if (!props.dishId) return
  if (!rating.value) {
    ElMessage.warning('请先选择评分')
    return
  }
  submitting.value = true
  try {
    await createReview({
      dish_id: props.dishId,
      rating: rating.value,
      content: content.value || undefined,
    })
    ElMessage.success('已发布')
    content.value = ''
    rating.value = 5
    await refresh()
  } catch (e: any) {
    ElMessage.error('发布失败（请确认已登录）')
  } finally {
    submitting.value = false
  }
}

onMounted(refresh)
</script>

<style scoped lang="scss">
.panel { border-radius:12px; border:1px solid var(--app-border); }
.head { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
.title { font-weight: 950; }
.composer { padding: 10px 0 16px; border-bottom:1px solid var(--app-border); margin-bottom:12px; }
.row { display:flex; align-items:center; gap:12px; margin-bottom:10px; }
.label { color: var(--app-muted); font-weight: 800; width: 44px; }
.actions { margin-top: 10px; display:flex; justify-content:flex-end; }
.btn { border-radius:10px; border:1px solid var(--app-border); }
.btn-primary { border-radius:10px; color:#fff; background: linear-gradient(135deg, rgba(99,102,241,.95), rgba(109,40,217,.95)); border:1px solid rgba(99, 102, 241, 0.25); }
.list { display:flex; flex-direction:column; gap:10px; }
.item { padding: 10px 12px; border:1px solid var(--app-border); border-radius: 12px; background:#fff; }
.top { display:flex; justify-content:space-between; align-items:center; }
.who { font-weight: 900; }
.txt { margin-top: 6px; color:#111827; }
.time { margin-top: 6px; font-size: 12px; color: var(--app-muted); }
.empty { padding: 18px 0; text-align:center; color: var(--app-muted); }
</style>
