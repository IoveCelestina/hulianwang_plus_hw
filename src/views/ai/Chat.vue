<template>
  <div class="page">
    <div class="page-head">
      <div class="hgroup">
        <div class="h1">AI 推荐</div>
        <div class="h2">描述你的口味，AI 会给你推荐菜品</div>
      </div>
      <el-button class="btn" :loading="booting" @click="resetSession">重置会话</el-button>
    </div>

    <el-card class="panel" shadow="never">
      <div class="chat">
        <div class="msgs" ref="scrollRef">
          <div v-for="(m, idx) in messages" :key="idx" class="msg" :data-role="m.role">
            <div class="bubble">
              <div class="content">{{ m.content }}</div>
              <div v-if="m.recommendations?.length" class="recs">
                <div class="rec" v-for="r in m.recommendations" :key="r.dish_id">
                  <div class="r1">
                    <b>{{ r.dish_name || ('Dish #' + r.dish_id) }}</b>
                    <span class="score" v-if="r.fit_score != null">fit {{ r.fit_score }}</span>
                  </div>
                  <div class="r2" v-if="r.reason">{{ r.reason }}</div>
                  <div class="r3">
                    <el-button class="btn" size="small" @click="goDish(r.dish_id)">查看</el-button>
                    <el-button class="btn-primary" size="small" @click="addDish(r.dish_id)">加购</el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="streaming" class="msg" data-role="assistant">
            <div class="bubble">
              <div class="content muted">AI 正在思考…</div>
            </div>
          </div>
        </div>

        <div class="composer">
          <el-input
            v-model="input"
            type="textarea"
            :rows="2"
            placeholder="例如：我想吃清淡一点的，不要香菜，偏高蛋白…"
            @keydown.enter.exact.prevent="send"
          />
          <el-button class="btn-primary" :loading="streaming" @click="send">发送</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createSession, streamMessageUrl } from '@/api/ai'
import { postSse } from '@/utils/sse'
import { useCartStore } from '@/stores/cart'
import { useRouter } from 'vue-router'

type ChatMsg = {
  role: 'user' | 'assistant'
  content: string
  recommendations?: any[]
}

const router = useRouter()
const cart = useCartStore()

const booting = ref(false)
const sessionId = ref<number | null>(null)

const messages = ref<ChatMsg[]>([
  { role: 'assistant', content: '你好～告诉我你想吃什么口味，我来帮你推荐。' },
])

const input = ref('')
const streaming = ref(false)
const controller = ref<AbortController | null>(null)

const scrollRef = ref<HTMLElement | null>(null)
async function scrollToBottom() {
  await nextTick()
  const el = scrollRef.value
  if (!el) return
  el.scrollTop = el.scrollHeight
}

onMounted(async () => {
  await resetSession()
})

async function resetSession() {
  controller.value?.abort()
  controller.value = null
  booting.value = true
  try {
    const res = await createSession()
    sessionId.value = res.session_id
    messages.value = [{ role: 'assistant', content: '会话已创建～说说你今天想吃什么？' }]
  } finally {
    booting.value = false
    await scrollToBottom()
  }
}

async function send() {
  if (!sessionId.value) return
  const text = input.value.trim()
  if (!text) return

  messages.value.push({ role: 'user', content: text })
  input.value = ''
  await scrollToBottom()

  streaming.value = true
  controller.value = new AbortController()

  // 聚合一条 assistant 消息
  const assistant: ChatMsg = { role: 'assistant', content: '' }
  messages.value.push(assistant)
  await scrollToBottom()

  try {
    await postSse(
      streamMessageUrl(sessionId.value),
      { content: text },
      (json) => {
        // 兼容：token / delta / text / recommendations / done
        if (json.token) assistant.content += String(json.token)
        if (json.delta) assistant.content += String(json.delta)
        if (json.text) assistant.content += String(json.text)
        if (json.recommendations) assistant.recommendations = json.recommendations
        if (json.done) {
          // noop
        }
        scrollToBottom()
      },
      controller.value.signal
    )
  } catch (e: any) {
    ElMessage.error(e?.message || 'AI 请求失败')
  } finally {
    streaming.value = false
    controller.value = null
    await scrollToBottom()
  }
}

function goDish(id: number) {
  router.push(`/dishes/${id}`)
}
async function addDish(id: number) {
  try {
    await cart.add(id, 1, {})
    ElMessage.success('已加入购物车')
  } catch {}
}
</script>

<style scoped lang="scss">
.page { padding: 18px; max-width: 1100px; margin: 0 auto; }
.page-head { display:flex; align-items:flex-end; justify-content:space-between; gap:14px; margin-bottom: 14px; }
.hgroup .h1 { font-size: 22px; font-weight: 950; }
.hgroup .h2 { margin-top: 6px; color: var(--app-muted); font-size: 13px; }
.panel { border-radius: 12px; border: 1px solid var(--app-border); background: rgba(255,255,255,.78); backdrop-filter: blur(10px); }

.chat { display:flex; flex-direction:column; gap: 12px; }
.msgs {
  height: 560px;
  overflow: auto;
  border-radius: 12px;
  border: 1px solid var(--app-border);
  background: #fff;
  padding: 12px;
}
.msg { display:flex; margin-bottom: 10px; }
.msg[data-role='user'] { justify-content: flex-end; }
.bubble {
  max-width: 78%;
  border-radius: 14px;
  padding: 10px 12px;
  border: 1px solid var(--app-border);
  background: rgba(15,23,42,.04);
}
.msg[data-role='assistant'] .bubble {
  background: #fff;
}
.content { white-space: pre-wrap; }
.muted { color: var(--app-muted); font-size: 12px; }

.recs { margin-top: 10px; display:flex; flex-direction:column; gap: 8px; }
.rec { border: 1px solid var(--app-border); border-radius: 12px; padding: 10px; background: rgba(79,70,229,.06); }
.r1 { display:flex; justify-content:space-between; gap: 10px; align-items:center; }
.score { font-size: 12px; font-weight: 900; color: var(--app-primary); }
.r2 { margin-top: 6px; color:#334155; font-size: 12px; }
.r3 { margin-top: 10px; display:flex; justify-content:flex-end; gap: 8px; }

.composer { display:flex; gap: 10px; align-items:flex-end; }
.btn { border-radius: 10px; border: 1px solid var(--app-border); font-weight: 900; }
.btn-primary {
  border-radius: 10px; border: 1px solid rgba(99,102,241,.25);
  background: linear-gradient(135deg, rgba(99,102,241,.95), rgba(109,40,217,.95)); color:#fff; font-weight: 900;
}
</style>
