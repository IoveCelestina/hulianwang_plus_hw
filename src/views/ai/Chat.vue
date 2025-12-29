<template>
  <div class="page">
    <div class="left">
      <div class="head">
        <div class="title">AI 点单</div>
        <el-button class="btn" @click="newSession" :loading="creating">新会话</el-button>
      </div>

      <div v-loading="sessionsLoading" class="sessions">
        <div
          v-for="s in sessions"
          :key="s.id"
          class="sitem"
          :data-active="s.id===activeSessionId"
          @click="openSession(s.id)"
        >
          <div class="st">{{ s.title || ('会话 #' + s.id) }}</div>
          <div class="sd" v-if="s.created_at">{{ s.created_at }}</div>
        </div>
      </div>
    </div>

    <div class="right">
      <div class="rhead">
        <div class="rt">{{ activeTitle }}</div>
        <el-button class="btn" @click="reloadMessages" :disabled="!activeSessionId">刷新</el-button>
      </div>

      <div class="msgs" v-loading="msgsLoading" ref="msgBox">
        <div v-if="messages.length===0 && !msgsLoading" class="empty">
          还没有消息，试试问：“推荐两道清淡不辣的菜，并加入购物车”
        </div>

        <div v-for="m in messages" :key="m.id" class="msg" :data-role="m.role">
          <div class="bubble">{{ m.content }}</div>
        </div>
      </div>

      <div class="composer">
        <el-input
          v-model="input"
          type="textarea"
          :rows="2"
          placeholder="输入你的需求，例如：推荐两道不辣的主食，加入购物车"
          @keydown.enter.exact.prevent="send"
        />
        <el-button class="btn-primary" :loading="sending" :disabled="!activeSessionId" @click="send">
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createAiSession, getAiMessages, listAiSessions, postAiMessage, type AiMessageOut, type AiSessionOut } from '@/api/ai'

const sessionsLoading = ref(false)
const sessions = ref<AiSessionOut[]>([])
const activeSessionId = ref<number | null>(null)
const messages = ref<AiMessageOut[]>([])
const msgsLoading = ref(false)

const input = ref('')
const sending = ref(false)
const creating = ref(false)

const msgBox = ref<HTMLDivElement | null>(null)

const activeTitle = computed(() => {
  const s = sessions.value.find(x => x.id === activeSessionId.value)
  return s?.title || (activeSessionId.value ? `会话 #${activeSessionId.value}` : '未选择会话')
})

async function loadSessions() {
  sessionsLoading.value = true
  try {
    sessions.value = await listAiSessions()
    if (!activeSessionId.value && sessions.value.length) {
      await openSession(sessions.value[0].id)
    }
  } finally {
    sessionsLoading.value = false
  }
}

async function openSession(id: number) {
  activeSessionId.value = id
  await reloadMessages()
}

async function reloadMessages() {
  if (!activeSessionId.value) return
  msgsLoading.value = true
  try {
    messages.value = await getAiMessages(activeSessionId.value)
    await nextTick()
    scrollBottom()
  } finally {
    msgsLoading.value = false
  }
}

function scrollBottom() {
  const el = msgBox.value
  if (!el) return
  el.scrollTop = el.scrollHeight
}

async function newSession() {
  creating.value = true
  try {
    const s = await createAiSession({ title: '新的点单会话' })
    await loadSessions()
    await openSession(s.id)
  } catch (e: any) {
    ElMessage.error('创建会话失败（请确认已登录）')
  } finally {
    creating.value = false
  }
}

async function send() {
  if (!activeSessionId.value) {
    ElMessage.warning('请先选择/创建会话')
    return
  }
  const content = input.value.trim()
  if (!content) return

  sending.value = true
  try {
    input.value = ''
    // 先把用户消息塞进去，体验更好
    messages.value = [
      ...messages.value,
      { id: Date.now(), role: 'user', content } as any,
    ]
    await nextTick()
    scrollBottom()

    const res = await postAiMessage(activeSessionId.value, { content })
    // 兼容：后端可能返回一条 assistant，也可能返回全量 messages
    if (Array.isArray(res)) {
      messages.value = res
    } else if (res?.role) {
      messages.value = [...messages.value, res]
    } else {
      // 如果返回结构不确定，就再拉一次
      await reloadMessages()
    }
    await nextTick()
    scrollBottom()
  } catch (e: any) {
    ElMessage.error('发送失败（请确认已登录）')
  } finally {
    sending.value = false
  }
}

onMounted(loadSessions)
</script>

<style scoped lang="scss">
.page { display:flex; gap:12px; padding: 14px; height: calc(100vh - 60px); }

.left {
  width: 280px;
  border: 1px solid var(--app-border);
  border-radius: 12px;
  background: rgba(255,255,255,.78);
  backdrop-filter: blur(10px);
  display:flex;
  flex-direction:column;
  overflow:hidden;
}
.head { padding: 12px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--app-border); }
.title { font-weight: 950; }
.sessions { padding: 8px; overflow:auto; flex:1; }
.sitem { padding: 10px; border-radius: 10px; border:1px solid transparent; cursor:pointer; }
.sitem[data-active="true"] { border-color: rgba(99,102,241,.25); background: rgba(99,102,241,.08); }
.st { font-weight: 900; }
.sd { margin-top: 4px; font-size:12px; color: var(--app-muted); }

.right {
  flex:1;
  border: 1px solid var(--app-border);
  border-radius: 12px;
  background: rgba(255,255,255,.78);
  backdrop-filter: blur(10px);
  display:flex;
  flex-direction:column;
  overflow:hidden;
}
.rhead { padding: 12px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--app-border); }
.rt { font-weight: 950; }

.msgs { flex:1; overflow:auto; padding: 12px; display:flex; flex-direction:column; gap:10px; }
.empty { color: var(--app-muted); text-align:center; padding: 24px 0; }

.msg { display:flex; }
.msg[data-role="user"] { justify-content:flex-end; }
.msg[data-role="assistant"] { justify-content:flex-start; }

.bubble {
  max-width: 72%;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--app-border);
  background: #fff;
  white-space: pre-wrap;
  line-height: 1.5;
}
.msg[data-role="user"] .bubble {
  background: rgba(99,102,241,.10);
  border-color: rgba(99,102,241,.25);
}

.composer {
  padding: 12px;
  border-top:1px solid var(--app-border);
  display:flex;
  gap:10px;
  align-items:flex-end;
}
.btn { border-radius:10px; border:1px solid var(--app-border); }
.btn-primary {
  border-radius: 10px;
  border: 1px solid rgba(99, 102, 241, 0.25);
  background: linear-gradient(135deg, rgba(99,102,241,.95), rgba(109,40,217,.95));
  color: #fff;
}
</style>
