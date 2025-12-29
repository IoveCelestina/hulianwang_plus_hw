<template>
  <div class="auth-shell">
    <div class="card">
      <div class="brand">
        <div class="logo">AI</div>
        <div>
          <div class="t1">Smart Ordering</div>
          <div class="t2">登录后开始点餐</div>
        </div>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="form">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>

        <el-button class="btn-primary" :loading="loading" @click="submit">登录</el-button>

        <div class="foot">
          <span class="muted">没有账号？</span>
          <el-button link type="primary" @click="goRegister">去注册</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const loading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({ username: '', password: '' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function submit() {
  if (!formRef.value) return
  await formRef.value.validate(async (ok) => {
    if (!ok) return
    loading.value = true
    try {
      await auth.login({ username: form.username, password: form.password })
      ElMessage.success('登录成功')
      const redirect = (route.query.redirect as string) || '/dishes'
      router.replace(redirect)
    } finally {
      loading.value = false
    }
  })
}
function goRegister() {
  router.push('/register')
}
</script>

<style scoped lang="scss">
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
.brand {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}
.logo {
  width: 42px; height: 42px; border-radius: 12px;
  background: linear-gradient(135deg, var(--app-primary), #6d28d9);
  color: #fff; display: grid; place-items: center; font-weight: 900;
}
.t1 { font-weight: 950; }
.t2 { color: var(--app-muted); font-size: 12px; margin-top: 4px; }
.form { margin-top: 10px; }
.btn-primary {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(99,102,241,.25);
  background: linear-gradient(135deg, rgba(99,102,241,.95), rgba(109,40,217,.95));
  color: #fff;
  font-weight: 900;
}
.foot {
  margin-top: 10px;
  display: flex;
  justify-content: center;
  gap: 6px;
  align-items: center;
}
.muted { color: var(--app-muted); font-size: 12px; }
</style>
