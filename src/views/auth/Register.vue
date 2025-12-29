<template>
  <div class="auth-shell">
    <div class="card">
      <div class="brand">
        <div class="logo">AI</div>
        <div>
          <div class="t1">创建账号</div>
          <div class="t2">注册后会自动登录</div>
        </div>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="form">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="手机号（可选）" prop="phone">
          <el-input v-model="form.phone" placeholder="例如：13800000000" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>

        <el-button class="btn-primary" :loading="loading" @click="submit">注册并登录</el-button>

        <div class="foot">
          <span class="muted">已有账号？</span>
          <el-button link type="primary" @click="goLogin">去登录</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const loading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({ username: '', phone: '', password: '' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  phone: [{ pattern: /^$|^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' }],
}

async function submit() {
  if (!formRef.value) return
  await formRef.value.validate(async (ok) => {
    if (!ok) return
    loading.value = true
    try {
      await auth.register({ username: form.username, password: form.password, phone: form.phone || undefined })
      ElMessage.success('注册成功')
      router.replace('/dishes')
    } finally {
      loading.value = false
    }
  })
}
function goLogin() {
  router.push('/login')
}
</script>

<style scoped lang="scss">
/* 与 Login 统一风格 */
.auth-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: radial-gradient(1200px 600px at 30% 20%, rgba(79,70,229,.16), transparent 60%),
              radial-gradient(900px 500px at 70% 70%, rgba(109,40,217,.14), transparent 55%),
              var(--app-bg);
  padding: 18px;
}
.card {
  width: 440px;
  max-width: 92vw;
  border-radius: 14px;
  border: 1px solid var(--app-border);
  background: rgba(255,255,255,.82);
  backdrop-filter: blur(10px);
  padding: 18px;
  box-shadow: 0 30px 70px rgba(17,24,39,.10);
}
.brand { display:flex; gap:12px; align-items:center; margin-bottom: 12px; }
.logo {
  width: 42px; height: 42px; border-radius: 12px;
  background: linear-gradient(135deg, var(--app-primary), #6d28d9);
  color: #fff; display: grid; place-items: center; font-weight: 900;
}
.t1 { font-weight: 950; }
.t2 { color: var(--app-muted); font-size: 12px; margin-top: 4px; }
.btn-primary {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(99,102,241,.25);
  background: linear-gradient(135deg, rgba(99,102,241,.95), rgba(109,40,217,.95));
  color: #fff;
  font-weight: 900;
}
.foot { margin-top: 10px; display:flex; justify-content:center; gap:6px; align-items:center; }
.muted { color: var(--app-muted); font-size: 12px; }
</style>
